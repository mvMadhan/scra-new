from app import mysql
import MySQLdb.cursors
from app.utils.email_sender import send_price_drop_email
from app.utils.scraper import scrape_product  # <--- correct import

print("📂 price_scanner.py LOADED")



def run_price_scan(user_id=None):
    print("🚀 run_price_scan() CALLED")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if user_id:
        print(f"Scanning for user: {user_id or 'ALL'}")

        cursor.execute("SELECT p.*, u.email FROM products p JOIN users u ON p.user_id = u.id WHERE p.user_id = %s", (user_id,))
    else:
        cursor.execute("SELECT p.*, u.email FROM products p JOIN users u ON p.user_id = u.id")

    products = cursor.fetchall()
    print(f"Found {len(products)} products to scan.")  # NEW PRINT

    for product in products:
        url = product['url']
        scraped_data = scrape_product(url)

        if not scraped_data:
            print(f"❌ Failed to scrape {url}")
            continue

        current_price = scraped_data['price']
        title = scraped_data['title']
        image_url = scraped_data['image']

        print(f"✅ Scraped {title} - ₹{current_price}")

        cursor.execute("UPDATE products SET price = %s WHERE id = %s", (current_price, product['id']))
        mysql.connection.commit()

        if product['alert_price'] and current_price <= product['alert_price']:
            print(f"📩 Price dropped! Will send email to {product['email']}")
            send_price_drop_email(
                to_email=product['email'],
                title=title,
                current_price=current_price,
                alert_price=product['alert_price'],
                product_url=url
            )
        else:
            print(f"ℹ️ No price drop for {title}. Current: ₹{current_price}, Alert: ₹{product['alert_price']}")
