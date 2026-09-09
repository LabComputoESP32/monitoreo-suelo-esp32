import random
import time
import dht

from machine import Pin, SoftSPI


# ==========================================
# VARIABLES DE HARDWARE REAL
# ==========================================

max_sensor = None
dht_sensor = None
hardware_inicializado = False


# ==========================================
# ESTADO DE LA SIMULACION
# ==========================================
#
# Cada ESP32 ejecuta su propio sensor_manager,
# por lo tanto cada nodo mantiene su propio
# estado independiente.
# ==========================================

estado_simulado = {
    "temperatura": None,
    "humedad": None
}


# ==========================================
# INICIALIZAR SENSORES REALES
# ==========================================

def inicializar_sensores(config_sensor):

    global max_sensor
    global dht_sensor
    global hardware_inicializado


    # El driver solamente se importa
    # cuando el nodo es REAL.
    from max31865 import MAX31865


    max_config = config_sensor[
        "max31865"
    ]


    # ======================================
    # SPI DEL MAX31865
    # ======================================

    spi = SoftSPI(
        baudrate=500000,
        polarity=0,
        phase=1,

        sck=Pin(
            max_config["sck"]
        ),

        miso=Pin(
            max_config["miso"]
        ),

        mosi=Pin(
            max_config["mosi"]
        )
    )


    cs = Pin(
        max_config["cs"],
        Pin.OUT
    )


    max_sensor = MAX31865(
        spi,
        cs,
        rtd_nominal=max_config[
            "rtd_nominal"
        ],
        ref_resistor=max_config[
            "ref_resistor"
        ],
        wires=max_config[
            "wires"
        ]
    )


    # ======================================
    # DHT11
    # ======================================

    dht_sensor = dht.DHT11(
        Pin(
            config_sensor[
                "dht_pin"
            ]
        )
    )


    hardware_inicializado = True


    print(
        "Sensores reales inicializados"
    )


# ==========================================
# LIMITAR VALOR
# ==========================================

def limitar(
    valor,
    minimo,
    maximo
):

    if valor < minimo:
        return minimo

    if valor > maximo:
        return maximo

    return valor


# ==========================================
# LEER SENSOR SIMULADO
# ==========================================

def leer_sensor_simulado(
    config_sensor
):

    global estado_simulado


    # ======================================
    # LEER CONFIGURACION DE SIMULACION
    # ======================================
    #
    # Si config.json tiene la seccion
    # "simulacion", utilizamos esos valores.
    #
    # Si no existe, utilizamos valores
    # predeterminados seguros.
    # ======================================

    simulacion = config_sensor.get(
        "simulacion",
        {}
    )


    temperatura_inicial = float(
        simulacion.get(
            "temperatura_inicial",
            26.0
        )
    )


    humedad_inicial = float(
        simulacion.get(
            "humedad_inicial",
            55.0
        )
    )


    temperatura_min = float(
        simulacion.get(
            "temperatura_min",
            22.0
        )
    )


    temperatura_max = float(
        simulacion.get(
            "temperatura_max",
            30.0
        )
    )


    humedad_min = float(
        simulacion.get(
            "humedad_min",
            45.0
        )
    )


    humedad_max = float(
        simulacion.get(
            "humedad_max",
            70.0
        )
    )


    variacion_temperatura = float(
        simulacion.get(
            "variacion_temperatura",
            0.15
        )
    )


    variacion_humedad = float(
        simulacion.get(
            "variacion_humedad",
            0.30
        )
    )


    # ======================================
    # PRIMERA LECTURA
    # ======================================

    if (
        estado_simulado["temperatura"]
        is None
    ):

        estado_simulado[
            "temperatura"
        ] = temperatura_inicial


        estado_simulado[
            "humedad"
        ] = humedad_inicial


    # ======================================
    # VARIACION ALEATORIA PEQUEÑA
    # ======================================

    cambio_temperatura = (
        random.randint(
            -100,
            100
        )
        / 100.0
        * variacion_temperatura
    )


    cambio_humedad = (
        random.randint(
            -100,
            100
        )
        / 100.0
        * variacion_humedad
    )


    # ======================================
    # TENDENCIA HACIA EL VALOR BASE
    # ======================================
    #
    # Evita que con el paso de las horas
    # el valor termine permanentemente
    # pegado al limite minimo o maximo.
    # ======================================

    correccion_temperatura = (
        temperatura_inicial
        - estado_simulado[
            "temperatura"
        ]
    ) * 0.02


    correccion_humedad = (
        humedad_inicial
        - estado_simulado[
            "humedad"
        ]
    ) * 0.02


    # ======================================
    # CALCULAR NUEVA TEMPERATURA
    # ======================================

    nueva_temperatura = (

        estado_simulado[
            "temperatura"
        ]

        + cambio_temperatura

        + correccion_temperatura
    )


    # ======================================
    # CALCULAR NUEVA HUMEDAD
    # ======================================

    nueva_humedad = (

        estado_simulado[
            "humedad"
        ]

        + cambio_humedad

        + correccion_humedad
    )


    # ======================================
    # RELACION SUAVE TEMPERATURA / HUMEDAD
    # ======================================
    #
    # Si la temperatura sube ligeramente,
    # la humedad tiende a bajar un poco.
    #
    # Es solamente una simulacion visual,
    # no un modelo fisico completo.
    # ======================================

    nueva_humedad -= (
        cambio_temperatura
        * 0.4
    )


    # ======================================
    # LIMITES
    # ======================================

    nueva_temperatura = limitar(
        nueva_temperatura,
        temperatura_min,
        temperatura_max
    )


    nueva_humedad = limitar(
        nueva_humedad,
        humedad_min,
        humedad_max
    )


    # ======================================
    # GUARDAR ESTADO
    # ======================================

    estado_simulado[
        "temperatura"
    ] = nueva_temperatura


    estado_simulado[
        "humedad"
    ] = nueva_humedad


    # ======================================
    # RETORNAR
    # ======================================

    return (
        round(
            nueva_temperatura,
            2
        ),

        round(
            nueva_humedad,
            2
        )
    )


# ==========================================
# LEER UNA MUESTRA
# ==========================================

def leer_sensor(
    config_sensor
):

    global hardware_inicializado


    tipo = config_sensor[
        "tipo"
    ]


    # ======================================
    # MODO SIMULADO
    #
    # SOLO Nodo 02 y Nodo 04
    # ======================================

    if tipo == "simulado":

        return leer_sensor_simulado(
            config_sensor
        )


    # ======================================
    # MODO REAL
    #
    # Nodo 01 y Nodo 03
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


        return (
            temperatura,
            humedad
        )


    # ======================================
    # TIPO DESCONOCIDO
    # ======================================

    else:

        print(
            "Tipo de sensor no reconocido:",
            tipo
        )


        return (
            None,
            None
        )


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

    print(
        "============================"
    )

    print(
        "INICIANDO PERIODO DE MEDICION"
    )

    print(
        "============================"
    )


    # ======================================
    # TOMAR MUESTRAS
    # ======================================

    for numero in range(
        cantidad_muestras
    ):

        temperatura, humedad = (
            leer_sensor(
                config_sensor
            )
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


        # ==================================
        # ESPERAR ENTRE LECTURAS
        # ==================================

        if (
            numero
            <
            cantidad_muestras - 1
        ):

            time.sleep(
                intervalo_segundos
            )


    # ======================================
    # PROMEDIO TEMPERATURA
    # ======================================

    if len(
        temperaturas
    ) > 0:

        temperatura_promedio = (

            sum(
                temperaturas
            )

            /
            len(
                temperaturas
            )
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

    if len(
        humedades
    ) > 0:

        humedad_promedio = (

            sum(
                humedades
            )

            /
            len(
                humedades
            )
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
        len(
            temperaturas
        ),
        "/",
        cantidad_muestras
    )


    print(
        "Lecturas humedad validas:",
        len(
            humedades
        ),
        "/",
        cantidad_muestras
    )


    return (
        temperatura_promedio,
        humedad_promedio
    )
