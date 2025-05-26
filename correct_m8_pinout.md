# Correct M8 Connector Pinout for Aquark Chlorinator

## M8 3-Pin Male Connector (View from Front/Plug End)

```
     GND (1)
    ╱       ╲
   ╱         ╲
  ╱           ╲
 ╱             ╲
B (2)         A (3)
 ╲             ╱
  ╲           ╱
   ╲         ╱
    ╲       ╱
     ╲_____╱
```

## Pin Assignment (CORRECT - Based on Your Testing)

| Pin Position | Function | RS485 Connection |
|--------------|----------|------------------|
| Pin 1 (Top) | GND | Ground |
| Pin 2 (Bottom Left) | B | RS485 B- (Inverting) |
| Pin 3 (Bottom Right) | A | RS485 A+ (Non-inverting) |

## Wiring Diagram (CORRECTED)

```
Raspberry Pi Zero W                RS485 to TTL Board           Aquark Chlorinator M8
┌─────────────────┐               ┌─────────────────┐          ┌──────────────┐
│ Pin 1  (3.3V)   │──────Red──────│ VCC             │          │              │
│ Pin 6  (GND)    │──────Black────│ GND             │──Black───│ Pin 1 (GND)  │
│ Pin 8  (TX)     │──────Yellow───│ TXD             │          │              │
│ Pin 10 (RX)     │──────Green────│ RXD             │          │     1        │
│                 │               │ A               │──White───│    ╱ ╲       │
│                 │               │ B               │──Brown───│   ╱   ╲      │
│                 │               │                 │          │  2     3     │
└─────────────────┘               └─────────────────┘          │ (B)   (A)    │
                                                               └──────────────┘
```

## Connection Summary (CORRECTED)

| Component 1 | Pin/Terminal | Component 2 | Pin/Terminal | Wire Color | Function |
|-------------|--------------|-------------|--------------|------------|----------|
| RPi Zero W | Pin 1 (3.3V) | RS485 Board | VCC | Red | Power |
| RPi Zero W | Pin 6 (GND) | RS485 Board | GND | Black | Ground |
| RPi Zero W | Pin 8 (TX) | RS485 Board | TXD | Yellow | Transmit Data |
| RPi Zero W | Pin 10 (RX) | RS485 Board | RXD | Green | Receive Data |
| RS485 Board | A | M8 Pin 3 | A+ | White | RS485 A+ (Non-inverting) |
| RS485 Board | B | M8 Pin 2 | B- | Brown | RS485 B- (Inverting) |
| RS485 Board | GND | M8 Pin 1 | GND | Black | Signal Ground |

## M8 Connector Visual Reference

```
Looking at the M8 Male Connector (plug end):

    ┌─────────────┐
   ╱      1      ╲     Pin 1: GND (Top)
  ╱     (GND)     ╲
 ╱                 ╲
╱                   ╲
│  2       3         │   Pin 2: B- (Bottom Left)
│ (B-)    (A+)       │   Pin 3: A+ (Bottom Right)
╲                   ╱
 ╲                 ╱
  ╲_______________╱
    M8 Male Plug
```

## What Was Wrong with Original Documentation

The manufacturer's documentation incorrectly stated the pinout as:
- **Wrong**: A, B, GND (or some other order)
- **Correct**: GND, B-, A+ (triangle formation)

This is unfortunately common with industrial connectors where manufacturers use different pin numbering conventions or have documentation errors.

## Verification Steps

Now that you have the correct pinout, you should be able to:

1. ✅ **Get Modbus responses** instead of frame check failures
2. ✅ **Read sensor data** (ORP, pH, EC) successfully  
3. ✅ **See proper LED activity** on RS485 board

## Next Steps

1. **Test your original code** with the corrected wiring
2. **Verify sensor readings** are reasonable values
3. **Set up Home Assistant integration** with working data

## Important Note

**Always document the correct pinout** for future reference, as the manufacturer's documentation is clearly incorrect for your device/serial number. Your systematic testing approach was the right solution when documentation fails!