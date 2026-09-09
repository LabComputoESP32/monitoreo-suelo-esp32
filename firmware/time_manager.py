import time
import ntptime


# ============================================================
# ESTADO DE SINCRONIZACION
# ============================================================

hora_sincronizada = False


# ============================================================
# SINCRONIZAR HORA POR INTERNET
# ============================================================

def sincronizar_hora():

    global hora_sincronizada

    print()
    print("============================")
    print("SINCRONIZANDO HORA")
    print("============================")

    try:

        # Sincroniza el reloj interno del ESP32
        # utilizando un servidor NTP.
        ntptime.settime()

        anio = time.gmtime()[0]

        if anio >= 2024:

            hora_sincronizada = True

            print(
                "Hora sincronizada correctamente"
            )

            print(
                "Hora UTC:",
                time.gmtime()
            )

            return True

        else:

            print(
                "ERROR: fecha obtenida no valida"
            )

            return False


    except Exception as error:

        print(
            "ERROR sincronizando hora:",
            error
        )

        return False


# ============================================================
# COMPROBAR SI EL RELOJ TIENE UNA FECHA VALIDA
# ============================================================

def reloj_valido():

    try:

        anio = time.gmtime()[0]

        return anio >= 2024

    except:

        return False


# ============================================================
# OBTENER TIMESTAMP UNIX EN MILISEGUNDOS
# ============================================================

def obtener_timestamp_ms():

    if not reloj_valido():

        print(
            "ADVERTENCIA: reloj no sincronizado"
        )

        return None


    segundos = time.time()


    # --------------------------------------------------------
    # MicroPython puede utilizar 1970 o 2000 como epoch,
    # dependiendo del puerto.
    # --------------------------------------------------------

    epoch_anio = time.gmtime(0)[0]


    if epoch_anio == 2000:

        # Segundos entre:
        # 01-01-1970 y 01-01-2000

        segundos += 946684800


    return int(
        segundos * 1000
    )
