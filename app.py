from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)

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

