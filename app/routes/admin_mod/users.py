from flask import Blueprint, render_template, session, redirect, url_for, flash
from app import mysql
import MySQLdb.cursors

admin_users_bp = Blueprint('admin_users', __name__)

@admin_users_bp.route('/admin/manage-users')
def manage_users():
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin.admin_login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT u.id, u.username, u.email, COUNT(p.id) AS product_count
        FROM users u
        LEFT JOIN products p ON u.id = p.user_id
        GROUP BY u.id, u.username, u.email
        ORDER BY u.id DESC
    """)
    users = cursor.fetchall()

    return render_template('adminside/admin_users.html', users=users)

# ✅ Delete user and all their products
@admin_users_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin.admin_login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()

    flash('User and their tracked products have been deleted.', 'info')
    return redirect(url_for('admin_users.manage_users'))

# ✅ View specific user's tracked products
@admin_users_bp.route('/admin/users/<int:user_id>/products')
def view_user_products(user_id):
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin.admin_login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM products WHERE user_id = %s ORDER BY added_on DESC", (user_id,))
    products = cursor.fetchall()

    return render_template('adminside/view_user_products.html', user=user, products=products)
