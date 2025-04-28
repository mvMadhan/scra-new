import re
import requests
from bs4 import BeautifulSoup


ZENROWS_API_KEY = "0256891d4a5c1fdcf9571a80fcf91181e569a43d"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def detect_source(url):
    if "amazon" in url:
        return "amazon"
    elif "flipkart" in url:
        return "flipkart"
    elif "meesho" in url:
        return "meesho"
    elif "ajio" in url:
        return "ajio"
    else:
        return "unknown"

def scrape_product(url):
    source = detect_source(url)

    try:
        if source == "amazon":
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            title = soup.find(id="productTitle").get_text(strip=True)
            price_el = soup.select_one(".a-price-whole, .a-price .a-offscreen")
            price = price_el.get_text(strip=True).replace(",", "").replace("₹", "") if price_el else "0"
            image_el = soup.select_one("#landingImage") or soup.select_one("#imgTagWrapperId img")
            image_url = image_el["src"] if image_el else ""

        elif source == "flipkart":
            result = scrape_flipkart_with_selenium(url)
            if result:
                return result
            else:
                print("❌ Flipkart failed even with Selenium.")
                return None

        elif source == "meesho":
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            title = soup.select_one("h1.pdp-title").get_text(strip=True)
            price = soup.select_one("h4.pdp-discounted-price").get_text(strip=True).replace(",", "").replace("₹", "")
            image_url = soup.select_one("img.pdp-image")["src"]

        elif source == "ajio":
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            title = soup.select_one("h1.title").get_text(strip=True)
            price = soup.select_one("div.price .price span").get_text(strip=True).replace(",", "").replace("₹", "")
            image_url = soup.select_one("img.image-image")["src"]

        else:
            return None

        return {
            "title": title,
            "price": float(re.findall(r'\d+\.\d+|\d+', price)[0]),
            "image": image_url,
            "source": source,
            "url": url
        }

    except Exception as e:
        print("Scraping error:", e)
        return None

def scrape_flipkart_with_selenium(url):
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        options = uc.ChromeOptions()
        options.add_argument("--user-data-dir=C:/Users/giris/AppData/Local/Google/Chrome/User Data")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver = uc.Chrome(options=options)

        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "B_NuCI")))

        if "Login" in driver.title or "robot" in driver.page_source.lower():
            print("⚠️ Blocked by Flipkart: CAPTCHA or Login")
            driver.save_screenshot("flipkart_blocked.png")
            driver.quit()
            return None

        title = driver.find_element(By.CLASS_NAME, "B_NuCI").text
        price = driver.find_element(By.CLASS_NAME, "_30jeq3").text.replace("₹", "").replace(",", "")
        image = driver.find_element(By.CSS_SELECTOR, "img._396cs4").get_attribute("src")

        driver.quit()

        return {
            "title": title.strip(),
            "price": float(re.findall(r'\d+\.\d+|\d+', price)[0]),
            "image": image,
            "source": "flipkart",
            "url": url
        }

    except Exception as e:
        print("🛑 Selenium Flipkart Error:", e)
        try:
            driver.quit()
        except:
            pass
        return None
