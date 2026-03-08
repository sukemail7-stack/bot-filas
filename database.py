import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    saldo INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS apostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valor INTEGER,
    modo TEXT,
    descricao TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS participantes (
    aposta_id INTEGER,
    user_id INTEGER
)
""")

conn.commit()


def get_saldo(user_id):
    cursor.execute("SELECT saldo FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO users (user_id, saldo) VALUES (?, ?)", (user_id, 0))
        conn.commit()
        return 0

    return result[0]


def add_saldo(user_id, valor):
    saldo = get_saldo(user_id)
    novo = saldo + valor

    cursor.execute("UPDATE users SET saldo = ? WHERE user_id = ?", (novo, user_id))
    conn.commit()


def remove_saldo(user_id, valor):
    saldo = get_saldo(user_id)
    novo = saldo - valor

    cursor.execute("UPDATE users SET saldo = ? WHERE user_id = ?", (novo, user_id))
    conn.commit()