import random
import time


# ==========================================
# LEER UNA MUESTRA DEL SENSOR
# ==========================================

def leer_sensor(config_sensor):

    tipo = config_sensor["tipo"]

    # Por ahora utilizamos datos simulados
    if tipo == "simulado":

        temperatura = random.randint(150, 350) / 10
        humedad = random.randint(300, 900) / 10

        return temperatura, humedad

    else:

        print("Tipo de sensor no reconocido")

        return None, None


# ==========================================
# OBTENER PROMEDIO DE VARIAS MUESTRAS
# ==========================================

def obtener_promedio(
    config_sensor,
    cantidad_muestras,
    intervalo_segundos
):

    suma_temperatura = 0
    suma_humedad = 0

    muestras_validas = 0

    print()
    print("============================")
    print("INICIANDO PERIODO DE MEDICION")
    print("============================")

    for numero in range(cantidad_muestras):

        temperatura, humedad = leer_sensor(
            config_sensor
        )

        # Comprobar que la lectura sea válida
        if temperatura is not None and humedad is not None:

            suma_temperatura += temperatura
            suma_humedad += humedad

            muestras_validas += 1

            print(
                "Lectura",
                numero + 1,
                "/",
                cantidad_muestras
            )

            print(
                "Temperatura:",
                temperatura,
                "C"
            )

            print(
                "Humedad:",
                humedad,
                "%"
            )

        else:

            print(
                "Lectura",
                numero + 1,
                "invalida"
            )

        # No esperamos después de la última lectura
        if numero < cantidad_muestras - 1:
            time.sleep(intervalo_segundos)


    # ======================================
    # VERIFICAR MUESTRAS
    # ======================================

    if muestras_validas == 0:

        print("No existen muestras validas")

        return None, None


    # ======================================
    # CALCULAR PROMEDIOS
    # ======================================

    promedio_temperatura = (
        suma_temperatura
        / muestras_validas
    )

    promedio_humedad = (
        suma_humedad
        / muestras_validas
    )


    # Redondear a 2 decimales

    promedio_temperatura = round(
        promedio_temperatura,
        2
    )

    promedio_humedad = round(
        promedio_humedad,
        2
    )


    return (
        promedio_temperatura,
        promedio_humedad
    )
