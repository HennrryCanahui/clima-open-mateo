from flask import Flask, jsonify, render_template, request
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)

API_TOKEN = "696969696969"

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token or token != API_TOKEN:
            return jsonify({"error": "Acceso no autorizado"}), 401
        return f(*args, **kwargs)
    return decorated

def get_db_connection():
    conn = sqlite3.connect('monitoreo_agricola.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea la tabla de sensores si no existe."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sensores_esp32 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            humedad_suelo_1 REAL,
            humedad_suelo_2 REAL,
            humedad_suelo_3 REAL,
            temperatura_1 REAL,
            temperatura_2 REAL,
            bomba_1 INTEGER,
            bomba_2 INTEGER,
            bomba_3 INTEGER,
            uv_index REAL,
            lluvia INTEGER,
            luz_lux REAL
        )
    ''')
    conn.commit()
    conn.close()

def get_clima_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pronostico_clima ORDER BY date DESC LIMIT 24")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows][::-1]

def get_sensores_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensores_esp32 ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows][::-1]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clima')
@require_token
def api_clima():
    data = get_clima_data()
    return jsonify(data)

@app.route('/api/sensores', methods=['POST'])
@require_token
def recibir_sensores():
    if not request.is_json:
        return jsonify({"error": "El contenido debe ser JSON"}), 400

    data = request.get_json()

    campos_float = ["humedad_suelo_1", "humedad_suelo_2", "humedad_suelo_3",
                    "temperatura_1", "temperatura_2", "uv_index", "luz_lux"]
    campos_int   = ["bomba_1", "bomba_2", "bomba_3", "lluvia"]

    valores = {}
    for campo in campos_float:
        val = data.get(campo)
        valores[campo] = float(val) if val is not None else None

    for campo in campos_int:
        val = data.get(campo)
        valores[campo] = int(val) if val is not None else None  # cast explícito, evita que bool/None rompa SQLite

    valores["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO sensores_esp32 (
                timestamp,
                humedad_suelo_1, humedad_suelo_2, humedad_suelo_3,
                temperatura_1, temperatura_2,
                bomba_1, bomba_2, bomba_3,
                uv_index, lluvia, luz_lux
            ) VALUES (
                :timestamp,
                :humedad_suelo_1, :humedad_suelo_2, :humedad_suelo_3,
                :temperatura_1, :temperatura_2,
                :bomba_1, :bomba_2, :bomba_3,
                :uv_index, :lluvia, :luz_lux
            )
        ''', valores)
        conn.commit()
        conn.close()
        return jsonify({"status": "ok", "mensaje": "Datos guardados correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sensores', methods=['GET'])
@require_token
def obtener_sensores():
    data = get_sensores_data()
    return jsonify(data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)