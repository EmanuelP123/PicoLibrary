# Mini-Lab 4: IoT CRM Browser (Pico 2W)

**Emanuel Petrini, PantherID 6288457, ISM 6106**

A Raspberry Pi Pico 2W browses the course CRM REST web service
(`https://iacademy.oracle.com/ords/ism6106/customer/`) and shows customers, contacts and
activities on a 16x2 LCD. It is built on [PicoLibrary](https://github.com/jitsengupta/PicoLibrary).

## Loading options (picked at boot)
- **Prev = Option A (EagerLoader):** loads every customer, then every customer's contacts and activities, before browsing starts.
- **Next = Option B (LazyLoader):** loads only the customers. A customer's contacts and activities are fetched the first time it is selected, then cached.

The LCD and the console both show the load time and the number of REST calls, so the two options can be compared.

## Hardware
| Part | Pin |
|---|---|
| 16x2 I2C LCD | SDA GP0, SCL GP1 |
| 8-LED NeoPixel ring | GP2 |
| Passive buzzer | GP16 |
| Prev / Next / Select buttons | GP17 / GP18 / GP19 |

Ring colours: blue = loading progress, amber = details not loaded yet, green = has activities, red = no activities.

## Controls
- **Prev / Next:** move through customers, contacts or activities.
- **Select:** go from customer to contacts, then to activities, then back to customers.

## Files
| File | Purpose |
|---|---|
| `main.py` | Entry point |
| `config.py` | WiFi SSID and password, base URL, and my customer name |
| `CRMController.py` | StateModel handler: states MODE, LOADING, CUSTOMERS, CONTACTS, ACTIVITIES |
| `DataLoader.py` | Strategy pattern: `DataLoader`, `EagerLoader` (A), `LazyLoader` (B) |
| `CRMService.py` | REST proxy over `Net.getJson()` |
| `CRMModel.py` | `Customer`, `Contact`, `Activity` |
| `CRMView.py` | LCD, light ring and buzzer output |
| `Trace.py` | Prints `[t s] Source -> Target: message` lines that follow the sequence diagrams |

All other `.py` files are the PicoLibrary modules this app needs.

## Run
1. Copy all the `.py` files to the Pico.
2. In `config.py`, set `WIFI_SSID` and `WIFI_PASSWORD`. Use a 2.4 GHz network.
3. Run `main.py` from Thonny.
