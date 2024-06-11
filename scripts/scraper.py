from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# def scrape_ohio_lottery():
# Initialize the webdriver
driver = webdriver.Chrome()

# Open the webpage
url = "https://www.ohiolottery.com/games/scratch-offs/prizes-remaining"
driver.get(url)


displayButton = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, "(//button[@class='button btn_dcfConfirmRetailerForm'])[3]"))
)
displayButton.click()


prize_list = driver.find_element(By.CLASS_NAME, "wrapper-list")

driver.close()
# return prize_list.text

