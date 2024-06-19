from flask import Flask, render_template
import mysql.connector
from scripts.config import db

app = Flask(__name__)

# MySQL connection configuration (taken from config/db.py)
db_config = db.DB_CONFIG

@app.route('/')
def index():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to fetch data from winning_odds table
        query = "SELECT ticket, odds, ev_gross, ev_net, percent_loss FROM winning_odds;"
        cursor.execute(query)
        data = cursor.fetchall()

        # Close cursor and connection
        cursor.close()
        conn.close()

        # Render template with data
        return render_template('index.html', data=data)

    except mysql.connector.Error as e:
        print(f"Error retrieving data from MySQL: {e}")
        return "Error fetching data from database"

if __name__ == '__main__':
    app.run(debug=True)
