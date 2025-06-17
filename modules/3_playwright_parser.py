"""
This script uses Playwright (with an asynchronous API) to scrape product information from the Rozetka website.

The process includes:
- Launching a Chromium browser with Ukrainian locale and user-agent settings.
- Searching for "Apple iPhone 15 128GB Black" on the Rozetka homepage.
- Navigating to the first product from the search results.
- Extracting key product information using XPath queries:
    - Product name
    - Color and memory size
    - Regular and promotional prices
    - Product code and number of reviews
    - Series, screen diagonal, and display resolution
    - Seller name (from either link or image alt)
    - All available product images
    - Full structured product specifications from the "Characteristics" tab

Helper function `safe_text()` is used to handle optional fields gracefully.

All the collected data is saved to an Excel file using the `save_to_exel()` function.

The script is useful for dynamically scraping product data from JavaScript-rendered pages where static HTML scraping is not sufficient.
"""

import re
import random
import asyncio
from patchright.async_api import Page, expect
from patchright.async_api import async_playwright

from _7_exel_template_write import save_to_exel

data={}

url = "https://rozetka.com.ua/"
SECONDS = 1000

async def safe_text(page, xpath: str) -> str | None:
    locator = page.locator(xpath)
    try:
        await page.wait_for_timeout(random.randint(3000, 5000))
        text = await locator.inner_text()
        return text.replace('\xa0', '')
    except Exception:
        return None


async def run(p):
    chromium = p.chromium
    browser = await chromium.launch(channel="chrome", headless=False)

    context = await browser.new_context(
        locale='ua-UA',
        color_scheme='dark',
        timezone_id='Europe/Kiev',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        java_script_enabled=True,
        viewport={ 'width': 1900, 'height': 1600 }
    )
    await context.set_extra_http_headers({
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": url,
    })
    page = await context.new_page()

    try:
        await page.goto(url, timeout = 300000, wait_until = "load")
    except TimeoutError as e:
        print(f"await page.goto doesn't load: {e}")

    text_box = page.locator('//input[@name="search"]')
    await expect(text_box).to_be_visible(timeout=10000)

    await text_box.type('Apple iPhone 15 128GB Black', delay=random.randint(700, 900))
    await page.wait_for_timeout(random.randint(3000, 5000))
    
    submit_button = page.locator('//button[contains(text(),"Знайти")]')
    await expect(submit_button).to_be_visible(timeout=10000)

    await submit_button.hover()
    await submit_button.click()
    await page.wait_for_timeout(random.randint(3000, 5000))

    first_result_link = page.locator('(//ul[@class="catalog-grid"]/li[1]//a)[1]')
    await expect(first_result_link).to_be_visible(timeout=10000)

    await first_result_link.hover()
    await first_result_link.click()


    data["full_name_of_the_product"] = await safe_text(page, '//h1')
    data["color"] = await safe_text(page, '//div[@class="var-options"]/p/span[contains(text(),"Колір")]/following-sibling::span')
    memory_size_raw = await safe_text(page, '//div[@class="var-options"]/p/span[contains(text(),"Вбудована пам\'ять")]/following-sibling::span')
    data["memory_size"] = int(memory_size_raw.replace('ГБ', '').strip()) if memory_size_raw else None
    promotional_price_raw = await safe_text(page, '//p[@class="product-price__small"]/following-sibling::p')
    data["promotional_price"] = int(promotional_price_raw.replace('₴', '').strip()) if promotional_price_raw else None
    regular_price_raw = await safe_text(page, '//p[@class="product-price__small"]')
    data["regular_price"] = int(regular_price_raw.replace('₴', '').strip()) if promotional_price_raw else None
    product_code_raw = await safe_text(page, '//div[@class="product-about__right"]//div[@class="rating text-base"]/span')
    data["product_code"] = int(product_code_raw.replace("Код:", "").strip()) if product_code_raw else None
    number_of_reviews_raw = await safe_text(page, '//div[@class="product-about__right"]//div[@class="rating text-base"]/a')
    data["number_of_reviews"] = int(number_of_reviews_raw.replace("відгуки", "").strip()) if number_of_reviews_raw else None
    data["series"] = await safe_text(page, '//dl/div[dt[@class="label" and span[contains(text(),"Серія")]]]/dd')
    data["screen_diagonal"] = await safe_text(page, '//dl/div[dt[@class="label" and span[contains(text(),"Діагональ екрана")]]]/dd')
    data["display_resolution"] = await safe_text(page, '//dl/div[dt[@class="label" and span[contains(text(),"Роздільна здатність дисплея")]]]/dd')

    
    try:
        seller_name = await page.locator('//p[@class="seller-title"]//a').inner_text()
        data["seller"] = seller_name

    except Exception:
        try:
            seller_name = await page.locator('//p[@class="seller-title"]//img').get_attribute('alt')
            data["seller"] = seller_name

        except AttributeError:
            seller_name = None

    images = []

    try:
        img_elements = page.locator('//div[@class="scrollbar__content"]/ul//li//img')
        count = await img_elements.count()

        for i in range(count):
            img = img_elements.nth(i)
            src = await img.get_attribute("src")
            images.append(src)

        data['all_product_photos'] = images

    except AttributeError as e:
        data['all_product_photos'] = []


    link_a = page.locator('//a[contains(text()," Характеристики")]')
    await expect(submit_button).to_be_visible(timeout=10000)

    await link_a.hover()    
    await link_a.click()

    await page.wait_for_timeout(random.randint(3000, 5000))


    product_specifications = {}
    try:
        await page.wait_for_selector('//main[@class="product-tabs__content"]//section', timeout=15000)
        sections = page.locator('//main[@class="product-tabs__content"]//section')
        count = await sections.count()

        for i in range(count):
            specs = {}
            section = sections.nth(i)
            divs = section.locator('xpath=./dl/div')
            divs_count = await divs.count()

            for d in range(divs_count):
                div = divs.nth(d)
                dts = div.locator('xpath=./dt')
                dds = div.locator('xpath=./dd')

                dt_count = await dts.count()
                dd_count = await dds.count()

                pair_count = min(dt_count, dd_count)

                
                for j in range(pair_count):
                    dt_text = await dts.nth(j).inner_text()
                    dd_text = await dds.nth(j).inner_text()
                    specs[dt_text.strip()] = dd_text.strip()

                product_specifications[f"product_specification_{i}"] = specs

        data["product_specifications"] = product_specifications

    except AttributeError:
        data["product_specifications"] = None
        data["product_specifications"] = product_specifications

    print(data)
    save_to_exel(data,"playwright_parse")
    
    print("="*50)
    
    await context.close()
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())