import pandas as pd
import os
import re

# File locations
DATA_URL = "data/raw"
OUTPUT_URL = "output"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_URL, exist_ok=True)

# Load orders
ORDERS_PATH = f"{DATA_URL}/orders.csv"

df_orders = pd.read_csv(ORDERS_PATH, dtype=str, keep_default_na=False, encoding="utf-8")

print("Original shape:", df_orders.shape)
#print(df_orders.head())

def section(title):
    print(f"\n{'-'*80}\n{title}\n{'-'*80}\n")

# ===================================================================================================================================================
# Task 1: Revenue
section("Task 1: Revenue")

# Remove unnecessary whitespace from all columns
for col in df_orders.columns:
    df_orders[col] = df_orders[col].str.strip()

# Count exact duplicate rows
duplicate_count = df_orders.duplicated().sum()

print("Exact duplicate rows:", duplicate_count)

# Remove exact duplicates
df_orders = df_orders.drop_duplicates().copy()

print("Rows after deduplication:", len(df_orders))

# Handle datetime differences
# Create an empty datetime column
df_orders["order_ts_parsed"] = pd.NaT

# Identify the two timestamp formats
format_us = df_orders["order_ts"].str.contains("/", regex=False)
format_eu = df_orders["order_ts"].str.contains(".", regex=False)

# Parse the first format
df_orders.loc[format_us, "order_ts_parsed"] = pd.to_datetime(
    df_orders.loc[format_us, "order_ts"],
    format="%m/%d/%Y %H:%M",
    errors="coerce"
)

# Parse the second format
df_orders.loc[format_eu, "order_ts_parsed"] = pd.to_datetime(
    df_orders.loc[format_eu, "order_ts"],
    format="%d.%m.%Y %H:%M:%S",
    errors="coerce"
)

print()
# Check parsing results
print("Unparsed timestamps:", df_orders["order_ts_parsed"].isna().sum())

print(df_orders[["order_ts", "order_ts_parsed"]].head(10))

# Handle currency conversion
# Convert amount from string to numeric
df_orders["amount"] = pd.to_numeric(df_orders["amount"],errors="coerce")

print()
# Check for invalid amounts
print("Invalid amounts:", df_orders["amount"].isna().sum())

# Create EUR amount column
df_orders["amount_eur"] = df_orders["amount"]

# Identify orders before 2023
hrk_orders = df_orders["order_ts_parsed"] < pd.Timestamp("2023-01-01")

# Convert HRK to EUR
df_orders.loc[hrk_orders, "amount_eur"] = (df_orders.loc[hrk_orders, "amount"] / 7.5345)

print(df_orders[["order_ts", "amount", "amount_eur"]].head(10))

# Calculate monthly net revenue
# Create a monthly column
df_orders["month"] = df_orders["order_ts_parsed"].dt.to_period("M")

# Calculate monthly net revenue
monthly_revenue = (df_orders.groupby("month")["amount_eur"].sum().reset_index())

# Include every month from January 2022 to December 2024
all_months = pd.period_range(start="2022-01",end="2024-12",freq="M")

# Set month as the index
monthly_revenue = monthly_revenue.set_index("month")

# Add any missing months, filling them with 0
monthly_revenue = monthly_revenue.reindex(all_months, fill_value=0)

# Turn month back into a regular column
monthly_revenue = monthly_revenue.rename_axis("month").reset_index()

# Round revenue to two decimal places
monthly_revenue["amount_eur"] = monthly_revenue["amount_eur"].round(2)

# Rename the column
monthly_revenue.columns = ["month", "net_revenue_eur"]

print("\nMONTHLY NET REVENUE (EUR)")
print(monthly_revenue.to_string(index=False))

# Export the monthly revenue to csv
monthly_revenue.to_csv(f"{OUTPUT_URL}/monthly_revenue.csv",index=False)

print("\nRevenue results saved successfully.")


# ===================================================================================================================================================
# Task 2: Average order to delivery time
section("Task 2: Average order to delivery time")

# File location
LOG_PATH = f"{DATA_URL}/delivery_events.log"

# Read delivery log
with open(LOG_PATH, encoding="utf-8") as f:
    lines = f.read().splitlines()

print("Number of log lines:", len(lines))

# Regular expressions for parsing
line_regex = re.compile(r"^\[(?P<ts>[^\]]+)\]\s+(?P<level>\w+)\s+(?P<rest>.*)$")
key_value_regex = re.compile(r"(\w+)=(\S*)")

# Parse log lines
parsed = []

for n, line in enumerate(lines, start=1):
    match = line_regex.match(line)
    if match is None:
        print("Could not parse line:", n, line)
        continue
    row = {"line_no": n, "timestamp": match["ts"], "level": match["level"]}
    row.update(dict(key_value_regex.findall(match["rest"])))
    parsed.append(row)

# Create DataFrame
df_log = pd.DataFrame(parsed)

print("Parsed log rows:", len(df_log))
print("\nFirst five rows:")
print(df_log.head().to_string(index=False))

# Use everything except added line number to compare log entries
content_cols = []
for col in df_log.columns:
    if col != "line_no":
        content_cols.append(col)

# Count duplicate entries
duplicate_logs = df_log.duplicated(subset=content_cols).sum()

print("\nDuplicate log entries:", duplicate_logs)

# Remove duplicates
df_log = df_log.drop_duplicates(subset=content_cols).copy()

print("Log rows after deduplication:", len(df_log))

# Convert timestamps to UTC
df_log["timestamp"] = pd.to_datetime(df_log["timestamp"],utc=True,errors="coerce")

# Check conversion
print("\nUnparsed delivery timestamps:", df_log["timestamp"].isna().sum())

print(df_log[["timestamp", "event", "order_id"]].head(10))

# Keep only pickup and delivery events
delivery_events = df_log[df_log["event"].isin(["picked_up", "delivered"])].copy()

# Count events for each order
event_counts = (delivery_events.groupby(["order_id", "event"]).size().unstack(fill_value=0))

# Make sure both columns exist
for event in ["picked_up", "delivered"]:
    if event not in event_counts.columns:
        event_counts[event] = 0

# Count orders by event combination
event_combinations = (event_counts.groupby(["picked_up", "delivered"]).size().reset_index(name="number_of_orders"))

print("\nEVENT COMBINATIONS")
print(event_combinations.to_string(index=False))

# Find orders with multiple pickup events
multiple_pickups = event_counts[event_counts["picked_up"] > 1]

# Find orders with multiple delivery events
multiple_deliveries = event_counts[event_counts["delivered"] > 1]

print("\nOrders with multiple pickup events:", len(multiple_pickups))
print("Orders with multiple delivery events:", len(multiple_deliveries))

# Keep only delivery events
delivery_events = df_log[df_log["event"] == "delivered"].copy()

# Keep one delivery timestamp per order
event_times = delivery_events[["order_id", "timestamp"]].rename(columns={"timestamp": "delivered"})

print("Delivered orders:", len(event_times))
print(event_times.head())

# Keep web orders only
web_orders = df_orders[df_orders["channel"] == "web"].copy()

# Keep only the columns needed for this analysis
web_orders = web_orders[["order_id", "order_ts_parsed", "delivery_zone"]]

# Match orders with theeir delivery timestamps
df_delivery = web_orders.merge(event_times,on="order_id",how="inner")

print("Web orders:", len(web_orders))
print("Orders matched to delivery events:", len(df_delivery))
print("Orders without delivery events:", len(web_orders) - len(df_delivery))

print(df_delivery.head())

# Convert order timestamps to Croatian local time
df_delivery["order_ts_local"] = (df_delivery["order_ts_parsed"].dt.tz_localize("Europe/Zagreb"))

# Convert to UTC
df_delivery["order_ts_utc"] = (df_delivery["order_ts_local"].dt.tz_convert("UTC"))

# Calculate order-to-delivery time in minutes
df_delivery["delivery_minutes"] = (df_delivery["delivered"] - df_delivery["order_ts_utc"]).dt.total_seconds() / 60

print("Average delivery time:", df_delivery["delivery_minutes"].mean())

# Calculate average delivery time per zone
zone_delivery = (df_delivery.groupby("delivery_zone")["delivery_minutes"].mean().reset_index())

zone_delivery["delivery_minutes"] = zone_delivery["delivery_minutes"].round(2)

print(zone_delivery)

# Create a month column from the order timestamp
df_delivery["month"] = df_delivery["order_ts_parsed"].dt.to_period("M")

# Calculate average delivery time by month and zone
monthly_zone_delivery = (df_delivery.groupby(["month", "delivery_zone"])["delivery_minutes"].mean().reset_index())

monthly_zone_delivery["delivery_minutes"] = (monthly_zone_delivery["delivery_minutes"].round(2))

print(monthly_zone_delivery.head(15))

# Save the results
monthly_zone_delivery.to_csv(f"{OUTPUT_URL}/monthly_delivery_by_zone.csv",index=False)

# ===================================================================================================================================================
# Task 4: Operations question for zone 3
section("Task 4: Operations question for zone 3")

# Select Zone 3 orders
zone_3 = df_delivery[df_delivery["delivery_zone"] == "3"].copy()

# Select June-August 2023
before_autumn = zone_3[(zone_3["month"] >= "2023-06") &(zone_3["month"] <= "2023-08")]

# Select September-November 2023
autumn = zone_3[(zone_3["month"] >= "2023-09") &(zone_3["month"] <= "2023-11")]

# Calculate averages
print("Zone 3 average before autumn:", round(before_autumn["delivery_minutes"].mean(), 2))
print("Zone 3 average during autumn:", round(autumn["delivery_minutes"].mean(), 2))

# A check to see how the delivery times moved for zone 3 to see what to say to the operations manager
zone_3_2023 = monthly_zone_delivery[(monthly_zone_delivery["delivery_zone"] == "3") &(monthly_zone_delivery["month"].astype(str).str.startswith("2023"))]

print(zone_3_2023)