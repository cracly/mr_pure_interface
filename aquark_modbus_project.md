# Aquark Mr. Pure Salt Chlorinator Modbus Integration Project

## Project Overview
Integration of Aquark Mr. Pure Salt chlorinator with Home Assistant via Raspberry Pi Zero W using Modbus RS485 communication protocol.

## Hardware Components
- Aquark Mr. Pure Salt chlorinator (with Modbus RS485 interface)
- Raspberry Pi Zero W
- RS485 to TTL converter board
- Dupont jumper wires (male-female and female-female)
- MicroSD card (16GB+ recommended)
- Power supply for RPi Zero W

## Pinout Diagrams

### Raspberry Pi Zero W GPIO Pinout (Relevant Pins)
```
Pin 1  [3.3V]     [5V] Pin 2
Pin 3  [GPIO 2]   [5V] Pin 4
Pin 5  [GPIO 3]   [GND] Pin 6
Pin 7  [GPIO 4]   [GPIO 14/TX] Pin 8
Pin 9  [GND]      [GPIO 15/RX] Pin 10
Pin 11 [GPIO 17]  [GPIO 18] Pin 12
Pin 13 [GPIO 27]  [GND] Pin 14
...
```

### RS485 to TTL Converter Board (Your Board Pinout)
```
VCC  - Power input (3.3V or 5V)
GND  - Ground
RXD  - Receiver Output (connects to RPi RX)
TXD  - Driver Input (connects to RPi TX)
A    - RS485 A+ (Non-inverting)
B    - RS485 B- (Inverting)
```

Note: This board automatically handles DE/RE control internally.

### Aquark Mr. Pure Salt Chlorinator Modbus Connector
```
GND  - Ground
A    - RS485 A+ (Non-inverting) 
B    - RS485 B- (Inverting)
```

## Wiring Connections

### Connection Table
| Component 1 | Pin/Terminal | Component 2 | Pin/Terminal | Wire Color Suggestion |
|-------------|--------------|-------------|--------------|----------------------|
| RPi Zero W | Pin 1 (3.3V) | RS485 Board | VCC | Red |
| RPi Zero W | Pin 6 (GND) | RS485 Board | GND | Black |
| RPi Zero W | Pin 8 (GPIO 14/TX) | RS485 Board | TXD | Yellow |
| RPi Zero W | Pin 10 (GPIO 15/RX) | RS485 Board | RXD | Green |
| RS485 Board | A | Chlorinator | A | White |
| RS485 Board | B | Chlorinator | B | Brown |
| RS485 Board | GND* | Chlorinator | GND | Black |

*Note: GND connection between RS485 board and chlorinator may not be necessary if both devices share common ground through RPi, but recommended for signal integrity.

### Wiring Diagram (Text Format)
```
Raspberry Pi Zero W                RS485 to TTL Board           Aquark Chlorinator
┌─────────────────┐               ┌─────────────────┐          ┌──────────────┐
│ Pin 1  (3.3V)   │──────Red──────│ VCC             │          │              │
│ Pin 6  (GND)    │──────Black────│ GND             │          │              │
│ Pin 8  (TX)     │──────Yellow───│ TXD             │          │              │
│ Pin 10 (RX)     │──────Green────│ RXD             │          │              │
│                 │               │ A               │───White──│ A            │
│                 │               │ B               │───Brown──│ B            │
│                 │               │ GND             │───Black──│ GND          │
└─────────────────┘               └─────────────────┘          └──────────────┘
```

## Software Setup

### 1. Raspberry Pi OS Installation
1. Flash Raspberry Pi OS Lite to microSD card
2. Enable SSH by creating empty `ssh` file in boot partition
3. Configure WiFi by creating `wpa_supplicant.conf` in boot partition:
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourWiFiName"
    psk="YourWiFiPassword"
}
```

### 2. Initial System Configuration
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-serial git -y
pip3 install pymodbus paho-mqtt pyserial
```

### 3. Enable UART
```bash
sudo raspi-config
# Navigate to: Interface Options > Serial Port
# - Would you like a login shell accessible over serial? NO
# - Would you like the serial port hardware enabled? YES
sudo reboot
```

### 4. Disable Bluetooth (to free up UART)
Add to `/boot/config.txt`:
```
dtoverlay=disable-bt
```

### 5. Test Serial Connection
```bash
# Check if serial port is available
ls -la /dev/serial*
# Should show /dev/serial0 or /dev/ttyS0
```

## Modbus Configuration

### Typical Modbus Settings for Pool Equipment
- **Baud Rate:** 9600 or 19200 bps
- **Data Bits:** 8
- **Parity:** None or Even
- **Stop Bits:** 1
- **Slave ID:** Usually 1 (check manual)

### Python Modbus Client Template
```python
from pymodbus.client.sync import ModbusSerialClient
import time

# Configure serial connection
client = ModbusSerialClient(
    method='rtu',
    port='/dev/serial0',
    baudrate=9600,
    timeout=3,
    parity='N',
    stopbits=1,
    bytesize=8
)

# Connect and read data
if client.connect():
    # Example: Read holding registers
    result = client.read_holding_registers(0, 10, unit=1)
    if not result.isError():
        print(f"Registers: {result.registers}")
    client.close()
```

## Home Assistant Integration Options

### Option 1: MQTT Discovery
- Run Python script on RPi that publishes to MQTT
- Use Home Assistant MQTT integration with auto-discovery

### Option 2: Modbus TCP Bridge
- Use `mbusd` to create TCP/IP bridge
- Connect Home Assistant directly via Modbus integration

### Option 3: Custom Integration
- Develop custom Home Assistant component
- Direct serial communication from HA

## Testing and Troubleshooting

### Serial Port Testing
```bash
# Test serial communication
sudo minicom -D /dev/serial0 -b 9600

# Check for data transmission
sudo cat /dev/serial0

# Monitor GPIO states
gpio readall
```

### Common Issues
1. **No response from device:**
   - Check wiring connections
   - Verify baud rate and communication parameters
   - Ensure proper RS485 termination if required

2. **Permission denied on serial port:**
   ```bash
   sudo usermod -a -G dialout $USER
   # Logout and login again
   ```

3. **GPIO conflicts:**
   - Disable other services using UART
   - Check for overlay conflicts in `/boot/config.txt`

## Project Structure
```
/home/pi/aquark-modbus/
├── config/
│   ├── modbus_config.yaml
│   └── mqtt_config.yaml
├── src/
│   ├── modbus_client.py
│   ├── mqtt_publisher.py
│   └── main.py
├── logs/
├── systemd/
│   └── aquark-modbus.service
└── README.md
```

## Safety Considerations
- Ensure all electrical connections are secure
- Use appropriate wire gauges for distances
- Consider surge protection for outdoor installations
- Verify chlorinator is powered off during initial wiring
- Test with multimeter before connecting to RPi

## Next Steps
1. Obtain Aquark Modbus register specification
2. Wire up hardware connections
3. Install and configure Raspberry Pi OS
4. Develop and test Modbus communication code
5. Integrate with Home Assistant
6. Set up monitoring and alerts

## Documentation References
- [Modbus Protocol Specification](https://modbus.org/docs/)
- [PyModbus Documentation](https://pymodbus.readthedocs.io/)
- [Home Assistant Modbus Integration](https://www.home-assistant.io/integrations/modbus/)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)