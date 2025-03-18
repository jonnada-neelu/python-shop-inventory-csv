# Program
import csv
import logging
import os
from tabulate import tabulate

logging.basicConfig(filename="shop.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")


class Product:
    def __init__(self, product_id, name, price, quantity):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity


class Inventory:
    def __init__(self, filename="inventory.csv"):
        self.filename = filename
        self.products = self.load_inventory()

    def load_inventory(self):
        """Load inventory from CSV file"""
        products = {}
        if not os.path.exists(self.filename):
            logging.warning("Inventory file not found. Creating a new one.")
            return products
        try:
            with open(self.filename, "r") as file:
                reader = csv.reader(file)
                next(reader, None)  
                for row in reader:
                    if len(row) < 4:  
                        continue
                    product_id, name, price, quantity = row
                    products[product_id] = Product(product_id, name, float(price), int(quantity))
        except Exception as e:
            logging.error(f"Error loading inventory: {e}")
        return products

    def save_inventory(self):
        """Save inventory back to CSV file"""
        with open(self.filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["product_id", "product_name", "price", "quantity"])
            for product in self.products.values():
                writer.writerow([product.product_id, product.name, product.price, product.quantity])

    def add_product(self, product_id, name, price, quantity):
        """Add a new product to inventory"""
        if product_id in self.products:
            logging.error("Product ID already exists")
            print("Product ID already exists!")
            return
        self.products[product_id] = Product(product_id, name, price, quantity)
        self.save_inventory()
        logging.info(f"Added product {name} with ID {product_id}.")
        print("Product added successfully!")

    def view_inventory(self):
        """Display inventory in tabular format"""
        if not self.products:
            print("No products in inventory.")
            return
        table = [[p.product_id, p.name, p.price, p.quantity] for p in self.products.values()]
        print(tabulate(table, headers=["Product ID", "Name", "Price", "Stock"], tablefmt="grid"))


class Sale:
    def __init__(self, sale_id):
        self.sale_id = sale_id
        self.items = []

    def add_item(self, product, quantity):
        total_price = product.price * quantity
        self.items.append([product.product_id, product.name, quantity, total_price])
        return total_price


class SalesManager:
    def __init__(self, filename="sales.csv"):
        self.filename = filename
        self.ensure_sales_file()

    def ensure_sales_file(self):
        """Create sales file if it does not exist"""
        if not os.path.exists(self.filename):
            with open(self.filename, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Sale ID", "Product ID", "Product Name", "Quantity Sold", "Total Price"])

    def get_existing_sales(self):
        """Return a list of existing sale IDs"""
        sales = set()
        try:
            with open(self.filename, "r") as file:
                reader = csv.reader(file)
                next(reader, None)  
                for row in reader:
                    if row:
                        sales.add(row[0])
        except FileNotFoundError:
            pass
        return sales

    def save_sale(self, sale):
        """Save sale to file"""
        existing_sales = self.get_existing_sales()
        if sale.sale_id in existing_sales:
            logging.error(f"Sale ID {sale.sale_id} already exists. Choose a different ID.")
            print("Sale ID already exists. Choose a different ID.")
            return

        with open(self.filename, "a", newline="") as file:
            writer = csv.writer(file)
            for item in sale.items:
                writer.writerow([sale.sale_id] + item)
        logging.info(f"Sale {sale.sale_id} recorded successfully.")

    def view_sales(self):
        """Display sales report"""
        if not os.path.exists(self.filename):
            print("No sales recorded yet.")
            return

        with open(self.filename, "r") as file:
            reader = csv.reader(file)
            sales = list(reader)
            if len(sales) <= 1:
                print("No sales recorded yet.")
                return
            print(tabulate(sales, headers="firstrow", tablefmt="grid"))


class ShopSystem:
    def __init__(self):
        self.inventory = Inventory()
        self.sales_manager = SalesManager()

    def menu(self):
        while True:
            print("\n--- Small Shop Management System ---")
            print("1. View Inventory")
            print("2. Add Product to Inventory")
            print("3. Process a Sale")
            print("4. View Sales Report")
            print("5. Exit")
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.inventory.view_inventory()
            elif choice == "2":
                self.add_product()
            elif choice == "3":
                self.process_sale()
            elif choice == "4":
                self.sales_manager.view_sales()
            elif choice == "5":
                print("Exiting system. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def add_product(self):
        product_id = input("Enter product ID: ").strip()
        name = input("Enter product name: ").strip()
        try:
            price = float(input("Enter product price: ").strip())
            quantity = int(input("Enter stock quantity: ").strip())
        except ValueError:
            print("Invalid input! Price must be a number, and quantity must be an integer.")
            return
        self.inventory.add_product(product_id, name, price, quantity)

    def process_sale(self):
        sale_id = input("Enter Sale ID: ").strip()
        sale = Sale(sale_id)
        while True:
            product_id = input("Enter Product ID to sell (or 'done' to finish): ").strip()
            if product_id.lower() == "done":
                break
            if product_id not in self.inventory.products:
                print("Invalid Product ID. Try again.")
                continue
            product = self.inventory.products[product_id]
            try:
                quantity = int(input(f"Enter quantity for {product.name}: ").strip())
                if quantity > product.quantity:
                    print("Not enough stock available.")
                    continue
                total_price = sale.add_item(product, quantity)
                product.quantity -= quantity
                print(f"Added {quantity} of {product.name} to sale. Total: ${total_price:.2f}")
            except ValueError:
                print("Invalid quantity! Enter a valid integer.")
                continue
        self.inventory.save_inventory()
        self.sales_manager.save_sale(sale)
        print(f"Sale {sale_id} recorded successfully.")


if __name__ == "__main__":
    ShopSystem().menu()
