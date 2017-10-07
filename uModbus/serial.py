from uModBus.functions import Functions
from machine import UART
import uModBus.const as Const
import struct
import time

class Serial:

    _uart = None
    _slave_addr = None

    def __init__(self, uart_id, baudrate=9600, data_bits=8, stop_bits=1, parity=None, pins=None):
        self._uart = UART(uart_id, baudrate = baudrate, bits = data_bits, parity = parity, \
                          stop = stop_bits, pins = pins)

    def _calculate_crc16(self, data):
        crc = 0xFFFF

        for char in data:
            crc = (crc >> 8) ^ Const.CRC16_TABLE[((crc) ^ char) & 0xFF]

        return struct.pack('<H',crc)

    def _uart_read(self):
        response = None

        for x in range(1, 10):
            if self._uart.any():
                response = self._uart.readall()
                break
            time.sleep(0.1)

        return response

    def _validate_resp_hdr(self, response, slave_addr, function_code, has_count=False):

        response_crc = response[-Const.CRC_LENGTH:]
        expected_crc = self._calculate_crc16(response[0:len(response) - Const.CRC_LENGTH])
        if (response_crc != expected_crc):
            raise OSError('Invalid response CRC')

        if (response[0] != slave_addr):
            raise ValueError('Wrong slave address')

        if (response[1] == (function_code + Const.ERROR_BIAS)):
            raise ValueError('Slave returned exception code: {:d}'.format(response[2]))

        header_length = Const.RESPONSE_HDR_LENGTH + 1 if has_count else Const.RESPONSE_HDR_LENGTH

        return response[header_length : len(response) - Const.CRC_LENGTH]

    def _validate_resp_data(self, data, function_code, address, value=None, quantity=None, signed = True):
        if function_code in [Const.WRITE_SINGLE_COIL, Const.WRITE_SINGLE_REGISTER]:
           fmt = '>H' + ('h' if signed else 'H')
           resp_addr, resp_value = struct.unpack(fmt, data)

           if (address == resp_addr) and (value == resp_value):
               return True

        elif function_code in [Const.WRITE_MULTIPLE_COILS, Const.WRITE_MULTIPLE_REGISTERS]:
            resp_addr, resp_qty = struct.unpack('>HH', data)

            if (address == resp_addr) and (quantity == resp_qty):
                return True

        return False

    def _to_short(self, byte_array, signed = True):
        response_quantity = int(len(byte_array) / 2)
        fmt = '>' + (('h' if signed else 'H') * response_quantity)

        return list(struct.unpack(fmt, byte_array))

    def read_coils(self, slave_addr, starting_address, coil_quantity):

        modbus_serial_pdu = bytearray()
        modbus_serial_pdu.append(slave_addr)

        functions = Functions()
        request = functions.read_coils(starting_address, coil_quantity)
        modbus_serial_pdu.extend(request)

        crc = self._calculate_crc16(modbus_serial_pdu)
        modbus_serial_pdu.extend(crc)

        self._uart.write(modbus_serial_pdu)
        response = self._uart_read()

        coil_status_pdu = None
        if (response is not None):
            coil_status_pdu = self._validate_resp_hdr(response, slave_addr, Const.READ_COILS, True)

        return coil_status_pdu

    def read_discrete_inputs(self, slave_addr, starting_address, input_quantity):

        modbus_serial_pdu = bytearray()
        modbus_serial_pdu.append(slave_addr)

        functions = Functions()
        request = functions.read_discrete_inputs(starting_address, input_quantity)
        modbus_serial_pdu.extend(request)

        crc = self._calculate_crc16(modbus_serial_pdu)
        modbus_serial_pdu.extend(crc)

        self._uart.write(modbus_serial_pdu)
        response = self._uart_read()

        input_status_pdu = None
        if (response is not None):
            input_status_pdu = self._validate_resp_hdr(response, slave_addr, Const.READ_DISCRETE_INPUTS, True)

        return input_status_pdu

    def read_holding_registers(self, slave_addr, starting_address, register_quantity, signed = True):

        modbus_serial_pdu = bytearray()
        modbus_serial_pdu.append(slave_addr)

        functions = Functions()
        request = functions.read_holding_registers(starting_address, register_quantity)
        modbus_serial_pdu.extend(request)

        crc = self._calculate_crc16(modbus_serial_pdu)
        modbus_serial_pdu.extend(crc)

        self._uart.write(modbus_serial_pdu)
        response = self._uart_read()

        register_value = None
        if (response is not None):
            register_value_pdu = self._validate_resp_hdr(response, slave_addr, Const.READ_HOLDING_REGISTERS, True)
            register_value = self._to_short(register_value_pdu, signed)

        return register_value

    def read_input_registers(self, slave_addr, starting_address, register_quantity, signed = True):

        modbus_serial_pdu = bytearray()
        modbus_serial_pdu.append(slave_addr)

        functions = Functions()
        request = functions.read_input_registers(starting_address, register_quantity)
        modbus_serial_pdu.extend(request)

        crc = self._calculate_crc16(modbus_serial_pdu)
        modbus_serial_pdu.extend(crc)

        self._uart.write(modbus_serial_pdu)
        response = self._uart_read()

        register_value = None
        if (response is not None):
            register_value_pdu = self._validate_resp_hdr(response, slave_addr, Const.READ_INPUT_REGISTER, True)
            register_value = self._to_short(register_value_pdu, signed)

        return register_value

    def write_single_coil(self, slave_addr, output_address, output_value):

        modbus_serial_pdu = bytearray()
        modbus_serial_pdu.append(slave_addr)

        functions = Functions()
        request = functions.write_single_coil(output_address, output_value)
        modbus_serial_pdu.extend(request)

        crc = self._calculate_crc16(modbus_serial_pdu)
        modbus_serial_pdu.extend(crc)

        self._uart.write(modbus_serial_pdu)
        response = self._uart_read()

        operation_status = False
        if (response is not None):
            response_pdu = self._validate_resp_hdr(response, slave_addr, Const.WRITE_SINGLE_COIL, False)
            operation_status = self._validate_resp_data(response_pdu, Const.WRITE_SINGLE_COIL,
                                                        output_address, value=output_value, signed=False)

        return operation_status

    def write_single_register(self, slave_addr, register_address, register_value, signed = True):

        modbus_serial_pdu = bytearray()
        modbus_serial_pdu.append(slave_addr)

        functions = Functions()
        request = functions.write_single_register(register_address, register_value, signed)
        modbus_serial_pdu.extend(request)

        crc = self._calculate_crc16(modbus_serial_pdu)
        modbus_serial_pdu.extend(crc)

        self._uart.write(modbus_serial_pdu)
        response = self._uart_read()

        operation_status = False
        if (response is not None):
            response_pdu = self._validate_resp_hdr(response, slave_addr, Const.WRITE_SINGLE_REGISTER, False)
            operation_status = self._validate_resp_data(response_pdu, Const.WRITE_SINGLE_REGISTER,
                                                        register_address, value=register_value, signed=signed)

        return operation_status

    def write_multiple_coils(self, slave_addr, starting_address, output_values):

        modbus_serial_pdu = bytearray()
        modbus_serial_pdu.append(slave_addr)

        functions = Functions()
        request = functions.write_multiple_coils(starting_address, output_values)
        modbus_serial_pdu.extend(request)

        crc = self._calculate_crc16(modbus_serial_pdu)
        modbus_serial_pdu.extend(crc)

        self._uart.write(modbus_serial_pdu)
        response = self._uart_read()

        operation_status = False
        if (response is not None):
            response_pdu = self._validate_resp_hdr(response, slave_addr, Const.WRITE_MULTIPLE_COILS, False)
            operation_status = self._validate_resp_data(response_pdu, Const.WRITE_MULTIPLE_COILS,
                                                        starting_address, quantity=len(output_values))

        return operation_status

    def write_multiple_registers(self, slave_addr, starting_address, register_values, signed=True):

        modbus_serial_pdu = bytearray()
        modbus_serial_pdu.append(slave_addr)

        functions = Functions()
        request = functions.write_multiple_registers(starting_address, register_values, signed)
        modbus_serial_pdu.extend(request)

        crc = self._calculate_crc16(modbus_serial_pdu)
        modbus_serial_pdu.extend(crc)

        self._uart.write(modbus_serial_pdu)
        response = self._uart_read()

        operation_status = False
        if (response is not None):
            response_pdu = self._validate_resp_hdr(response, slave_addr, Const.WRITE_MULTIPLE_REGISTERS, False)
            operation_status = self._validate_resp_data(response_pdu, Const.WRITE_MULTIPLE_REGISTERS,
                                                        starting_address, quantity=len(register_values))

        return operation_status
