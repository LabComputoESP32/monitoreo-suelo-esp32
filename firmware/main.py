import time
import ujson

from wifi_manager import conectar_wifi

from sensor_manager import leer_sensor

from firebase_manager import (
    enviar_datos,
    obtener_siguiente_muestra
)

from updater import verificar_y_actualizar


# ==========================================
# CARGAR CONFIGURACION
# ==========================================

with open(
    "config.json",
    "r"
) as archivo:

    config = ujson.load(
        archivo
    )


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

print(
    "================================"
)

print(
    "SISTEMA DE MONITOREO DE SUELO"
)

print(
    "================================"
)

print(
    "Nodo:",
    config_nodo["id"]
)

print(
    "Nombre:",
    config_nodo["nombre"]
)

print(
    "Profundidad:",
    config_nodo["profundidad_cm"],
    "cm"
)

print(
    "================================"
)

print()


# ==========================================
# CONECTAR WIFI
# ==========================================

wlan = conectar_wifi(
    config_wifi
)


if not wlan.isconnected():

    print(
        "No hay conexion WiFi."
    )

    print(
        "El sistema no puede continuar."
    )

    raise Exception(
        "Sin conexion WiFi"
    )


# ==========================================
# VERIFICAR ACTUALIZACIONES
# ==========================================

print()

print(
    "Consultando actualizaciones..."
)

verificar_y_actualizar(
    config_github
)


# ==========================================
# CONFIGURACION DE MEDICION
# ==========================================

intervalo = (
    config_medicion[
        "intervalo_segundos"
    ]
)


# ==========================================
# RECUPERAR NUMERO DE MUESTRA
# ==========================================

contador = obtener_siguiente_muestra(
    config_firebase,
    config_nodo
)


# Si Firebase no responde,
# NO comenzamos desde cero.
# Esperamos hasta recuperar el contador.

while contador is None:

    print()

    print(
        "No se pudo recuperar "
        "el numero de muestra."
    )

    print(
        "Reintentando en 5 segundos..."
    )

    time.sleep(5)

    contador = obtener_siguiente_muestra(
        config_firebase,
        config_nodo
    )


print()

print(
    "Sistema listo."
)

print(
    "Iniciando desde muestra:",
    contador
)


# ==========================================
# CICLO PRINCIPAL
# ==========================================

while True:

    print()

    print(
        "--------------------------------"
    )

    print(
        "Muestra:",
        contador
    )


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
    # ENVIAR DATOS A FIREBASE
    # ======================================

    resultado = enviar_datos(
        config_firebase,
        config_nodo,
        temperatura,
        humedad,
        contador
    )


    # ======================================
    # ACTUALIZAR CONTADOR
    # ======================================

    if resultado:

        print(
            "Datos enviados correctamente"
        )

        contador += 1

    else:

        print(
            "Error enviando datos"
        )

        print(
            "La muestra",
            contador,
            "se intentara nuevamente"
        )


    # ======================================
    # ESPERAR SIGUIENTE MEDICION
    # ======================================

    print(
        "Esperando",
        intervalo,
        "segundos..."
    )

    time.sleep(
        intervalo
    )
