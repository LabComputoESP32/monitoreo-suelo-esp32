import random


def leer_sensor(config_sensor):

    tipo = config_sensor["tipo"]

    # Por ahora usamos datos simulados
    if tipo == "simulado":

        # Temperatura simulada entre 15.0 y 35.0 °C
        temperatura = random.randint(150, 350) / 10

        # Humedad simulada entre 30.0 y 90.0 %
        humedad = random.randint(300, 900) / 10

        return temperatura, humedad

    else:

        print("Tipo de sensor no reconocido")

        return None, None
