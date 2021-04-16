#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#
from uModBus.serial import Serial
from uModBus.tcp import TCP
from network import WLAN
import machine

####################### TCP MODBUS #########################
WIFI_SSID = 'your ssid'
WIFI_PASS = 'your password'

wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_SSID, auth=(None, WIFI_PASS), timeout=5000)
while not wlan.isconnected():
    machine.idle() # save power while waiting

print('WLAN connection succeeded!')

slave_ip = 'slave ip'
modbus_obj = TCP(slave_ip)

######################### RTU SERIAL MODBUS #########################
#uart_id = 0x01
#modbus_obj = Serial(uart_id, pins=('P9', 'P10'))
# if the serial modbus requires a ctrl pin, you can set it like this:
#modbus_obj = Serial(uart_id, pins=('P9','P10'), ctrl_pin='P8')

######################### READ COILS #########################
#slave_addr=0x0A
#starting_address=0x00
#coil_quantity=100

#coil_status = modbus_obj.read_coils(slave_addr, starting_address, coil_quantity)
#print('Coil status: ' + ' '.join('{:d}'.format(x) for x in coil_status))

###################### READ DISCRETE INPUTS ##################
#slave_addr=0x0A
#starting_address=0x0
#input_quantity=100

#input_status = modbus_obj.read_discrete_inputs(slave_addr, starting_address, input_quantity)
#print('Input status: ' + ' '.join('{:d}'.format(x) for x in input_status))

###################### READ HOLDING REGISTERS ##################
#slave_addr=0x0A
#starting_address=0x00
#register_quantity=100
#signed=True

#register_value = modbus_obj.read_holding_registers(slave_addr, starting_address, register_quantity, signed)
#print('Holding register value: ' + ' '.join('{:d}'.format(x) for x in register_value))

###################### READ INPUT REGISTERS ##################
#slave_addr=0x0A
#starting_address=0x00
#register_quantity=100
#signed=True

#register_value = modbus_obj.read_input_registers(slave_addr, starting_address, register_quantity, signed)
#print('Input register value: ' + ' '.join('{:d}'.format(x) for x in register_value))

###################### WRITE SINGLE COIL ##################
#slave_addr=0x0A
#output_address=0x00
#output_value=0xFF00

#return_flag = modbus_obj.write_single_coil(slave_addr, output_address, output_value)
#output_flag = 'Success' if return_flag else 'Failure'
#print('Writing single coil status: ' + output_flag)

###################### WRITE SINGLE REGISTER ##################
#slave_addr=0x0A
#register_address=0x01
#register_value=-32768
#signed=True

#return_flag = modbus_obj.write_single_register(slave_addr, register_address, register_value, signed)
#output_flag = 'Success' if return_flag else 'Failure'
#print('Writing single coil status: ' + output_flag)

###################### WRITE MULTIPLE COILS ##################
#slave_addr=0x0A
#starting_address=0x00
#output_values=[1,1,1,0,0,1,1,1,0,0,1,1,1]

#return_flag = modbus_obj.write_multiple_coils(slave_addr, starting_address, output_values)
#output_flag = 'Success' if return_flag else 'Failure'
#print('Writing multiple coil status: ' + output_flag)

###################### WRITE MULTIPLE REGISTERS ##################
slave_addr=0x0A
register_address=0x01
register_values=[2, -4, 6, -256, 1024]
signed=True

return_flag = modbus_obj.write_multiple_registers(slave_addr, register_address, register_values, signed)
output_flag = 'Success' if return_flag else 'Failure'
print('Writing multiple register status: ' + output_flag)
