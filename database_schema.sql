CREATE DATABASE IF NOT EXISTS ecommerce_analytics;
USE ecommerce_analytics;

CREATE TABLE customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    gender VARCHAR(10),
    age INT,
    city VARCHAR(50),
    signup_date DATE
);

CREATE TABLE products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(12,2)
);

CREATE TABLE orders (
    order_id VARCHAR(12) PRIMARY KEY,
    customer_id VARCHAR(10),
    order_date DATE,
    payment_method VARCHAR(30),
    status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_id VARCHAR(12),
    product_id VARCHAR(10),
    quantity INT,
    unit_price DECIMAL(12,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
