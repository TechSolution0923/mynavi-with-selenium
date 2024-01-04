from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def main():

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox") # linux only    
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--headless=new") # for Chrome >= 109
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")

    service=Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://job.mynavi.jp/25/pc/")

    WebDriverWait(driver=driver, timeout=5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "nav03"))
    )

    goToCompany(driver)
    time.sleep(5)

    page_total_number = get_total_number(driver)
    
    scraping_result = []
    company_url_names = []
    for i in range(page_total_number - 1):
        company_url_names.extend(scrape_company_name_url(driver))
        driver.find_element(By.CSS_SELECTOR, "a#upperNextPage").click()
        time.sleep(1)

    for company_url_name in company_url_names:
        print(company_url_name['url'])
        driver.get(company_url_name['url'])
        company_main_info = scrape_company_main_info(driver)
        print(company_main_info)
        scraping_result.append({
            "company_url": company_url_name['url'],
            "company_name": company_url_name['name'],
            "company_location": company_main_info['company_location'],
            "company_members": company_main_info['company_members']
        })

def goToCompany(driver):
    driver.find_element(By.CSS_SELECTOR, ".nav03 > a").click()

    WebDriverWait(driver=driver, timeout=5).until(
        EC.presence_of_element_located((By.ID, "indGroup0"))
    )

    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    driver.find_element(By.CSS_SELECTOR, "div#indGroup0 > div.listInnerBody > p.check > span:nth-of-type(1) > a").click()

    driver.find_element(By.CSS_SELECTOR, "div#indGroup1 > h6").click()
    driver.find_element(By.CSS_SELECTOR, "div#indGroup1 > div.listInnerBody > p.check > span:nth-of-type(1) > a").click()
    
    driver.find_element(By.CSS_SELECTOR, "div#indGroup2 > h6").click()
    driver.find_element(By.CSS_SELECTOR, "div#indGroup2 > div.listInnerBody > p.check > span:nth-of-type(1) > a").click()

    driver.find_element(By.CSS_SELECTOR, "div#indGroup3 > h6").click()
    driver.find_element(By.CSS_SELECTOR, "div#indGroup3 > div.listInnerBody > p.check > span:nth-of-type(1) > a").click()

    driver.find_element(By.CSS_SELECTOR, "div#indGroup4 > h6").click()
    driver.find_element(By.CSS_SELECTOR, "div#indGroup4 > div.listInnerBody > p.check > span:nth-of-type(1) > a").click()

    driver.find_element(By.CSS_SELECTOR, "div#indGroup5 > h6").click()
    driver.find_element(By.CSS_SELECTOR, "div#indGroup5 > div.listInnerBody > p.check > span:nth-of-type(1) > a").click()

    driver.find_element(By.CSS_SELECTOR, "div#indGroup6 > h6").click()
    driver.find_element(By.CSS_SELECTOR, "div#indGroup6 > div.listInnerBody > p.check > span:nth-of-type(1) > a").click()

    driver.find_element(By.CSS_SELECTOR, "div#indGroup7 > h6").click()
    driver.find_element(By.CSS_SELECTOR, "div#indGroup7 > div.listInnerBody > p.check > span:nth-of-type(1) > a").click()

    time.sleep(5)

    driver.find_element(By.CSS_SELECTOR, "button#doSearch").click()

def get_total_number(driver):
    WebDriverWait(driver=driver, timeout=5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "mainpagePnation"))
    )

    total_number_element = driver.find_element(By.CSS_SELECTOR, "div.mainpagePnation > div.inner > p.count > span.txt3").text
    total_number = int(''.join(filter(str.isdigit, total_number_element.split("/")[1].split(")")[0])))
    return total_number

def scrape_company_name_url(driver):
    company_data = []
    try:
        sel = Selector(text = driver.page_source)
        for item in sel.xpath("//div[contains(@id, 'contentsleft')] / div[contains(@class, 'boxSearchresultEach')]"):
            company_data.append({
                'name' : item.css('div.boxSearchresultEach_head > h3.withCheck > a::text').get().replace("\u3000", ""),
                'url' : "https://job.mynavi.jp" + item.css('div.boxSearchresultEach_head > h3.withCheck > a::attr(href)').get()
            })
    except:
        print("Error: Fetch Failed Company Url and Name")
    return company_data

def scrape_company_main_info(driver):
    WebDriverWait(driver=driver, timeout=5).until(
        EC.presence_of_element_located((By.ID, "companyData"))
    )

    company_location = ''
    company_members = []

    try:
        company_location = driver.find_element(By.CSS_SELECTOR, "td#corpDescDtoListDescText50").text
    except:
        print("In this, there is no location")

    try:
        driver.find_element(By.CSS_SELECTOR, "#headerObogTabLink").click()
        time.sleep(3)

        sel = Selector(text = driver.page_source)
        for item in sel.xpath("//table[contains(@class, 'personList')] / tbody / tr"):
            company_members.append({
                'article_title': item.css('td.personData > div.personText > h2 > a::text').get(), 
                'article_url': "https://job.mynavi.jp" + item.css('td.personData > div.personText > h2 > a::attr(href)').get(),
                'name': item.css('td.personData > div.personText > p.person::text').get().replace("\n", "").replace(" ", "")
            })
    except:
        print("In here, there is no member's info")

    return {
        'company_location': company_location.replace("\u3000", " "),
        'company_members': company_members
    }

if __name__ == '__main__':
    main()
