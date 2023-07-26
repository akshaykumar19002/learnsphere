from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


def scrape_indeed(job_name):
    website = 'https://www.indeed.com/career/python-developer/career-advice/Canada--KY?from=top_sb'
    driver = webdriver.Chrome()
    driver.get(website)

    # Find the search box element using its by css selector
    search_box = driver.find_element("id", "input-title-autocomplete")
    search_clear = driver.find_element("id", "clear-title-localized")
    search_clear.click()
    # Clear the existing value (if any) and enter the keyword
    search_box.send_keys(job_name)
    find_jobs_desc = driver.find_element("id", "title-location-search-btn")
    find_jobs_desc.click()
    driver.implicitly_wait(90)
    sleep(10)

    notes = []
    end_index = 0
    restrict = 0
    for lis in driver.find_elements(By.XPATH, '//li'):
        notes.append(lis.text)
        if restrict == 0:
            if lis.text.startswith("interviewing"):
                end = lis.text
                end_index = notes.index(end)
                restrict = 1
            elif lis.text.endswith("2023 Indeed"):
                end = lis.text
                end_index = notes.index(end)
                restrict = 1

    notes.remove('Skills')
    start_index = notes.index('Skills') + 1
    desired_list = notes[start_index:end_index]
    driver.quit()  # Close the driver after scraping

    return desired_list[:-1]  # Return the list of elements
