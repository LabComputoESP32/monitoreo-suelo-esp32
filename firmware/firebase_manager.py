import urequests
import ujson


def enviar_datos(config_firebase, config_nodo, temperatura, humedad, contador):

    # Datos de configuración
    FIREBASE = config_firebase["url"]
    RUTA_BASE = config_firebase["ruta_base"]

    NODO = config_nodo["id"]
    PROFUNDIDAD = config_nodo["profundidad_cm"]

    # Ruta para sobrescribir la última lectura
    URL_ACTUAL = (
        FIREBASE
        + "/"
        + RUTA_BASE
        + "/"
        + NODO
        + "/ultima_lectura.json"
    )

    # Ruta para almacenar el historial
    URL_HISTORIAL = (
        FIREBASE
        + "/"
        + RUTA_BASE
        + "/"
        + NODO
        + "/historial.json"
    )

    # Datos que se enviarán a Firebase
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

    datos_json = ujson.dumps(datos)

    try:

        # =====================================
        # ACTUALIZAR ULTIMA LECTURA
        # =====================================

        respuesta = urequests.put(
            URL_ACTUAL,
            data=datos_json,
            headers=headers
        )

        print(
            "Ultima lectura:",
            respuesta.status_code
        )

        respuesta.close()


        # =====================================
        # GUARDAR EN HISTORIAL
        # =====================================

        respuesta = urequests.post(
            URL_HISTORIAL,
            data=datos_json,
            headers=headers
        )

        print(
            "Historial:",
            respuesta.status_code
        )

        respuesta.close()

        return True


    except Exception as error:

        print("Error enviando a Firebase:")
        print(error)

        return False
