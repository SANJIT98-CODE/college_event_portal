# init_db.py
import sqlite3

conn = sqlite3.connect('events.db')
c = conn.cursor()

# Create tables
c.execute('''
    CREATE TABLE IF NOT EXISTS events1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        date TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTERGER,
        name TEXT,
        email TEXT,
        phone TEXT
    )
    ''')

# Insert sample events
sample_events = [
    ("Tech Talk", "A seminar on emerging tech","2025-06-15"),
    ("Hackthon", "24-hour coding challenge", "2025-06-20"),
    ("AI Workshop", "Hands-on working on AI basics", "2025-06-25")
]
c.executemany('INSERT INTO events (title, description, date) VALUES (?, ?, ?)', sample_events)


# New registrations table creation
c.execute('''
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        event_id INTEGER NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events(id)
    )
''')

conn.commit()
conn.close()




