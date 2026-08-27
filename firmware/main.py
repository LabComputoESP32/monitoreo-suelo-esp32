import time
import ujson

from wifi_manager import conectar_wifi
from sensor_manager import leer_sensor
from firebase_manager import enviar_datos
from updater import verificar_y_actualizar


# ==========================================
# CARGAR CONFIGURACION
# ==========================================

with open("config.json", "r") as archivo:
    config = ujson.load(archivo)

config_wifi = config["wifi"]
config_sensor = config["sensor"]
config_firebase = config["firebase"]
config_nodo = config["nodo"]
config_medicion = config["medicion"]
config_github = config["github"]


# ==========================================
# MOSTRAR INFORMACION DEL NODO
# ==========================================

print()
print("================================")
print("SISTEMA DE MONITOREO DE SUELO")
print("================================")
print("Nodo:", config_nodo["id"])
print("Nombre:", config_nodo["nombre"])
print(
    "Profundidad:",
    config_nodo["profundidad_cm"],
    "cm"
)
print("================================")
print()


# ==========================================
# CONECTAR WIFI
# ==========================================

wlan = conectar_wifi(config_wifi)

if not wlan.isconnected():

    print("No hay conexion WiFi.")
    print("El sistema no puede continuar.")

    raise Exception("Sin conexion WiFi")


# ==========================================
# VERIFICAR ACTUALIZACION EN GITHUB
# ==========================================

print()
print("Consultando actualizaciones...")

verificar_y_actualizar(
    config_github
)

# Si existe una actualizacion,
# updater.py reiniciara automaticamente
# el ESP32.
#
# Si no existe actualizacion,
# el programa continua normalmente.


# ==========================================
# CONFIGURACION DE MEDICION
# ==========================================

intervalo = config_medicion[
    "intervalo_segundos"
]

contador = 0


# ==========================================
# CICLO PRINCIPAL
# ==========================================

while True:

    print()
    print("--------------------------------")
    print("Muestra:", contador)

    # ======================================
    # LEER SENSOR
    # ======================================

    temperatura, humedad = leer_sensor(
        config_sensor
    )

    print(
        "Temperatura:",
        temperatura,
        "C"
    )

    print(
        "Humedad:",
        humedad,
        "%"
    )


    # ======================================
    # ENVIAR A FIREBASE
    # ======================================

    resultado = enviar_datos(
        config_firebase,
        config_nodo,
        temperatura,
        humedad,
        contador
    )


    if resultado:

        print(
            "Datos enviados correctamente"
        )

    else:

        print(
            "Error al enviar los datos"
        )


    # ======================================
    # SIGUIENTE MUESTRA
    # ======================================

    contador += 1

    print(
        "Esperando",
        intervalo,
        "segundos..."
    )

    time.sleep(intervalo)
