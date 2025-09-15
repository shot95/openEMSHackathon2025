from pymodbus.client import ModbusTcpClient
import struct

def registers_to_float(registers):
    return struct.unpack('>f', struct.pack('>HH', registers[0], registers[1]))[0]

client = ModbusTcpClient('172.16.101.196', port=5020)  # Replace with your Raspberry Pi's IP and chosen port
if client.connect():
    print("Connected successfully")

    # Read all relevant registers
    result = client.read_input_registers(address=2001, count=53)  # Use keyword arguments
    if not result.isError():
        # Extract and convert values
        voltage_1 = registers_to_float(result.registers[0:2])
        voltage_2 = registers_to_float(result.registers[2:4])
        voltage_3 = registers_to_float(result.registers[4:6])

        current_1 = registers_to_float(result.registers[12:14])
        current_2 = registers_to_float(result.registers[20:22])
        current_3 = registers_to_float(result.registers[28:30])

        active_power_1 = registers_to_float(result.registers[14:16])
        active_power_2 = registers_to_float(result.registers[22:24])
        active_power_3 = registers_to_float(result.registers[30:32])

        total_active_power = registers_to_float(result.registers[40:42])

        frequency = registers_to_float(result.registers[51:53])

        print(f"Voltage Phase 1: {voltage_1:.2f} V")
        print(f"Voltage Phase 2: {voltage_2:.2f} V")
        print(f"Voltage Phase 3: {voltage_3:.2f} V")
        print(f"Current Phase 1: {current_1:.2f} A")
        print(f"Current Phase 2: {current_2:.2f} A")
        print(f"Current Phase 3: {current_3:.2f} A")
        print(f"Active Power Phase 1: {active_power_1:.2f} W")
        print(f"Active Power Phase 2: {active_power_2:.2f} W")
        print(f"Active Power Phase 3: {active_power_3:.2f} W")
        print(f"Total Active Power: {total_active_power:.2f} W")
        print(f"Frequency: {frequency:.2f} Hz")
    else:
        print(f"Error: {result}")

    client.close()
else:
    print("Unable to connect")
