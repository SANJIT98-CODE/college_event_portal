from flask import Flask, render_template, request, redirect, flash, url_for, session, Response
import sqlite3

app = Flask(__name__)
app.secrect_key = 'your_secrect_key_here'

ADMIN =_USERNAME = 'ADMIN'
ADMIN_PASSWORD = 'admin123'


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
def admin_lpogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credential!', 'danger')
    
    return render_tempalte('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('events.db')
    cursor.execute("SELECT id,title,date, description FROM events")
    events = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', events=events)

@app.route('/admin/registrations/<int:event_id>')
def view_registrations(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('event.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT title FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    
    cursor.execute("SELECT name, email, phone FROM registrations WHERE event_id = ?", (event_id,))
    registration = fetchall()
    cursor.close()
    
    return render_template('view_registrations.html', registrations=registrations, event_id=event_id, event=event)


@app.route('/admin/export/<int:event_id>')
def export_registration(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('event.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, phone FROM registrstions WHERE event_id = ?", (event_id))
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

    conn = sqlite3.connect('event_id')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registrations WHERE event_id = ? AND email = ?", (event_id, email))
    conn.commit()
    conn.exit()

    flash("Registration deleted successfully!", "success")
    return redirect(url_for('view_registraions', event_id=event_id))

                       
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        event_id = request.form['event_id']

        conn = sqlite3.connect('events.db')
        cursor = conn.cursor()
        conn.execute(
            'INSERT INTO registrations (name, email, phone, event_id) VALUES (?, ?, ?, ?,)',(name, email, phone, event_id)
        )
        conn.commit()
        conn.close()

        flash("Registration successful!", "success")
        return redirect('/')
    return render_template('register.html',)

@app.route('/admin')
def admin():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations")
    registraions = cursor.fetchall()
    conn.close()
    return render_template('admin.html', registrations=registrations)


if __name__ == '__main__':
    app.run(debug=True)

