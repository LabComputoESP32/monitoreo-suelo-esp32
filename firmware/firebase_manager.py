import urequests
import time


# ==========================================
# OBTENER SIGUIENTE NUMERO DE MUESTRA
# ==========================================

def obtener_siguiente_muestra(
    config_firebase,
    config_nodo
):

    url_base = config_firebase["url"].rstrip("/")
    ruta_base = config_firebase["ruta_base"]
    nodo_id = config_nodo["id"]

    url = (
        url_base
        + "/"
        + ruta_base
        + "/"
        + nodo_id
        + "/ultima_lectura.json"
    )

    respuesta = None

    try:

        print(
            "Consultando ultima muestra en Firebase..."
        )

        respuesta = urequests.get(
            url,
            timeout=10
        )

        print(
            "Firebase HTTP:",
            respuesta.status_code
        )

        if respuesta.status_code != 200:

            print(
                "No se pudo consultar ultima muestra"
            )

            return None


        datos = respuesta.json()


        # ==================================
        # SI TODAVIA NO HAY DATOS
        # ==================================

        if datos is None:

            print(
                "No existen muestras anteriores"
            )

            print(
                "Siguiente muestra: 0"
            )

            return 0


        # ==================================
        # SI NO EXISTE CAMPO MUESTRA
        # ==================================

        if "muestra" not in datos:

            print(
                "No existe campo muestra"
            )

            print(
                "Siguiente muestra: 0"
            )

            return 0


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


    except Exception as error:

        print()
        print(
            "ERROR consultando Firebase:"
        )

        print(error)

        return None


    finally:

        if respuesta is not None:

            try:
                respuesta.close()

            except:
                pass


# ==========================================
# ENVIAR DATOS A FIREBASE
# ==========================================

def enviar_datos(
    config_firebase,
    config_nodo,
    temperatura_promedio,
    humedad_promedio,
    contador,
    cantidad_lecturas
):

    url_base = config_firebase["url"].rstrip("/")
    ruta_base = config_firebase["ruta_base"]
    nodo_id = config_nodo["id"]


    # ======================================
    # DATOS QUE SE ENVIARAN
    # ======================================

    datos = {

        "temperatura_promedio":
            temperatura_promedio,

        "humedad_promedio":
            humedad_promedio,

        "profundidad_cm":
            config_nodo["profundidad_cm"],

        "cantidad_lecturas":
            cantidad_lecturas,

        "muestra":
            contador,

        "timestamp": {
            ".sv": "timestamp"
        }
    }


    # ======================================
    # URL ULTIMA LECTURA
    # ======================================

    url_ultima = (
        url_base
        + "/"
        + ruta_base
        + "/"
        + nodo_id
        + "/ultima_lectura.json"
    )


    # ======================================
    # URL HISTORIAL
    #
    # Ahora usamos el numero de muestra
    # como ID.
    #
    # Ejemplo:
    # historial/118
    # historial/119
    # historial/120
    #
    # Esto evita duplicados.
    # ======================================

    url_historial = (
        url_base
        + "/"
        + ruta_base
        + "/"
        + nodo_id
        + "/historial/"
        + str(contador)
        + ".json"
    )


    respuesta_ultima = None
    respuesta_historial = None


    try:

        # ==================================
        # 1. ENVIAR ULTIMA LECTURA
        # ==================================

        respuesta_ultima = urequests.put(
            url_ultima,
            json=datos,
            timeout=10
        )


        print(
            "Ultimo promedio:",
            respuesta_ultima.status_code
        )


        if respuesta_ultima.status_code != 200:

            print(
                "ERROR enviando ultima lectura"
            )

            return False


        # Cerrar conexion inmediatamente
        respuesta_ultima.close()

        respuesta_ultima = None


        # Pequeña pausa para liberar socket
        time.sleep_ms(300)


        # ==================================
        # 2. ENVIAR HISTORIAL
        # ==================================

        respuesta_historial = urequests.put(
            url_historial,
            json=datos,
            timeout=10
        )


        print(
            "Historial:",
            respuesta_historial.status_code
        )


        if respuesta_historial.status_code != 200:

            print(
                "ERROR enviando historial"
            )

            return False


        respuesta_historial.close()

        respuesta_historial = None


        # ==================================
        # TODO CORRECTO
        # ==================================

        print(
            "Promedio enviado correctamente"
        )


        return True


    except Exception as error:

        print()
        print(
            "ERROR enviando datos a Firebase:"
        )

        print(error)


        return False


    finally:

        # ==================================
        # GARANTIZAR CIERRE DE CONEXIONES
        # ==================================

        if respuesta_ultima is not None:

            try:

                respuesta_ultima.close()

            except:
                pass


        if respuesta_historial is not None:

            try:

                respuesta_historial.close()

            except:
                pass
