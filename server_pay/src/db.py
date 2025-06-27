import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('vpn_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (telegram_id INTEGER PRIMARY KEY, is_admin INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  telegram_id INTEGER, 
                  start_date TEXT, 
                  end_date TEXT, 
                  is_trial INTEGER DEFAULT 0,
                  FOREIGN KEY (telegram_id) REFERENCES users (telegram_id))''')
    conn.commit()
    conn.close()

def check_db_validity():
    try:
        conn = sqlite3.connect('vpn_users.db')
        c = conn.cursor()
        c.execute('SELECT 1 FROM users LIMIT 1')
        c.execute('SELECT 1 FROM subscriptions LIMIT 1')
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def is_admin(telegram_id):
    conn = sqlite3.connect('vpn_users.db')
    c = conn.cursor()
    c.execute('SELECT is_admin FROM users WHERE telegram_id = ?', (telegram_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1

def add_admin(telegram_id):
    conn = sqlite3.connect('vpn_users.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (telegram_id, is_admin) VALUES (?, 1)', (telegram_id,))
    conn.commit()
    conn.close()

def remove_admin(telegram_id):
    conn = sqlite3.connect('vpn_users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET is_admin = 0 WHERE telegram_id = ?', (telegram_id,))
    conn.commit()
    conn.close()

def activate_trial(telegram_id):
    conn = sqlite3.connect('vpn_users.db')
    c = conn.cursor()
    start_date = datetime.datetime.now().isoformat()
    end_date = (datetime.datetime.now() + datetime.timedelta(weeks=1)).isoformat()
    c.execute('INSERT OR REPLACE INTO users (telegram_id, is_admin) VALUES (?, 0)', (telegram_id,))
    c.execute('INSERT INTO subscriptions (telegram_id, start_date, end_date, is_trial) VALUES (?, ?, ?, 1)',
              (telegram_id, start_date, end_date))
    conn.commit()
    conn.close()
    return end_date

def check_trial(telegram_id):
    conn = sqlite3.connect('vpn_users.db')
    c = conn.cursor()
    c.execute('SELECT end_date, is_trial FROM subscriptions WHERE telegram_id = ? AND end_date > ?',
              (telegram_id, datetime.datetime.now().isoformat()))
    result = c.fetchone()
    conn.close()
    if result:
        return datetime.datetime.fromisoformat(result[0]) if result[1] == 1 else None
    return None

def check_trial_used(telegram_id):
    conn = sqlite3.connect('vpn_users.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM subscriptions WHERE telegram_id = ? AND is_trial = 1', (telegram_id,))
    result = c.fetchone()
    conn.close()
    return result[0] > 0

def check_subscription(telegram_id):
    conn = sqlite3.connect('vpn_users.db')
    c = conn.cursor()
    c.execute('SELECT end_date, is_trial FROM subscriptions WHERE telegram_id = ? AND end_date > ?',
              (telegram_id, datetime.datetime.now().isoformat()))
    result = c.fetchone()
    conn.close()
    if result:
        return {'end_date': datetime.datetime.fromisoformat(result[0]), 'is_trial': result[1] == 1}
    return None