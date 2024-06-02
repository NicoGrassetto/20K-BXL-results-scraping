from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://prod.chronorace.be/result/sibp/Classement20km.aspx?eventId=2159234678608985&lng=NL"
driver = webdriver.Firefox(service=Service('/Users/nicograssetto/Desktop/20k-bxl-results-scraping/geckodriver'))
driver.get(url)
driver.maximize_window()  

NUMBER_OF_TABLES = 1948
all_dfs = []
for table_nbr in range(NUMBER_OF_TABLES):
    table_nbr = table_nbr + 1
    print(f"Table number: {table_nbr}")

    # Get all anchors
    anchor_elements = driver.find_elements(By.TAG_NAME, "a")

    # Filter for potentially relevant "next page" anchors
    potential_next_page_anchors = (
        anchor
        for anchor in anchor_elements
        if anchor.get_attribute("data-bind") == "text: $data, click: $root.setPage"
    )

    # Try to find the first relevant anchor with explicit wait
    try:
        next_page_anchor = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable(
                (By.XPATH, ".//a[@data-bind='text: $data, click: $root.setPage'][text()='" + str(table_nbr) + "']")
            )
        )
    except Exception as e:
        print(f"No next page found for table {table_nbr} within 60 seconds")
        continue  # Move to the next table
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    table: Tag = tables[0]

    data = []
    for row in table.find_all("tr")[1:]:
        row_data = [td.text.strip() for td in row.find_all("td")]
        data.append(row_data)

    all_dfs.append(pd.DataFrame(data[1:], columns=data[0]))

    # Click the relevant anchor
    next_page_anchor.click()
    print(f"Clicked next page for table {table_nbr}")

df_combined = pd.concat(all_dfs, ignore_index=True)
df_combined.to_excel("20k-scraped-data.xlsx", index=False)
driver.quit()
