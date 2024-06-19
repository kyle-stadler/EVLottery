from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
from config import db

def scrape_data():
    # Initialize the headless webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    # Open the webpage
    URL = "https://www.ohiolottery.com/games/scratch-offs/prizes-remaining"
    driver.get(URL)

    # Wait for the display all button to appear and click it
    displayButton = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "(//button[@class='button btn_dcfConfirmRetailerForm'])[3]"))
    )
    displayButton.click()
    prize_list = driver.find_element(By.CLASS_NAME, "wrapper-list")
    return prize_list.text

def classify_scraped_data(prize_list):
    lines = prize_list.split('\n')
    games_and_prizes = {}
    current_title = None
    current_prizes = {}

    for line in lines:
        line = line.strip()
        if line.startswith('('):  # Every game title starts with a (
            if current_title:
                # Saves the previous title's prizes to games_and_prizes
                games_and_prizes[current_title] = current_prizes
            # Start a new title and reset the prize dictionary
            current_title = line
            current_prizes = {}
        elif current_title:
            # Process prize and remaining count lines
            if '$' in line: # Every prize starts with a $
                prize_amount = line
            elif line.replace(',', '').isdigit():
                # Expecting a remaining count
                remaining_count = int(line.replace(',', ''))
                current_prizes[prize_amount] = remaining_count

    # Adding the last collected title and prizes
    if current_title:
        games_and_prizes[current_title] = current_prizes
    return games_and_prizes

def create_and_insert_data(db_config, prize_info):
    # Connect to the MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor() 
    for title, prizes in prize_info.items():
        # Create a sanitized table name
        table_name = title.replace(' ', '_').replace('(', '').replace(')', '').replace('$', '').replace(',', '').replace('\'','')
        # Drop the table if it already exists (TODO: change to add to data)
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        # Create the table
        create_table_query = f"""
        CREATE TABLE `{table_name}` (
            prize VARCHAR(255) NOT NULL,
            remaining INT NOT NULL
        )
        """
        cursor.execute(create_table_query)      
        # Insert the data into the table
        for prize, remaining in prizes.items():
            insert_query = f"INSERT INTO `{table_name}` (prize, remaining) VALUES (%s, %s)"
            cursor.execute(insert_query, (prize, remaining))     
    # Commit the transaction
    conn.commit()
    # Close the cursor and connection
    cursor.close()
    conn.close()

input_string = scrape_data()
prize_info = classify_scraped_data(input_string)

db_config = db.DB_CONFIG

create_and_insert_data(db_config, prize_info)
