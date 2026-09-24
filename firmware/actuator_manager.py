import time


# ============================================================
# ESTADO DEL ACTUADOR LOGICO
# ============================================================

estado_actuador = False

modo_actual = "manual"

temporizador_activo = False

inicio_temporizador = None

duracion_temporizador_ms = 0


# ============================================================
# MOSTRAR ESTADO
# ============================================================

def mostrar_estado():

    print()

    print(
        "================================"
    )

    print(
        "ACTUADOR LOGICO"
    )

    print(
        "================================"
    )

    if estado_actuador:

        print(
            "Estado: ON"
        )

    else:

        print(
            "Estado: OFF"
        )

    print(
        "Modo:",
        modo_actual
    )

    print(
        "================================"
    )


# ============================================================
# APLICAR COMANDO
# ============================================================

def aplicar_comando(
    comando
):

    global estado_actuador
    global modo_actual
    global temporizador_activo
    global inicio_temporizador
    global duracion_temporizador_ms


    if comando is None:

        return False


    estado = comando.get(
        "estado",
        False
    )


    modo = comando.get(
        "modo",
        "manual"
    )


    duracion = int(
        comando.get(
            "duracion_min",
            0
        )
    )


    # ========================================================
    # MODO MANUAL
    # ========================================================

    if modo == "manual":

        # Cualquier orden manual cancela
        # un temporizador anterior.

        temporizador_activo = False

        inicio_temporizador = None

        duracion_temporizador_ms = 0

        modo_actual = "manual"

        estado_actuador = bool(
            estado
        )


        print()

        print(
            "================================"
        )

        print(
            "COMANDO APLICADO AL ACTUADOR"
        )

        print(
            "================================"
        )


        if estado_actuador:

            print(
                "ACTUADOR LOGICO -> ON"
            )

        else:

            print(
                "ACTUADOR LOGICO -> OFF"
            )


        print(
            "Modo: manual"
        )

        print(
            "================================"
        )


        return True


    # ========================================================
    # MODO TEMPORIZADOR
    # ========================================================

    elif modo == "temporizador":

        # Si por alguna razon recibimos
        # temporizador con estado OFF,
        # apagamos directamente.

        if not estado:

            temporizador_activo = False

            inicio_temporizador = None

            duracion_temporizador_ms = 0

            estado_actuador = False

            modo_actual = "manual"


            print()

            print(
                "ACTUADOR LOGICO -> OFF"
            )

            return True


        # Validar duracion

        if duracion <= 0:

            print(
                "Duracion de temporizador invalida"
            )

            return False


        # Encender actuador

        estado_actuador = True

        modo_actual = "temporizador"

        temporizador_activo = True


        # Tiempo de inicio usando reloj interno
        # monotono del ESP32.

        inicio_temporizador = (
            time.ticks_ms()
        )


        duracion_temporizador_ms = (
            duracion
            * 60
            * 1000
        )


        print()

        print(
            "================================"
        )

        print(
            "TEMPORIZADOR INICIADO"
        )

        print(
            "================================"
        )

        print(
            "ACTUADOR LOGICO -> ON"
        )

        print(
            "Duracion:",
            duracion,
            "minutos"
        )

        print(
            "El monitoreo continuara normalmente."
        )

        print(
            "================================"
        )


        return True


    # ========================================================
    # MODO DESCONOCIDO
    # ========================================================

    else:

        print(
            "Modo de control desconocido:",
            modo
        )

        return False


# ============================================================
# ACTUALIZAR TEMPORIZADOR
# ============================================================

def actualizar_actuador():

    global estado_actuador
    global modo_actual
    global temporizador_activo
    global inicio_temporizador
    global duracion_temporizador_ms


    # No hay temporizador activo

    if not temporizador_activo:

        return False


    if inicio_temporizador is None:

        return False


    tiempo_transcurrido = (
        time.ticks_diff(
            time.ticks_ms(),
            inicio_temporizador
        )
    )


    # ========================================================
    # TEMPORIZADOR AUN ACTIVO
    # ========================================================

    if (
        tiempo_transcurrido
        <
        duracion_temporizador_ms
    ):

        return False


    # ========================================================
    # TEMPORIZADOR FINALIZADO
    # ========================================================

    estado_actuador = False

    temporizador_activo = False

    inicio_temporizador = None

    duracion_temporizador_ms = 0

    modo_actual = "manual"


    print()

    print(
        "================================"
    )

    print(
        "TEMPORIZADOR FINALIZADO"
    )

    print(
        "================================"
    )

    print(
        "ACTUADOR LOGICO -> OFF"
    )

    print(
        "================================"
    )


    return True


# ============================================================
# OBTENER ESTADO
# ============================================================

def obtener_estado():

    return {

        "estado":
            estado_actuador,

        "modo":
            modo_actual,

        "temporizador_activo":
            temporizador_activo

    }
