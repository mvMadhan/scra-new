from flask import Blueprint, render_template, session, redirect, url_for
from app import mysql
import MySQLdb.cursors

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def home():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE user_id = %s ORDER BY added_on DESC", (session['id'],))
    products = cursor.fetchall()

    for product in products:
        cursor.execute("SELECT price, checked_on FROM price_history WHERE product_id = %s ORDER BY checked_on", (product['id'],))
        product['history'] = cursor.fetchall()

    return render_template("dashboard.html", username=session['username'], tracked_products=products, current_year=2025)