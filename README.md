# Mercato Nova – Data Engineering Take-Home Task

## 1. Project overview

This project analyses Mercato Nova's operational data to answer business questions related to revenue, delivery performance and customer loyalty.

Python and pandas are used to profile, clean, transform and analyse the raw datasets. The analysis produces structured output files that support the final results and recommendations.

## 2. Requirements and setup

Requirements:
- Python 3
- pandas (if using the profiling scripts as well)

Install the required packages:

```bash
pip install pandas
```

DuckDB was attempted to be used but I switched to pandas due to issues with DuckDB.

## 3. How to run

Put the necessary data files into `data/raw/` before running the scripts. Run all commands from the project root directory.

1. Run the data profiling script.

```bash
python profile_raw.py
```

2. Run the analysis script:

```bash
python analysis.py
```

The scripts read the original files from `data/raw/` and save the analysis results in the `output/` directory.

## 4. Data quality findings

### orders.csv
- Order timestamps use two formats (MM/DD/YYYY HH:MM and DD.MM.YYYY HH:MM:SS) and do not include timezone information.
- Transaction amounts look like they are in HRK before 1 January 2023 and EUR from that date onward. Earlier amounts were converted using the fixed rate of 1 EUR = 7.5345 HRK.
- The dataset has 912 rows with exactly one duplicate (not only a reused order_id but a full duplicate row).

### customers.json
- After 30.6.2023, there is a shift in the CRM schema, moving phone number and email into a separate nested object and adding the marketing_opt_in field.
- Some phone numbers are written in an international format (e.g. +385991234567) and some are written in the local format (099/123-4567).
- Some emails are written in all lowercase, and some have uppercase letters.
- There are 179 entries that have exactly one duplicate that has a different customer ID, different registered_at and all other fields the same, representing the same person who registered again.
- There are 35 entries that have exactly one duplicate that has all the fields except the customer ID the same, representing duplicate entries probably made by the app itself.

### delivery_events.log
- The timestamps here use the ISO 8601 format and include UTC timezone information, which is different from the one in orders.csv.
- The logs contain 158 duplicated rows, which were removed during the analysis.
- There are 605 orders that were picked up but never delivered.
- In total, 1,153 web orders could not be matched to a completed delivery event.
- The events aren't ordered by the timestamp, but the timeline checks out (deliveries are consistently after pickups).

## 5. Important assumptions

- **Timezone:** timestamps in orders.csv are assumed to represent local Croatian time (Europe/Zagreb). They were converted to UTC before being compared with delivery event timestamps.
- **Currency:** transactions in orders.csv dated before 1.1.2023 are treated as HRK and converted to EUR using 1 EUR = 7.5345 HRK. Transactions from that date onward are treated as EUR.
- **Duplicate orders:** exact duplicates in orders.csv are treated as double writes and are handled by removing the duplicate.
- **Refunds:** Refunds are represented by negative transaction amounts and are included in net revenue calculations. They are attributed to the month in which the refund transaction was recorded.
- **Delivery records:** Delivery-time calculations use orders with matching pickup and delivery events. Orders without a completed delivery event are excluded from average delivery-time calculations.

## 6. Results and answers to the assignments

### Task 1: Monthly net revenue
- Monthly net revenue was calculated from sales and refund transactions, with all amounts converted to EUR.
- Revenue shows an overall upward trend from 2022 to 2024, with December being the highest-revenue month in each year.
- Full monthly results are available in output/monthly_revenue.csv.
- Since this was pure conversion of currencies and then summing of values, and having figured out the switch of currency, I would say I am very confident in my answer.

### Task 2: Average delivery time
- The average delivery time for orders that have both pickup and delivery events was 75.27 minutes.
- Average delivery time varies by zone, Zone 1 having the shortest average at 62.14 minutes, while Zone 5 had the longest at 86.45 minutes.
- Monthly delivery performance by zone is available in output/monthly_delivery_by_zone.csv.
- Since this task included a lot of timezone conversion and table matching, as well as due to not including transitions from Winter to Summer time calculation and vice versa, I would say I am aware that the results are not 100% correct, but I am confident that they are extremely close to the realistic value.

### Task 3: Churn
- Churn analysis was not completed this time, but it would have looked at how many people have had an order in 2024 or had their loyalty membership renewed or started in that year. Since we do not have information on how long a membership lasts and when it ends, the "lost" members would be ones that hadn't made an order in 2024 and didn't start that membership in that year.

### Task 4: Operations question
- Zone 3 experienced a substantial increase in delivery time from September to November 2023, with its average increasing to 117.63 minutes compared to 68.84 minutes for the period right before that, from June to August (an increase in delivery time of around 70.9%).
- I would recommend hiring an additional driver for Zone 3, although I can't guarantee that would solve the issue completely.
- Having not performed a thorough analysis of the reason the delivery times increased in autumn of 2023, I would not say that my recommendation is surely correct, but I also do think that hiring another driver would boost delivery times in that zone. The one aspect I am not so sure about is by how much.

## Next steps

- Investigate the sustained increase in delivery times in Zone 3 in autumn of 2023 and how they correlate to the number of drivers in that area, their working hours and workload to determine the need for additional drivers.
- Complete the customer loyalty and churn analysis, including a comparison of cancellations and new loyalty registrations.
- Conduct a thorough investigation into the 605 missing deliveries, trying to find matches with low battery or lost GPS logs and see if these are really incomplete deliveries or just missing records.

## AI tool usage

AI agents were used as assistant tools during the assignment to help educate myself more directly and help write and troubleshoot the Python scripts and unsuccessful SQL and database code. All ideas and data findings were made by me and the co-authored code was reviewed, understood, hand-written and most of the time altered by myself to ensure proper understanding.