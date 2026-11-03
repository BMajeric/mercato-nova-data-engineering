CREATE TABLE IF NOT EXISTS stores (
    store_id VARCHAR PRIMARY KEY,
    store_name VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    store_address VARCHAR
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    phone VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL,
    loyalty_tier VARCHAR NOT NULL,
    marketing_opt_in BOOLEAN
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR PRIMARY KEY,
    order_timestamp TIMESTAMPTZ NOT NULL,
    channel VARCHAR NOT NULL,
    delivery_zone INTEGER,
    currency_original VARCHAR(3) NOT NULL,
    amount_original DECIMAL(12,2) NOT NULL,
    amount_eur DECIMAL(12,2) NOT NULL,
    original_order_id VARCHAR REFERENCES orders(order_id),
    store_id VARCHAR REFERENCES stores(store_id) NOT NULL,
    customer_id VARCHAR REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS delivery_events (
    delivery_id BIGINT PRIMARY KEY,
    delivery_timestamp TIMESTAMPTZ NOT NULL,
    alert_level VARCHAR NOT NULL,
    message_type VARCHAR NOT NULL,
    event_type VARCHAR,
    order_id VARCHAR REFERENCES orders(order_id),
    driver_id VARCHAR NOT NULL,
    app_version VARCHAR,
    battery INTEGER,
    raw_message VARCHAR NOT NULL
);