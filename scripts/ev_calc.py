from config import db
import mysql.connector
import pandas as pd
import re

# Connect to db and initiate a cursor
db_config = db.DB_CONFIG
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def calculate_ev(prize, remaining, remaining_sum):
    if remaining == 0:
        return 0
    # REGEX needed here to account for the prizes that are in the {xK/YR for y years} format
    annual_amount_match = re.search(r'\$([\d]+)K/YR FOR (\d+) YRS', prize)
    lump_sum_match = re.search(r'\$(\d+)', prize)
    if annual_amount_match: # Converts {xK/YR for y years} to a lump sum payment
        annual_amount = int(annual_amount_match.group(1)) * 1000  # Convert K to thousands
        years = int(annual_amount_match.group(2))
        prize = annual_amount * years
    elif lump_sum_match: # Some cases have lump sum options {$ xxx}
        prize = int(lump_sum_match.group(1))
    else: # Handles all others {$xxx}
        prize = re.sub(r'[^\d.]', '', str(prize))
        prize = int(float(prize))
    # Calculate expected value
    expected_value = prize * (remaining / remaining_sum)
    return expected_value

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

# Dictionary to store total expected values for each table
table_ev = {}

# Iterate through each table and calculate the EV for each prize
for table in tables:
    table_name = table[0]
    
    # Skip the 'winning_odds' table
    if table_name == 'winning_odds':
        continue
    
    # Check if the expected_value column exists, if not, add it
    cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE 'expected_value'")
    result = cursor.fetchone()
    if result is None:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN expected_value DOUBLE")
    
    # Fetch the data from the table
    cursor.execute(f"SELECT prize, remaining FROM {table_name}")
    data = cursor.fetchall()
    
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data, columns=['prize', 'remaining'])
    
    remaining_row_sum = df['remaining'].sum()

    # Calculate the expected value for each row
    df['expected_value'] = df.apply(lambda row: calculate_ev(row['prize'], row['remaining'], remaining_row_sum), axis=1)
    
    # Update the expected_value column in the table
    for index, row in df.iterrows():
        cursor.execute(f"""
            UPDATE {table_name}
            SET expected_value = %s
            WHERE prize = %s AND remaining = %s
        """, (row['expected_value'], row['prize'], row['remaining']))
    
    # Commit the changes to the db
    conn.commit()
    
    # Calculate the total expected value for the table
    total_expected_value = df['expected_value'].sum()
    table_ev[table_name] = total_expected_value

# Add a new column to 'winning_odds' to store EV/odds if it doesn't exist
cursor.execute("SHOW COLUMNS FROM winning_odds LIKE 'ev_gross'")
result = cursor.fetchone()
if result is None:
    cursor.execute("ALTER TABLE winning_odds ADD COLUMN ev_gross DOUBLE")

# Add new columns to 'winning_odds' to store net ev and % loss if they don't exist
cursor.execute("SHOW COLUMNS FROM winning_odds LIKE 'ev_net'")
result = cursor.fetchone()
if result is None:
    cursor.execute("ALTER TABLE winning_odds ADD COLUMN ev_net DOUBLE")

cursor.execute("SHOW COLUMNS FROM winning_odds LIKE 'percent_loss'")
result = cursor.fetchone()
if result is None:
    cursor.execute("ALTER TABLE winning_odds ADD COLUMN percent_loss VARCHAR(10)")

# Fetch odds for each table from the 'winning_odds' table
cursor.execute("SELECT ticket, odds FROM winning_odds")
odds_data = cursor.fetchall()
odds_dict = {ticket: odds for ticket, odds in odds_data}

# Updating | populating the gross ev in the 'winning_odds' table
for table_name, total_ev in table_ev.items():
    odds = odds_dict.get(table_name, None)
    if odds is not None:
        ev_gross = total_ev / odds
        # Update the winning_odds table with the calculated ev_gross
        cursor.execute("""
            UPDATE winning_odds
            SET ev_gross = %s
            WHERE ticket = %s
        """, (ev_gross, table_name))

# Commit the changes to the database
conn.commit()

# Fetch the updated EV/odds data
cursor.execute("SELECT ticket, ev_gross FROM winning_odds")
ev_data = cursor.fetchall()

# Updating | populating the gross ev and percent loss in the 'winning_odds' table
for ticket, ev_gross in ev_data:
    # Extract the cost from the ticket name (last digit or digits)
    cost_match = re.search(r'_(\d+)$', ticket)
    if cost_match:
        cost = int(cost_match.group(1))
        ev_net = ev_gross - cost
        percent_loss = 1 - (ev_gross / cost)
        percent_loss_str = f"{percent_loss * -100:.2f}%"
        cursor.execute("""
            UPDATE winning_odds
            SET ev_net = %s, percent_loss = %s
            WHERE ticket = %s
        """, (ev_net, percent_loss_str, ticket))

# Commit the changes to the database
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()
