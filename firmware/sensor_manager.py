import random
import time
import dht

from machine import Pin, SoftSPI


# ==========================================
# VARIABLES DE HARDWARE
# ==========================================

max_sensor = None
dht_sensor = None
hardware_inicializado = False


# ==========================================
# INICIALIZAR SENSORES REALES
# ==========================================

def inicializar_sensores(config_sensor):

    global max_sensor
    global dht_sensor
    global hardware_inicializado

    # Importar el driver SOLO cuando
    # realmente se utilizará el MAX31865.
    #
    # Esto permite que los nodos simulados
    # sigan funcionando aunque todavía
    # no tengan max31865.py.
    from max31865 import MAX31865

    max_config = config_sensor["max31865"]

    # ======================================
    # SPI DEL MAX31865
    # ======================================

    spi = SoftSPI(
        baudrate=500000,
        polarity=0,
        phase=1,

        sck=Pin(max_config["sck"]),
        miso=Pin(max_config["miso"]),
        mosi=Pin(max_config["mosi"])
    )

    cs = Pin(
        max_config["cs"],
        Pin.OUT
    )

    max_sensor = MAX31865(
        spi,
        cs,
        rtd_nominal=max_config["rtd_nominal"],
        ref_resistor=max_config["ref_resistor"],
        wires=max_config["wires"]
    )

    # ======================================
    # DHT11
    # ======================================

    dht_sensor = dht.DHT11(
        Pin(config_sensor["dht_pin"])
    )

    hardware_inicializado = True

    print("Sensores reales inicializados")


# ==========================================
# LEER UNA MUESTRA
# ==========================================

def leer_sensor(config_sensor):

    global hardware_inicializado

    tipo = config_sensor["tipo"]


    # ======================================
    # MODO SIMULADO
    # ======================================

    if tipo == "simulado":

        temperatura = (
            random.randint(150, 350) / 10
        )

        humedad = (
            random.randint(300, 900) / 10
        )

        return temperatura, humedad


    # ======================================
    # MODO REAL
    # ======================================

    elif tipo == "real":

        if not hardware_inicializado:

            inicializar_sensores(
                config_sensor
            )


        temperatura = None
        humedad = None


        # ----------------------------------
        # TEMPERATURA MAX31865 + PT100
        # ----------------------------------

        try:

            temperatura = round(
                max_sensor.temperature(),
                2
            )

        except Exception as error:

            print(
                "ERROR MAX31865:",
                error
            )


        # ----------------------------------
        # HUMEDAD DHT11
        # ----------------------------------

        try:

            dht_sensor.measure()

            humedad = (
                dht_sensor.humidity()
            )

        except Exception as error:

            print(
                "ERROR DHT11:",
                error
            )


        return temperatura, humedad


    else:

        print(
            "Tipo de sensor no reconocido:",
            tipo
        )

        return None, None


# ==========================================
# OBTENER PROMEDIO
# ==========================================

def obtener_promedio(
    config_sensor,
    cantidad_muestras,
    intervalo_segundos
):

    temperaturas = []
    humedades = []


    print()
    print("============================")
    print("INICIANDO PERIODO DE MEDICION")
    print("============================")


    for numero in range(cantidad_muestras):

        temperatura, humedad = leer_sensor(
            config_sensor
        )


        print()
        print(
            "Lectura",
            numero + 1,
            "/",
            cantidad_muestras
        )


        # ==================================
        # TEMPERATURA
        # ==================================

        if temperatura is not None:

            temperaturas.append(
                temperatura
            )

            print(
                "Temperatura:",
                temperatura,
                "C"
            )

        else:

            print(
                "Temperatura: lectura invalida"
            )


        # ==================================
        # HUMEDAD
        # ==================================

        if humedad is not None:

            humedades.append(
                humedad
            )

            print(
                "Humedad:",
                humedad,
                "%"
            )

        else:

            print(
                "Humedad: lectura invalida"
            )


        # No esperar después de la última
        if numero < cantidad_muestras - 1:

            time.sleep(
                intervalo_segundos
            )


    # ======================================
    # PROMEDIO TEMPERATURA
    # ======================================

    if len(temperaturas) > 0:

        temperatura_promedio = (
            sum(temperaturas)
            / len(temperaturas)
        )

        temperatura_promedio = round(
            temperatura_promedio,
            2
        )

    else:

        temperatura_promedio = None


    # ======================================
    # PROMEDIO HUMEDAD
    # ======================================

    if len(humedades) > 0:

        humedad_promedio = (
            sum(humedades)
            / len(humedades)
        )

        humedad_promedio = round(
            humedad_promedio,
            2
        )

    else:

        humedad_promedio = None


    # ======================================
    # INFORMACION
    # ======================================

    print()

    print(
        "Lecturas temperatura validas:",
        len(temperaturas),
        "/",
        cantidad_muestras
    )

    print(
        "Lecturas humedad validas:",
        len(humedades),
        "/",
        cantidad_muestras
    )


    return (
        temperatura_promedio,
        humedad_promedio
    )
