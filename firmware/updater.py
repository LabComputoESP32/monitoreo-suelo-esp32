import urequests
import ujson
import os
import time
import machine
import gc


# ============================================================
# ARCHIVOS QUE SE ACTUALIZARAN
# ============================================================
#
# updater.py queda al final para que el actualizador
# se reemplace a si mismo solamente después de haber
# instalado los demás archivos.
# ============================================================

ARCHIVOS_FIRMWARE = [

    "main.py",

    "wifi_manager.py",

    "sensor_manager.py",

    "firebase_manager.py",

    "offline_manager.py",

    "time_manager.py",

    "max31865.py",

    "updater.py"
]


# ============================================================
# COMPROBAR SI UN ARCHIVO EXISTE
# ============================================================

def archivo_existe(nombre):

    try:

        os.stat(nombre)

        return True

    except:

        return False


# ============================================================
# CERRAR RESPUESTA HTTP
# ============================================================

def cerrar_respuesta(respuesta):

    if respuesta is not None:

        try:

            respuesta.close()

        except:

            pass


# ============================================================
# VERSION LOCAL
# ============================================================

def leer_version_local():

    try:

        with open(
            "version.json",
            "r"
        ) as archivo:

            datos = ujson.load(
                archivo
            )


        return datos[
            "version"
        ]


    except Exception as error:

        print(
            "Error leyendo version local:"
        )

        print(
            error
        )


        return None


# ============================================================
# VERSION GITHUB
# ============================================================

def leer_version_github(
    config_github
):

    respuesta = None


    try:

        url = (
            config_github[
                "version_url"
            ]
        )


        # Evitar cache
        url = (
            url
            + "?nocache="
            + str(
                time.ticks_ms()
            )
        )


        respuesta = urequests.get(
            url,
            timeout=10
        )


        print(
            "GitHub HTTP:",
            respuesta.status_code
        )


        if (
            respuesta.status_code
            != 200
        ):

            return None


        datos = respuesta.json()


        return datos[
            "version"
        ]


    except Exception as error:

        print(
            "Error consultando GitHub:"
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
# CONVERTIR VERSION
# ============================================================

def convertir_version(
    version
):

    try:

        partes = version.split(".")


        return tuple(
            int(parte)
            for parte in partes
        )


    except:

        return (
            0,
            0,
            0
        )


# ============================================================
# DESCARGAR ARCHIVO
# ============================================================

def descargar_archivo(
    config_github,
    nombre_archivo
):

    base_url = (
        config_github[
            "firmware_base_url"
        ]
    )


    url = (
        base_url
        + nombre_archivo
        + "?nocache="
        + str(
            time.ticks_ms()
        )
    )


    archivo_temporal = (
        nombre_archivo
        + ".new"
    )


    respuesta = None


    print()

    print(
        "Descargando:",
        nombre_archivo
    )


    try:

        respuesta = urequests.get(
            url,
            timeout=15
        )


        print(
            "HTTP:",
            respuesta.status_code
        )


        if (
            respuesta.status_code
            != 200
        ):

            print(
                "No se pudo descargar:",
                nombre_archivo
            )

            return False


        contenido = (
            respuesta.content
        )


        # ----------------------------------------------------
        # Cerrar HTTP antes de escribir
        # ----------------------------------------------------

        cerrar_respuesta(
            respuesta
        )

        respuesta = None


        # ----------------------------------------------------
        # Guardar como .new
        # ----------------------------------------------------

        with open(
            archivo_temporal,
            "wb"
        ) as archivo:

            archivo.write(
                contenido
            )


        print(
            "Descarga correcta:",
            nombre_archivo
        )


        # Liberar RAM

        del contenido

        gc.collect()


        return True


    except Exception as error:

        print(
            "Error descargando:",
            nombre_archivo
        )

        print(
            error
        )


        return False


    finally:

        cerrar_respuesta(
            respuesta
        )


# ============================================================
# ELIMINAR ARCHIVOS TEMPORALES
# ============================================================

def limpiar_temporales():

    for nombre in ARCHIVOS_FIRMWARE:

        temporal = (
            nombre
            + ".new"
        )


        try:

            os.remove(
                temporal
            )

        except:

            pass


# ============================================================
# INSTALAR UN ARCHIVO
# ============================================================

def instalar_archivo(
    nombre
):

    temporal = (
        nombre
        + ".new"
    )


    respaldo = (
        nombre
        + ".bak"
    )


    print(
        "Actualizando:",
        nombre
    )


    # ========================================================
    # COMPROBAR QUE EL .NEW EXISTA
    # ========================================================

    if not archivo_existe(
        temporal
    ):

        print(
            "ERROR:"
        )

        print(
            "No existe archivo temporal:",
            temporal
        )

        return False


    # ========================================================
    # BORRAR RESPALDO ANTERIOR
    # ========================================================

    try:

        os.remove(
            respaldo
        )

    except:

        pass


    archivo_original_existia = (
        archivo_existe(
            nombre
        )
    )


    # ========================================================
    # SI EL ARCHIVO YA EXISTE, HACER BACKUP
    # ========================================================

    if archivo_original_existia:

        try:

            os.rename(
                nombre,
                respaldo
            )


            print(
                "Respaldo creado:",
                respaldo
            )


        except Exception as error:

            print(
                "No se pudo respaldar:",
                nombre
            )

            print(
                error
            )


            return False


    else:

        print(
            "Archivo nuevo:",
            nombre
        )


    # ========================================================
    # INSTALAR NUEVO ARCHIVO
    # ========================================================

    try:

        os.rename(
            temporal,
            nombre
        )


        print(
            "Instalado correctamente:",
            nombre
        )


        return True


    except Exception as error:

        print(
            "ERROR instalando:",
            nombre
        )

        print(
            error
        )


        # ----------------------------------------------------
        # SI HABIA ARCHIVO ANTERIOR, RESTAURAR
        # ----------------------------------------------------

        if archivo_original_existia:

            try:

                os.rename(
                    respaldo,
                    nombre
                )


                print(
                    "Archivo anterior restaurado"
                )


            except Exception as error_restore:

                print(
                    "ERROR restaurando backup:"
                )

                print(
                    error_restore
                )


        return False


# ============================================================
# RESTAURAR ARCHIVOS YA INSTALADOS
# ============================================================

def restaurar_instalados(
    instalados
):

    print()

    print(
        "Restaurando archivos anteriores..."
    )


    # Recorrer al reves

    for nombre in reversed(
        instalados
    ):

        respaldo = (
            nombre
            + ".bak"
        )


        # ----------------------------------------------------
        # Si existe respaldo, restaurarlo
        # ----------------------------------------------------

        if archivo_existe(
            respaldo
        ):

            try:

                if archivo_existe(
                    nombre
                ):

                    os.remove(
                        nombre
                    )


                os.rename(
                    respaldo,
                    nombre
                )


                print(
                    "Restaurado:",
                    nombre
                )


            except Exception as error:

                print(
                    "ERROR restaurando:",
                    nombre
                )

                print(
                    error
                )


        # ----------------------------------------------------
        # Si no habia backup significa que era archivo nuevo
        # ----------------------------------------------------

        else:

            try:

                if archivo_existe(
                    nombre
                ):

                    os.remove(
                        nombre
                    )


                print(
                    "Archivo nuevo eliminado:",
                    nombre
                )


            except:

                pass


# ============================================================
# INSTALAR TODOS LOS ARCHIVOS
# ============================================================

def instalar_archivos():

    print()

    print(
        "============================"
    )

    print(
        "INSTALANDO ACTUALIZACION"
    )

    print(
        "============================"
    )


    instalados = []


    for nombre in ARCHIVOS_FIRMWARE:

        resultado = instalar_archivo(
            nombre
        )


        if not resultado:

            print()

            print(
                "ERROR DURANTE INSTALACION"
            )


            restaurar_instalados(
                instalados
            )


            return False


        instalados.append(
            nombre
        )


    return True


# ============================================================
# GUARDAR NUEVA VERSION
# ============================================================

def guardar_version(
    version
):

    datos = {

        "version":
            version

    }


    archivo_temporal = (
        "version.json.new"
    )


    try:

        with open(
            archivo_temporal,
            "w"
        ) as archivo:

            ujson.dump(
                datos,
                archivo
            )


        try:

            os.remove(
                "version.json"
            )

        except:

            pass


        os.rename(
            archivo_temporal,
            "version.json"
        )


        return True


    except Exception as error:

        print(
            "ERROR guardando version:"
        )

        print(
            error
        )


        return False


# ============================================================
# VERIFICAR Y ACTUALIZAR
# ============================================================

def verificar_y_actualizar(
    config_github
):

    print()

    print(
        "============================"
    )

    print(
        "VERIFICANDO ACTUALIZACIONES"
    )

    print(
        "============================"
    )


    version_local = (
        leer_version_local()
    )


    version_remota = (
        leer_version_github(
            config_github
        )
    )


    print(
        "Version local:",
        version_local
    )


    print(
        "Version GitHub:",
        version_remota
    )


    # ========================================================
    # VALIDAR VERSIONES
    # ========================================================

    if version_local is None:

        print(
            "No se pudo leer version local"
        )

        return False


    if version_remota is None:

        print(
            "No se pudo leer version GitHub"
        )

        return False


    local = convertir_version(
        version_local
    )


    remota = convertir_version(
        version_remota
    )


    # ========================================================
    # NO HAY ACTUALIZACION
    # ========================================================

    if remota <= local:

        print()

        print(
            "Firmware actualizado"
        )


        return False


    # ========================================================
    # NUEVA VERSION
    # ========================================================

    print()

    print(
        "NUEVA VERSION DISPONIBLE"
    )


    print(
        version_local,
        "->",
        version_remota
    )


    print()

    print(
        "Descargando firmware..."
    )


    # ========================================================
    # DESCARGAR TODOS LOS ARCHIVOS PRIMERO
    # ========================================================
    #
    # No se modifica ningun archivo hasta que TODOS
    # hayan sido descargados correctamente.
    # ========================================================

    for nombre in ARCHIVOS_FIRMWARE:

        resultado = descargar_archivo(

            config_github,

            nombre
        )


        if not resultado:

            print()

            print(
                "ACTUALIZACION CANCELADA"
            )


            limpiar_temporales()


            return False


    # ========================================================
    # INSTALAR
    # ========================================================

    resultado = instalar_archivos()


    if not resultado:

        print()

        print(
            "ERROR INSTALANDO ACTUALIZACION"
        )


        limpiar_temporales()


        return False


    # ========================================================
    # GUARDAR VERSION
    # ========================================================

    resultado_version = guardar_version(
        version_remota
    )


    if not resultado_version:

        print()

        print(
            "ADVERTENCIA:"
        )

        print(
            "Firmware instalado,"
        )

        print(
            "pero no se pudo guardar version."
        )


        return False


    # ========================================================
    # ACTUALIZACION COMPLETA
    # ========================================================

    print()

    print(
        "============================"
    )

    print(
        "ACTUALIZACION COMPLETADA"
    )

    print(
        "============================"
    )


    print(
        "Nueva version:",
        version_remota
    )


    print(
        "Reiniciando ESP32..."
    )


    time.sleep(
        3
    )


    machine.reset()
