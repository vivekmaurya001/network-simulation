# Network Protocol Simulation

## 📋 ASSIGNMENT OVERVIEW

**Course:** Computer Networks  
**Topic:** 5-Layer Network Protocol Implementation  
**Objective:** Simulate data transmission through network layers and measure KPIs  

---

## 🎯 WHAT WAS IMPLEMENTED

This simulation implements a complete network protocol stack with **5 layers** (Application, Transport, Network, Data Link, Physical) that transmits data from **Node 1 to Node 5** through a network topology.

### Network Topology
```
    [1] ←→ [2] ←→ [3]
     ↓              ↓
    [4] ←——————→ [5]
     
    [6] ←→ [1]
```

**Selected Path:** Node 1 → Node 4 → Node 5

---

## 📊 SIMULATION RESULTS

### Key Performance Indicators (KPIs)

| Metric | Value | Status |
|--------|-------|--------|
| **Throughput** | 0.82 Mbps | ✅ Good |
| **Average Latency** | 9.99 ms | ✅ Excellent |
| **Packet Loss** | 0.00% | ✅ Perfect |
| **Jitter** | 61.04 ms | ⚠️ Moderate |
| **Success Rate** | 100.00% | ✅ Perfect |

### Transmission Statistics
- **Total Packets Sent:** 50
- **Packets Received:** 50
- **Packets Lost:** 0
- **Success Rate:** 100%

---

## 🔧 IMPLEMENTATION DETAILS

### Step 1: Application Layer
**Function:** Generate data and measure KPIs

**What it does:**
- Generates application-level data packets
- Calculates final KPIs: Throughput, Latency, Packet Loss, Jitter, Success Rate
- Measures end-to-end performance

**Code Implementation:**
```python
class ApplicationLayer:
    def generate_data(self, packet_id: int) -> bytes
    def calculate_kpis(self, sent, received, latencies, start, end) -> dict
```

---

### Step 2: Transport Layer
**Function:** Create packets with transport headers

**What it does:**
- Breaks data into manageable packets
- Adds source/destination port numbers
- Adds sequence numbers for ordering
- Calculates checksum for error detection

**Packet Structure:**
```
[Source Port | Dest Port | Sequence # | Checksum | Payload]
   (8080)       (9090)       (0-49)                (1024 bytes)
```

**Code Implementation:**
```python
class TransportLayer:
    def create_packet(self, data: bytes, seq_num: int) -> TransportPacket
    def verify_packet(self, packet: TransportPacket) -> bool
```

---

### Step 3: Network Layer
**Function:** Add IP addressing and routing

**What it does:**
- Assigns IP addresses to each node
- Implements routing algorithm (BFS - Breadth-First Search)
- Finds shortest path from source to destination
- Adds IP headers with source/destination IPs

**IP Address Mapping:**
- Node 1: 192.168.1.1
- Node 2: 192.168.1.2
- Node 3: 192.168.1.3
- Node 4: 192.168.1.4
- Node 5: 192.168.1.5
- Node 6: 192.168.1.6

**Code Implementation:**
```python
class NetworkLayer:
    def add_network_header(self, transport_packet, source, dest) -> NetworkPacket
    def find_path(self, source: int, dest: int) -> List[int]
```

---

### Step 4: Routing (Path Selection)
**Selected Path:** 1 → 4 → 5

**Why this path?**
- Shortest path: Only 2 hops
- Alternative path (1→2→3→5) would be 3 hops
- Lower latency with fewer intermediate nodes

---

### Step 5: Data Link Layer
**Function:** Convert packets to frames with MAC addressing

**What it does:**
- Adds MAC (hardware) addresses to packets
- Converts packets into frames
- Adds CRC (Cyclic Redundancy Check) for error detection
- Verifies frame integrity at receiver

**Frame Structure:**
```
[Source MAC | Dest MAC | Network Packet | CRC Checksum]
```

**MAC Address Mapping:**
- Node 1: 00:00:00:00:00:01
- Node 4: 00:00:00:00:00:04
- Node 5: 00:00:00:00:00:05

**Code Implementation:**
```python
class DataLinkLayer:
    def create_frame(self, network_packet, source, dest) -> Frame
    def verify_frame(self, frame: Frame) -> bool
```

---

### Step 6: Physical Layer (Signal Conversion)
**Function:** Convert frames to physical signals

**What it does:**
- Converts digital frames to binary bits
- Uses BPSK (Binary Phase Shift Keying) modulation
- Converts: 0 → -1, 1 → +1
- Prepares signal for transmission

**Code Implementation:**
```python
def frame_to_signal(self, frame: Frame) -> np.ndarray:
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    signal = 2 * bits - 1  # BPSK modulation
```

---

### Step 7: AWGN Channel (Transmission)
**Function:** Simulate real-world wireless channel

**What it does:**
- Simulates Additive White Gaussian Noise (AWGN) channel
- Adds random noise to transmitted signal
- Models real-world interference and signal degradation
- Uses SNR (Signal-to-Noise Ratio) = 15 dB

**AWGN Formula:**
```
Received_Signal = Transmitted_Signal + Gaussian_Noise
```

**Bit Error Rate (BER) Calculation:**
```python
BER = 0.5 × erfc(√SNR)
```

For SNR = 15 dB, BER ≈ 0.000000 (extremely low)

**Code Implementation:**
```python
def transmit_through_awgn(self, signal: np.ndarray) -> np.ndarray:
    noise = np.sqrt(noise_power) * np.random.randn(len(signal))
    received_signal = signal + noise
```

---

### Step 8: Receiver Processing
**Function:** Demodulate and verify at receiver (Node 5)

**What it does:**
- Demodulates received signal back to bits
- Reconstructs frames from bits
- Verifies frame integrity using CRC
- Verifies packet integrity using checksum
- Calculates KPIs for performance evaluation

**Reverse Processing:**
```
Physical Signal → Bits → Frame → Packet → Data
```

---

## 📈 PERFORMANCE ANALYSIS

### Throughput Analysis
- **Achieved:** 0.82 Mbps
- **Explanation:** Good data rate for 1024-byte packets over 2 hops
- **Calculation:** (50 packets × 1024 bytes × 8 bits) / total_time

### Latency Analysis
- **Achieved:** 9.99 ms average
- **Explanation:** Excellent low latency
- **Factors:** 2 hops, processing time at each layer

### Packet Loss Analysis
- **Achieved:** 0.00% loss
- **Explanation:** Perfect transmission with good SNR (15 dB)
- **Reason:** AWGN noise is low, error detection mechanisms work well

### Jitter Analysis
- **Achieved:** 61.04 ms
- **Explanation:** Moderate variation in packet delivery times
- **Cause:** Processing variations, queue delays at intermediate nodes

---

## 🎨 VISUALIZATION

The simulation generates 4 graphs:

1. **Packet Transmission Statistics**
   - Bar chart showing Sent/Received/Lost packets

2. **Latency Distribution**
   - Histogram showing distribution of packet latencies

3. **KPI Summary**
   - Horizontal bar chart of all KPIs

4. **Success Rate Pie Chart**
   - Visual representation of transmission success

---

## 🚀 HOW TO RUN THE CODE

### Requirements
```bash
pip install numpy matplotlib scipy
```

### Execution
```bash
python network_protocol_simulation.py
```

### Expected Output
1. Detailed console output showing each packet's journey
2. KPI results displayed in terminal
3. PNG visualization file: `simulation_results.png`

---

## 🔄 CUSTOMIZATION OPTIONS

You can modify these parameters in the code:

```python
config = NetworkConfig(
    num_nodes=6,          # Number of nodes in network
    packet_size=1024,     # Size of each packet (bytes)
    num_packets=50,       # Number of packets to send
    snr_db=15.0,          # Signal-to-Noise Ratio (higher = less noise)
    bandwidth=10e6,       # Channel bandwidth (Hz)
    distance=100.0        # Distance between nodes (meters)
)
```

## 🔍 DETAILED PACKET JOURNEY EXAMPLE

**Packet #1 Journey (Node 1 → Node 5):**

```
Step 1: Application generates 1024 bytes
        ↓
Step 2: Transport adds header [Port 8080→9090, Seq#0, Checksum]
        ↓
Step 3: Network adds [IP: 192.168.1.1 → 192.168.1.5]
        ↓
Step 4: Routing selects path [1→4→5]
        ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOP 1: Node 1 → Node 4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 5: DataLink creates frame [MAC: 01→04, CRC]
        ↓
Step 6: Physical converts to 8144 bits BPSK signal
        ↓
Step 7: Transmit through AWGN channel (SNR=15dB)
        ↓ (noise added: signal + gaussian_noise)
Step 8: Receive signal, demodulate to bits
        ↓
        Verify CRC ✓
        ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOP 2: Node 4 → Node 5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 5: DataLink creates frame [MAC: 04→05, CRC]
        ↓
Step 6: Physical converts to 8144 bits BPSK signal
        ↓
Step 7: Transmit through AWGN channel (SNR=15dB)
        ↓ (noise added: signal + gaussian_noise)
Step 8: Receive signal, demodulate to bits
        ↓
        Verify CRC ✓
        ↓
        Verify Transport Checksum ✓
        ↓
        Packet delivered successfully! ✓
```

**Total time for Packet #1:** ~9.99 ms

---