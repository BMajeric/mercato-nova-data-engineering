CREATE TABLE IF NOT EXISTS stg_orders (
    order_id VARCHAR,
    order_ts VARCHAR,
    channel VARCHAR,
    store_id VARCHAR,
    delivery_zone VARCHAR,
    customer_id VARCHAR,
    amount VARCHAR,
    original_order_id VARCHAR
);

CREATE TABLE IF NOT EXISTS stg_stores (
    store_id VARCHAR,
    store_name VARCHAR,
    city VARCHAR,
    address VARCHAR
);

CREATE TABLE IF NOT EXISTS stg_customers (
    customer_id VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    city VARCHAR,
    registered_at VARCHAR,
    loyalty_tier VARCHAR,
    marketing_opt_in VARCHAR
);

CREATE TABLE IF NOT EXISTS stg_delivery_events (
    source_line_number BIGINT,
    delivery_timestamp VARCHAR,
    alert_level VARCHAR,
    message_type VARCHAR,
    event_type VARCHAR,
    order_id VARCHAR,
    driver_id VARCHAR,
    app_version VARCHAR,
    battery VARCHAR,
    raw_message VARCHAR
);