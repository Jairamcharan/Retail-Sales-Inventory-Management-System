# Retail Sales & Inventory Management System

project built with **Python, Tkinter, and SQL (SQLite)**.

## Features
- Add products
- View products
- Search by product name or category
- Record sales
- Automatically reduce stock after a sale
- Identify low-stock products
- View sales summary
- Store data permanently in an SQL database

## Technologies
- Python
- Tkinter
- SQL
- SQLite

## How to Run

1. Install Python 3.
2. Open Terminal in this folder.
3. Run:

```bash
python3 app.py
```

The `retail.db` database is created automatically the first time the application runs.

## Database

### products
- product_id
- product_name
- category
- price
- stock

### sales
- sale_id
- product_id
- quantity
- total_amount
- sale_date

**Retail Sales & Inventory Management System | Python, SQL, SQLite**

Developed a desktop application to manage products, inventory, and sales using Python and SQL. Implemented product search, stock tracking, sales recording, automatic stock updates, low-stock detection, and sales summary features using a relational SQLite database.
