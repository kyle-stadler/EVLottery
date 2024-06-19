# WIP

# Ohio Lottery Live Expected Value Dashboard

This application scrapes data from the Ohio Lottery Website (https://www.ohiolottery.com/games/scratch-offs/prizes-remaining) and stores the number of remaining prizes in a mySQL database. It then calculates the Expected Value (EV) of each game and the expected percentage loss of money from buying the
ticket in the long-run.

## Methodology

The state of Ohio (any many other states) publish a record of the number of prizes remaining for each active lottery ticket daily. This application is
designed to take advantage of potential cases where the jackpot, or other big prizes, have not been claimed at the expected rate. For example, let's say the state prints 100,000 tickets: 5 of those are jackpots, 50,000 are the minimum prize, and the rest are between them. If, say, after 5 months, the number of minimum prize tickets outstandings drops to 30,000 while the number of jackpots remains 5. The odds of hitting the jackpot is higher now then it was when the tickets were first printed.

## Getting Started

This is a WIP application. I want to expand the front-end and host it, but for now you it's all local and you can set it up yourself.

### Prerequisites

Make sure you have the following:

- Python
- Flask
- pandas

### Installation

1. Clone the repository to your local machine.

2. Install the required Python packages.

### Running the Application

1. Set up your mySQL

   - Download mySQL https://www.mysql.com/downloads/
   - Setup your database with a username and password

2. Create a config folder within the scripots directory

   - Within it, creater an **init**.py file and a db.py file
   - Populate the db.py with the db credentias
     ```
     DB_CONFIG = {
     'user': 'root',
     'password': 'foo',
     'host': 'localhost',
     'database': 'database_name'
     }
     ```

3. (WIP: WILL BE AUTOMATED) Run the scripts

   - Run in this order:

   1. scraper.py
   2. removed_vesitgal.py
   3. ev_calc.py

4. Run app.py

5. Open a web browser and navigate to the localhost the app is running on (should show in console)

### Usage

1. The home page (index.html) provides a Dashboard where the expected value of each game is displayed in a table

### File Structure

    app.py: The main Flask application file.
    scripts/
        config/
            db.py: Configuration file for storing sensitive information, such as the database config
            __init__.py: Needed so db info can be imported
        ev_calc.py: Populates the database with the expected values for each game
        remove_vestigal.py: Removes games that are not in cirulation which can get scraped into the databse
        scraper.py: Scrapes game data from the Ohio Lottery website
    templates/
        index.html: Home page template.
    static/
        css/
            style.css: Stylesheet for HTML templates.
