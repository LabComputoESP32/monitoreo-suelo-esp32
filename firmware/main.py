import time
import ujson

from wifi_manager import conectar_wifi

from sensor_manager import obtener_promedio

from firebase_manager import (
    enviar_registro_pendiente,
    obtener_siguiente_muestra
)

from offline_manager import (
    guardar_pendiente,
    listar_pendientes,
    leer_pendiente,
    eliminar_pendiente,
    obtener_siguiente_muestra_local,
    actualizar_contador_local,
    cantidad_pendientes
)

from time_manager import (
    sincronizar_hora,
    obtener_timestamp_ms
)

from updater import verificar_y_actualizar


# ============================================================
# CARGAR CONFIGURACION
# ============================================================

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


# ============================================================
# CONFIGURACION DE MUESTREO
# ============================================================

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


# ============================================================
# ESTADO GENERAL
# ============================================================

wlan = None

hora_sincronizada = False


# ============================================================
# INFORMACION DEL NODO
# ============================================================

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

print(
    "Lecturas por promedio:",
    cantidad_muestras
)

print(
    "Intervalo entre lecturas:",
    intervalo_muestreo,
    "segundos"
)


# ============================================================
# INTENTAR CONEXION WIFI
# ============================================================

def intentar_wifi():

    global wlan


    # Si ya esta conectado no hacemos nada

    if (
        wlan is not None
        and wlan.isconnected()
    ):

        return True


    print()

    print(
        "Intentando conectar WiFi..."
    )


    try:

        wlan = conectar_wifi(
            config_wifi
        )


        if wlan.isconnected():

            print(
                "WiFi conectado"
            )

            print(
                "IP:",
                wlan.ifconfig()[0]
            )

            return True


    except Exception as error:

        print(
            "ERROR conectando WiFi:",
            error
        )


    print(
        "WiFi no disponible"
    )


    return False


# ============================================================
# SINCRONIZAR RELOJ
# ============================================================

def intentar_sincronizar_hora():

    global hora_sincronizada


    if hora_sincronizada:

        return True


    if (
        wlan is None
        or not wlan.isconnected()
    ):

        return False


    print()

    print(
        "Intentando sincronizar hora..."
    )


    try:

        resultado = sincronizar_hora()


        if resultado:

            hora_sincronizada = True

            print(
                "Reloj listo"
            )

            return True


    except Exception as error:

        print(
            "ERROR sincronizando hora:",
            error
        )


    return False


# ============================================================
# PROCESAR DATOS PENDIENTES
# ============================================================

def procesar_pendientes():

    # --------------------------------------------------------
    # Sin WiFi no hacemos nada.
    # Los archivos permanecen guardados.
    # --------------------------------------------------------

    if (
        wlan is None
        or not wlan.isconnected()
    ):

        return False


    pendientes = listar_pendientes()


    if len(pendientes) == 0:

        return True


    print()

    print(
        "================================"
    )

    print(
        "RECUPERANDO DATOS PENDIENTES"
    )

    print(
        "================================"
    )

    print(
        "Cantidad:",
        len(pendientes)
    )


    # --------------------------------------------------------
    # Los archivos ya vienen ordenados:
    #
    # 0000000752.json
    # 0000000753.json
    # 0000000754.json
    #
    # De esta manera se envian cronologicamente.
    # --------------------------------------------------------

    for nombre_archivo in pendientes:

        print()

        print(
            "Procesando:",
            nombre_archivo
        )


        registro = leer_pendiente(
            nombre_archivo
        )


        if registro is None:

            print(
                "No fue posible leer el archivo."
            )

            print(
                "Se detiene recuperacion."
            )

            return False


        resultado = enviar_registro_pendiente(

            config_firebase,

            config_nodo,

            registro
        )


        # ====================================================
        # FIREBASE CONFIRMO
        # ====================================================

        if resultado:

            print(
                "Firebase confirmo muestra:",
                registro["muestra"]
            )


            eliminado = eliminar_pendiente(
                nombre_archivo
            )


            if not eliminado:

                print(
                    "ADVERTENCIA:"
                )

                print(
                    "Firebase recibio el dato,"
                )

                print(
                    "pero no se pudo borrar copia local."
                )


        # ====================================================
        # FIREBASE FALLO
        # ====================================================

        else:

            print(
                "No se pudo enviar muestra:",
                registro["muestra"]
            )

            print(
                "El archivo permanece guardado."
            )

            return False


        # Liberar socket

        time.sleep_ms(
            300
        )


    print()

    print(
        "Todos los pendientes fueron procesados."
    )


    return True


# ============================================================
# CONEXION INICIAL
# ============================================================

internet_disponible = intentar_wifi()


# ============================================================
# SINCRONIZAR HORA
# ============================================================

if internet_disponible:

    intentar_sincronizar_hora()


# ============================================================
# VERIFICAR ACTUALIZACIONES
# ============================================================

if internet_disponible:

    print()

    print(
        "Consultando actualizaciones..."
    )


    try:

        verificar_y_actualizar(
            config_github
        )

    except Exception as error:

        print(
            "No fue posible consultar actualizaciones:"
        )

        print(
            error
        )


else:

    print()

    print(
        "Sin Internet."
    )

    print(
        "Se omite comprobacion de actualizaciones."
    )


# ============================================================
# RECUPERAR PENDIENTES AL ARRANCAR
# ============================================================

if internet_disponible:

    procesar_pendientes()


# ============================================================
# DETERMINAR SIGUIENTE NUMERO DE MUESTRA
# ============================================================

print()

print(
    "================================"
)

print(
    "RECUPERANDO CONTADOR"
)

print(
    "================================"
)


# ------------------------------------------------------------
# Contador local
# ------------------------------------------------------------

siguiente_local = (
    obtener_siguiente_muestra_local()
)


print(
    "Siguiente muestra local:",
    siguiente_local
)


# ------------------------------------------------------------
# Contador Firebase
# ------------------------------------------------------------

siguiente_firebase = None


if (
    wlan is not None
    and wlan.isconnected()
):

    siguiente_firebase = (
        obtener_siguiente_muestra(
            config_firebase,
            config_nodo
        )
    )


print(
    "Siguiente muestra Firebase:",
    siguiente_firebase
)


# ------------------------------------------------------------
# Elegir el numero MAYOR.
#
# Ejemplo:
#
# Firebase = 751
# Local    = 756
#
# siguiente = 756
#
# Esto evita reutilizar numeros durante una caida de Internet.
# ------------------------------------------------------------

if siguiente_firebase is None:

    contador = siguiente_local

else:

    contador = max(
        siguiente_local,
        siguiente_firebase
    )


# ------------------------------------------------------------
# Sincronizar contador local con Firebase.
#
# Si Firebase va en 751 y local estaba vacio,
# guardamos que la ultima utilizada fue 750.
# ------------------------------------------------------------

if contador > 0:

    actualizar_contador_local(
        contador - 1
    )


print()

print(
    "SIGUIENTE PERIODO:",
    contador
)


# ============================================================
# CICLO PRINCIPAL
# ============================================================

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


    # ========================================================
    # 1. VERIFICAR WIFI
    # ========================================================

    if (
        wlan is None
        or not wlan.isconnected()
    ):

        print()

        print(
            "WiFi desconectado."
        )


        # Intentamos recuperar conexion.
        #
        # Si falla NO detenemos el programa.

        conexion_recuperada = (
            intentar_wifi()
        )


        if conexion_recuperada:

            print(
                "Conexion recuperada."
            )


            # Al regresar Internet,
            # sincronizamos NTP.

            hora_sincronizada = False

            intentar_sincronizar_hora()


            # Antes de generar nuevos envios,
            # recuperar cola pendiente.

            procesar_pendientes()


    # ========================================================
    # 2. TOMAR MUESTRAS
    # ========================================================

    temperatura_promedio, humedad_promedio = (
        obtener_promedio(
            config_sensor,
            cantidad_muestras,
            intervalo_muestreo
        )
    )


    # ========================================================
    # 3. VALIDAR PROMEDIO
    # ========================================================

    if (
        temperatura_promedio is None
        or humedad_promedio is None
    ):

        print()

        print(
            "No fue posible calcular promedio."
        )

        print(
            "Se intentara nuevamente."
        )

        continue


    # ========================================================
    # 4. TIMESTAMP ORIGINAL
    # ========================================================

    if hora_sincronizada:

        timestamp = (
            obtener_timestamp_ms()
        )

    else:

        # ----------------------------------------------------
        # Si el ESP arranco sin Internet y nunca logro
        # sincronizar NTP, no inventamos una fecha.
        #
        # El registro se conserva pero el timestamp sera None.
        # ----------------------------------------------------

        timestamp = None


    # ========================================================
    # 5. MOSTRAR PROMEDIO
    # ========================================================

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

    print(
        "Muestra:",
        contador
    )

    print(
        "Timestamp:",
        timestamp
    )


    # ========================================================
    # 6. CREAR REGISTRO
    # ========================================================

    registro = {

        "temperatura_promedio":
            temperatura_promedio,

        "humedad_promedio":
            humedad_promedio,

        "profundidad_cm":
            config_nodo[
                "profundidad_cm"
            ],

        "cantidad_lecturas":
            cantidad_muestras,

        "muestra":
            contador,

        "timestamp":
            timestamp
    }


    # ========================================================
    # 7. GUARDAR PRIMERO EN MEMORIA LOCAL
    # ========================================================

    print()

    print(
        "Guardando muestra localmente..."
    )


    guardado = guardar_pendiente(
        registro
    )


    if not guardado:

        print()

        print(
            "ERROR CRITICO:"
        )

        print(
            "No fue posible guardar la muestra."
        )

        print(
            "No se avanzara el contador."
        )


        time.sleep(
            2
        )

        continue


    print(
        "Muestra almacenada en flash."
    )


    # ========================================================
    # 8. AVANZAR CONTADOR
    # ========================================================
    #
    # IMPORTANTE:
    #
    # El contador avanza aunque no haya Internet.
    #
    # Ejemplo:
    #
    # 752 guardada
    # 753 guardada
    # 754 guardada
    #
    # Cuando vuelva Internet se enviaran todas.
    # ========================================================

    contador = (
        obtener_siguiente_muestra_local()
    )


    print(
        "Siguiente muestra:",
        contador
    )


    # ========================================================
    # 9. INTENTAR ENVIAR PENDIENTES
    # ========================================================

    if (
        wlan is not None
        and wlan.isconnected()
    ):

        procesar_pendientes()


    else:

        print()

        print(
            "Sin WiFi."
        )

        print(
            "La medicion permanece guardada."
        )

        print(
            "Pendientes:",
            cantidad_pendientes()
        )
