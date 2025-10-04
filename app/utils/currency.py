from __future__ import annotations
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple

import requests
from flask import current_app
from ..extensions import db
from ..models import ExchangeRateCache


CACHE_TTL_MINUTES = 60


def fetch_countries_and_currencies() -> Dict[str, str]:
    url = current_app.config["RESTCOUNTRIES_API_URL"]
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    country_to_currency: Dict[str, str] = {}
    for item in data:
        name = item.get("name", {}).get("common") or item.get("name", {}).get("official")
        currencies = item.get("currencies", {})
        currency_codes = list(currencies.keys()) if currencies else []
        if name and currency_codes:
            country_to_currency[name] = currency_codes[0]
    return dict(sorted(country_to_currency.items(), key=lambda kv: kv[0]))


def get_rates_cached(base_currency: str) -> Dict[str, float]:
    base_currency = base_currency.upper()
    cache: ExchangeRateCache | None = ExchangeRateCache.query.filter_by(base_currency=base_currency).first()
    if cache and cache.fetched_at > datetime.utcnow() - timedelta(minutes=CACHE_TTL_MINUTES):
        return json.loads(cache.rates_json)

    url = f"{current_app.config['EXCHANGE_RATE_API_BASE_URL']}/{base_currency}"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    rates = data.get("rates") or {}

    if cache is None:
        cache = ExchangeRateCache(base_currency=base_currency, rates_json=json.dumps(rates))
        db.session.add(cache)
    else:
        cache.rates_json = json.dumps(rates)
        cache.fetched_at = datetime.utcnow()
    db.session.commit()
    return rates


def convert_amount(amount: float, from_currency: str, to_currency: str) -> Tuple[float, float]:
    if from_currency.upper() == to_currency.upper():
        return amount, 1.0
    rates = get_rates_cached(from_currency.upper())
    rate = rates.get(to_currency.upper())
    if rate is None:
        # Fallback: try reverse via base
        base_rates = get_rates_cached("USD")
        rate_from = base_rates.get(from_currency.upper())
        rate_to = base_rates.get(to_currency.upper())
        if rate_from and rate_to:
            rate = rate_to / rate_from
    if rate is None:
        raise ValueError(f"No conversion rate from {from_currency} to {to_currency}")
    return amount * rate, rate
