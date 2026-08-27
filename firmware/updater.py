import urequests
import ujson
import os
import time
import machine
import gc


# ==========================================
# ARCHIVOS QUE SE ACTUALIZARAN
# ==========================================

ARCHIVOS_FIRMWARE = [
    "main.py",
    "wifi_manager.py",
    "sensor_manager.py",
    "firebase_manager.py"
]


# ==========================================
# VERSION LOCAL
# ==========================================

def leer_version_local():

    try:

        with open("version.json", "r") as archivo:
            datos = ujson.load(archivo)

        return datos["version"]

    except Exception as error:

        print("Error leyendo version local:")
        print(error)

        return None


# ==========================================
# VERSION GITHUB
# ==========================================

def leer_version_github(config_github):

    try:

        url = config_github["version_url"]

        # Evitar recibir una version vieja por cache
        url = url + "?nocache=" + str(time.ticks_ms())

        respuesta = urequests.get(url)

        print("GitHub HTTP:", respuesta.status_code)

        if respuesta.status_code == 200:

            datos = respuesta.json()

            respuesta.close()

            return datos["version"]

        respuesta.close()

        return None

    except Exception as error:

        print("Error consultando GitHub:")
        print(error)

        return None


# ==========================================
# CONVERTIR VERSION
# ==========================================

def convertir_version(version):

    partes = version.split(".")

    return tuple(
        int(parte)
        for parte in partes
    )


# ==========================================
# DESCARGAR ARCHIVO
# ==========================================

def descargar_archivo(config_github, nombre_archivo):

    base_url = config_github["firmware_base_url"]

    url = (
        base_url
        + nombre_archivo
        + "?nocache="
        + str(time.ticks_ms())
    )

    archivo_temporal = nombre_archivo + ".new"

    print()
    print("Descargando:", nombre_archivo)

    try:

        respuesta = urequests.get(url)

        print("HTTP:", respuesta.status_code)

        if respuesta.status_code != 200:

            respuesta.close()

            print("No se pudo descargar:", nombre_archivo)

            return False

        contenido = respuesta.content

        respuesta.close()

        # Guardar primero como archivo temporal
        with open(archivo_temporal, "wb") as archivo:
            archivo.write(contenido)

        print("Descarga correcta:", nombre_archivo)

        # Liberar memoria
        del contenido
        gc.collect()

        return True

    except Exception as error:

        print("Error descargando:", nombre_archivo)
        print(error)

        return False


# ==========================================
# ELIMINAR ARCHIVOS TEMPORALES
# ==========================================

def limpiar_temporales():

    for nombre in ARCHIVOS_FIRMWARE:

        temporal = nombre + ".new"

        try:
            os.remove(temporal)
        except:
            pass


# ==========================================
# REEMPLAZAR ARCHIVOS
# ==========================================

def instalar_archivos():

    print()
    print("============================")
    print("INSTALANDO ACTUALIZACION")
    print("============================")

    for nombre in ARCHIVOS_FIRMWARE:

        temporal = nombre + ".new"

        respaldo = nombre + ".bak"

        print("Actualizando:", nombre)

        # Eliminar respaldo viejo
        try:
            os.remove(respaldo)
        except:
            pass

        # Crear respaldo del archivo actual
        try:
            os.rename(nombre, respaldo)

        except Exception as error:

            print("No se pudo respaldar:", nombre)
            print(error)

            return False

        # Convertir archivo temporal en archivo real
        try:

            os.rename(
                temporal,
                nombre
            )

        except Exception as error:

            print("Error instalando:", nombre)
            print(error)

            # Restaurar archivo anterior
            try:
                os.rename(
                    respaldo,
                    nombre
                )
            except:
                pass

            return False

    return True


# ==========================================
# GUARDAR NUEVA VERSION
# ==========================================

def guardar_version(version):

    datos = {
        "version": version
    }

    with open("version.json", "w") as archivo:
        ujson.dump(datos, archivo)


# ==========================================
# VERIFICAR Y ACTUALIZAR
# ==========================================

def verificar_y_actualizar(config_github):

    print()
    print("============================")
    print("VERIFICANDO ACTUALIZACIONES")
    print("============================")

    version_local = leer_version_local()

    version_remota = leer_version_github(
        config_github
    )

    print("Version local:", version_local)
    print("Version GitHub:", version_remota)

    if version_local is None:
        print("No se pudo leer version local")
        return False

    if version_remota is None:
        print("No se pudo leer version GitHub")
        return False


    local = convertir_version(
        version_local
    )

    remota = convertir_version(
        version_remota
    )


    # ======================================
    # NO HAY ACTUALIZACION
    # ======================================

    if remota <= local:

        print()
        print("Firmware actualizado")

        return False


    # ======================================
    # HAY ACTUALIZACION
    # ======================================

    print()
    print("NUEVA VERSION DISPONIBLE")
    print(
        version_local,
        "->",
        version_remota
    )

    print()
    print("Descargando firmware...")


    # ======================================
    # DESCARGAR TODOS LOS ARCHIVOS
    # ======================================

    for nombre in ARCHIVOS_FIRMWARE:

        resultado = descargar_archivo(
            config_github,
            nombre
        )

        if not resultado:

            print()
            print("ACTUALIZACION CANCELADA")

            limpiar_temporales()

            return False


    # ======================================
    # INSTALAR
    # ======================================

    resultado = instalar_archivos()

    if not resultado:

        print()
        print("ERROR INSTALANDO ACTUALIZACION")

        return False


    # ======================================
    # ACTUALIZAR VERSION LOCAL
    # ======================================

    guardar_version(
        version_remota
    )


    print()
    print("============================")
    print("ACTUALIZACION COMPLETADA")
    print("============================")
    print(
        "Nueva version:",
        version_remota
    )

    print("Reiniciando ESP32...")

    time.sleep(3)

    machine.reset()
