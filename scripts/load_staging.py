import duckdb
import json

DB_PATH = "db/mercato_nova.duckdb"

# Connect to database file
con = duckdb.connect(DB_PATH)

# Execute the insertion of orders into the staging table
con.execute("""
    INSERT INTO stg_orders
    SELECT *
    FROM read_csv(
        'data/raw/orders.csv',
        all_varchar = true,
        header = true
    )
""")

# Execute the insertion of stores into the staging table 
con.execute("""
    INSERT INTO stg_stores
    SELECT * 
    FROM read_csv(
        'data/raw/stores.csv',
        all_varchar = true,
        header = true
    )
""")

print(f"Orders: {con.execute("SELECT COUNT(*) FROM stg_orders").fetchone()[0]}")
print(f"Stores: {con.execute("SELECT COUNT(*) FROM stg_stores").fetchone()[0]}")

con.close()
