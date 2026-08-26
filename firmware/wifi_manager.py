import network
import time


def conectar_wifi(config_wifi):

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Esta configuración es la que funcionó
    # correctamente en el ESP32-C3
    wlan.config(txpower=14)

    # Datos obtenidos desde config.json
    WIFI_SSID = config_wifi["ssid"]
    WIFI_PASSWORD = config_wifi["password"]

    print("Connectign to WiFi...")

    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    # Wait for connection
    timeout = 10

    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if wlan.isconnected():
        print("Success! IP:", wlan.ifconfig()[0])

    else:
        print("Connection failed. Status:", wlan.status())

    return wlan
