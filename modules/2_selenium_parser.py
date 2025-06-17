"""
This script automates the process of scraping detailed product information from the Rozetka online store using Selenium and undetected-chromedriver.

Key features:
- Launches Chrome in undetectable mode to bypass anti-bot detection.
- Navigates to Rozetka’s homepage and performs a search for "Apple iPhone 15 128GB Black".
- Clicks on the first search result and extracts various product data, including:
  - Full name
  - Color and memory size
  - Promotional and regular prices
  - Product code and number of reviews
  - Series, screen diagonal, and display resolution
  - Seller information (either as text or from an image alt attribute)
  - All product image links
  - Full product specifications from the "Характеристики" tab

Utility functions:
- `human_typing()` simulates realistic typing delays.
- `parse_data()` handles basic element text extraction with safe error handling.
- `wait_until()` ensures elements are visible before interacting with them.

At the end, all collected data is saved to an Excel file using `save_to_exel()`.

Requirements:
- undetected_chromedriver
- Selenium
- openpyxl_templates (for saving to Excel)
"""
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException,NoSuchAttributeException
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC

from _7_exel_template_write import save_to_exel


url = "https://rozetka.com.ua/"
options = uc.ChromeOptions()

# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-notifications")
# options.add_argument("--headless")

options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")
driver = uc.Chrome(options=options)

driver.get(url)
time.sleep(10)

wait = WebDriverWait(driver, 10) 

def wait_until(element, timeout=10):
    wait = WebDriverWait(driver, timeout)
    wait.until(lambda _ : element.is_displayed())

def human_typing(element, text, min_delay=0.05, max_delay=0.15):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))

def parse_data(element):
    try:
        element = driver.find_element(By.XPATH, element)
        return element.text.strip()
    except (NoSuchElementException):
        return None
    except Exception as e:
        print(f"[parse_data] Error: {e}")
        return None

try:

    text_box = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="search"]')))

    wait_until(text_box)
    human_typing(text_box, "Apple iPhone 15 128GB Black")

except NoSuchElementException as e:
    print(f"Error when try find_element:text_box: {e}")

try:
    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Знайти")]')))
    wait_until(submit_button)

    
    submit_button.click()
    time.sleep(10)

except NoSuchElementException as e:
    print(f"Error when try find_element:submit_button: {e}")


try:
    first_result_link = driver.find_element(By.XPATH,'(//ul[@class="catalog-grid"]/li[1]//a)[1]')
    wait_until(first_result_link)

    first_result_link.click()

except NoSuchElementException as e:
    print(f"Error when try find_element:first_result: {e}")

time.sleep(10)

print("first_result_link.clicked ")
print("="*50)

data = {}

data["full_name_of_the_product"] = parse_data('//h1')

data["color"] = parse_data('//div[@class="var-options"]/p/span[contains(text(),"Колір")]/following-sibling::span')
memory_size_raw = parse_data( '//div[@class="var-options"]/p/span[contains(text(),"Вбудована пам\'ять")]/following-sibling::span') 
data["memory_size"] = int(memory_size_raw.replace('ГБ', '').strip()) if memory_size_raw else None
promotional_price_raw =parse_data( '//p[@class="product-price__small"]/following-sibling::p') 
data["promotional_price"] = int(promotional_price_raw.replace('₴', '').replace('\xa0', '').replace(' ', '').strip()) if promotional_price_raw else None
regular_price_raw = parse_data( '//p[@class="product-price__small"]') 
data["regular_price"] = int(regular_price_raw.replace('₴', '').replace('\xa0', '').replace(' ', '').strip()) if regular_price_raw else None
product_code_raw = parse_data( '//div[@class="product-about__right"]//div[@class="rating text-base"]/span')
data["product_code"] = int(product_code_raw.replace("Код:", "").strip()) if product_code_raw else None
number_of_reviews_raw = parse_data( '//div[@class="product-about__right"]//div[@class="rating text-base"]/a')
data["number_of_reviews"] =int( number_of_reviews_raw.replace("відгуки", "").strip()) if product_code_raw else None
data["series"] = parse_data( '//dl/div[dt[@class="label" and span[contains(text(),"Серія")]]]/dd')
data["screen_diagonal"] = parse_data( '//dl/div[dt[@class="label" and span[contains(text(),"Діагональ екрана")]]]/dd')
data["display_resolution"] = parse_data( '//dl/div[dt[@class="label" and span[contains(text(),"Роздільна здатність дисплея")]]]/dd')

print("simple data parsed")
print("="*50)

try:
    seller_block = driver.find_element(By.XPATH, '//p[@class="seller-title"]')
    wait_until(seller_block)

    try:
        seller_name = seller_block.find_element(By.XPATH, './/a').text
    except NoSuchElementException:
        try:
            seller_name = seller_block.find_element(By.XPATH, './/img').get_attribute('alt')
        except NoSuchElementException:
            seller_name = None
            
    data["seller"] = seller_name

except NoSuchElementException:
    seller_name = None



images = []

try:
    ul = driver.find_element('xpath','//div[@class="scrollbar__content"]/ul')
    wait_until(ul)
except NoSuchElementException as e:
    ul = None


if ul:
    try:
        img_list = ul.find_elements(By.XPATH,'./li//img')
        if img_list and len(img_list) > 0:
            [wait_until(img) for img in img_list]

        if img_list:
            for i,img in enumerate(img_list):
                images.append(img.get_attribute("src"))
                
        data["all_product_photos"] = images

    except NoSuchElementException as e:
        img_list = None


product_specifications = {}

try:
    link_a =  driver.find_element(By.XPATH,'//a[contains(text(),"Характеристики")]')
    wait_until(link_a)

    if link_a:       
        link_a.click()
        time.sleep(10)

except NoSuchElementException as e:
    link_a = None

try:

    wait.until(EC.presence_of_element_located((By.XPATH, '//main[@class="product-tabs__content"]//section')))
    product_specifications_sections = driver.find_elements(By.XPATH,'//main[@class="product-tabs__content"]//section/dl')
    wait_until(product_specifications_sections[0])

    if product_specifications_sections:
        for i,dl in enumerate(product_specifications_sections):
            specs = {}
            divs = dl.find_elements(By.XPATH,'./div')
            for div in divs:
                dts = div.find_elements(By.XPATH, './dt')
                dds = div.find_elements(By.XPATH, './dd')
                for dt, dd in zip(dts, dds):
                    specs[dt.text.strip()] = dd.text.strip()
                product_specifications[f"product_specification_{i}"] = specs
    else:
        product_specifications[f"product_specification_0"] = None

    data["product_specifications"] = product_specifications

except NoSuchElementException as e:
    product_specifications_sections = None

print(data)
save_to_exel(data,"selenium_parse")

driver.quit()
