class CoffeShop:
    def __init__(self):
        self.inventory = {
        'arabica': 0,
        'robusta': 0,
        'liberica': 0
    }
        self.sales = {
        'arabica': 0,
        'robusta': 0,
        'liberica': 0
    }
    def add_inventory(self,coffee_type,amout):
        if coffe_type in self_inventory:
           self.inventory[coffe_type]+=amount
           print(f"{amount} kg of {coffee_type} added in inventory")
        else:
            print(f"{coffee_type} is not a valid coffee type")
            
    def update_inventory(self,coffee_type,amount):
        if coffee_type in self.inventory:
            if self.inventory[coffee_type]<amount:
                print(f"{coffee_type}is not in stock") 
                print("not enough inventory")
            else:
                self.inventory[coffee_type]-=amount
                print(f"{amount}kg of{coffee_type}is sold.")
                self.inventory[coffee_type]+=amount   
        else:
            print(f"{coffee_type}is not a valid coffee type")
            
    def view_inventory(self):
        print(f"current_inventory")
        for cofee_type,amount in self.inventory.items():
            print(f"{coffee_type}:{amount}kg")
            
    def view_sales(self):
        print(f"sales data:")
        for coffee_type,amount in self.inventory.sales.items():
            print(f"{coffee_type}:{amount}kg")
            
            coffee_shop=Coffee_Shop()
            
        #add inventory
        coffee_shop.add_inventory('arabica',15)
        coffee_shop.add_inventory('robusta',10)
        coffee_shop.add_inventory('liberica',20)
        
        #update invenotry and record sales
        coffee_shop.update_inventory('arabica',20)
        coffee_shop.update_inventory('robusta',5)
        coffee_shop.update_inventory('liberica',10)
        
        #view current inventory and sales
        coffee_shop.view_inventory()
        coffee_shop.view_sales()
        