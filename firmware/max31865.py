
import time
import math


class MAX31865:

    CONFIG_REG = 0x00
    RTD_MSB_REG = 0x01
    FAULT_STATUS_REG = 0x07

    CONFIG_BIAS = 0x80
    CONFIG_1SHOT = 0x20
    CONFIG_3WIRE = 0x10
    CONFIG_CLEAR_FAULT = 0x02
    CONFIG_FILTER_50HZ = 0x01

    RTD_A = 3.9083e-3
    RTD_B = -5.775e-7


    def __init__(
        self,
        spi,
        cs,
        rtd_nominal=100.0,
        ref_resistor=430.0,
        wires=2
    ):

        self.spi = spi
        self.cs = cs

        self.cs.value(1)

        self.rtd_nominal = rtd_nominal
        self.ref_resistor = ref_resistor

        config = self._read_u8(
            self.CONFIG_REG
        )

        # PT100 de 2 o 4 hilos
        if wires == 3:
            config |= self.CONFIG_3WIRE
        else:
            config &= ~self.CONFIG_3WIRE

        # México usa red eléctrica de 60 Hz
        config &= ~self.CONFIG_FILTER_50HZ

        # Desactivar bias inicialmente
        config &= ~self.CONFIG_BIAS

        self._write_u8(
            self.CONFIG_REG,
            config
        )


    # ======================================
    # SPI
    # ======================================

    def _read_u8(self, address):

        self.cs.value(0)

        self.spi.write(
            bytes([address & 0x7F])
        )

        datos = self.spi.read(
            1,
            0xFF
        )

        self.cs.value(1)

        return datos[0]


    def _read_u16(self, address):

        self.cs.value(0)

        self.spi.write(
            bytes([address & 0x7F])
        )

        datos = self.spi.read(
            2,
            0xFF
        )

        self.cs.value(1)

        return (
            datos[0] << 8
        ) | datos[1]


    def _write_u8(
        self,
        address,
        value
    ):

        self.cs.value(0)

        self.spi.write(
            bytes([
                address | 0x80,
                value
            ])
        )

        self.cs.value(1)


    # ======================================
    # FAULT
    # ======================================

    def clear_faults(self):

        config = self._read_u8(
            self.CONFIG_REG
        )

        config &= ~0x2C

        config |= (
            self.CONFIG_CLEAR_FAULT
        )

        self._write_u8(
            self.CONFIG_REG,
            config
        )


    def fault_status(self):

        return self._read_u8(
            self.FAULT_STATUS_REG
        )


    # ======================================
    # LECTURA RTD
    # ======================================

    def read_rtd(self):

        self.clear_faults()

        # Encender bias
        config = self._read_u8(
            self.CONFIG_REG
        )

        config |= self.CONFIG_BIAS

        self._write_u8(
            self.CONFIG_REG,
            config
        )

        time.sleep_ms(10)

        # Conversión única
        config |= self.CONFIG_1SHOT

        self._write_u8(
            self.CONFIG_REG,
            config
        )

        # Conversión MAX31865
        time.sleep_ms(70)

        valor = self._read_u16(
            self.RTD_MSB_REG
        )

        # Apagar bias
        config = self._read_u8(
            self.CONFIG_REG
        )

        config &= ~self.CONFIG_BIAS

        self._write_u8(
            self.CONFIG_REG,
            config
        )

        # Bit 0 indica fault.
        fallo = valor & 0x01

        valor >>= 1

        if fallo:

            codigo = self.fault_status()

            raise OSError(
                "MAX31865 fault: 0x%02X"
                % codigo
            )

        return valor


    # ======================================
    # RESISTENCIA
    # ======================================

    def resistance(self):

        valor = self.read_rtd()

        resistencia = (
            valor / 32768.0
        )

        resistencia *= (
            self.ref_resistor
        )

        return resistencia


    # ======================================
    # TEMPERATURA
    # ======================================

    def temperature(self):

        resistencia = self.resistance()

        a = self.RTD_A
        b = self.RTD_B

        z1 = -a

        z2 = (
            a * a
            - 4 * b
        )

        z3 = (
            4 * b
        ) / self.rtd_nominal

        z4 = 2 * b

        temperatura = (
            z2
            + z3 * resistencia
        )

        temperatura = (
            math.sqrt(temperatura)
            + z1
        ) / z4


        if temperatura >= 0:

            return temperatura


        # Corrección para temperaturas negativas
        r = (
            resistencia
            / self.rtd_nominal
            * 100
        )

        temperatura = -242.02

        temperatura += (
            2.2228 * r
        )

        temperatura += (
            2.5859e-3
            * r**2
        )

        temperatura -= (
            4.8260e-6
            * r**3
        )

        temperatura -= (
            2.8183e-8
            * r**4
        )

        temperatura += (
            1.5243e-10
            * r**5
        )

        return temperatura
