import uModBus.const as Const
import struct

class Functions:

    def __init__(self):
        pass

    def read_coils(self, starting_address, quantity):
        if not (1 <= quantity <= 2000):
            raise ValueError('Illegal quantity of coils')

        return struct.pack('>BHH', Const.READ_COILS, starting_address, quantity)

    def read_discrete_inputs(self, starting_address, quantity):
        if not (1 <= quantity <= 2000):
            raise ValueError('Illegal quantity of discrete inputs')

        return struct.pack('>BHH', Const.READ_DISCRETE_INPUTS, starting_address, quantity)

    def read_holding_registers(self, starting_address, quantity):
        if not (1 <= quantity <= 125):
            raise ValueError('Illegal quantity of holding registers')

        return struct.pack('>BHH', Const.READ_HOLDING_REGISTERS, starting_address, quantity)

    def read_input_registers(self, starting_address, quantity):
        if not (1 <= quantity <= 125):
            raise ValueError('Illegal quantity of input registers')

        return struct.pack('>BHH', Const.READ_INPUT_REGISTER, starting_address, quantity)

    def write_single_coil(self, output_address, output_value):
        if output_value not in [0x0000, 0xFF00]:
            raise ValueError('Illegal coil value')

        return struct.pack('>BHH', Const.WRITE_SINGLE_COIL, output_address, output_value)

    def write_single_register(self, register_address, register_value, signed=True):
        fmt = 'h' if signed else 'H'

        return struct.pack('>BH' + fmt, Const.WRITE_SINGLE_REGISTER, register_address, register_value)

    def write_multiple_coils(self, starting_address, value_list):
        sectioned_list = [value_list[i:i + 8] for i in range(0, len(value_list), 8)]

        output_value=[]
        for index, byte in enumerate(sectioned_list):
            output = sum(v << i for i, v in enumerate(byte))
            output_value.append(output)

        fmt = 'B' * len(output_value)

        return struct.pack('>BHHB' + fmt, Const.WRITE_MULTIPLE_COILS, starting_address,
                          len(value_list), (len(value_list) // 8) + 1, *output_value)

    def write_multiple_registers(self, starting_address, register_values, signed=True):
        quantity = len(register_values)

        if not (1 <= quantity <= 123):
            raise ValueError('Illegal quantity of registers')

        fmt = ('h' if signed else 'H') * quantity
        return struct.pack('>BHHB' + fmt, Const.WRITE_MULTIPLE_REGISTERS, starting_address,
                           quantity, quantity * 2, *register_values)
