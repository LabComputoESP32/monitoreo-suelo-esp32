import urequests
import time


# ============================================================
# CERRAR RESPUESTA DE FORMA SEGURA
# ============================================================

def cerrar_respuesta(respuesta):

    if respuesta is not None:

        try:
            respuesta.close()

        except:
            pass


# ============================================================
# OBTENER SIGUIENTE NUMERO DE MUESTRA
# ============================================================

def obtener_siguiente_muestra(
    config_firebase,
    config_nodo
):

    url_base = (
        config_firebase["url"]
        .rstrip("/")
    )

    ruta_base = (
        config_firebase["ruta_base"]
    )

    nodo_id = (
        config_nodo["id"]
    )


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


        # ====================================================
        # SI NO EXISTEN DATOS ANTERIORES
        # ====================================================

        if datos is None:

            print(
                "No existen muestras anteriores"
            )

            print(
                "Siguiente muestra: 0"
            )

            return 0


        # ====================================================
        # SI NO EXISTE EL CAMPO MUESTRA
        # ====================================================

        if "muestra" not in datos:

            print(
                "No existe campo muestra"
            )

            print(
                "Siguiente muestra: 0"
            )

            return 0


        ultima_muestra = int(
            datos["muestra"]
        )


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

        print(
            error
        )


        return None


    finally:

        cerrar_respuesta(
            respuesta
        )


# ============================================================
# CONSTRUIR REGISTRO
# ============================================================

def construir_datos(
    config_nodo,
    temperatura_promedio,
    humedad_promedio,
    contador,
    cantidad_lecturas,
    timestamp_ms=None,
    profundidad_cm=None
):


    # ========================================================
    # PROFUNDIDAD
    # ========================================================

    if profundidad_cm is None:

        profundidad_cm = (
            config_nodo[
                "profundidad_cm"
            ]
        )


    # ========================================================
    # TIMESTAMP
    # ========================================================
    #
    # Si recibimos timestamp_ms:
    # usamos la hora ORIGINAL de la medicion.
    #
    # Si no recibimos timestamp_ms:
    # Firebase coloca la hora del servidor.
    # ========================================================

    if timestamp_ms is None:

        timestamp = {
            ".sv": "timestamp"
        }

    else:

        timestamp = int(
            timestamp_ms
        )


    # ========================================================
    # REGISTRO
    # ========================================================

    datos = {

        "temperatura_promedio":
            temperatura_promedio,

        "humedad_promedio":
            humedad_promedio,

        "profundidad_cm":
            profundidad_cm,

        "cantidad_lecturas":
            cantidad_lecturas,

        "muestra":
            int(contador),

        "timestamp":
            timestamp
    }


    return datos


# ============================================================
# ENVIAR REGISTRO A FIREBASE
# ============================================================

def enviar_registro(
    config_firebase,
    config_nodo,
    datos
):


    url_base = (
        config_firebase["url"]
        .rstrip("/")
    )


    ruta_base = (
        config_firebase[
            "ruta_base"
        ]
    )


    nodo_id = (
        config_nodo[
            "id"
        ]
    )


    contador = int(
        datos[
            "muestra"
        ]
    )


    # ========================================================
    # URL HISTORIAL
    # ========================================================

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


    # ========================================================
    # URL ULTIMA LECTURA
    # ========================================================

    url_ultima = (
        url_base
        + "/"
        + ruta_base
        + "/"
        + nodo_id
        + "/ultima_lectura.json"
    )


    respuesta_historial = None
    respuesta_ultima = None


    try:

        # ====================================================
        # 1. ENVIAR HISTORIAL
        # ====================================================
        #
        # Primero guardamos el historico.
        #
        # Si algo falla despues, el registro al menos
        # permanece guardado en el historial.
        #
        # PUT + numero de muestra permite volver a intentar
        # sin crear duplicados.
        # ====================================================

        print(
            "Enviando historial:",
            contador
        )


        respuesta_historial = (
            urequests.put(
                url_historial,
                json=datos,
                timeout=10
            )
        )


        print(
            "Historial:",
            respuesta_historial.status_code
        )


        if (
            respuesta_historial.status_code
            != 200
        ):

            print(
                "ERROR enviando historial"
            )

            return False


        cerrar_respuesta(
            respuesta_historial
        )

        respuesta_historial = None


        # Liberar socket

        time.sleep_ms(
            300
        )


        # ====================================================
        # 2. ACTUALIZAR ULTIMA LECTURA
        # ====================================================

        print(
            "Actualizando ultima lectura:",
            contador
        )


        respuesta_ultima = (
            urequests.put(
                url_ultima,
                json=datos,
                timeout=10
            )
        )


        print(
            "Ultimo promedio:",
            respuesta_ultima.status_code
        )


        if (
            respuesta_ultima.status_code
            != 200
        ):

            print(
                "ERROR enviando ultima lectura"
            )

            return False


        cerrar_respuesta(
            respuesta_ultima
        )

        respuesta_ultima = None


        # ====================================================
        # TODO CORRECTO
        # ====================================================

        print(
            "Promedio enviado correctamente"
        )


        return True


    except Exception as error:

        print()

        print(
            "ERROR enviando datos a Firebase:"
        )

        print(
            error
        )


        return False


    finally:

        cerrar_respuesta(
            respuesta_historial
        )

        cerrar_respuesta(
            respuesta_ultima
        )


# ============================================================
# ENVIAR DATOS NORMALES
# ============================================================
#
# Esta funcion conserva compatibilidad con tu main.py actual.
#
# Por ahora, si main.py no manda timestamp_ms,
# Firebase sigue poniendo el timestamp del servidor.
#
# Mas adelante main.py enviara el timestamp local.
# ============================================================

def enviar_datos(
    config_firebase,
    config_nodo,
    temperatura_promedio,
    humedad_promedio,
    contador,
    cantidad_lecturas,
    timestamp_ms=None
):


    datos = construir_datos(

        config_nodo,

        temperatura_promedio,

        humedad_promedio,

        contador,

        cantidad_lecturas,

        timestamp_ms=
            timestamp_ms
    )


    return enviar_registro(
        config_firebase,
        config_nodo,
        datos
    )


# ============================================================
# ENVIAR REGISTRO PENDIENTE
# ============================================================
#
# Esta sera la funcion utilizada por offline_manager.
#
# Recibe exactamente el registro que estaba guardado
# en la memoria flash.
#
# De esta manera conserva:
#
# - numero de muestra
# - temperatura
# - humedad
# - profundidad
# - cantidad de lecturas
# - timestamp ORIGINAL
# ============================================================

def enviar_registro_pendiente(
    config_firebase,
    config_nodo,
    registro
):


    # ========================================================
    # VALIDAR MUESTRA
    # ========================================================

    if (
        "muestra"
        not in registro
    ):

        print(
            "ERROR: registro pendiente sin muestra"
        )

        return False


    # ========================================================
    # VALIDAR TEMPERATURA
    # ========================================================

    if (
        "temperatura_promedio"
        not in registro
    ):

        print(
            "ERROR: registro pendiente sin temperatura"
        )

        return False


    # ========================================================
    # VALIDAR HUMEDAD
    # ========================================================

    if (
        "humedad_promedio"
        not in registro
    ):

        print(
            "ERROR: registro pendiente sin humedad"
        )

        return False


    # ========================================================
    # OBTENER TIMESTAMP ORIGINAL
    # ========================================================

    timestamp_original = (
        registro.get(
            "timestamp",
            None
        )
    )


    if (
        timestamp_original
        is None
    ):

        print(
            "ADVERTENCIA:"
        )

        print(
            "Registro pendiente sin timestamp original"
        )


    # ========================================================
    # CONSTRUIR REGISTRO PARA FIREBASE
    # ========================================================

    datos = construir_datos(

        config_nodo,

        registro[
            "temperatura_promedio"
        ],

        registro[
            "humedad_promedio"
        ],

        registro[
            "muestra"
        ],

        registro.get(
            "cantidad_lecturas",
            12
        ),

        timestamp_ms=
            timestamp_original,

        profundidad_cm=
            registro.get(
                "profundidad_cm",
                config_nodo[
                    "profundidad_cm"
                ]
            )
    )


    print()

    print(
        "Enviando registro pendiente:"
    )

    print(
        "Muestra:",
        datos["muestra"]
    )

    print(
        "Timestamp original:",
        datos["timestamp"]
    )


    # ========================================================
    # ENVIAR
    # ========================================================

    return enviar_registro(
        config_firebase,
        config_nodo,
        datos
    )
