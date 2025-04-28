from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app import mysql
import MySQLdb.cursors
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.price_scanner import run_price_scan

# Blueprint for admin scan routes
admin_scan_bp = Blueprint('admin_scan', __name__)

# 🌐 Global Scheduler
scheduler = BackgroundScheduler()
scheduler.start()
scheduled_job = None  # Reference to the current job


@admin_scan_bp.route('/admin/trigger-scan', methods=['GET', 'POST'])
def trigger_scan():
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin.admin_login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        print("🧪 Raw interval_value:", request.form.get('interval_value'))  # ✅ ADD THIS
        interval_value = int(request.form.get('interval_value'))

        interval_unit = request.form.get('interval_unit')

        global scheduled_job

        # 🧠 Log Trigger Details
        print(f"📥 Trigger Scan Request: User = {user_id}, Interval = {interval_value} {interval_unit}")

        # ✅ Manual scan (run once)
        if interval_value == 0:
            print("🧠 Inside scan.py - about to call run_price_scan()")
            if user_id == "all":
                run_price_scan()
                flash("✅ Manual scan triggered for ALL users!", "success")
            else:
                run_price_scan(user_id=int(user_id))
                flash(f"✅ Manual scan triggered for User ID {user_id}!", "success")

        # ⏰ Schedule recurring scans
        else:
            # Cancel previous scheduled job if it exists
            if scheduled_job:
                print("🔁 Removing previous scheduled job...")
                scheduler.remove_job(scheduled_job.id)

            # Setup new job
            selected_user = None if user_id == "all" else int(user_id)

            scheduled_job = scheduler.add_job(
                func=lambda: run_price_scan(user_id=selected_user),
                trigger="interval",
                **{interval_unit: interval_value}
            )

            flash(f"🕒 Scheduled scan every {interval_value} {interval_unit} for {'ALL users' if user_id == 'all' else 'User ID ' + user_id}", "info")
            print(f"✅ Scheduled scan job started: every {interval_value} {interval_unit}")

        return redirect(url_for('admin_scan.trigger_scan'))

    return render_template('adminside/admin_trigger_scan.html', users=users)
