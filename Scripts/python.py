import streamlit as st
import pandas as pd
import sqlite3
from faker import Faker
from datetime import datetime


# Database Manager Class
class DatabaseManager:
    def __init__(self, db_name="zomato.db"):
        self.db_name = db_name
        self.init_db()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        conn = self.connect()
        cursor = conn.cursor()

        # Customers Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            signup_date TEXT,
            is_premium BOOLEAN,
            preferred_cuisine TEXT,
            total_orders INTEGER,
            average_rating REAL
        )''')

        # Restaurants Table
        cursor.execute('''CREATE TABLE IF NOT EXISTS Restaurants (
            restaurant_id INTEGER PRIMARY KEY,
            name TEXT,
            cuisine_type TEXT,
            location TEXT,
            owner_name TEXT,
            average_delivery_time REAL,
            contact_number TEXT,
            rating REAL,
            total_orders INTEGER,
            is_active BOOLEAN
        )''')

        conn.commit()
        conn.close()

    def execute_query(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        conn.close()

    def fetch_query(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results

    # CRUD Operations
    def create_entry(self, table, data):
        placeholders = ", ".join(["?" for _ in data])
        columns = ", ".join(data.keys())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(data.values()))

    def read_entries(self, table):
        query = f"SELECT * FROM {table}"
        return self.fetch_query(query)

  

    def delete_entry(self, table, where_clause, where_values):
        query = f"DELETE FROM {table} WHERE {where_clause}"
        self.execute_query(query, tuple(where_values))


# Streamlit UI Class
# StreamlitUI class
class StreamlitUI:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def home_page(self):
        st.subheader("Welcome to Zomato Data Insights")

    def view_data(self):
        st.subheader("View Data")
        table = st.selectbox("Select Table to View", ["Customers", "Restaurants"])
        data = self.db_manager.read_entries(table)
        columns = self.get_table_columns(table)
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(df)

    def get_table_columns(self, table):
        if table == "Customers":
            return [
                "Customer ID", "Name", "Email", "Phone", "Location", "Signup Date",
                "Is Premium", "Preferred Cuisine", "Total Orders", "Average Rating"
            ]
        elif table == "Restaurants":
            return [
                "Restaurant ID", "Name", "Cuisine Type", "Location", "Owner Name",
                "Average Delivery Time", "Contact Number", "Rating", "Total Orders", "Is Active"
            ]

    def add_data(self):
        st.subheader("Add New Data")
        choice = st.selectbox("Select Data to Add", ["Customer", "Restaurant"])
        if choice == "Customer":
            self.add_customer()
        elif choice == "Restaurant":
            self.add_restaurant()

    def add_customer(self):
        st.subheader("Add New Customer")
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        location = st.text_input("Location")
        signup_date = st.date_input("Signup Date")
        is_premium = st.checkbox("Is Premium?")
        preferred_cuisine = st.selectbox("Preferred Cuisine", ["Indian", "Chinese", "Italian", "Mexican", "American"])
        total_orders = st.number_input("Total Orders", min_value=1, max_value=1000)
        average_rating = st.number_input("Average Rating", min_value=1.0, max_value=5.0, step=0.1)

        if st.button("Add Customer"):
            data = {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "signup_date": signup_date.strftime("%Y-%m-%d"),
                "is_premium": is_premium,
                "preferred_cuisine": preferred_cuisine,
                "total_orders": total_orders,
                "average_rating": average_rating,
            }
            self.db_manager.create_entry("Customers", data)
            st.success("Customer added successfully!")

    def add_restaurant(self):
        st.subheader("Add New Restaurant")
        name = st.text_input("Restaurant Name")
        cuisine_type = st.selectbox("Cuisine Type", ["Indian", "Chinese", "Italian", "Mexican", "American"])
        location = st.text_input("Location")
        owner_name = st.text_input("Owner Name")
        avg_delivery_time = st.number_input("Average Delivery Time (mins)", min_value=1, max_value=180)
        contact_number = st.text_input("Contact Number")
        rating = st.number_input("Rating", min_value=1.0, max_value=5.0, step=0.1)
        total_orders = st.number_input("Total Orders", min_value=1, max_value=5000)
        is_active = st.checkbox("Is Active?")

        if st.button("Add Restaurant"):
            data = {
                "name": name,
                "cuisine_type": cuisine_type,
                "location": location,
                "owner_name": owner_name,
                "average_delivery_time": avg_delivery_time,
                "contact_number": contact_number,
                "rating": rating,
                "total_orders": total_orders,
                "is_active": is_active,
            }
            self.db_manager.create_entry("Restaurants", data)
            st.success("Restaurant added successfully!")

   
    
    def delete_data(self):
        st.subheader("Delete Data")
        table = st.selectbox("Select Table to Delete From", ["Customers", "Restaurants"])
        id_to_delete = st.number_input(f"Enter {table[:-1]} ID to Delete", min_value=1)
        if st.button("Delete"):
            self.db_manager.delete_entry(table, f"{table[:-1].lower()}_id = ?", [id_to_delete])
            st.success(f"{table[:-1]} deleted successfully!")


# Main App
def app():
    db_manager = DatabaseManager()
    ui = StreamlitUI(db_manager)

    st.title("Zomato Data Insights Tool")
    menu = ["Home", "View Data", "Add Data", "Delete Data"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        ui.home_page()
    elif choice == "View Data":
        ui.view_data()
    elif choice == "Add Data":
        ui.add_data()
  
    elif choice == "Delete Data":
        ui.delete_data()


if __name__ == "__main__":
    app()
