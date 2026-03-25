from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)

def get_db_data():
    conn = sqlite3.connect('monitoreo_agricola.db')
    conn.row_factory = sqlite3.Row # Para obtener diccionarios
    cursor = conn.cursor()
    # Obtenemos los últimos 24 registros guardados
    cursor.execute("SELECT * FROM pronostico_clima ORDER BY date DESC LIMIT 24")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows][::-1] # Invertir para que el orden sea cronológico

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clima')
def api_clima():
    data = get_db_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)