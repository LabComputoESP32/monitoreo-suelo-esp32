import urequests
import ujson
import os


# ============================================================
# ARCHIVO DE ESTADO LOCAL
# ============================================================

ARCHIVO_ESTADO = "control_state.json"
ARCHIVO_TEMP = "control_state.tmp"


# ============================================================
# ESTADO LOCAL
# ============================================================

ultimo_comando_ejecutado = 0

confirmacion_pendiente = None

estado_inicializado = False


# ============================================================
# URL DEL COMANDO
# ============================================================

def obtener_url_comando(
    config_firebase,
    config_nodo
):

    url_base = config_firebase[
        "url"
    ].rstrip("/")

    nodo_id = config_nodo[
        "id"
    ]

    return (
        url_base
        + "/comandos/"
        + nodo_id
        + ".json"
    )


# ============================================================
# URL DE CONFIRMACION
# ============================================================

def obtener_url_confirmacion(
    config_firebase,
    config_nodo
):

    url_base = config_firebase[
        "url"
    ].rstrip("/")

    nodo_id = config_nodo[
        "id"
    ]

    return (
        url_base
        + "/estado_control/"
        + nodo_id
        + ".json"
    )


# ============================================================
# CARGAR ESTADO LOCAL
# ============================================================

def cargar_estado_local():

    global ultimo_comando_ejecutado
    global confirmacion_pendiente


    datos = None


    # --------------------------------------------------------
    # Intentar archivo principal
    # --------------------------------------------------------

    try:

        with open(
            ARCHIVO_ESTADO,
            "r"
        ) as archivo:

            datos = ujson.load(
                archivo
            )

    except:

        datos = None


    # --------------------------------------------------------
    # Si hubo un corte durante escritura,
    # intentar recuperar archivo temporal.
    # --------------------------------------------------------

    if datos is None:

        try:

            with open(
                ARCHIVO_TEMP,
                "r"
            ) as archivo:

                datos = ujson.load(
                    archivo
                )

        except:

            datos = None


    # --------------------------------------------------------
    # No existe estado previo
    # --------------------------------------------------------

    if datos is None:

        ultimo_comando_ejecutado = 0

        confirmacion_pendiente = None

        return False


    ultimo_comando_ejecutado = int(
        datos.get(
            "ultimo_comando_ejecutado",
            0
        )
    )


    confirmacion_pendiente = datos.get(
        "confirmacion_pendiente",
        None
    )


    return True


# ============================================================
# GUARDAR ESTADO LOCAL
# ============================================================

def guardar_estado_local():

    datos = {

        "ultimo_comando_ejecutado":
            ultimo_comando_ejecutado,

        "confirmacion_pendiente":
            confirmacion_pendiente

    }


    try:

        # Primero escribir temporal

        with open(
            ARCHIVO_TEMP,
            "w"
        ) as archivo:

            ujson.dump(
                datos,
                archivo
            )


        # Borrar versión anterior

        try:

            os.remove(
                ARCHIVO_ESTADO
            )

        except:

            pass


        # Convertir temporal en principal

        os.rename(
            ARCHIVO_TEMP,
            ARCHIVO_ESTADO
        )


        return True


    except Exception as error:

        print(
            "ERROR guardando estado de control:",
            error
        )

        return False


# ============================================================
# LEER ULTIMO COMANDO CONFIRMADO EN FIREBASE
# ============================================================

def obtener_ultimo_confirmado(
    config_firebase,
    config_nodo
):

    url = obtener_url_confirmacion(
        config_firebase,
        config_nodo
    )


    respuesta = None


    try:

        respuesta = urequests.get(
            url,
            timeout=5
        )


        if respuesta.status_code != 200:

            return None


        datos = respuesta.json()


        if not datos:

            return 0


        return int(
            datos.get(
                "comando_id",
                0
            )
        )


    except Exception as error:

        print(
            "ERROR leyendo confirmacion:",
            error
        )

        return None


    finally:

        if respuesta is not None:

            try:

                respuesta.close()

            except:

                pass


# ============================================================
# INICIALIZAR ESTADO
# ============================================================

def inicializar_estado(
    config_firebase,
    config_nodo
):

    global estado_inicializado
    global ultimo_comando_ejecutado


    if estado_inicializado:

        return


    cargar_estado_local()


    # --------------------------------------------------------
    # Si todavía no tenemos historial local,
    # utilizar la última confirmación existente
    # en Firebase como punto de partida.
    # --------------------------------------------------------

    if (
        ultimo_comando_ejecutado == 0
        and confirmacion_pendiente is None
    ):

        ultimo_confirmado = (
            obtener_ultimo_confirmado(
                config_firebase,
                config_nodo
            )
        )


        if (
            ultimo_confirmado is not None
            and ultimo_confirmado != 0
        ):

            ultimo_comando_ejecutado = (
                ultimo_confirmado
            )

            guardar_estado_local()


    estado_inicializado = True


# ============================================================
# CONSULTAR COMANDO
# ============================================================

def consultar_comando(
    config_firebase,
    config_nodo
):

    url = obtener_url_comando(
        config_firebase,
        config_nodo
    )


    respuesta = None


    try:

        respuesta = urequests.get(
            url,
            timeout=5
        )


        if respuesta.status_code != 200:

            print(
                "Control HTTP:",
                respuesta.status_code
            )

            return None


        comando = respuesta.json()


        if not comando:

            return None


        comando_id = int(
            comando.get(
                "comando_id",
                0
            )
        )


        if comando_id == 0:

            return None


        # ====================================================
        # YA FUE EJECUTADO
        # ====================================================

        if (
            comando_id
            ==
            ultimo_comando_ejecutado
        ):

            return None


        return comando


    except Exception as error:

        print(
            "ERROR consultando comando:",
            error
        )

        return None


    finally:

        if respuesta is not None:

            try:

                respuesta.close()

            except:

                pass


# ============================================================
# MOSTRAR COMANDO
# ============================================================

def mostrar_comando(
    comando
):

    estado = comando.get(
        "estado",
        False
    )


    modo = comando.get(
        "modo",
        "manual"
    )


    duracion = comando.get(
        "duracion_min",
        0
    )


    comando_id = comando.get(
        "comando_id",
        0
    )


    print()

    print(
        "================================"
    )

    print(
        "NUEVO COMANDO RECIBIDO"
    )

    print(
        "================================"
    )


    if estado:

        print(
            "Estado: ON"
        )

    else:

        print(
            "Estado: OFF"
        )


    print(
        "Modo:",
        modo
    )


    print(
        "Duracion:",
        duracion,
        "minutos"
    )


    print(
        "Comando ID:",
        comando_id
    )


    print(
        "================================"
    )


# ============================================================
# ENVIAR CONFIRMACION FIREBASE
# ============================================================

def confirmar_comando(
    config_firebase,
    config_nodo,
    comando
):

    url = obtener_url_confirmacion(
        config_firebase,
        config_nodo
    )


    datos = {

        "comando_id":
            comando.get(
                "comando_id",
                0
            ),

        "recibido":
            True,

        "estado":
            comando.get(
                "estado",
                False
            ),

        "modo":
            comando.get(
                "modo",
                "manual"
            ),

        "duracion_min":
            comando.get(
                "duracion_min",
                0
            )

    }


    respuesta = None


    try:

        print()

        print(
            "Confirmando comando en Firebase..."
        )


        respuesta = urequests.put(
            url,
            json=datos,
            timeout=5
        )


        print(
            "Confirmacion HTTP:",
            respuesta.status_code
        )


        if respuesta.status_code == 200:

            print(
                "Comando confirmado correctamente"
            )

            return True


        return False


    except Exception as error:

        print(
            "ERROR confirmando comando:",
            error
        )

        return False


    finally:

        if respuesta is not None:

            try:

                respuesta.close()

            except:

                pass


# ============================================================
# REGISTRAR COMANDO COMO EJECUTADO
# ============================================================

def registrar_comando_ejecutado(
    config_firebase,
    config_nodo,
    comando
):

    global ultimo_comando_ejecutado
    global confirmacion_pendiente


    comando_id = int(
        comando.get(
            "comando_id",
            0
        )
    )


    if comando_id == 0:

        return False


    # ========================================================
    # PRIMERO GUARDAR EN FLASH
    # ========================================================
    #
    # Desde este momento el comando NO volverá
    # a ejecutarse aunque Firebase falle.
    # ========================================================

    ultimo_comando_ejecutado = (
        comando_id
    )


    confirmacion_pendiente = {

        "comando_id":
            comando_id,

        "estado":
            comando.get(
                "estado",
                False
            ),

        "modo":
            comando.get(
                "modo",
                "manual"
            ),

        "duracion_min":
            comando.get(
                "duracion_min",
                0
            )

    }


    guardar_estado_local()


    print()

    print(
        "Comando marcado como ejecutado localmente."
    )


    # ========================================================
    # INTENTAR CONFIRMAR
    # ========================================================

    confirmado = confirmar_comando(
        config_firebase,
        config_nodo,
        confirmacion_pendiente
    )


    if confirmado:

        confirmacion_pendiente = None

        guardar_estado_local()


    else:

        print(
            "Confirmacion pendiente."
        )

        print(
            "NO se volvera a ejecutar el comando."
        )


    return True


# ============================================================
# REINTENTAR CONFIRMACION PENDIENTE
# ============================================================

def reintentar_confirmacion_pendiente(
    config_firebase,
    config_nodo
):

    global confirmacion_pendiente


    if confirmacion_pendiente is None:

        return True


    print()

    print(
        "Reintentando confirmacion pendiente..."
    )


    confirmado = confirmar_comando(
        config_firebase,
        config_nodo,
        confirmacion_pendiente
    )


    if confirmado:

        confirmacion_pendiente = None

        guardar_estado_local()

        print(
            "Confirmacion pendiente resuelta."
        )

        return True


    return False


# ============================================================
# REVISAR CONTROL
# ============================================================

def revisar_control(
    config_firebase,
    config_nodo
):

    inicializar_estado(
        config_firebase,
        config_nodo
    )


    # ========================================================
    # PRIMERO REINTENTAR CONFIRMACIONES
    # ========================================================

    reintentar_confirmacion_pendiente(
        config_firebase,
        config_nodo
    )


    # ========================================================
    # BUSCAR COMANDO NUEVO
    # ========================================================

    comando = consultar_comando(
        config_firebase,
        config_nodo
    )


    if comando is None:

        return None


    mostrar_comando(
        comando
    )


    return comando
