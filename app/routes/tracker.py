from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from app import mysql
from app.utils.scraper import scrape_product
import MySQLdb.cursors
from datetime import datetime

tracker_bp = Blueprint('tracker', __name__)


@tracker_bp.route('/track', methods=['POST'])
def add_product():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    product_url = request.form['product_url']
    data = scrape_product(product_url)

    if data:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO products (user_id, url, title, price, image_url, source)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['id'], data['url'], data['title'], data['price'], data['image'], data['source']))
        mysql.connection.commit()

        # Log to price_history table
        product_id = cursor.lastrowid
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO price_history (product_id, price, timestamp, user_id)
            VALUES (%s, %s, %s, %s)
        """, (product_id, data['price'], now, session['id']))
        mysql.connection.commit()

        flash("Product is now being tracked!", "success")
    else:
        flash("Could not fetch product details. Check URL or site support.", "danger")

    return redirect(url_for('dashboard.home'))


@tracker_bp.route('/delete/<int:product_id>')
def delete_product(product_id):
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s AND user_id = %s", (product_id, session['id']))
    mysql.connection.commit()
    flash("Product removed from tracking.", "info")

    return redirect(url_for('dashboard.home'))


@tracker_bp.route('/tracker')
def view_tracker():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE user_id = %s ORDER BY added_on DESC", (session['id'],))
    products = cursor.fetchall()

    return render_template('tracker.html', tracked_products=products, username=session['username'], current_year=2025)


@tracker_bp.route('/set-alerts/<int:product_id>', methods=['POST'])
def set_alerts(product_id):
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    alert_type = 'percent'
    alert_value = request.form.get('percentage')
    fixed_price = request.form.get('target_price')

    if fixed_price:
        alert_type = 'fixed'
        alert_value = fixed_price

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT price FROM products WHERE id = %s AND user_id = %s", (product_id, session['id']))
    current_price_row = cursor.fetchone()

    if not current_price_row:
        flash("Product not found.", "danger")
        return redirect(url_for('tracker.view_tracker'))

    current_price = current_price_row[0]
    try:
        if alert_type == 'percent':
            alert_price = float(current_price) * (1 - float(alert_value) / 100)
        else:
            alert_price = float(alert_value)
    except (ValueError, TypeError):
        flash("Invalid alert value.", "danger")
        return redirect(url_for('tracker.view_tracker'))

    cursor.execute("""
        INSERT INTO alerts (user_id, product_id, alert_type, alert_value, alert_price)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE alert_type=%s, alert_value=%s, alert_price=%s
    """, (
        session['id'], product_id, alert_type, alert_value, alert_price,
        alert_type, alert_value, alert_price
    ))
    mysql.connection.commit()
    flash("Alert preferences saved!", "success")

    return redirect(url_for('tracker.view_tracker'))
