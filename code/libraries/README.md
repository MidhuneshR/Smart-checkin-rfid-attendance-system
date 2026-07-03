# Software Libraries & Requirements

This folder details the dependencies and third-party libraries required to run the **Smart Check-In RFID Attendance System** on a Raspberry Pi.

## Python Dependency Installation

To install all the required Python modules on a Raspberry Pi, run:

```bash
pip install -r requirements.txt
```

### Dependencies Overview

| Library Name | Version | Purpose |
| :--- | :--- | :--- |
| `RPi.GPIO` | `>=0.7.1` | General-purpose input/output (GPIO) control for LED and Buzzer pins. |
| `spidev` | `>=3.5` | SPI protocol support, necessary for communicating with the MFRC522 RFID reader. |
| `mfrc522` | `>=0.0.7` | High-level library wrapper (SimpleMFRC522) to handle scanning RFID card UID. |
| `adafruit-blinka` | `>=8.0.0` | CircuitPython compatibility layer for interfacing with I2C and hardware busses. |
| `adafruit-circuitpython-charlcd` | `>=2.3.0` | I2C controller for character liquid crystal displays (16x2 LCD). |
| `adafruit-circuitpython-ds3231` | `>=2.2.0` | Interface driver for communicating with the DS3231 Real-Time Clock module. |
| `requests` | `>=2.28.0` | HTTP client to sync student scans with the cloud database API endpoint. |

---

## Hardware Driver Configurations (Raspberry Pi OS)

Before running the script on a physical Raspberry Pi, you must enable **SPI** and **I2C** interfaces using the system configuration utility.

1. Open a terminal and launch the config tool:
   ```bash
   sudo raspi-config
   ```
2. Navigate to **Interface Options**.
3. Enable **I2C** and select **Yes**.
4. Enable **SPI** and select **Yes**.
5. Select **Finish** and reboot your Raspberry Pi:
   ```bash
   sudo reboot
   ```

## Verifying I2C Bus Connections

To verify that the LCD display and DS3231 RTC are detected on the I2C bus:

```bash
sudo apt-get install -y i2c-tools
i2cdetect -y 1
```

A properly wired system will display devices at addresses:
- **`0x27`**: Liquid Crystal Display (LCD)
- **`0x68`**: DS3231 Real-Time Clock (RTC)
