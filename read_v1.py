#!/usr/bin/env python3
"""
Corrected Aquark Mr. Pure Salt Chlorinator Reader
Based on the official specification document
"""

from pymodbus.client import ModbusSerialClient
import paho.mqtt.client as mqtt
import time
import logging

# Set up logging (reduce to INFO to see less debug output)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger()

# Modbus setup - Based on specification
client = ModbusSerialClient(
    method='rtu',
    port='/dev/serial0',
    baudrate=9600,
    timeout=3,  # Increased timeout
    parity='N',
    stopbits=1,
    bytesize=8
)

# MQTT setup
mqtt_client = mqtt.Client("chlorinator_publisher")
mqtt_client.connect("192.168.1.30", 1883, 60)

def read_sensor_data():
    """Read all sensor data according to specification"""
    
    # According to spec, all sensor data is read with Function Code 0x04 (Input Registers)
    # Slave ID should be 8 (from address 0x0001 default value)
    
    sensor_data = {}
    
    try:
        # Read ORP - Address 0x0000, Range -2000~2000 mV
        result = client.read_input_registers(0x0000, 1, slave=8)
        if not result.isError():
            raw_orp = result.registers[0]
            # Convert from unsigned to signed if needed (handle negative values)
            if raw_orp > 32767:  # If > 32767, it's a negative number in 2's complement
                orp = raw_orp - 65536
            else:
                orp = raw_orp
            sensor_data['orp'] = orp
            print(f"ORP: {orp} mV")
        else:
            print(f"Failed to read ORP: {result}")
    
    except Exception as e:
        print(f"Error reading ORP: {e}")
    
    try:
        # Read pH - Address 0x0001, Range 0~1400, Divided by 100
        result = client.read_input_registers(0x0001, 1, slave=8)
        if not result.isError():
            raw_ph = result.registers[0]
            ph = raw_ph / 100.0  # Spec says "Divided by 100 for actual value"
            sensor_data['ph'] = ph
            print(f"pH: {ph:.2f}")
        else:
            print(f"Failed to read pH: {result}")
            
    except Exception as e:
        print(f"Error reading pH: {e}")
    
    try:
        # Read Electrical Conductivity - Address 0x0002, Range 0~9999 ppm
        result = client.read_input_registers(0x0002, 1, slave=8)
        if not result.isError():
            ec = result.registers[0]
            sensor_data['ec'] = ec
            print(f"Electrical Conductivity: {ec} ppm")
        else:
            print(f"Failed to read EC: {result}")
            
    except Exception as e:
        print(f"Error reading EC: {e}")
    
    # Additional readings from spec
    try:
        # Read Pool Temperature - Address 0x0003, Range -1000~1000 °C
        result = client.read_input_registers(0x0003, 1, slave=8)
        if not result.isError():
            raw_temp = result.registers[0]
            # Handle negative temperatures (similar to ORP)
            if raw_temp > 32767:
                temp = (raw_temp - 65536) / 10.0  # Assuming division by 10 like other temp sensors
            else:
                temp = raw_temp / 10.0
            sensor_data['pool_temp'] = temp
            print(f"Pool Temperature: {temp:.1f} °C")
        else:
            print(f"Failed to read Pool Temperature: {result}")
            
    except Exception as e:
        print(f"Error reading Pool Temperature: {e}")
    
    try:
        # Read Chlorine Production - Address 0x0005, Range 0~120 %
        result = client.read_input_registers(0x0005, 1, slave=8)
        if not result.isError():
            chlorine = result.registers[0]
            sensor_data['chlorine'] = chlorine
            print(f"Chlorine Production: {chlorine}%")
        else:
            print(f"Failed to read Chlorine Production: {result}")
            
    except Exception as e:
        print(f"Error reading Chlorine Production: {e}")
    
    return sensor_data

def read_system_status():
    """Read system status and alarms"""
    
    status_data = {}
    
    # Read some status registers using Function Code 0x02 (Read Discrete Inputs)
    status_addresses = {
        0x0000: "Power Supply Abnormal",
        0x0001: "pH Regulation", 
        0x0002: "ORP Regulation",
        0x0003: "Controller Over-temperature Protection",
        0x0030: "No Flow"
    }
    
    for addr, desc in status_addresses.items():
        try:
            result = client.read_discrete_inputs(addr, 1, slave=8)
            if not result.isError():
                status = result.bits[0]
                status_data[desc.lower().replace(' ', '_')] = status
                print(f"{desc}: {'ACTIVE' if status else 'NORMAL'}")
        except Exception as e:
            print(f"Error reading {desc}: {e}")
    
    return status_data

def test_basic_connectivity():
    """Test basic connectivity with different approaches"""
    
    print("=== Testing Basic Connectivity ===")
    
    # Test 1: Try to read the slave address setting (should return 8)
    try:
        result = client.read_holding_registers(0x0001, 1, slave=8)
        if not result.isError():
            parallel_addr = result.registers[0]
            print(f"✓ Successfully read Parallel Address Setting: {parallel_addr}")
            return True
        else:
            print(f"✗ Failed to read Parallel Address: {result}")
    except Exception as e:
        print(f"✗ Error reading Parallel Address: {e}")
    
    # Test 2: Try to read device model (should return 0, 1, 2, or 3)
    try:
        result = client.read_holding_registers(0x0000, 1, slave=8)
        if not result.isError():
            model = result.registers[0]
            model_names = {0: "Shutdown", 1: "Auto mode", 2: "Boost mode", 3: "Factory test mode"}
            model_name = model_names.get(model, f"Unknown ({model})")
            print(f"✓ Successfully read Model/Mode: {model_name}")
            return True
        else:
            print(f"✗ Failed to read Model: {result}")
    except Exception as e:
        print(f"✗ Error reading Model: {e}")
    
    return False

def main():
    print("Aquark Mr. Pure Salt Chlorinator Reader")
    print("Based on Official Specification")
    print("=" * 50)
    
    if not client.connect():
        print("Failed to connect to Modbus device.")
        return
    
    print("Modbus connection established.")
    
    # Test basic connectivity first
    if not test_basic_connectivity():
        print("\n⚠️  Basic connectivity test failed!")
        print("This suggests either:")
        print("1. Wrong slave ID (try different IDs)")
        print("2. Communication parameter mismatch")
        print("3. Device not responding properly")
        client.close()
        return
    
    print("\n✓ Basic connectivity successful!")
    print("\n" + "=" * 50)
    
    try:
        loop_count = 0
        while True:
            print(f"\n--- Reading Cycle {loop_count + 1} ---")
            
            # Read sensor data
            sensor_data = read_sensor_data()
            
            # Read system status every 10th cycle
            if loop_count % 10 == 0:
                print("\n--- System Status ---")
                status_data = read_system_status()
            
            # Send data to Home Assistant via MQTT
            for key, value in sensor_data.items():
                if value is not None:
                    topic = f"pool/{key}"
                    mqtt_client.publish(topic, value)
                    print(f"Published {topic}: {value}")
            
            print(f"\nWaiting 30 seconds...")
            time.sleep(30)
            loop_count += 1
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        client.close()
        mqtt_client.disconnect()
        print("Connections closed.")

if __name__ == "__main__":
    main()
