CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    gender VARCHAR(6) NOT NULL,
    "DOB" DATE
);

CREATE TABLE IF NOT EXISTS prop_feats (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    wealth_segment VARCHAR(50) NOT NULL,
    deceased_indicator CHAR(1) NOT NULL,
    owns_car VARCHAR(3) NOT NULL,
    property_valuation INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS job_title (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    job_title VARCHAR(100),
    job_industry_category VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS location (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    address VARCHAR(255) NOT NULL,
    postcode VARCHAR(20) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT NOT NULL,
    brand VARCHAR(50),
    product_line VARCHAR(15) NOT NULL,
    product_class VARCHAR(6) NOT NULL,
    product_size VARCHAR(6),
    list_price DECIMAL(10, 2) NOT NULL,
    standard_cost DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (product_id, brand)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    transaction_date DATE NOT NULL,
    online_order BOOLEAN,
    order_status VARCHAR(25) NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    brand VARCHAR(50) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id, brand) REFERENCES products(product_id, brand)
);