# IoT Temperature Monitoring System

> **Authors:**
> - **Aditya Khetrapal (Roll No. :- 23095005)**
> - **Vivek Maurya (Roll No. :- 23095122)**

---

## APPLICATION OVERVIEW

### **Selected Application: IoT Temperature Monitoring System**

**Real-World Use Case:** Smart Building Climate Control

This simulation implements a **real IoT application** that monitors environmental conditions in critical infrastructure:

```
┌─────────────────────────────────────────────────────────┐
│  APPLICATION: IoT Temperature Sensor Network            │
│                                                          │
│   Sensor Node (Node 1)                                │
│     Location: Server Room A                             │
│     Sensor ID: TEMP_SENSOR_001                          │
│     Measures: Temperature & Humidity                     │
│                                                          │
│   Central Server (Node 5)                             │
│     Purpose: Real-time monitoring & alerting            │
│     Actions: Log data, trigger cooling systems          │
└─────────────────────────────────────────────────────────┘
```

---

## WHY THIS APPLICATION?

**Problem:** Server rooms and data centers require constant temperature monitoring to prevent:
- Equipment overheating (costly damage)
- System failures and downtime
- Fire hazards
- Reduced equipment lifespan

**Solution:** IoT sensors continuously transmit temperature/humidity data to a central monitoring system through a reliable network protocol.

---

## WHAT DATA DOES THE APPLICATION GENERATE?

Each sensor reading contains:

```json
{
  "sensor_id": "TEMP_SENSOR_001",
  "location": "Server_Room_A",
  "temperature_celsius": 24.73,
  "humidity_percent": 55.42,
  "timestamp": 1735776234.567,
  "packet_number": 12,
  "alert": "NORMAL"  // or "HIGH_TEMP" if temp > 26°C
}
```

### Data Generation Details:
- **Temperature Range:** 18-28°C (realistic server room conditions)
- **Humidity Range:** 30-70% (optimal operating range)
- **Alert System:** Flags high temperature readings (>26°C)
- **Frequency:** Continuous monitoring (50 readings in this simulation)
- **Data Size:** 1024 bytes per reading (includes metadata)

---

## HOW DATA FLOWS THROUGH THE LAYERS

### Complete Data Journey (Step-by-Step):

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: APPLICATION LAYER (Node 1 - Sensor)            │
├─────────────────────────────────────────────────────────┤
│ Generate sensor reading:                                 │
│ • Temperature: 24.73°C                                   │
│ • Humidity: 55.42%                                       │
│ • Status: NORMAL                                         │
│ • Format: JSON (1024 bytes)                             │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: TRANSPORT LAYER                                 │
├─────────────────────────────────────────────────────────┤
│ Wrap sensor data in transport packet:                   │
│ • Source Port: 8080 (Sensor Port)                       │
│ • Dest Port: 9090 (Server Port)                         │
│ • Sequence Number: 12                                    │
│ • Checksum: 54321 (error detection)                     │
│ • Payload: [JSON sensor data]                           │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: NETWORK LAYER                                   │
├─────────────────────────────────────────────────────────┤
│ Add IP addressing:                                       │
│ • Source IP: 192.168.1.1 (Sensor Node)                  │
│ • Dest IP: 192.168.1.5 (Server Node)                    │
│ • TTL: 64 (Time To Live)                                │
│ • Contains: [Transport Packet]                          │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: ROUTING DECISION                                │
├─────────────────────────────────────────────────────────┤
│ Path Selection (BFS Algorithm):                         │
│ • Option 1: Node 1 → 2 → 3 → 5 (3 hops)               │
│ • Option 2: Node 1 → 4 → 5 (2 hops) ✓ SELECTED        │
│ • Reason: Shortest path, lowest latency                 │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: DATA LINK LAYER (Hop 1: Node 1 → 4)           │
├─────────────────────────────────────────────────────────┤
│ Convert packet to frame:                                │
│ • Source MAC: 00:00:00:00:00:01                         │
│ • Dest MAC: 00:00:00:00:00:04                           │
│ • CRC: 12845 (frame integrity check)                    │
│ • Contains: [Network Packet]                            │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 6: PHYSICAL LAYER (Signal Conversion)              │
├─────────────────────────────────────────────────────────┤
│ Convert frame to electrical/radio signal:               │
│ • Method: BPSK Modulation                               │
│ • Binary: 0 → -1, 1 → +1                               │
│ • Signal Length: 8144 bits                              │
│ • Ready for wireless transmission                       │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 7: AWGN CHANNEL (Wireless Transmission)            │
├─────────────────────────────────────────────────────────┤
│ Transmit through real-world wireless channel:           │
│ • Channel Type: AWGN (Additive White Gaussian Noise)    │
│ • SNR: 15 dB (Signal-to-Noise Ratio)                   │
│ • Effects: Interference, fading, noise                  │
│ • Formula: Received = Signal + Gaussian_Noise          │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 8: RECEIVER (Node 4 - Intermediate Router)        │
├─────────────────────────────────────────────────────────┤
│ Demodulate and verify:                                  │
│ • Demodulation: Signal → Bits (threshold detection)    │
│ • CRC Check: ✓ Frame integrity verified                │
│ • BER: 0.000001 (very low error rate)                  │
│ • Forward to next hop (Node 4 → 5)                     │
└─────────────────────────────────────────────────────────┘
                    ↓
        [Repeat Steps 5-8 for Hop 2: Node 4 → 5]
                    ↓
┌─────────────────────────────────────────────────────────┐
│ FINAL: APPLICATION LAYER (Node 5 - Server)             │
├─────────────────────────────────────────────────────────┤
│ Receive and process sensor data:                        │
│ • Extract JSON data                                      │
│ • Log temperature: 24.73°C ✓                            │
│ • Check alert status: NORMAL ✓                          │
│ • Update dashboard                                       │
│ • No action needed (temp within range)                  │
└─────────────────────────────────────────────────────────┘
```

---

## SIMULATION RESULTS

### Overall Key Performance Indicators (KPIs)

| Metric | Value | Status | Impact on IoT Application |
|--------|-------|--------|---------------------------|
| **Throughput** | ~0.82 Mbps | Good | Sufficient for continuous sensor data |
| **Average Latency** | ~9.99 ms | Excellent | Real-time monitoring possible |
| **Packet Loss** | 0.00% | Perfect | No data loss, all readings received |
| **Jitter** | Moderate | Acceptable | Acceptable for monitoring (not control) |
| **Success Rate** | 100.00% | Perfect | Reliable system |

### Per-Layer KPI and QoS Metrics
The simulation now tracks comprehensive metrics for **each layer** (Application, Transport, Network, Data Link, and Physical). For each layer, it evaluates:
- **KPI Metrics:** Throughput, Average Processing Time, Success/Error Rate, Protocol Overhead, and Bytes Processed.
- **QoS Metrics:** Reliability, Efficiency, Performance, and Overall QoS Score.

### Visualized Results
Upon completion, the simulation generates a comprehensive performance dashboard (`simulation_results_with_layer_kpi.png`) containing:
- Packet Transmission Statistics & Latency Distribution
- Overall KPIs Summary
- Per-Layer Throughput, Processing Time, and Success Rate
- QoS Metrics Comparison Across All Layers
- Protocol Overhead by Layer

### What This Means for the IoT Application:

- **Reliable Monitoring:** 100% of sensor readings delivered successfully  
- **Real-Time Data:** < 10ms latency enables instant alerts  
- **No Data Loss:** Critical temperature readings never missed  
- **Consistent Updates:** Jitter acceptable for non-critical monitoring  
- **Scalable:** Can support multiple sensors simultaneously  

---

## APPLICATION LAYER IMPLEMENTATION

### Code Structure:

```python
class ApplicationLayer:
    """
    IoT Temperature Monitoring System
    
    Simulates a real-world IoT sensor that:
    - Monitors temperature and humidity
    - Generates periodic sensor readings
    - Formats data in JSON
    - Sends to central monitoring server
    """
    
    def __init__(self, config):
        self.sensor_id = "TEMP_SENSOR_001"
        self.location = "Server_Room_A"
        self.kpis = {...}  # Performance metrics
    
    def generate_data(self, packet_id):
        """
        Generate realistic IoT sensor data
        
        Returns:
        {
            'sensor_id': 'TEMP_SENSOR_001',
            'location': 'Server_Room_A',
            'temperature_celsius': 24.73,
            'humidity_percent': 55.42,
            'timestamp': 1735776234.567,
            'packet_number': 12,
            'alert': 'NORMAL'
        }
        """
        temperature = 20.0 + random(18-28°C range)
        humidity = 50.0 + random(30-70% range)
        
        sensor_data = {
            'sensor_id': self.sensor_id,
            'location': self.location,
            'temperature_celsius': round(temperature, 2),
            'humidity_percent': round(humidity, 2),
            'timestamp': current_time,
            'packet_number': packet_id,
            'alert': 'HIGH_TEMP' if temp > 26 else 'NORMAL'
        }
        
        return json.dumps(sensor_data).encode()
```

### Sample Output:

```
================================================================
PACKET 1/50
================================================================
[Application] IoT Sensor Data Generated:
  └─ Sensor: TEMP_SENSOR_001 at Server_Room_A
  └─ Temperature: 24.73°C
  └─ Humidity: 55.42%
  └─ Status: NORMAL
[Transport] Created packet #0 with checksum 54321
[Network] Added IP header: 192.168.1.1 -> 192.168.1.5
[DataLink] Created frame: 00:00:00:00:00:01 -> 00:00:00:00:00:04
[Physical] Converted to 8144 bits signal
[Physical] Transmitted through AWGN channel (SNR=15 dB)
[Physical] Frame received successfully (BER=0.000001)

✓ Packet 0 delivered successfully!
```

---

## REAL-WORLD APPLICATIONS

### Similar IoT Systems Using This Architecture:

1. **Smart Buildings**
   - HVAC control systems
   - Energy management
   - Fire detection systems

2. **Industrial IoT**
   - Manufacturing equipment monitoring
   - Warehouse environmental control
   - Cold chain logistics

3. **Healthcare**
   - Hospital temperature monitoring
   - Vaccine storage tracking
   - Medical equipment status

4. **Agriculture**
   - Greenhouse climate control
   - Soil moisture sensors
   - Livestock monitoring

5. **Smart Cities**
   - Air quality monitoring
   - Traffic sensors
   - Street lighting control

---

## 🔧 TECHNICAL SPECIFICATIONS

### Application Layer Details:

**Protocol:** Custom JSON-based IoT protocol  
**Port:** 8080 (Sensor) → 9090 (Server)  
**Data Format:** JSON  
**Encoding:** UTF-8  
**Packet Size:** 1024 bytes  
**Update Frequency:** Configurable (50 samples in simulation)  

### Sensor Specifications:

**Sensor ID:** TEMP_SENSOR_001  
**Location:** Server_Room_A  
**Temperature Range:** 18-28°C (operating)  
**Humidity Range:** 30-70%  
**Alert Threshold:** > 26°C (high temperature warning)  
**Accuracy:** ±0.5°C, ±2% humidity  

### Network Requirements:

**Minimum Bandwidth:** 0.5 Mbps (achieved: 0.82 Mbps ✓)  
**Maximum Latency:** 50 ms (achieved: 9.99 ms ✓)  
**Packet Loss Tolerance:** < 5% (achieved: 0% ✓)  
**Reliability:** 95%+ (achieved: 100% ✓)  

---

## 🚀 HOW TO RUN THE APPLICATION

### Prerequisites:
```bash
pip install numpy matplotlib scipy
```

### Running the Simulation:
```bash
python basic.py
```
