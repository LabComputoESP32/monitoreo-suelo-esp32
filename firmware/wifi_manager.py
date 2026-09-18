import network
import time


# ============================================================
# CONFIGURACION
# ============================================================

# Dejamos 14 porque es el valor que ya comprobamos
# que funciona bien en nuestros ESP32-C3.
TX_POWER = 14

# Cuanto esperamos inicialmente antes de continuar offline.
TIEMPO_ESPERA_INICIAL = 10


# ============================================================
# CONFIGURAR INTERFAZ WIFI
# ============================================================

def configurar_interfaz(wlan):

    # Activar interfaz STA
    if not wlan.active():

        wlan.active(True)

        time.sleep_ms(500)


    # ========================================================
    # POTENCIA DE TRANSMISION
    # ========================================================

    try:

        wlan.config(
            txpower=TX_POWER
        )

        print(
            "TxPower:",
            TX_POWER,
            "dBm"
        )

    except Exception as error:

        print(
            "No se pudo configurar txpower:",
            error
        )


    # ========================================================
    # DESACTIVAR AHORRO DE ENERGIA
    # ========================================================

    try:

        wlan.config(
            pm=network.WLAN.PM_NONE
        )

        print(
            "Power management WiFi: OFF"
        )

    except Exception as error:

        print(
            "No se pudo configurar PM_NONE:",
            error
        )


    # ========================================================
    # RECONEXION AUTOMATICA ILIMITADA
    # ========================================================
    #
    # -1 = continuar intentando reconectar.
    #
    # IMPORTANTE:
    # No debemos apagar la interfaz despues,
    # porque eso cancelaria estos intentos.
    # ========================================================

    try:

        wlan.config(
            reconnects=-1
        )

        print(
            "Reintentos automaticos: ilimitados"
        )

    except Exception as error:

        print(
            "No se pudo configurar reconnects:",
            error
        )


# ============================================================
# MOSTRAR CALIDAD DE CONEXION
# ============================================================

def mostrar_estado(wlan):

    if not wlan.isconnected():

        print(
            "WiFi no conectado"
        )

        try:

            print(
                "Estado:",
                wlan.status()
            )

        except:

            pass

        return


    print(
        "WiFi conectado"
    )

    print(
        "IP:",
        wlan.ifconfig()[0]
    )


    try:

        rssi = wlan.status(
            "rssi"
        )

        print(
            "RSSI:",
            rssi,
            "dBm"
        )

    except:

        pass


# ============================================================
# CONECTAR WIFI
# ============================================================

def conectar_wifi(config_wifi):

    wlan = network.WLAN(
        network.STA_IF
    )


    # ========================================================
    # SI YA ESTA CONECTADO
    # ========================================================

    if wlan.isconnected():

        mostrar_estado(
            wlan
        )

        return wlan


    # ========================================================
    # CONFIGURAR INTERFAZ
    # ========================================================

    print()

    print(
        "============================"
    )

    print(
        "CONEXION WIFI"
    )

    print(
        "============================"
    )


    configurar_interfaz(
        wlan
    )


    ssid = config_wifi[
        "ssid"
    ]

    password = config_wifi[
        "password"
    ]


    # ========================================================
    # INICIAR CONEXION
    # ========================================================

    print()

    print(
        "Conectando a:",
        ssid
    )


    try:

        wlan.connect(
            ssid,
            password
        )

    except Exception as error:

        # Si el driver ya estaba intentando conectarse,
        # no apagamos la interfaz.
        #
        # Lo dejamos continuar trabajando
        # en segundo plano.

        print(
            "Aviso wlan.connect():",
            error
        )


    # ========================================================
    # ESPERAR CONEXION INICIAL
    # ========================================================

    segundos = 0


    while (
        not wlan.isconnected()
        and segundos < TIEMPO_ESPERA_INICIAL
    ):

        print(
            "Esperando WiFi:",
            segundos + 1,
            "/",
            TIEMPO_ESPERA_INICIAL
        )

        time.sleep(
            1
        )

        segundos += 1


    # ========================================================
    # RESULTADO
    # ========================================================

    if wlan.isconnected():

        print()

        mostrar_estado(
            wlan
        )


    else:

        print()

        print(
            "WiFi aun no disponible."
        )

        print(
            "El ESP32 continuara trabajando offline."
        )

        print(
            "El controlador WiFi seguira intentando"
        )

        print(
            "reconectar en segundo plano."
        )


        try:

            print(
                "Estado actual:",
                wlan.status()
            )

        except:

            pass


    return wlan
