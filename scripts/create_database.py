import duckdb

DB_PATH = "db/mercato_nova.duckdb"

sql_paths = [
    "db/create_tables.sql",
    "db/create_staging_tables.sql"
]

# Connect to database file
con = duckdb.connect(DB_PATH)

# Read and execute SQL
for sql_file in sql_paths:
    with open(sql_file, "r", encoding="utf-8") as f:
        con.execute(f.read())

# Verify tables
print(con.execute("SHOW TABLES").fetchdf())

con.close()