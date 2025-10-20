from flask import Flask, request, jsonify, redirect
import os, sqlite3, random, string

import time
import psycopg2

for i in range(10):
    try:
        conn = psycopg2.connect(
            host="url-db",
            dbname="urlshortener",
            user="postgres",
            password="secret"
        )
        print("✅ Datenbankverbindung erfolgreich!")
        break
    except psycopg2.OperationalError:
        print("⏳ Warten auf Datenbank...")
        time.sleep(3)
else:
    raise Exception("❌ Konnte keine Verbindung zur Datenbank herstellen.")

app = Flask(__name__)

DB_PATH = os.getenv("DB_PATH", "urls.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS urls (code TEXT PRIMARY KEY, long_url TEXT)")
    return conn

def gen_code(n=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    long_url = data.get("url")
    code = gen_code()
    conn = get_db()
    conn.execute("INSERT INTO urls VALUES (?, ?)", (code, long_url))
    conn.commit()
    conn.close()
    return jsonify(short_url=f"http://localhost:5001/{code}")

@app.route("/<code>")
def redirect_to(code):
    conn = get_db()
    cursor = conn.execute("SELECT long_url FROM urls WHERE code=?", (code,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return redirect(result[0])
    return "URL not found", 404

@app.route("/")
def index():
    return "URL Shortener API läuft!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)