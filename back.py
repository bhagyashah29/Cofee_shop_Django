from models.db import (
    initialize_database,
    upsert_inventory_delta,
    get_inventory_quantity,
    record_sale_amount,
    fetch_inventory,
    fetch_sales,
)


VALID_COFFEE_TYPES = {"arabica", "robusta", "liberica"}


class CoffeeShop:
    def __init__(self):
        initialize_database()

    def add_inventory(self, coffee_type: str, amount: int) -> None:
        if coffee_type not in VALID_COFFEE_TYPES:
            print(f"{coffee_type} is not a valid coffee type")
            return
        if amount <= 0:
            print("Amount must be positive")
            return
        new_qty = upsert_inventory_delta(coffee_type, amount)
        print(f"{amount} kg of {coffee_type} added to inventory (now {new_qty} kg)")

    def update_inventory(self, coffee_type: str, amount: int) -> None:
        if coffee_type not in VALID_COFFEE_TYPES:
            print(f"{coffee_type} is not a valid coffee type")
            return
        if amount <= 0:
            print("Amount must be positive")
            return
        current_qty = get_inventory_quantity(coffee_type)
        if current_qty < amount:
            print(f"{coffee_type} is not in stock")
            print("Not enough inventory")
            return
        new_qty = upsert_inventory_delta(coffee_type, -amount)
        total_sales = record_sale_amount(coffee_type, amount)
        print(f"{amount} kg of {coffee_type} is sold (inventory {new_qty} kg, total sales {total_sales} kg)")

    def view_inventory(self) -> None:
        print("Current inventory:")
        rows = fetch_inventory()
        for coffee_type, amount in rows:
            print(f"{coffee_type}: {amount} kg")

    def view_sales(self) -> None:
        print("Sales data:")
        rows = fetch_sales()
        for coffee_type, amount in rows:
            print(f"{coffee_type}: {amount} kg")


if __name__ == "__main__":
    coffee_shop = CoffeeShop()
    # Seed inventory
    coffee_shop.add_inventory("arabica", 15)
    coffee_shop.add_inventory("robusta", 10)
    coffee_shop.add_inventory("liberica", 20)

    # Sales
    coffee_shop.update_inventory("arabica", 2)
    coffee_shop.update_inventory("robusta", 5)
    coffee_shop.update_inventory("liberica", 10)

    # View
    coffee_shop.view_inventory()
    coffee_shop.view_sales()
        