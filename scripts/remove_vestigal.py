import mysql.connector
from config import db

# This script is needed since there are some games that get scraped that are not in circulation anymore

db_config = db.DB_CONFIG

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Retrieve the list of table names from the 'ticket' column of the 'winning_odds' table
cursor.execute("SELECT ticket FROM winning_odds")
tickets = cursor.fetchall()
ticket_tables = {ticket[0] for ticket in tickets}

# Retrieve the list of all tables in the database
cursor.execute("SHOW TABLES")
all_tables = cursor.fetchall()
all_tables = {table[0] for table in all_tables}

# Identify tables not present in the 'ticket' column of the 'winning_odds' table, since these tix are in cirulation
tables_to_drop = all_tables - ticket_tables - {'winning_odds'}

# Drop tables not listed in the 'ticket' column of the 'winning_odds' table
for table in tables_to_drop:
    drop_query = f"DROP TABLE {table}"
    cursor.execute(drop_query)
    print(f"Table {table} has been dropped.")

# Close the connection
conn.commit()
cursor.close()
conn.close()