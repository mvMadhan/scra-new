from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app import mysql
import MySQLdb.cursors
from app.utils.scraper import scrape_product  # ✅ Make sure this works


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['admin_loggedin'] = True
            session['admin_username'] = username
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('admin_login.html')

@admin_bp.route('/admin/dashboard')
def dashboard():
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin.admin_login'))
    return render_template('admin_dashboard.html', admin=session['admin_username'])

# ✅ Fixed logout endpoint (was previously wrong)
@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_loggedin', None)
    session.pop('admin_username', None)
    flash("Logged out from admin panel.", "info")
    return redirect(url_for('admin.admin_login'))

# Add these below the logout function in admin.py


@admin_bp.route('/admin/view-tracked-products')
def view_all_tracked():
    return "<h1>All Tracked Products (To be implemented)</h1>"


@admin_bp.route('/admin/trigger-scan', methods=['GET', 'POST'])
def trigger_scan():
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin.admin_login'))

    import MySQLdb.cursors
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        user_id = request.form.get('user_id')

        if user_id == 'all':
            cursor.execute("SELECT * FROM products")
        else:
            cursor.execute("SELECT * FROM products WHERE user_id = %s", (user_id,))

        products = cursor.fetchall()

        from app.utils.scraper import scrape_product  # Make sure this exists

        updated_count = 0
        for product in products:
            scraped = scrape_product(product['url'])
            if scraped and scraped['price'] != product['price']:
                # Update the product price
                cursor.execute(
                    "UPDATE products SET price = %s WHERE id = %s",
                    (scraped['price'], product['id'])
                )
                # Log to price_history with user_id
                cursor.execute(
                    "INSERT INTO price_history (product_id, user_id, price, timestamp) VALUES (%s, %s, %s, NOW())",
                    (product['id'], product['user_id'], scraped['price'])
                )
                updated_count += 1

        mysql.connection.commit()
        flash(f"Scan complete. {updated_count} product(s) updated.", "success")
        return redirect(url_for('admin.trigger_scan'))

    # GET request
    cursor.execute("SELECT id, username FROM users ORDER BY id DESC")
    users = cursor.fetchall()
    return render_template('adminside/admin_trigger_scan.html', users=users)


@admin_bp.route('/admin/manage-coupons')
def manage_coupons():
    return "<h1>Manage Coupons (To be implemented)</h1>"

@admin_bp.route('/admin/notifications')
def notifications():
    return "<h1>Notification System (To be implemented)</h1>"

