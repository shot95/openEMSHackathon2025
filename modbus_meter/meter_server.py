from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore.store import ModbusSequentialDataBlock
import random
import struct
import asyncio
import logging
import argparse

# Define the register offset
OFFSET = 2001

# Add these variables at the beginning of your script, outside of any function
SMOOTHING_FACTOR = 0.1
last_voltage = 230
last_current = 10
last_active_power = 0
last_apparent_power = 2500
last_reactive_power = 0
last_frequency = 50


def float_to_registers(value):
    return struct.unpack('>HH', struct.pack('>f', value))


# Add this function to your script
def smooth_random(last_value, min_value, max_value, smoothing_factor):
    target = random.uniform(min_value, max_value)
    return last_value + (target - last_value) * smoothing_factor


def parse_args():
    parser = argparse.ArgumentParser(description="Modbus TCP server for simulated meter")
    parser.add_argument('-p', '--port', type=int, default=5020,
                        help="Port to run the server on (default: 5020)")
    return parser.parse_args()


# Define your custom Modbus table
store = ModbusSlaveContext(
    ir=ModbusSequentialDataBlock(OFFSET, [0] * (300080 - OFFSET + 1)),
    hr=ModbusSequentialDataBlock(0, [0] * 100),
    co=ModbusSequentialDataBlock(0, [0] * 100),
    di=ModbusSequentialDataBlock(0, [0] * 100)
)
context = ModbusServerContext(slaves=store, single=True)


# Periodically update registers
async def updating_writer(context):
    global last_voltage, last_current, last_active_power, last_apparent_power
    global last_reactive_power, last_frequency

    while True:
        # Generate smooth random values
        voltage = smooth_random(last_voltage, 220, 240, SMOOTHING_FACTOR)
        current = smooth_random(last_current, 0, 20, SMOOTHING_FACTOR)
        active_power = smooth_random(last_active_power, -5000, 5000, SMOOTHING_FACTOR)
        apparent_power = smooth_random(last_apparent_power, 0, 5000, SMOOTHING_FACTOR)
        reactive_power = smooth_random(last_reactive_power, -5000, 5000, SMOOTHING_FACTOR)
        frequency = smooth_random(last_frequency, 49.5, 50.5, SMOOTHING_FACTOR)

        # Update last values
        last_voltage, last_current = voltage, current
        last_active_power, last_apparent_power, last_reactive_power = active_power, apparent_power, reactive_power
        last_frequency = frequency

        # Use the same values for all phases
        voltages = [voltage] * 3
        currents = [current] * 3
        active_powers = [active_power] * 3
        apparent_powers = [apparent_power] * 3
        reactive_powers = [reactive_power] * 3

        # Update registers
        values = []

        # Voltages (300001 - 300006)
        for voltage in voltages:
            values.extend(float_to_registers(voltage))

        # Dummy values for 300007 - 300012
        values.extend([0] * 6)

        # Currents and Powers (300013 - 300046)
        for i in range(3):
            values.extend(float_to_registers(currents[i]))
            values.extend(float_to_registers(active_powers[i]))
            values.extend(float_to_registers(apparent_powers[i]))
            values.extend(float_to_registers(reactive_powers[i]))

        # Dummy values for 300037 - 300040
        values.extend([0] * 4)

        # Total powers (300041 - 300046)
        values.extend(float_to_registers(sum(active_powers)))
        values.extend(float_to_registers(sum(apparent_powers)))
        values.extend(float_to_registers(sum(reactive_powers)))

        # Dummy values for 300047 - 300051
        values.extend([0] * 5)

        # Frequency (300052)
        values.extend(float_to_registers(frequency))

        # Dummy values for 300053 - 300080
        values.extend([0] * 28)

        # Log the first few values being written
        logging.info(f"Writing values: {values[:10]}")  # Log first 10 values

        # Update the input registers
        context[0].setValues(4, OFFSET, values)

        await asyncio.sleep(1)  # Update every second


# Add this near the top of your file
logging.basicConfig(level=logging.INFO)


async def run_server(port):
    server_localhost = await StartAsyncTcpServer(context=context, address=("127.0.0.1", port))
    server_all = await StartAsyncTcpServer(context=context, address=("0.0.0.0", port))
    logging.info(f"Server starting on 127.0.0.1:{port} and 0.0.0.0:{port}")
    return server_localhost, server_all


async def main(port):
    updater_task = asyncio.create_task(updating_writer(context))
    server_localhost, server_all = await run_server(port)

    try:
        await asyncio.gather(
            updater_task,
            server_localhost.serve_forever(),
            server_all.serve_forever()
        )
    except asyncio.CancelledError:
        logging.info("Tasks cancelled")
    finally:
        logging.info("Server stopped")


if __name__ == "__main__":
    args = parse_args()
    logging.info(f"Starting server on port {args.port}...")
    try:
        asyncio.run(main(args.port))
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
