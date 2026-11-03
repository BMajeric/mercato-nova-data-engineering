import pandas as pd
import re
from IPython.display import display

DATA_URL = "data/raw"

def section(title):
    print(f"\n{'-'*80}\n{title}\n{'-'*80}\n")


# SECTION orders.csv
section("ORDERS TABLE - orders.csv")

ORDERS_PATH = f"{DATA_URL}/orders.csv"
df_orders = pd.read_csv(ORDERS_PATH, dtype=str, keep_default_na=False, encoding="utf-8")


print(f"Number of rows and columns:  {df_orders.shape}")
print()

# Checking if the data really has all order ids unique

placeholders = {"", "NA", "N/A", "NULL", "null", "None", "-", "?", "0"}

print("Number of placeholders or null-values and distinct values by column:")
for c in df_orders.columns:
    s = df_orders[c].str.strip()
    n_placeholder = s.isin(placeholders).sum()
    print(f"{c:20s} placeholder-like: {n_placeholder:7d}  distinct: {s.nunique():7d}")

print()


# Result says order_id has some repeats
# Check if those are full repeats or just a reuse of the id for a different order

df_orders_2 = df_orders.copy()
for c in df_orders_2.columns:
    df_orders_2[c] = df_orders_2[c].str.strip()

duplicates = df_orders_2[df_orders_2.duplicated("order_id")]        # keeps only the rows where there was a row with the same order_id before it in the dataframe
dupe_rows = df_orders_2[df_orders_2.duplicated()]                   # keeps fully duplicated rows (all columns hold the same value)
print(f"Surplus rows that are not just pure duplicates:      {len(duplicates) - len(dupe_rows)}")
print(f"Fully duplicated rows:                               {len(dupe_rows)}")
print()

id_prefixes = {}
for order_id in df_orders["order_id"]:
    prefix = order_id[:1]
    if prefix in id_prefixes:
        id_prefixes[prefix] += 1
    else:
        id_prefixes[prefix] = 1

print(f"Order id prefixes and their counts: {id_prefixes}")


# SECTION delivery_events.log
section("DELIVERY APP EXPORT - delivery_events.log")
LOG_PATH = f"{DATA_URL}/delivery_events.log"

with open(LOG_PATH, encoding="utf-8") as f:
    lines = f.read().splitlines()

# Regexes for the general form (time stamp + level + the rest)
# and regex for the rest part to extract the key=value pairs
line_regex = re.compile(r"^\[(?P<ts>[^\]]+)\]\s+(?P<level>\w+)\s+(?P<rest>.*)$")
key_value_regex = re.compile(r"(\w+)=(\S*)")

parsed = []
for n, line in enumerate(lines, start=1):
    m = line_regex.match(line)
    row = {"line_no": n, "timestamp": m["ts"], "level": m["level"]}
    row.update(dict(key_value_regex.findall(m["rest"])))
    row["raw"] = line
    parsed.append(row)

df_log = pd.DataFrame(parsed)
#display(df_log)
print(len(lines), len(df_log))
print()

# Take out all columns that have the line number because it messes with dupe finding
# Line_no colums were just here to see which line it is more clearly even though now looking at the output they seem useless
# since all of the lines have an id that is line number-1 but I will leave them here so it is easier to check without remembering the -1
content_cols = []
for c in df_log.columns:
    if c != "line_no":
        content_cols.append(c)

# Check for duplicate lines
dupes_log = df_log[df_log.duplicated(subset=content_cols)]               # only the dupes
dupes_all = df_log[df_log.duplicated(subset=content_cols, keep=False)]   # dupes and originals to see where the dupes came from

print(f"Number of duplicated log rows: {len(dupes_log)}\n")
print(dupes_all.sort_values("raw").head(20))
print()

# Check if some deliveries got picked up and not delivered

duple_less_log = df_log.drop_duplicates(subset=content_cols)
pd_events = duple_less_log[duple_less_log["event"].isin(["picked_up", "delivered"])]       # keep only pickup and delivery events, drop everything else

print(duple_less_log["event"].value_counts())           # how many occurances of each non-null option (delivered/picked up) are in the event column
groups = pd_events.groupby("order_id")                  # shove all events for one order id into the same group

print(groups["event"].agg(lambda s: tuple(sorted(s))).value_counts())           # show the counts for each unique value for an id


# SECTION customers.json
section("LOYALTY-PROGRAM CRM EXPORT - customers.json")

CUSTOMERS_PATH = f"{DATA_URL}/customers.json"

# Customers list is nested inside the json so it needs to be extracted
tmp = pd.read_json(CUSTOMERS_PATH, dtype=False, encoding="utf-8")
df_customers = pd.json_normalize(tmp["customers"].tolist())

df_customers_2 = df_customers.copy()

# Check for duplicates
dupes_customers = df_customers[df_customers.duplicated()]                       # fully duplicated rows
#dupes_customer_ids = df_customers[df_customers.duplicated("customer_id")]       # rows with the same customer id

print(f"Number of customer rows: {len(df_customers)}")
print(f"Number of duplicated customer rows: {len(dupes_customers)}")
#print(f"Number of duplicated customer ids: {len(dupes_customer_ids)}\n")

# Move the email and phone out of the contact depth
df_customers_2["email"] = df_customers_2["email"].combine_first(df_customers_2["contact.email"])
df_customers_2["phone"] = df_customers_2["phone"].combine_first(df_customers_2["contact.phone"])

# Drop the columns that don't matter for this match or that are no longer needed
df_customers_2 = df_customers_2.drop(columns=["contact.email", "contact.phone", "marketing_opt_in"])

# Clean email
df_customers_2["email"] = df_customers_2["email"].str.strip().str.lower()

## Standardise phone number to +385XXXXXXXXX
def standardise_phone(num):
    if not isinstance(num, str):   # keeps NaN as is because it is treated as a float not string
        return num
    num = num.replace(" ", "")
    m = re.fullmatch(r"0(\d{2})/(\d{3})-(\d{3,4})", num)
    if m:
        return f"+385{m.group(1)}{m.group(2)}{m.group(3)}"
    return num

df_customers_2["phone"] = df_customers_2["phone"].apply(standardise_phone)  # re. functions need apply to work

# Check duplicates by every column to see if people have the same phone numbers or emails
for c in df_customers_2.columns:
    dupes = df_customers_2[df_customers_2.duplicated(c)]
    print(f"Number of duplicated {c}: {len(dupes)}")
print()

# This resulted in the same number of duped emails and phones so I want to know how many times some people were written inside
columns = ["first_name", "last_name", "email", "phone"]
dupes = df_customers_2[df_customers_2.duplicated(subset=columns)]
print(f"How many people have the same first and last name and contact info: {len(dupes)}\n")

# Check how many people have how many dupes
sizes = dupes.groupby(columns, dropna=False).size().sort_values(ascending=False)
print(f"How many people have how many dupes:\nDup  People\n{sizes.value_counts()}\n")

# Check how many people have all info except registration date and id the same
columns = ["first_name", "last_name", "email", "phone", "city", "loyalty_tier"]
dupes_reregister = df_customers_2[df_customers_2.duplicated(subset=columns)]

# Check how many people have exact same entries except for the id (probably real duplicates)
columns = ["first_name", "last_name", "email", "phone", "city", "registered_at", "loyalty_tier"]
dupes_complete = df_customers_2[df_customers_2.duplicated(subset=columns, keep=False)]      # dupes with originals
dupes_only = df_customers_2[df_customers_2.duplicated(subset=columns)]                      # dupes without originals

print(f"Number of people who probably re-registered: {len(dupes_reregister)-(len(dupes_only))}")    
print(f"Number of people who are complete duplicates except ids: {len(dupes_only)}\n")
print(dupes_complete)

print()
display(df_customers_2)

