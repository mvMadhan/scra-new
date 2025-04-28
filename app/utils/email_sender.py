import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASS = "fziraqntsdchytxw"  # App password (not real password)

def send_price_drop_email(to_email, title, current_price, alert_price, product_url):
    print(f"📩 Preparing to send email to {to_email}")
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASS)

        message = MIMEMultipart()
        message['From'] = SENDER_EMAIL
        message['To'] = to_email
        message['Subject'] = "🛒 Price Drop Alert!"

        body = f"""
        <h2>Good news!</h2>
        <p>The product you were tracking has dropped in price!</p>
        <p><strong>{title}</strong></p>
        <p>Current Price: ₹{current_price}</p>
        <p>Your Alert Price: ₹{alert_price}</p>
        <p><a href="{product_url}" target="_blank">View Product</a></p>
        <br><br>
        <p>Keep saving with Smart Price Tracker!</p>
        """

        message.attach(MIMEText(body, 'html'))
        server.sendmail(SENDER_EMAIL, to_email, message.as_string())
        server.quit()
        print(f"✅ Email sent successfully to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
