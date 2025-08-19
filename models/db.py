import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple


# Compute the path to the existing Django SQLite database (db.sqlite3 at project root)
DATABASE_PATH = Path(__file__).resolve().parents[1] / 'db.sqlite3'


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def initialize_database() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                coffee_type TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                coffee_type TEXT PRIMARY KEY,
                amount INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


def upsert_inventory_delta(coffee_type: str, delta_quantity: int) -> int:
    """Increase or decrease inventory by delta; returns the resulting quantity."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO inventory (coffee_type, quantity) VALUES (?, 0)",
            (coffee_type,),
        )
        cursor.execute(
            "UPDATE inventory SET quantity = quantity + ? WHERE coffee_type = ?",
            (delta_quantity, coffee_type),
        )
        cursor.execute(
            "SELECT quantity FROM inventory WHERE coffee_type = ?",
            (coffee_type,),
        )
        row = cursor.fetchone()
        conn.commit()
    return int(row[0]) if row else 0


def get_inventory_quantity(coffee_type: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT quantity FROM inventory WHERE coffee_type = ?",
            (coffee_type,),
        )
        row = cursor.fetchone()
    return int(row[0]) if row else 0


def record_sale_amount(coffee_type: str, add_amount: int) -> int:
    """Increase total sales for a coffee type by add_amount; returns the total."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO sales (coffee_type, amount) VALUES (?, 0)",
            (coffee_type,),
        )
        cursor.execute(
            "UPDATE sales SET amount = amount + ? WHERE coffee_type = ?",
            (add_amount, coffee_type),
        )
        cursor.execute(
            "SELECT amount FROM sales WHERE coffee_type = ?",
            (coffee_type,),
        )
        row = cursor.fetchone()
        conn.commit()
    return int(row[0]) if row else 0


def fetch_inventory() -> List[Tuple[str, int]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT coffee_type, quantity FROM inventory ORDER BY coffee_type ASC")
        rows = cursor.fetchall()
    return [(str(coffee_type), int(quantity)) for coffee_type, quantity in rows]


def fetch_sales() -> List[Tuple[str, int]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT coffee_type, amount FROM sales ORDER BY coffee_type ASC")
        rows = cursor.fetchall()
    return [(str(coffee_type), int(amount)) for coffee_type, amount in rows]

