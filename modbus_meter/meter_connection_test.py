from pymodbus.client import ModbusTcpClient
import struct


def registers_to_float(registers):
    return struct.unpack('<f', struct.pack('<HH', registers[0], registers[1]))[0]


client = ModbusTcpClient('192.168.2.165', port=5020)  # Replace with your Raspberry Pi's IP and chosen port
if client.connect():
    print("Connected successfully")

    # Read active power registers
    result = client.read_input_registers(2015, 28)  # Start from 2015 (300015) and read 28 registers
    if not result.isError():
        # Extract and convert active power values
        active_power_1 = registers_to_float(result.registers[0:2])
        active_power_2 = registers_to_float(result.registers[8:10])
        active_power_3 = registers_to_float(result.registers[16:18])
        total_active_power = registers_to_float(result.registers[26:28])

        print(f"Active Power Phase 1: {active_power_1:.2f} W")
        print(f"Active Power Phase 2: {active_power_2:.2f} W")
        print(f"Active Power Phase 3: {active_power_3:.2f} W")
        print(f"Total Active Power: {total_active_power:.2f} W")
    else:
        print(f"Error: {result}")

    client.close()
else:
    print("Unable to connect")