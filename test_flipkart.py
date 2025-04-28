from app.utils.scraper import scrape_flipkart

# Flipkart product URL for testing
url = "https://www.flipkart.com/fastrack-revoltt-fr2-1-38-advanced-blazing-fast-ui-working-crown-aivoice-assistant-ip68-smartwatch/p/itm1f795ebf8cee2"

print("🧪 Testing Flipkart Scraper...")

result = scrape_flipkart(url)

if result:
    print("✅ Title:", result['title'])
    print("💰 Price:", result['price'])
    print("🖼️ Image URL:", result['image_url'])
else:
    print("❌ Scraper failed or Flipkart blocked the request.")
