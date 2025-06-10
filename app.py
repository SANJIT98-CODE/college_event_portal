from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('events.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    events = conn.executed('SELECT * FROM events1').fecthall()
    conn.close()
    return render_template('home.html', events=events)

if __name__ == '__main__':
    app.run(debug=True)

