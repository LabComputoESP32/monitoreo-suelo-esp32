import os
import ujson


# ============================================================
# CONFIGURACION
# ============================================================

DIRECTORIO_PENDIENTES = "pendientes"

ARCHIVO_CONTADOR = "contador_local.json"


# ============================================================
# CREAR DIRECTORIO SI NO EXISTE
# ============================================================

def asegurar_directorio():

    try:

        os.mkdir(
            DIRECTORIO_PENDIENTES
        )

        print(
            "Directorio de pendientes creado"
        )

    except OSError:

        # Ya existe
        pass


# ============================================================
# GENERAR NOMBRE DEL ARCHIVO PENDIENTE
# ============================================================

def obtener_nombre_archivo(muestra):

    numero = int(
        muestra
    )

    nombre = "{:010d}.json".format(
        numero
    )

    return (
        DIRECTORIO_PENDIENTES
        + "/"
        + nombre
    )


# ============================================================
# GUARDAR MEDICION PENDIENTE
# ============================================================

def guardar_pendiente(registro):

    asegurar_directorio()


    if "muestra" not in registro:

        raise ValueError(
            "El registro no contiene 'muestra'"
        )


    archivo_final = (
        obtener_nombre_archivo(
            registro["muestra"]
        )
    )


    archivo_temporal = (
        archivo_final
        + ".tmp"
    )


    try:

        # Primero escribir temporal
        with open(
            archivo_temporal,
            "w"
        ) as archivo:

            ujson.dump(
                registro,
                archivo
            )


        # Eliminar anterior si existe
        try:

            os.remove(
                archivo_final
            )

        except OSError:

            pass


        # Convertir temporal en definitivo
        os.rename(
            archivo_temporal,
            archivo_final
        )


        print(
            "Pendiente guardado:",
            registro["muestra"]
        )


        # También actualizar contador local
        actualizar_contador_local(
            registro["muestra"]
        )


        return True


    except Exception as error:

        print(
            "ERROR guardando pendiente:",
            error
        )


        try:

            os.remove(
                archivo_temporal
            )

        except:

            pass


        return False


# ============================================================
# LISTAR PENDIENTES
# ============================================================

def listar_pendientes():

    asegurar_directorio()


    try:

        archivos = os.listdir(
            DIRECTORIO_PENDIENTES
        )


        archivos_json = []


        for nombre in archivos:

            if nombre.endswith(
                ".json"
            ):

                archivos_json.append(
                    nombre
                )


        archivos_json.sort()


        return archivos_json


    except Exception as error:

        print(
            "ERROR listando pendientes:",
            error
        )


        return []


# ============================================================
# LEER PENDIENTE
# ============================================================

def leer_pendiente(nombre_archivo):

    ruta = (
        DIRECTORIO_PENDIENTES
        + "/"
        + nombre_archivo
    )


    try:

        with open(
            ruta,
            "r"
        ) as archivo:

            datos = ujson.load(
                archivo
            )


        return datos


    except Exception as error:

        print(
            "ERROR leyendo pendiente:",
            error
        )


        return None


# ============================================================
# ELIMINAR PENDIENTE
# ============================================================

def eliminar_pendiente(nombre_archivo):

    ruta = (
        DIRECTORIO_PENDIENTES
        + "/"
        + nombre_archivo
    )


    try:

        os.remove(
            ruta
        )


        print(
            "Pendiente eliminado:",
            nombre_archivo
        )


        return True


    except Exception as error:

        print(
            "ERROR eliminando pendiente:",
            error
        )


        return False


# ============================================================
# CONTAR PENDIENTES
# ============================================================

def cantidad_pendientes():

    return len(
        listar_pendientes()
    )


# ============================================================
# MOSTRAR PENDIENTES
# ============================================================

def mostrar_pendientes():

    archivos = listar_pendientes()


    print()
    print("============================")
    print("DATOS PENDIENTES")
    print("============================")

    print(
        "Cantidad:",
        len(archivos)
    )


    for nombre in archivos:

        registro = leer_pendiente(
            nombre
        )


        print()

        print(
            "Archivo:",
            nombre
        )


        print(
            registro
        )


# ============================================================
# GUARDAR CONTADOR LOCAL
# ============================================================

def guardar_contador_local(
    ultima_muestra
):

    archivo_temporal = (
        ARCHIVO_CONTADOR
        + ".tmp"
    )


    datos = {

        "ultima_muestra":
            int(
                ultima_muestra
            )

    }


    try:

        # Primero escribir temporal
        with open(
            archivo_temporal,
            "w"
        ) as archivo:

            ujson.dump(
                datos,
                archivo
            )


        # Eliminar archivo anterior
        try:

            os.remove(
                ARCHIVO_CONTADOR
            )

        except OSError:

            pass


        # Renombrar
        os.rename(
            archivo_temporal,
            ARCHIVO_CONTADOR
        )


        print(
            "Contador local actualizado:",
            int(
                ultima_muestra
            )
        )


        return True


    except Exception as error:

        print(
            "ERROR guardando contador local:",
            error
        )


        try:

            os.remove(
                archivo_temporal
            )

        except:

            pass


        return False


# ============================================================
# LEER CONTADOR LOCAL
# ============================================================

def leer_contador_local():

    try:

        with open(
            ARCHIVO_CONTADOR,
            "r"
        ) as archivo:

            datos = ujson.load(
                archivo
            )


        if (
            "ultima_muestra"
            not in datos
        ):

            return None


        return int(
            datos[
                "ultima_muestra"
            ]
        )


    except OSError:

        # El archivo todavía no existe
        return None


    except Exception as error:

        print(
            "ERROR leyendo contador local:",
            error
        )


        return None


# ============================================================
# ACTUALIZAR CONTADOR SOLO SI LA MUESTRA ES MAYOR
# ============================================================

def actualizar_contador_local(
    muestra
):

    muestra = int(
        muestra
    )


    actual = leer_contador_local()


    if (
        actual is None
        or
        muestra > actual
    ):

        return guardar_contador_local(
            muestra
        )


    return True


# ============================================================
# OBTENER SIGUIENTE MUESTRA LOCAL
# ============================================================

def obtener_siguiente_muestra_local():

    ultima = leer_contador_local()


    if ultima is None:

        return 0


    return (
        ultima + 1
    )
