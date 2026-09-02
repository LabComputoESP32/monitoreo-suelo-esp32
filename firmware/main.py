import time
import ujson

from wifi_manager import conectar_wifi

from sensor_manager import obtener_promedio

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
# INFORMACION DEL NODO
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


# ==========================================
# CONECTAR WIFI
# ==========================================

wlan = conectar_wifi(
    config_wifi
)


if not wlan.isconnected():

    raise Exception(
        "Sin conexion WiFi"
    )


# ==========================================
# VERIFICAR ACTUALIZACIONES
# ==========================================

print()
print("Consultando actualizaciones...")

verificar_y_actualizar(
    config_github
)


# ==========================================
# CONFIGURACION DE MUESTREO
# ==========================================

intervalo_muestreo = (
    config_medicion[
        "intervalo_muestreo_segundos"
    ]
)

cantidad_muestras = (
    config_medicion[
        "cantidad_muestras"
    ]
)


print()

print(
    "Lecturas por promedio:",
    cantidad_muestras
)

print(
    "Intervalo entre lecturas:",
    intervalo_muestreo,
    "segundos"
)


# ==========================================
# RECUPERAR CONTADOR
# ==========================================

contador = obtener_siguiente_muestra(
    config_firebase,
    config_nodo
)


while contador is None:

    print(
        "No se pudo recuperar contador."
    )

    print(
        "Reintentando en 5 segundos..."
    )

    time.sleep(5)

    contador = obtener_siguiente_muestra(
        config_firebase,
        config_nodo
    )


# ==========================================
# CICLO PRINCIPAL
# ==========================================

while True:

    print()

    print(
        "================================"
    )

    print(
        "PERIODO:",
        contador
    )

    print(
        "================================"
    )


    # ======================================
    # TOMAR MUESTRAS Y PROMEDIAR
    # ======================================

    temperatura_promedio, humedad_promedio = (
        obtener_promedio(
            config_sensor,
            cantidad_muestras,
            intervalo_muestreo
        )
    )


    # ======================================
    # VERIFICAR PROMEDIO
    # ======================================

    if (
        temperatura_promedio is None
        or humedad_promedio is None
    ):

        print(
            "No fue posible calcular promedio"
        )

        continue


    print()

    print(
        "---------- PROMEDIO ----------"
    )

    print(
        "Temperatura promedio:",
        temperatura_promedio,
        "C"
    )

    print(
        "Humedad promedio:",
        humedad_promedio,
        "%"
    )


    # ======================================
    # ENVIAR SOLO PROMEDIO
    # ======================================

    resultado = enviar_datos(
        config_firebase,
        config_nodo,
        temperatura_promedio,
        humedad_promedio,
        contador,
        cantidad_muestras
    )


    if resultado:

        print(
            "Promedio enviado correctamente"
        )

        contador += 1

    else:

        print(
            "Error enviando promedio"
        )

        print(
            "Se conserva el numero:",
            contador
        )
