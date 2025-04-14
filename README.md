# Grocery Store Management System 🛒

A full-stack web application to manage products, orders, and inventory for a grocery store. Built with Flask, MySQL, HTML/CSS, Bootstrap, and JavaScript.

## 🔧 Features

- User registration and login system
- Add and delete products
- Assign categories to products
- Place orders with quantity and stock checks
- Cancel orders with automatic stock restoration
- Flash messages for success and errors
- Responsive UI with Bootstrap
- Session-based authentication

## 🧰 Tech Stack

- Python (Flask)
- MySQL
- HTML & CSS
- Bootstrap 5
- JavaScript

## 📁 Project Structure

- /templates – HTML templates (login, signup, index, etc.)
- /static – CSS and other static files
- app.py – Main Flask app
- grocery_store2 – MySQL database with product, category, order, log tables

## 🗃️ Database Tables

- categories
- products
- orders
- order_items
- users
- logs

## 🚀 Getting Started

1. Clone the repo  
2. Create a MySQL database named `grocery_store2`  
3. Import the SQL schema (manually or via script)  
4. Run the Flask app:

```bash
python app.py
Navigate to http://localhost:5000