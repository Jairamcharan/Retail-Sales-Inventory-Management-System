import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "retail.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            sale_date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    conn.commit()
    conn.close()

def clear_fields():
    name_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    stock_entry.delete(0, tk.END)

def refresh_products():
    for item in product_tree.get_children():
        product_tree.delete(item)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, product_name, category, price, stock FROM products")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        product_tree.insert("", tk.END, values=row)

def add_product():
    name = name_entry.get().strip()
    category = category_entry.get().strip()

    try:
        price = float(price_entry.get())
        stock = int(stock_entry.get())
        if not name or not category or price < 0 or stock < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Enter valid product details.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (product_name, category, price, stock) VALUES (?, ?, ?, ?)",
        (name, category, price, stock)
    )
    conn.commit()
    conn.close()

    clear_fields()
    refresh_products()
    messagebox.showinfo("Success", "Product added successfully.")

def search_products():
    keyword = search_entry.get().strip()

    for item in product_tree.get_children():
        product_tree.delete(item)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_id, product_name, category, price, stock
        FROM products
        WHERE product_name LIKE ? OR category LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        product_tree.insert("", tk.END, values=row)

def record_sale():
    selected = product_tree.selection()

    if not selected:
        messagebox.showwarning("Select Product", "Select a product first.")
        return

    item = product_tree.item(selected[0])
    product_id, name, category, price, stock = item["values"]

    try:
        quantity = int(quantity_entry.get())
        if quantity <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Quantity", "Enter a valid quantity.")
        return

    if quantity > int(stock):
        messagebox.showerror("Insufficient Stock", "Not enough stock available.")
        return

    total = float(price) * quantity
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE products SET stock = stock - ? WHERE product_id = ?",
        (quantity, product_id)
    )

    cursor.execute(
        """INSERT INTO sales (product_id, quantity, total_amount, sale_date)
           VALUES (?, ?, ?, ?)""",
        (product_id, quantity, total, date)
    )

    conn.commit()
    conn.close()

    quantity_entry.delete(0, tk.END)
    refresh_products()
    messagebox.showinfo("Sale Recorded", f"Sale recorded. Total: ₹{total:.2f}")

def show_low_stock():
    for item in product_tree.get_children():
        product_tree.delete(item)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_id, product_name, category, price, stock
        FROM products
        WHERE stock <= 5
    """)
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        product_tree.insert("", tk.END, values=row)

def show_sales_summary():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM sales")
    count, revenue = cursor.fetchone()

    cursor.execute("""
        SELECT COALESCE(SUM(quantity), 0)
        FROM sales
    """)
    units = cursor.fetchone()[0]

    conn.close()

    messagebox.showinfo(
        "Sales Summary",
        f"Total Transactions: {count}\n"
        f"Units Sold: {units}\n"
        f"Total Revenue: ₹{revenue:.2f}"
    )

setup_database()

root = tk.Tk()
root.title("Retail Sales & Inventory Management")
root.geometry("900x600")

title = ttk.Label(
    root,
    text="Retail Sales & Inventory Management",
    font=("Arial", 18, "bold")
)
title.pack(pady=10)

form = ttk.Frame(root)
form.pack(pady=5)

ttk.Label(form, text="Product Name").grid(row=0, column=0, padx=5, pady=5)
name_entry = ttk.Entry(form, width=22)
name_entry.grid(row=0, column=1, padx=5)

ttk.Label(form, text="Category").grid(row=0, column=2, padx=5)
category_entry = ttk.Entry(form, width=18)
category_entry.grid(row=0, column=3, padx=5)

ttk.Label(form, text="Price").grid(row=1, column=0, padx=5, pady=5)
price_entry = ttk.Entry(form, width=22)
price_entry.grid(row=1, column=1, padx=5)

ttk.Label(form, text="Stock").grid(row=1, column=2, padx=5)
stock_entry = ttk.Entry(form, width=18)
stock_entry.grid(row=1, column=3, padx=5)

ttk.Button(form, text="Add Product", command=add_product).grid(
    row=2, column=0, columnspan=4, pady=8
)

search_frame = ttk.Frame(root)
search_frame.pack(pady=5)

ttk.Label(search_frame, text="Search").pack(side=tk.LEFT, padx=5)
search_entry = ttk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(search_frame, text="Search", command=search_products).pack(side=tk.LEFT, padx=5)
ttk.Button(search_frame, text="Show All", command=refresh_products).pack(side=tk.LEFT, padx=5)
ttk.Button(search_frame, text="Low Stock", command=show_low_stock).pack(side=tk.LEFT, padx=5)

columns = ("ID", "Product", "Category", "Price", "Stock")
product_tree = ttk.Treeview(root, columns=columns, show="headings", height=14)

for column in columns:
    product_tree.heading(column, text=column)
    product_tree.column(column, width=150)

product_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

sale_frame = ttk.Frame(root)
sale_frame.pack(pady=8)

ttk.Label(sale_frame, text="Quantity").pack(side=tk.LEFT, padx=5)
quantity_entry = ttk.Entry(sale_frame, width=10)
quantity_entry.pack(side=tk.LEFT, padx=5)

ttk.Button(sale_frame, text="Record Sale", command=record_sale).pack(side=tk.LEFT, padx=5)
ttk.Button(sale_frame, text="Sales Summary", command=show_sales_summary).pack(side=tk.LEFT, padx=5)

refresh_products()
root.mainloop()
