from flask import Flask, render_template, request, redirect, flash, url_for, session, Response
from config import ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY
from flask_wtf.csrf import CSRFProtect
import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

print("Loaded ADMIN_USERNAME:", ADMIN_USERNAME)
print("Loaded ADMIN_PASSWORD:", ADMIN_PASSWORD)
print("Loaded SECRET_KEY:", SECRET_KEY)

app = Flask(__name__)
app.secret_key = SECRET_KEY

csrf = CSRFProtect(app)

def get_db_connection():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events1').fetchall()
    conn.close()
    return render_template('home.html', events=events)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print("Enter Username:", username)
        print("Enter Password:", password)
        print("Expected Username:", ADMIN_USERNAME)
        print("Expected Password:", ADMIN_PASSWORD)

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credential!', 'danger')
            return redirect("/admin/login")
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id,title,date, description FROM events")
    events = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', events=events)

@app.route('/admin/export/<int:event_id>')
def export_registrations(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, phone FROM registrations WHERE event_id = ?",(event_id,))
    data = cursor.fetchall()
    conn.close()

    output = "Name,Email,Phone\n"
    for reg in data:
        output += f"{reg[0]},{reg[1]},{reg[2]}\n"

    return Response(
        output,
        mimetype="text/cvs",
        headers={"Content-Dsposition": f"attachment;filname=event_{event_id}_registrations.csv"}
    )


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/registrations/<int:event_id>')
def view_registrations(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT title FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    
    cursor.execute("SELECT name, email, phone FROM registrations WHERE event_id = ?", (event_id,))
    registration = cursor.fetchall()
    cursor.close()
    
    return render_template('view_registrations.html', registrations=registrations, event_id=event_id, event=event)


@app.route('/admin/export/<int:event_id>')
def export_registration(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, phone FROM registrations WHERE event_id = ?", (event_id))
    data = cursor.fetchall()
    conn.close()
    
    output = "Name,Email,Phone\n"
    for row in data:
        output += f"{row[0]},{row[1]},{row[2]}\n"
    
    return Response(
        output,
        mimetype="text/cvs",
        headers={"Content-Disposition": f"attachment; filename=event_{event_id}_registrations.csv"}
    )

@app.route('/admin/delete-registration', methods=['POST'])
def delete_registration():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    event_id = request.form['event_id']
    email = request.form['email']

    conn = sqlite3.connect('events.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registrations WHERE event_id = ? AND email = ?", (event_id, email))
    conn.commit()
    conn.close()

    flash("Registration deleted successfully!", "success")
    return redirect(url_for('view_registrations', event_id=event_id))

                       
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        event_id = request.form.get("event_id")

        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format!", "danger")
            return redirect("/register")

        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        conn.execute(
            'INSERT INTO registrations (name, email, phone, event_id) VALUES (?, ?, ?, ?)',(name, email, phone, event_id)
        )
        conn.commit()
        conn.close()

        flash("Registration successful!", "success")
        return redirect('/')

    conn = sqlite3.connect('events.db')
    events = conn.execute("SELECT * FROM events").fetchall()
    conn.close()
    return render_template("register.html", events=events)

@app.context_processor
def inject_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return dict(csrf_token=generate_csrf())
    
if __name__ == '__main__':
    app.run(debug=True)

