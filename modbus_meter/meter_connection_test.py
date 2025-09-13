from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.2.165', port=5020)  # Replace with your Raspberry Pi's IP and chosen port
if client.connect():
    print("Connected successfully")
    result = client.read_input_registers(2001, 10)
    if not result.isError():
        print(f"Registers: {result.registers}")
    else:
        print(f"Error: {result}")
    client.close()
else:
    print("Unable to connect")