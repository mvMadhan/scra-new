from flask import Blueprint, render_template, session, redirect, url_for
from app import mysql
import MySQLdb.cursors

coupons_bp = Blueprint('coupons', __name__)

@coupons_bp.route('/coupons')
def view_coupons():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM coupons ORDER BY expiry_date ASC")
    coupons = cursor.fetchall()

    return render_template('coupons.html', username=session['username'], coupons=coupons, current_year=2025)
