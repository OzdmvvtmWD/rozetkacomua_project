"""
This script is a web scraper designed to extract product data from a specific product page on the Ukrainian e-commerce website Rozetka.

It uses `cloudscraper` and `BeautifulSoup` to bypass Cloudflare protection and parse the HTML content of the page. The script collects key mobile phone product details such as:

- Product name
- Price (regular and promotional)
- Color and memory size
- Product code and number of reviews
- Series, screen diagonal, and display resolution
- Seller information
- All product photos (image URLs)
- Full product specifications (grouped into sections)

The collected data is:
1. Saved to an Excel file using a templated workbook (`openpyxl_templates`);
2. Saved to a Django database, creating a new `Mobile` object (or retrieving one if it already exists);
3. Saves each photo URL as a `Photo` object linked via ForeignKey to the corresponding `Mobile` entry.

The script can be used as part of a larger data aggregation or e-commerce monitoring system to collect structured information from product pages.
"""


import requests
import cloudscraper
# from requests.AttributeErrors import ProxyError,ConnectionError,Timeout
from bs4 import BeautifulSoup

from load_django import *
from parser_app.models import Photo, Mobile
from _7_exel_template_write import save_to_exel




data={}
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}
url = "https://rozetka.com.ua/apple-iphone-15-128gb-black/p395460480/"


scraper = cloudscraper.create_scraper()
response = scraper.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')
try:
    data["full_name_of_the_product"] = soup.h1.text.strip()
except AttributeError:
    data["full_name_of_the_product"] = None

try:
    price = soup.find('p', class_='product-price__small')
    data["regular_price"] = int(price.text.replace('\xa0', '').replace('₴', '').strip())
except AttributeError:
    data["regular_price"] = None
try:
    data["promotional_price"] =int( price.find_next('p').text.replace('\xa0', '').replace('₴', '').strip())
except AttributeError:
    data["promotional_price"] = None

try:
    var_options = soup.find_all('div', class_='var-options')
    color_found = None
    for v in var_options:
        try:
            color_span = v.find('p').find('span', string=lambda t: t and "Колір" in t)
            if color_span:
                color_found = color_span.find_next('span').text.strip()
                break
        except AttributeError:
            continue
    data["color"] = color_found
except AttributeError:
    data["color"] = None

try:
    memory_found = None
    for v in var_options:
        try:
            memory_span = v.find('p').find('span', string=lambda t: t and "Вбудована пам'ять" in t)
            if memory_span:
                memory_found = memory_span.find_next('span').text.replace('ГБ', '').strip()
                break
        except AttributeError:
            continue
    data["memory_size"] = int(memory_found)
except AttributeError:
    data["memory_size"] = None

try:
    product_about = soup.find('div', class_='product-about__right')
    rating_div = product_about.find('div', class_='rating text-base')
    code_span = rating_div.find('span')
    data["product_code"] = int(code_span.text.replace('\xa0', '').replace('Код:', '').strip())
except AttributeError:
    data["product_code"] = None

try:
    review_span = soup.find('div', class_="product-comment-rating").find('span', string=lambda t: t and "відгуки" in t)
    data["number_of_reviews"] = int(review_span.text.replace("відгуки", '').strip())
except AttributeError:
    data["number_of_reviews"] = None

try:
    list_item = soup.find('dl', class_="list").find_all('dt', class_='label')
    series = None
    for lst in list_item:
        span = lst.find('span', string=lambda t: t and "Серія" in t)
        if span:
            series = lst.find_next('dd').text.strip()
            break
    data["series"] = series
except AttributeError:
    data["series"] = None

try:
    diagonal = None
    for lst in list_item:
        span = lst.find('span', string=lambda t: t and "Діагональ екрана" in t)
        if span:
            diagonal = lst.find_next('dd').text.strip()
            break
    data["screen_diagonal"] = diagonal
except AttributeError:
    data["screen_diagonal"] = None

try:
    resolution = None
    for lst in list_item:
        span = lst.find('span', string=lambda t: t and "Роздільна здатність дисплея" in t)
        if span:
            resolution = lst.find_next('dd').text.strip()
            break
    data["display_resolution"] = resolution
except AttributeError:
    data["display_resolution"] = None

try:
    images = []
    img_list = soup.find('app-slider', class_="preview-slider").find_all('img')
    for img in img_list:
        src = img.attrs.get('src')
        if src:
            images.append(src)
    data["all_product_photos"] = images
except AttributeError:
    data["all_product_photos"] = None

try:
    seller_block = soup.find('p',class_="seller-title")
    try:
        seller_name = seller_block.find('a')
        data["seller"] = seller_name.strip()
    except Exception:
        try:
            seller_name = seller_block.find('img').get('alt')
            data["seller"] = seller_name.strip()
        except AttributeError:
            pass
    try:
        seller_block = soup.find('div',class_="comment__vars").find('span', string=lambda t: t and "Продавець:" in t).text
        data["seller"] = seller_block.replace("Продавець:", '').strip()

    except AttributeError:
        data["seller"]= None

except AttributeError:
    data["seller"]= None

try:
    product_specifications = {}
    try:
        link_c = soup.find('a', class_="product-characteristics").get('href')
    except AttributeError:
        link_c = None

    if link_c:
        response_c = scraper.get(link_c, headers=headers)
        soup_c = BeautifulSoup(response_c.text, 'html.parser')
        sections = soup_c.find('main', class_="product-tabs__content").find_all('section')

        for i, section in enumerate(sections):
            specs = {}
            try:
                divs = section.find_all('div')
                for div in divs:
                    dts = div.find_all('dt')
                    dds = div.find_all('dd')
                    for dt, dd in zip(dts, dds):
                        specs[dt.text.strip()] = dd.text.strip()
                product_specifications[f"product_specification_{i}"] = specs
            except AttributeError:
                continue
    data["product_specifications"] = product_specifications or None
except AttributeError:
    data["product_specifications"] = None

print(data)
save_to_exel(data,"requestsBS4_parse")

mobile_model,created = Mobile.objects.get_or_create(
    full_name_of_the_product =data["full_name_of_the_product"],
    color =data["color"],
    memory_size = data["memory_size"],
    seller = data["seller"],
    regular_price = data["regular_price"],
    promotional_price = data["promotional_price"],
    product_code = data["product_code"],
    number_of_reviews =data["number_of_reviews"],
    series = data["series"],
    screen_diagonal = data["screen_diagonal"],
    display_resolution = data["display_resolution"],
    product_specifications = data['product_specifications']

)
for d in data['all_product_photos']:
    photo,created = Photo.objects.get_or_create(
        url = d,
        mobile_id = mobile_model

    )

mobiles = Mobile.objects.all()

for mobile in mobiles:
    print(mobile)