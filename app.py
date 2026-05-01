from flask import Flask, jsonify, render_template, request
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)

# --- Seguridad ---
API_TOKEN = "696969696969"  # Cambia esto por un token seguro

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token or token != API_TOKEN:
            return jsonify({"error": "Acceso no autorizado"}), 401
        return f(*args, **kwargs)
    return decorated


# --- Base de datos ---
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

            -- Humedad del suelo (3 sensores, valor 0-100%)
            humedad_suelo_1 REAL,
            humedad_suelo_2 REAL,
            humedad_suelo_3 REAL,

            -- Temperatura (2 sensores digitales)
            temperatura_1 REAL,
            temperatura_2 REAL,

            -- Bombas de agua (estado: 0=apagada, 1=encendida)
            bomba_1 INTEGER,
            bomba_2 INTEGER,
            bomba_3 INTEGER,

            -- Sensores ambientales
            uv_index REAL,
            lluvia INTEGER,   -- 0=sin lluvia, 1=lluvia detectada
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
    """Retorna los últimos 50 registros de sensores."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensores_esp32 ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows][::-1]


# --- Rutas públicas ---
@app.route('/')
def index():
    return render_template('index.html')


# --- Rutas protegidas ---
@app.route('/api/clima')
@require_token
def api_clima():
    data = get_clima_data()
    return jsonify(data)

@app.route('/api/sensores', methods=['POST'])
@require_token
def recibir_sensores():
    """
    Recibe el JSON del ESP32 y lo guarda en la base de datos.

    Ejemplo del JSON esperado:
    {
        "humedad_suelo_1": 65.3,
        "humedad_suelo_2": 70.1,
        "humedad_suelo_3": 58.9,
        "temperatura_1": 24.5,
        "temperatura_2": 25.1,
        "bomba_1": 0,
        "bomba_2": 1,
        "bomba_3": 0,
        "uv_index": 3.2,
        "lluvia": 0,
        "luz_lux": 1200.5
    }
    """
    if not request.is_json:
        return jsonify({"error": "El contenido debe ser JSON"}), 400

    data = request.get_json()

    # Campos permitidos con sus valores por defecto (None si no vienen)
    campos = [
        "humedad_suelo_1", "humedad_suelo_2", "humedad_suelo_3",
        "temperatura_1", "temperatura_2",
        "bomba_1", "bomba_2", "bomba_3",
        "uv_index", "lluvia", "luz_lux"
    ]

    valores = {campo: data.get(campo) for campo in campos}
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
    """Retorna los últimos registros de sensores para el dashboard."""
    data = get_sensores_data()
    return jsonify(data)


if __name__ == '__main__':
    init_db()  # Crea las tablas si no existen al iniciar
    app.run(debug=True, host='0.0.0.0', port=5000)