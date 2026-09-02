import urequests
import ujson


# ==========================================
# OBTENER SIGUIENTE NUMERO DE MUESTRA
# ==========================================

def obtener_siguiente_muestra(
    config_firebase,
    config_nodo
):

    FIREBASE = config_firebase["url"]
    RUTA_BASE = config_firebase["ruta_base"]
    NODO = config_nodo["id"]

    URL_ACTUAL = (
        FIREBASE
        + "/"
        + RUTA_BASE
        + "/"
        + NODO
        + "/ultima_lectura.json"
    )

    print()
    print("Consultando ultima muestra en Firebase...")

    try:

        respuesta = urequests.get(
            URL_ACTUAL
        )

        print(
            "Firebase HTTP:",
            respuesta.status_code
        )

        if respuesta.status_code == 200:

            datos = respuesta.json()

            respuesta.close()

            # ----------------------------------
            # NODO SIN DATOS ANTERIORES
            # ----------------------------------

            if datos is None:

                print(
                    "No existen muestras anteriores"
                )

                print(
                    "Comenzando desde muestra 0"
                )

                return 0


            # ----------------------------------
            # EXISTE UNA MUESTRA ANTERIOR
            # ----------------------------------

            if "muestra" in datos:

                ultima_muestra = datos["muestra"]

                siguiente_muestra = (
                    ultima_muestra + 1
                )

                print(
                    "Ultima muestra:",
                    ultima_muestra
                )

                print(
                    "Siguiente muestra:",
                    siguiente_muestra
                )

                return siguiente_muestra


            # ----------------------------------
            # NO EXISTE CAMPO MUESTRA
            # ----------------------------------

            print(
                "No existe el campo muestra"
            )

            print(
                "Comenzando desde muestra 0"
            )

            return 0


        else:

            print(
                "No se pudo consultar Firebase"
            )

            respuesta.close()

            return None


    except Exception as error:

        print(
            "Error obteniendo contador:"
        )

        print(error)

        return None


# ==========================================
# ENVIAR DATOS A FIREBASE
# ==========================================

def enviar_datos(
    config_firebase,
    config_nodo,
    temperatura,
    humedad,
    contador
):

    # ======================================
    # CONFIGURACION
    # ======================================

    FIREBASE = config_firebase["url"]
    RUTA_BASE = config_firebase["ruta_base"]

    NODO = config_nodo["id"]

    PROFUNDIDAD = (
        config_nodo["profundidad_cm"]
    )


    # ======================================
    # URL ULTIMA LECTURA
    # ======================================

    URL_ACTUAL = (
        FIREBASE
        + "/"
        + RUTA_BASE
        + "/"
        + NODO
        + "/ultima_lectura.json"
    )


    # ======================================
    # URL HISTORIAL
    # ======================================

    URL_HISTORIAL = (
        FIREBASE
        + "/"
        + RUTA_BASE
        + "/"
        + NODO
        + "/historial.json"
    )


    # ======================================
    # DATOS
    # ======================================

    datos = {

        "temperatura": temperatura,

        "humedad": humedad,

        "profundidad_cm": PROFUNDIDAD,

        "muestra": contador,

        "timestamp": {
            ".sv": "timestamp"
        }
    }


    headers = {
        "Content-Type": "application/json"
    }


    datos_json = ujson.dumps(
        datos
    )


    try:

        # ==================================
        # ACTUALIZAR ULTIMA LECTURA
        # ==================================

        respuesta = urequests.put(
            URL_ACTUAL,
            data=datos_json,
            headers=headers
        )

        codigo_actual = (
            respuesta.status_code
        )

        print(
            "Ultima lectura:",
            codigo_actual
        )

        respuesta.close()


        # ==================================
        # COMPROBAR PUT
        # ==================================

        if codigo_actual != 200:

            print(
                "Error actualizando ultima lectura"
            )

            return False


        # ==================================
        # GUARDAR HISTORIAL
        # ==================================

        respuesta = urequests.post(
            URL_HISTORIAL,
            data=datos_json,
            headers=headers
        )

        codigo_historial = (
            respuesta.status_code
        )

        print(
            "Historial:",
            codigo_historial
        )

        respuesta.close()


        # ==================================
        # COMPROBAR POST
        # ==================================

        if codigo_historial != 200:

            print(
                "Error guardando historial"
            )

            return False


        return True


    except Exception as error:

        print(
            "Error enviando a Firebase:"
        )

        print(error)

        return False
