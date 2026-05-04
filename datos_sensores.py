import requests
import random
import time
from datetime import datetime

SERVER_URL = "http://localhost:5000/api/sensores"
API_TOKEN = "696969696969"

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Token": API_TOKEN
}

estado = {
    "humedad_suelo_1": 45.0,
    "humedad_suelo_2": 50.0,
    "humedad_suelo_3": 55.0,
    "temperatura_1": 25.0,
    "temperatura_2": 26.0,
    "uv_index": 5.0,
    "luz_lux": 5000.0
}

def simular_fluctuacion(valor_actual, min_val, max_val, variacion_max):
    cambio = random.uniform(-variacion_max, variacion_max)
    nuevo_valor = valor_actual + cambio
    return round(max(min(nuevo_valor, max_val), min_val), 2)

def generar_datos_esp32():
    global estado

    estado["humedad_suelo_1"] = simular_fluctuacion(estado["humedad_suelo_1"], 10.0, 95.0, 2.0)
    estado["humedad_suelo_2"] = simular_fluctuacion(estado["humedad_suelo_2"], 10.0, 95.0, 2.0)
    estado["humedad_suelo_3"] = simular_fluctuacion(estado["humedad_suelo_3"], 10.0, 95.0, 2.0)
    estado["temperatura_1"]   = simular_fluctuacion(estado["temperatura_1"],   15.0, 40.0, 0.5)
    estado["temperatura_2"]   = simular_fluctuacion(estado["temperatura_2"],   15.0, 40.0, 0.5)
    estado["uv_index"]        = simular_fluctuacion(estado["uv_index"],         0.0, 11.0, 0.3)
    estado["luz_lux"]         = simular_fluctuacion(estado["luz_lux"],          0.0, 15000.0, 100.0)

    lluvia = 0  # Forzado a 1 para pruebas; restaurar lógica real cuando sea necesario:
                # lluvia = 1 if estado["uv_index"] < 2.0 and random.random() > 0.7 else 0

    return {
        "humedad_suelo_1": estado["humedad_suelo_1"],
        "humedad_suelo_2": estado["humedad_suelo_2"],
        "humedad_suelo_3": estado["humedad_suelo_3"],
        "temperatura_1":   estado["temperatura_1"],
        "temperatura_2":   estado["temperatura_2"],
        "uv_index":        estado["uv_index"],
        "lluvia":          int(lluvia),  # cast explícito por seguridad
        "luz_lux":         estado["luz_lux"],
        "bomba_1": 1 if estado["humedad_suelo_1"] < 30 else 0,
        "bomba_2": 1 if estado["humedad_suelo_2"] < 30 else 0,
        "bomba_3": 1 if estado["humedad_suelo_3"] < 30 else 0,
    }

def enviar_datos():
    payload = generar_datos_esp32()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Enviando datos...")
    print(f"    lluvia={payload['lluvia']} | uv={payload['uv_index']} | "
          f"temp={payload['temperatura_1']}°C | hum1={payload['humedad_suelo_1']}% | "
          f"bomba_1={payload['bomba_1']} bomba_2={payload['bomba_2']} bomba_3={payload['bomba_3']}")

    try:
        response = requests.post(SERVER_URL, json=payload, headers=HEADERS, timeout=5)
        if response.status_code in (200, 201):
            print(f"    ✅ Guardado correctamente")
        else:
            print(f"    ⚠️ Error {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        print("    ❌ Servidor no responde. ¿Está corriendo Flask?")
    except Exception as e:
        print(f"    ❌ Error inesperado: {e}")

if __name__ == '__main__':
    print("🚀 Simulador de Riego Inteligente")
    print(f"📡 → {SERVER_URL}")
    print("-" * 40)
    try:
        while True:
            enviar_datos()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nSimulación detenida.")