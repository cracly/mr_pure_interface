# Aquark Chlorinator Reader Setup Instructions

## Overview
This guide will help you set up the robust chlorinator reader with:
1. **Comprehensive sensor reading** from all available registers
2. **Robust error handling** and automatic reconnection
3. **Full MQTT integration** with Home Assistant auto-discovery
4. **Automatic startup** as a system service

## Step 1: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
pip3 install pymodbus paho-mqtt

# Or install system-wide (recommended for service)
sudo apt install python3-pip
sudo pip3 install pymodbus paho-mqtt
```

## Step 2: Create Project Directory

```bash
# Create project directory
mkdir -p /home/pi/aquark-chlorinator
cd /home/pi/aquark-chlorinator

# Create log directory
sudo mkdir -p /var/log
sudo chown pi:pi /var/log
```

## Step 3: Install Scripts

Save the following files in `/home/pi/aquark-chlorinator/`:

1. **`chlorinator_reader.py`** - Main reader script (from the robust reader artifact)
2. **`mqtt_test.py`** - MQTT test script
3. **`chlorinator_config.json`** - Configuration file (created automatically)

```bash
# Make scripts executable
chmod +x /home/pi/aquark-chlorinator/chlorinator_reader.py
chmod +x /home/pi/aquark-chlorinator/mqtt_test.py
```

## Step 4: Test MQTT Connection

Before running the full reader, test your MQTT setup:

```bash
cd /home/pi/aquark-chlorinator
python3 mqtt_test.py
```

**Expected output:**
```
✅ Connected to MQTT broker successfully
✅ Published pool/chlorinator/pool_temperature: 24.5
✅ Published pool/chlorinator/orp: 720
✅ Published pool/chlorinator/ph: 7.35
✅ Published pool/chlorinator/chlorine_production: 45
```

**If MQTT test fails:**
- Check your Home Assistant IP address
- Verify MQTT broker is running in Home Assistant
- Check firewall settings

## Step 5: Configure the Reader

The configuration file will be created automatically on first run. You can customize it:

```json
{
  "modbus": {
    "port": "/dev/serial0",
    "baudrate": 9600,
    "timeout": 5,
    "parity": "N",
    "stopbits": 1,
    "bytesize": 8,
    "slave_id": 8
  },
  "mqtt": {
    "host": "192.168.1.30",
    "port": 1883,
    "username": null,
    "password": null,
    "client_id": "aquark_chlorinator",
    "topic_prefix": "pool/chlorinator",
    "homeassistant_discovery": true,
    "discovery_prefix": "homeassistant"
  },
  "reading": {
    "interval": 30,
    "retry_attempts": 3,
    "retry_delay": 5
  }
}
```

**Edit the config file:**
```bash
nano /home/pi/aquark-chlorinator/chlorinator_config.json
```

**Key settings to verify:**
- `mqtt.host`: Your Home Assistant IP
- `mqtt.username/password`: If you have MQTT authentication enabled
- `reading.interval`: How often to read sensors (seconds)

## Step 6: Test the Reader

Run the reader manually first to verify everything works:

```bash
cd /home/pi/aquark-chlorinator
python3 chlorinator_reader.py
```

**Expected output:**
```
2024-01-20 10:30:00 - INFO - Chlorinator Reader starting up
2024-01-20 10:30:01 - INFO - Modbus connection established  
2024-01-20 10:30:01 - INFO - MQTT connected successfully
2024-01-20 10:30:02 - INFO - Published HA discovery for pool_temperature
2024-01-20 10:30:05 - INFO - Successfully read 15 sensors
2024-01-20 10:30:05 - INFO - Pool Temperature: 24.5 °C
2024-01-20 10:30:05 - INFO - ORP: 720 mV
2024-01-20 10:30:05 - INFO - pH: 7.35 
2024-01-20 10:30:05 - INFO - Chlorine Production: 45 %
```

**Press Ctrl+C to stop when satisfied it's working.**

## Step 7: Setup Automatic Startup

Create systemd service file:

```bash
sudo nano /etc/systemd/system/aquark-chlorinator.service
```

**Paste the service configuration:**
```ini
[Unit]
Description=Aquark Chlorinator MQTT Reader
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/aquark-chlorinator
ExecStart=/usr/bin/python3 /home/pi/aquark-chlorinator/chlorinator_reader.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

**Enable and start the service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start at boot
sudo systemctl enable aquark-chlorinator.service

# Start the service now
sudo systemctl start aquark-chlorinator.service

# Check service status
sudo systemctl status aquark-chlorinator.service
```

## Step 8: Monitor the Service

**Check service logs:**
```bash
# Real-time logs
sudo journalctl -u aquark-chlorinator.service -f

# Recent logs
sudo journalctl -u aquark-chlorinator.service -n 50

# Logs from today
sudo journalctl -u aquark-chlorinator.service --since today
```

**Check log file:**
```bash
tail -f /var/log/chlorinator.log
```

**Service management commands:**
```bash
# Stop service
sudo systemctl stop aquark-chlorinator.service

# Restart service  
sudo systemctl restart aquark-chlorinator.service

# Disable service
sudo systemctl disable aquark-chlorinator.service
```

## Step 9: Home Assistant Integration

The reader will automatically create these entities in Home Assistant:

### Sensors Created:
- **Pool Temperature** (`sensor.pool_temperature`)
- **Pool ORP** (`sensor.pool_orp`) 
- **Pool pH** (`sensor.pool_ph`)
- **Pool Chlorine Production** (`sensor.pool_chlorine_production`)

### Finding Your Sensors:
1. Go to **Settings** → **Devices & Services**
2. Look for **MQTT** integration
3. Check for new **Aquark Pool Chlorinator** device
4. Or go to **Settings** → **Entities** and search for "pool"

### Add to Dashboard:
1. Go to your Home Assistant dashboard
2. Click **Edit Dashboard**
3. Click **Add Card**
4. Choose **Entities Card**
5. Add your pool sensors

## Step 10: Troubleshooting

### Common Issues:

**1. No MQTT Connection:**
```bash
# Test MQTT manually
python3 mqtt_test.py

# Check Home Assistant MQTT broker
# Settings → Add-ons → Mosquitto broker → Start
```

**2. No Modbus Connection:**
```bash
# Check serial port permissions
ls -la /dev/serial0
sudo chmod 666 /dev/serial0

# Test with original simple script
python3 read.py  # Your original working script
```

**3. Service Won't Start:**
```bash
# Check service status
sudo systemctl status aquark-chlorinator.service

# Check for errors
sudo journalctl -u aquark-chlorinator.service -n 20
```

**4. Sensors Not Appearing in HA:**
```bash
# Check MQTT messages
# In Home Assistant: Settings → Devices & Services → MQTT → Configure
# Listen to topic: pool/chlorinator/+
```

### Log Locations:
- **Service logs**: `sudo journalctl -u aquark-chlorinator.service`
- **Application logs**: `/var/log/chlorinator.log`
- **MQTT test logs**: Terminal output when running `mqtt_test.py`

## Step 11: Advanced Configuration

### Custom MQTT Topics:
Edit `chlorinator_config.json` to change topic structure:
```json
{
  "mqtt": {
    "topic_prefix": "pool/sensors",  # Changes topics to pool/sensors/ph etc.
    "homeassistant_discovery": false  # Disable auto-discovery
  }
}
```

### Reading Interval:
```json
{
  "reading": {
    "interval": 60,  # Read every 60 seconds instead of 30
    "retry_attempts": 5,  # More retries on failure
    "retry_delay": 10   # Longer delay between retries
  }
}
```

### Additional Sensors:
The reader automatically reads ALL available registers from the specification. To see all available data, check the logs or add more sensors to the `priority_sensors` list in the code.

## Success Indicators:

✅ **MQTT test passes**  
✅ **Manual reader run shows sensor data**  
✅ **Service starts and stays running**  
✅ **Home Assistant shows new pool sensors**  
✅ **Sensor values update every 30 seconds**

Your chlorinator should now be fully integrated with Home Assistant!