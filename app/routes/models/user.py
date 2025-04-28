# ✅ Append to app/routes/admin/users.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app import mysql

admin_users_bp = Blueprint('admin_users', __name__)

# View all users
@admin_users_bp.route('/admin/users')
def manage_users():
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin.admin_login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT u.id, u.username, u.email, COUNT(p.id) AS product_count FROM users u LEFT JOIN products p ON u.id = p.user_id GROUP BY u.id")
    users = cursor.fetchall()
    return render_template('adminside/admin_users.html', users=users)

# View products of a specific user
@admin_users_bp.route('/admin/users/<int:user_id>/products')
def view_user_products(user_id):
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin.admin_login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT title, price, url FROM products WHERE user_id = %s", (user_id,))
    products = cursor.fetchall()

    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    return render_template('adminside/admin_user_products.html', products=products, username=user[0])

# Delete a user and all their tracked products
@admin_users_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin.admin_login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    flash("User and their tracked products deleted successfully.", "success")
    return redirect(url_for('admin_users.manage_users'))
