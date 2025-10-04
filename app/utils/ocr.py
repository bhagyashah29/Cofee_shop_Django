from __future__ import annotations
import io
import json
from datetime import datetime
from typing import Dict, Any

from flask import current_app
from PIL import Image

try:
    import pytesseract
except Exception:  # pragma: no cover
    pytesseract = None


class OCRResult:
    def __init__(self, text: str, fields: Dict[str, Any]):
        self.text = text
        self.fields = fields

    def to_json(self) -> str:
        return json.dumps({"text": self.text, "fields": self.fields})


def parse_receipt(image_bytes: bytes) -> OCRResult:
    if not current_app.config.get("OCR_ENABLED", True):
        return OCRResult(text="", fields={})

    if pytesseract is None:
        return OCRResult(text="", fields={})

    tesseract_cmd = current_app.config.get("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)

    # Very naive heuristics to extract some fields
    fields: Dict[str, Any] = {}
    for line in text.splitlines():
        low = line.lower().strip()
        if "total" in low or "amount" in low:
            # pull the last numeric token
            tokens = [t for t in low.replace(",", " ").split() if any(c.isdigit() for c in t)]
            if tokens:
                try:
                    fields["amount"] = float(tokens[-1].replace("$", ""))
                except Exception:
                    pass
        if "date" in low or "/" in low or "-" in low:
            fields.setdefault("date", str(datetime.utcnow().date()))
        if "restaurant" in low or "cafe" in low or "store" in low:
            fields.setdefault("merchant", line.strip())

    return OCRResult(text=text, fields=fields)
