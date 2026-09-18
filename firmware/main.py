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

wifi_estaba_conectado = False


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
# COMPROBAR SI EL RELOJ YA TIENE UNA FECHA VALIDA
# ============================================================

def reloj_valido():

    try:

        fecha = time.localtime()

        anio = fecha[0]

        # Si el reloj marca 2024 o posterior,
        # consideramos que ya contiene una fecha real.

        return anio >= 2024

    except Exception:

        return False


# ============================================================
# COMPROBAR WIFI
# ============================================================

def wifi_conectado():

    try:

        return (
            wlan is not None
            and wlan.isconnected()
        )

    except Exception:

        return False


# ============================================================
# INTENTAR CONEXION WIFI
# ============================================================

def intentar_wifi():

    global wlan


    # Si ya esta conectado no hacemos nada

    if wifi_conectado():

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

def intentar_sincronizar_hora(
    forzar=False
):

    global hora_sincronizada


    # --------------------------------------------------------
    # Si el reloj ya era valido y no estamos forzando
    # una nueva sincronizacion, no hacemos NTP otra vez.
    # --------------------------------------------------------

    if (
        not forzar
        and reloj_valido()
    ):

        hora_sincronizada = True

        return True


    # --------------------------------------------------------
    # NTP requiere WiFi.
    # --------------------------------------------------------

    if not wifi_conectado():

        # Aunque no haya WiFi, el reloj podria conservar
        # la hora de una sincronizacion anterior.

        hora_sincronizada = reloj_valido()

        return hora_sincronizada


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


    # --------------------------------------------------------
    # Si NTP falla pero el RTC conserva una fecha valida,
    # seguimos pudiendo generar timestamps.
    # --------------------------------------------------------

    if reloj_valido():

        hora_sincronizada = True

        print(
            "NTP no respondio,"
        )

        print(
            "pero el reloj local sigue siendo valido."
        )

        return True


    hora_sincronizada = False

    return False


# ============================================================
# PROCESAR DATOS PENDIENTES
# ============================================================

def procesar_pendientes():

    # --------------------------------------------------------
    # Sin WiFi no hacemos nada.
    # Los archivos permanecen guardados.
    # --------------------------------------------------------

    if not wifi_conectado():

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
    # Los archivos ya vienen ordenados.
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
# MANEJAR WIFI RECUPERADO
# ============================================================

def manejar_wifi_recuperado():

    global hora_sincronizada


    if not wifi_conectado():

        return False


    print()

    print(
        "================================"
    )

    print(
        "WIFI RECUPERADO"
    )

    print(
        "================================"
    )


    try:

        print(
            "IP:",
            wlan.ifconfig()[0]
        )

    except:

        pass


    try:

        print(
            "RSSI:",
            wlan.status("rssi"),
            "dBm"
        )

    except:

        pass


    # --------------------------------------------------------
    # Dejamos unos segundos para que la red y DHCP
    # terminen de estabilizarse antes de NTP/Firebase.
    # --------------------------------------------------------

    print(
        "Esperando estabilizacion de red..."
    )

    time.sleep(
        2
    )


    # --------------------------------------------------------
    # Al recuperar la red intentamos actualizar NTP.
    #
    # Si NTP falla pero el RTC ya tenia hora correcta,
    # conservara esa hora.
    # --------------------------------------------------------

    intentar_sincronizar_hora(
        forzar=True
    )


    # --------------------------------------------------------
    # Recuperar los datos almacenados durante la desconexion.
    # --------------------------------------------------------

    procesar_pendientes()


    return True


# ============================================================
# COMPROBAR RELOJ AL ARRANCAR
# ============================================================

if reloj_valido():

    hora_sincronizada = True

    print()

    print(
        "Reloj local conserva una fecha valida."
    )


# ============================================================
# CONEXION INICIAL
# ============================================================

internet_disponible = intentar_wifi()

wifi_estaba_conectado = internet_disponible


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


if wifi_conectado():

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
    # 1. VERIFICAR WIFI AL INICIO DEL PERIODO
    # ========================================================

    estado_wifi_actual = wifi_conectado()


    # --------------------------------------------------------
    # CASO A:
    # El periodo anterior termino sin WiFi,
    # pero el driver se reconecto por si solo.
    # --------------------------------------------------------

    if (
        estado_wifi_actual
        and not wifi_estaba_conectado
    ):

        manejar_wifi_recuperado()

        wifi_estaba_conectado = True


    # --------------------------------------------------------
    # CASO B:
    # Sigue desconectado.
    # Intentamos iniciar/reanudar conexion.
    # --------------------------------------------------------

    elif not estado_wifi_actual:

        wifi_estaba_conectado = False

        print()

        print(
            "WiFi desconectado."
        )


        conexion_recuperada = (
            intentar_wifi()
        )


        if conexion_recuperada:

            manejar_wifi_recuperado()

            wifi_estaba_conectado = True


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
    # 4. REVISAR WIFI DESPUES DE LAS 12 LECTURAS
    # ========================================================
    #
    # ESTA ES LA MEJORA IMPORTANTE.
    #
    # Durante las 12 lecturas transcurre aproximadamente
    # un minuto.
    #
    # El driver WiFi puede recuperar la conexion durante
    # ese tiempo.
    #
    # Antes el main.py no se enteraba hasta el siguiente
    # periodo.
    # ========================================================

    estado_wifi_despues_medicion = (
        wifi_conectado()
    )


    if (
        estado_wifi_despues_medicion
        and not wifi_estaba_conectado
    ):

        print()

        print(
            "WiFi regreso durante el periodo de medicion."
        )

        manejar_wifi_recuperado()

        wifi_estaba_conectado = True


    elif not estado_wifi_despues_medicion:

        wifi_estaba_conectado = False


    # ========================================================
    # 5. COMPROBAR RELOJ ANTES DEL TIMESTAMP
    # ========================================================

    if reloj_valido():

        hora_sincronizada = True


    # Si el reloj aun no es valido pero el WiFi ya regreso,
    # intentamos NTP antes de crear el registro.

    elif wifi_conectado():

        intentar_sincronizar_hora()


    # ========================================================
    # 6. TIMESTAMP ORIGINAL
    # ========================================================

    if (
        hora_sincronizada
        and reloj_valido()
    ):

        timestamp = (
            obtener_timestamp_ms()
        )

    else:

        # ----------------------------------------------------
        # Esto solo deberia ocurrir si el equipo arranco
        # completamente sin Internet y nunca habia tenido
        # una hora valida.
        # ----------------------------------------------------

        timestamp = None


    # ========================================================
    # 7. MOSTRAR PROMEDIO
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
    # 8. CREAR REGISTRO
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
    # 9. GUARDAR PRIMERO EN MEMORIA LOCAL
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
    # 10. AVANZAR CONTADOR
    # ========================================================

    contador = (
        obtener_siguiente_muestra_local()
    )


    print(
        "Siguiente muestra:",
        contador
    )


    # ========================================================
    # 11. REVISAR WIFI NUEVAMENTE ANTES DE ENVIAR
    # ========================================================

    estado_wifi_final = (
        wifi_conectado()
    )


    # Puede regresar incluso entre el promedio
    # y el guardado local.

    if (
        estado_wifi_final
        and not wifi_estaba_conectado
    ):

        print()

        print(
            "WiFi recuperado antes del envio."
        )

        manejar_wifi_recuperado()

        wifi_estaba_conectado = True


    elif not estado_wifi_final:

        wifi_estaba_conectado = False


    # ========================================================
    # 12. INTENTAR ENVIAR PENDIENTES
    # ========================================================

    if wifi_conectado():

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
