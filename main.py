import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple
import time
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class NetworkConfig:
    """Network configuration parameters"""
    num_nodes: int = 6
    packet_size: int = 1024  # bytes
    num_packets: int = 100
    snr_db: float = 20.0  # Signal-to-Noise Ratio in dB
    bandwidth: float = 10e6  # 10 MHz
    distance: float = 100.0  # meters between nodes

@dataclass
class LayerKPIs:
    """KPI tracking for each network layer"""
    layer_name: str
    packets_processed: int = 0
    errors: int = 0
    total_time: float = 0.0
    avg_time_per_packet: float = 0.0
    error_rate: float = 0.0
    
    def calculate(self):
        """Calculate derived metrics"""
        if self.packets_processed > 0:
            self.avg_time_per_packet = self.total_time / self.packets_processed
            self.error_rate = (self.errors / self.packets_processed) * 100
    
@dataclass
class NodeAddress:
    """Node addressing information"""
    node_id: int
    ip_address: str
    mac_address: str

@dataclass
class LinkState:
    """Link state information for network monitoring"""
    source_node: int
    dest_node: int
    bandwidth: float = 10e6  # bits/sec
    latency: float = 1.0     # ms
    packet_loss_rate: float = 0.0  # percentage
    is_active: bool = True
    
    def get_link_metric(self) -> float:
        """Calculate link cost metric (lower is better)"""
        if not self.is_active:
            return float('inf')
        return (self.latency * (1 + self.packet_loss_rate/100)) / (self.bandwidth / 1e6)
    
# ============================================================================
# LAYER 5: APPLICATION LAYER
# ============================================================================

class ApplicationLayer:
    """
    Application Layer - IoT Temperature Monitoring System
    
    This application simulates a real-world IoT sensor network that:
    - Monitors temperature from multiple sensor nodes
    - Generates periodic sensor readings
    - Sends data from sensor nodes to a central monitoring station
    - Measures network performance (KPIs)
    
    Use Case: Smart Building Climate Control System
    Node 1: Temperature Sensor in Server Room → Node 5: Central Monitoring Server
    """
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.kpis = {
            'throughput': 0.0,
            'latency': 0.0,
            'packet_loss': 0.0,
            'jitter': 0.0,
            'success_rate': 0.0
        }
        self.layer_kpi = LayerKPIs("Application Layer")
        self.sensor_id = "TEMP_SENSOR_001"
        self.location = "Server_Room_A"
        
    def generate_data(self, packet_id: int) -> bytes:
        """
        Generate IoT sensor data (Temperature readings)
        
        Simulates a real temperature sensor sending data to monitoring server:
        - Sensor ID and location
        - Temperature reading (realistic values between 18-28°C)
        - Humidity reading (30-70%)
        - Timestamp
        - Packet sequence number
        """
        import time
        
        # Generate realistic sensor data
        temperature = 20.0 + np.random.uniform(-2, 8)  # 18-28°C range
        humidity = 50.0 + np.random.uniform(-20, 20)    # 30-70% range
        timestamp = time.time()
        
        # Create IoT data packet in JSON-like format
        sensor_data = {
            'sensor_id': self.sensor_id,
            'location': self.location,
            'temperature_celsius': round(temperature, 2),
            'humidity_percent': round(humidity, 2),
            'timestamp': timestamp,
            'packet_number': packet_id,
            'alert': 'HIGH_TEMP' if temperature > 26 else 'NORMAL'
        }
        
        # Convert to string and pad to packet size
        data_str = json.dumps(sensor_data)
        padding_needed = self.config.packet_size - len(data_str)
        if padding_needed > 0:
            data_str += ' ' * padding_needed
        
        return data_str.encode()[:self.config.packet_size]
    
    def calculate_kpis(self, sent_packets: int, received_packets: int, 
                       latencies: List[float], start_time: float, end_time: float) -> dict:
        """Calculate Key Performance Indicators"""
        total_time = end_time - start_time
        
        # Throughput (Mbps)
        total_data = received_packets * self.config.packet_size * 8  # bits
        self.kpis['throughput'] = (total_data / total_time) / 1e6 if total_time > 0 else 0
        
        # Average Latency (ms)
        self.kpis['latency'] = np.mean(latencies) * 1000 if latencies else 0
        
        # Packet Loss Rate (%)
        self.kpis['packet_loss'] = ((sent_packets - received_packets) / sent_packets * 100) if sent_packets > 0 else 0
        
        # Jitter (ms) - variation in latency
        self.kpis['jitter'] = np.std(latencies) * 1000 if len(latencies) > 1 else 0
        
        # Success Rate (%)
        self.kpis['success_rate'] = (received_packets / sent_packets * 100) if sent_packets > 0 else 0
        
        return self.kpis
    
    def print_kpis(self):
        """Display KPI results"""
        print("\n" + "="*60)
        print("KEY PERFORMANCE INDICATORS (KPIs)")
        print("="*60)
        print(f"Throughput:        {self.kpis['throughput']:.2f} Mbps")
        print(f"Average Latency:   {self.kpis['latency']:.2f} ms")
        print(f"Packet Loss:       {self.kpis['packet_loss']:.2f} %")
        print(f"Jitter:            {self.kpis['jitter']:.2f} ms")
        print(f"Success Rate:      {self.kpis['success_rate']:.2f} %")
        print("="*60)

# ============================================================================
# LAYER 4: TRANSPORT LAYER
# ============================================================================

@dataclass
class TransportPacket:
    """Transport layer packet structure"""
    source_port: int
    dest_port: int
    sequence_num: int
    payload: bytes
    checksum: int
    timestamp: float
    flags: str = "ACK"  # ACK, SYN, FIN, RST
    window_size: int = 65535  # For flow control
    acknowledgment_num: int = 0  # For flow control
    fragment_id: int = 0  # For fragmentation
    fragment_offset: int = 0  # For fragmentation
    more_fragments: bool = False  # Fragment flag
    
class TransportLayer:
    """Transport Layer - Packet management, flow control, and fragmentation"""
    
    def __init__(self):
        self.source_port = 8080
        self.dest_port = 9090
        self.layer_kpi = LayerKPIs("Transport Layer")
        self.fragment_buffer = {}  # Store fragments for reassembly
        self.flow_control_window = 65535  # Sliding window size
        self.max_segment_size = 512  # MSS for fragmentation
        self.retransmission_timeout = 5.0  # seconds
        self.sent_segments = {}  # Track sent segments for retransmission
        self.ack_received = {}  # Track acknowledgments
        
    def create_packet(self, data: bytes, seq_num: int, flags: str = "ACK") -> List[TransportPacket]:
        """Create transport layer packet(s) with fragmentation support"""
        packets = []
        
        # Fragmentation if needed
        if len(data) > self.max_segment_size:
            packets = self._fragment_data(data, seq_num, flags)
            print(f"  [Transport] Fragmented into {len(packets)} segments (MSS={self.max_segment_size})")
        else:
            checksum = self._calculate_checksum(data)
            packet = TransportPacket(
                source_port=self.source_port,
                dest_port=self.dest_port,
                sequence_num=seq_num,
                payload=data,
                checksum=checksum,
                timestamp=time.time(),
                flags=flags,
                window_size=self.flow_control_window
            )
            packets.append(packet)
            print(f"  [Transport] Created packet #{seq_num} with checksum {checksum} (size: {len(data)} bytes)")
        
        # Store for potential retransmission
        for pkt in packets:
            self.sent_segments[pkt.sequence_num] = pkt
        
        return packets
    
    def _fragment_data(self, data: bytes, seq_num: int, flags: str) -> List[TransportPacket]:
        """Fragment data into multiple segments"""
        packets = []
        fragment_id = seq_num
        offset = 0
        
        while offset < len(data):
            chunk = data[offset:offset + self.max_segment_size]
            more_frags = (offset + self.max_segment_size) < len(data)
            
            packet = TransportPacket(
                source_port=self.source_port,
                dest_port=self.dest_port,
                sequence_num=seq_num + (offset // self.max_segment_size),
                payload=chunk,
                checksum=self._calculate_checksum(chunk),
                timestamp=time.time(),
                flags=flags,
                fragment_id=fragment_id,
                fragment_offset=offset,
                more_fragments=more_frags
            )
            packets.append(packet)
            offset += self.max_segment_size
        
        return packets
    
    def send_ack(self, seq_num: int) -> TransportPacket:
        """Send acknowledgment packet"""
        ack_packet = TransportPacket(
            source_port=self.dest_port,
            dest_port=self.source_port,
            sequence_num=0,
            acknowledgment_num=seq_num,
            payload=b'',
            checksum=0,
            timestamp=time.time(),
            flags="ACK"
        )
        return ack_packet
    
    def _calculate_checksum(self, data: bytes) -> int:
        """Simple checksum calculation"""
        return sum(data) % 65536
    
    def verify_packet(self, packet: TransportPacket) -> bool:
        """Verify packet integrity"""
        calculated = self._calculate_checksum(packet.payload)
        return calculated == packet.checksum

# ============================================================================
# LAYER 3: NETWORK LAYER
# ============================================================================

@dataclass
class NetworkPacket:
    """Network layer packet with addressing"""
    source_ip: str
    dest_ip: str
    ttl: int
    transport_packet: TransportPacket
    
class NetworkLayer:
    """Network Layer - Adds IP addressing, routing, QoS, and link management"""
    
    def __init__(self):
        self.routing_table = {
            1: [2, 4],  # Node 1 can reach nodes 2 and 4
            2: [1, 3],  # Node 2 can reach nodes 1 and 3
            3: [2, 5],  # Node 3 can reach nodes 2 and 5
            4: [1, 5],  # Node 4 can reach nodes 1 and 5
            5: [3, 4],  # Node 5 can reach nodes 3 and 4
            6: [1]      # Node 6 can reach node 1
        }
        self.layer_kpi = LayerKPIs("Network Layer")
        self.node_addresses = {
            1: NodeAddress(1, "192.168.1.1", "00:00:00:00:00:01"),
            2: NodeAddress(2, "192.168.1.2", "00:00:00:00:00:02"),
            3: NodeAddress(3, "192.168.1.3", "00:00:00:00:00:03"),
            4: NodeAddress(4, "192.168.1.4", "00:00:00:00:00:04"),
            5: NodeAddress(5, "192.168.1.5", "00:00:00:00:00:05"),
            6: NodeAddress(6, "192.168.1.6", "00:00:00:00:00:06"),
        }
        
        # QoS and link state features
        self.link_states = self._initialize_link_states()
        self.packet_queue = {}  # Priority queues per node
        self.congestion_level = {}  # Congestion metrics per node
        self.qos_config = {'priority': 0, 'bandwidth': 10e6, 'delay_tolerance': 100}  # ms
        
    def _initialize_link_states(self) -> dict:
        """Initialize link state information for all node pairs"""
        links = {}
        for src in range(1, 7):
            for dest in self.routing_table.get(src, []):
                link_key = (src, dest)
                links[link_key] = LinkState(src, dest)
        return links
    
    def get_link_state(self, src: int, dest: int) -> LinkState:
        """Get link state information"""
        return self.link_states.get((src, dest), None)
    
    def add_network_header(self, transport_packet: TransportPacket, 
                          source_node: int, dest_node: int, 
                          priority: int = 0) -> NetworkPacket:
        """Add network layer addressing with QoS support"""
        source_ip = self.node_addresses[source_node].ip_address
        dest_ip = self.node_addresses[dest_node].ip_address
        
        # Check congestion and apply QoS
        congestion = self._check_congestion(dest_node)
        
        packet = NetworkPacket(
            source_ip=source_ip,
            dest_ip=dest_ip,
            ttl=64,
            transport_packet=transport_packet
        )
        
        qos_indicator = f" [QoS: P{priority}]" if priority > 0 else ""
        congestion_indicator = f" [Congestion: {congestion:.0%}]" if congestion > 0.5 else ""
        print(f"  [Network] Added IP header: {source_ip} -> {dest_ip}{qos_indicator}{congestion_indicator}")
        return packet
    
    def _check_congestion(self, node_id: int) -> float:
        """Check congestion level at a node (0.0 to 1.0)"""
        if node_id not in self.congestion_level:
            self.congestion_level[node_id] = 0.0
        return self.congestion_level[node_id]
    
    def update_congestion(self, node_id: int, load: float):
        """Update congestion level at a node"""
        self.congestion_level[node_id] = min(1.0, max(0.0, load))
    
    def update_link_state(self, src: int, dest: int, latency: float, packet_loss: float):
        """Update link state with measured metrics"""
        link = self.get_link_state(src, dest)
        if link:
            link.latency = latency
            link.packet_loss_rate = packet_loss
    
    def find_path(self, source: int, dest: int, use_qos: bool = True) -> List[int]:
        """Find routing path using BFS or Dijkstra's algorithm for QoS-aware routing"""
        if source == dest:
            return [source]
        
        if use_qos:
            return self._find_qos_path(source, dest)
        else:
            return self._find_shortest_path(source, dest)
    
    def _find_shortest_path(self, source: int, dest: int) -> List[int]:
        """Find routing path using BFS (hop count)"""
        visited = set()
        queue = [(source, [source])]
        
        while queue:
            node, path = queue.pop(0)
            if node == dest:
                return path
            
            if node in visited:
                continue
            visited.add(node)
            
            for neighbor in self.routing_table.get(node, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path found
    
    def _find_qos_path(self, source: int, dest: int) -> List[int]:
        """Find routing path using Dijkstra's algorithm considering link quality"""
        import heapq
        
        distances = {node: float('inf') for node in range(1, 7)}
        distances[source] = 0
        previous = {}
        pq = [(0, source)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == dest:
                # Reconstruct path
                path = []
                node = dest
                while node in previous:
                    path.append(node)
                    node = previous[node]
                path.append(source)
                return path[::-1]
            
            for neighbor in self.routing_table.get(current, []):
                if neighbor not in visited:
                    link = self.get_link_state(current, neighbor)
                    if link:
                        edge_cost = link.get_link_metric()
                        new_dist = current_dist + edge_cost
                        
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            previous[neighbor] = current
                            heapq.heappush(pq, (new_dist, neighbor))
        
        return []  # No path found

# ============================================================================
# LAYER 2: DATA LINK LAYER
# ============================================================================

@dataclass
class Frame:
    """Data link layer frame"""
    source_mac: str
    dest_mac: str
    network_packet: NetworkPacket
    crc: int
    
class DataLinkLayer:
    """Data Link Layer - MAC management, switching, and error handling"""
    
    def __init__(self, network_layer: NetworkLayer):
        self.network_layer = network_layer
        self.layer_kpi = LayerKPIs("Data Link Layer")
        self.mac_address_table = {}  # MAC learning table (port, VLAN -> MAC)
        self.vlan_config = {}  # VLAN configuration
        self.collision_detect = 0  # CSMA/CD collision counter
        self.frame_buffer = {}  # Buffer for received frames
        self.retransmit_count = {}  # Track retransmissions
        self.max_retries = 3
        
    def create_frame(self, network_packet: NetworkPacket, 
                     source_node: int, dest_node: int, vlan_id: int = 0) -> Frame:
        """Create data link frame with VLAN and error handling support"""
        source_mac = self.network_layer.node_addresses[source_node].mac_address
        dest_mac = self.network_layer.node_addresses[dest_node].mac_address
        
        # MAC learning
        self._learn_mac(source_mac, source_node, vlan_id)
        
        # Calculate CRC
        crc = self._calculate_crc(network_packet)
        
        frame = Frame(
            source_mac=source_mac,
            dest_mac=dest_mac,
            network_packet=network_packet,
            crc=crc
        )
        
        vlan_info = f" [VLAN: {vlan_id}]" if vlan_id > 0 else ""
        print(f"  [DataLink] Created frame: {source_mac} -> {dest_mac}{vlan_info}")
        return frame
    
    def _learn_mac(self, mac_address: str, port: int, vlan_id: int = 0):
        """Learn MAC addresses for switching/bridging"""
        key = (mac_address, vlan_id)
        self.mac_address_table[key] = port
    
    def _calculate_crc(self, network_packet: NetworkPacket) -> int:
        """Calculate CRC checksum (32-bit polynomial)"""
        data = network_packet.transport_packet.payload
        # More realistic CRC using XOR operations
        crc = 0xFFFFFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xEDB88320
                else:
                    crc >>= 1
        return crc ^ 0xFFFFFFFF
    
    def verify_frame(self, frame: Frame) -> bool:
        """Verify frame integrity using CRC"""
        calculated_crc = self._calculate_crc(frame.network_packet)
        return calculated_crc == frame.crc
    
    def detect_collision(self, source_node: int) -> bool:
        """Simulate CSMA/CD collision detection"""
        collision_probability = np.random.random() < 0.05  # 5% collision chance
        if collision_probability:
            self.collision_detect += 1
            return True
        return False
    
    def get_mac_from_ip(self, ip_address: str) -> str:
        """ARP-like functionality to resolve IP to MAC"""
        for node_id, addr in self.network_layer.node_addresses.items():
            if addr.ip_address == ip_address:
                return addr.mac_address
        return "FF:FF:FF:FF:FF:FF"  # Broadcast MAC

# ============================================================================
# LAYER 1: PHYSICAL LAYER
# ============================================================================

class PhysicalLayer:
    """Physical Layer - Converts to signals and simulates AWGN channel"""
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.layer_kpi = LayerKPIs("Physical Layer")
        self.ber_values = []  # Track BER for each transmission
        
    def frame_to_signal(self, frame: Frame) -> np.ndarray:
        """Convert frame to physical signal (bits)"""
        # Convert frame data to binary
        data = frame.network_packet.transport_packet.payload
        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        
        # BPSK modulation: 0 -> -1, 1 -> 1
        signal = 2 * bits - 1
        print(f"  [Physical] Converted to {len(signal)} bits signal")
        return signal.astype(float)
    
    def transmit_through_awgn(self, signal: np.ndarray) -> np.ndarray:
        """Simulate AWGN (Additive White Gaussian Noise) channel"""
        # Calculate noise power from SNR
        signal_power = np.mean(signal ** 2)
        snr_linear = 10 ** (self.config.snr_db / 10)
        noise_power = signal_power / snr_linear
        
        # Add Gaussian noise
        noise = np.sqrt(noise_power) * np.random.randn(len(signal))
        received_signal = signal + noise
        
        print(f"  [Physical] Transmitted through AWGN channel (SNR={self.config.snr_db} dB)")
        return received_signal
    
    def signal_to_frame(self, received_signal: np.ndarray, original_frame: Frame) -> Tuple[Frame, bool]:
        """Demodulate signal back to frame"""
        # BPSK demodulation
        bits = (received_signal > 0).astype(np.uint8)
        
        # Convert bits back to bytes
        num_bytes = len(bits) // 8
        byte_data = np.packbits(bits[:num_bytes * 8])
        
        # Reconstruct frame (simplified - reuse structure)
        success = True
        
        # Simulate bit errors based on noise
        ber = self._calculate_ber(received_signal)
        if np.random.random() < ber * 100:  # Probabilistic error
            success = False
            print(f"  [Physical] Frame corrupted (BER={ber:.6f})")
        else:
            print(f"  [Physical] Frame received successfully (BER={ber:.6f})")
        
        return original_frame, success
    
    def _calculate_ber(self, received_signal: np.ndarray) -> float:
        """Calculate Bit Error Rate"""
        snr_linear = 10 ** (self.config.snr_db / 10)
        # BER for BPSK in AWGN
        from scipy.special import erfc
        ber = 0.5 * erfc(np.sqrt(snr_linear))
        self.ber_values.append(ber)
        return ber

# ============================================================================
# MAIN NETWORK SIMULATOR
# ============================================================================

class NetworkSimulator:
    """Main network simulator orchestrating all layers"""
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.app_layer = ApplicationLayer(config)
        self.transport_layer = TransportLayer()
        self.network_layer = NetworkLayer()
        self.datalink_layer = DataLinkLayer(self.network_layer)
        self.physical_layer = PhysicalLayer(config)
        
        self.sent_packets = 0
        self.received_packets = 0
        self.latencies = []
        self.layer_kpis = []  # Collect all layer KPIs
        
    def simulate_transmission(self, source_node: int, dest_node: int):
        """Simulate complete network transmission"""
        print("\n" + "="*60)
        print(f"STARTING IoT SENSOR TRANSMISSION")
        print(f"Temperature Sensor (Node {source_node}) → Monitoring Server (Node {dest_node})")
        print("="*60)
        
        # Find routing path
        path = self.network_layer.find_path(source_node, dest_node)
        print(f"\n[Routing] Path selected: {' -> '.join(map(str, path))}")
        
        if not path:
            print("ERROR: No path found!")
            return
        
        start_time = time.time()
        
        # Transmit multiple packets
        for packet_id in range(self.config.num_packets):
            print(f"\n{'─'*60}")
            print(f"PACKET {packet_id + 1}/{self.config.num_packets}")
            print(f"{'─'*60}")
            
            packet_start = time.time()
            
            # Step 1: Application Layer - Generate IoT sensor data
            app_start = time.time()
            data = self.app_layer.generate_data(packet_id)
            self.app_layer.layer_kpi.packets_processed += 1
            self.app_layer.layer_kpi.total_time += time.time() - app_start
            
            # Display the sensor reading
            try:
                sensor_reading = json.loads(data.decode().strip())
                print(f"[Application] IoT Sensor Data Generated:")
                print(f"  └─ Sensor: {sensor_reading['sensor_id']} at {sensor_reading['location']}")
                print(f"  └─ Temperature: {sensor_reading['temperature_celsius']}°C")
                print(f"  └─ Humidity: {sensor_reading['humidity_percent']}%")
                print(f"  └─ Status: {sensor_reading['alert']}")
            except:
                print(f"[Application] Generated {len(data)} bytes of sensor data")
            
            # Step 2: Transport Layer - Create packet(s) with fragmentation support
            transport_start = time.time()
            transport_packets = self.transport_layer.create_packet(data, packet_id)
            self.transport_layer.layer_kpi.packets_processed += len(transport_packets)
            self.transport_layer.layer_kpi.total_time += time.time() - transport_start
            
            # Process each transport packet/fragment
            for transport_packet in transport_packets:
                
                # Step 3 & 4: Network Layer - Add addressing and select path
                network_start = time.time()
                network_packet = self.network_layer.add_network_header(
                    transport_packet, source_node, dest_node
                )
                self.network_layer.layer_kpi.packets_processed += 1
                self.network_layer.layer_kpi.total_time += time.time() - network_start
                
                # Simulate transmission through each hop in path
                success = True
                for i in range(len(path) - 1):
                    current_node = path[i]
                    next_node = path[i + 1]
                    
                    print(f"\n  Hop {i+1}: Node {current_node} -> Node {next_node}")
                    
                    # Step 5: Data Link Layer - Create frame
                    datalink_start = time.time()
                    frame = self.datalink_layer.create_frame(
                        network_packet, current_node, next_node
                    )
                    self.datalink_layer.layer_kpi.packets_processed += 1
                    self.datalink_layer.layer_kpi.total_time += time.time() - datalink_start
                    
                    # Step 6: Physical Layer - Convert to signal
                    physical_start = time.time()
                    signal = self.physical_layer.frame_to_signal(frame)
                    
                    # Step 7: Transmit through AWGN channel
                    received_signal = self.physical_layer.transmit_through_awgn(signal)
                    
                    # Step 8: Receive and demodulate
                    received_frame, hop_success = self.physical_layer.signal_to_frame(
                        received_signal, frame
                    )
                    self.physical_layer.layer_kpi.packets_processed += 1
                    self.physical_layer.layer_kpi.total_time += time.time() - physical_start
                    
                    if not hop_success:
                        self.physical_layer.layer_kpi.errors += 1
                    
                    if not hop_success:
                        success = False
                        break
                    
                    # Verify frame
                    if not self.datalink_layer.verify_frame(received_frame):
                        self.datalink_layer.layer_kpi.errors += 1
                        success = False
                        print(f"  [DataLink] CRC check failed!")
                        break
                
                if not success:
                    break
            
            if success:
                self.received_packets += 1
                packet_latency = time.time() - packet_start
                self.latencies.append(packet_latency)
                print(f"\n✓ Packet {packet_id} delivered successfully!")
            else:
                print(f"\n✗ Packet {packet_id} lost during transmission")
        
        end_time = time.time()
        
        # Calculate and display KPIs
        self.app_layer.calculate_kpis(
            self.sent_packets, self.received_packets, 
            self.latencies, start_time, end_time
        )
        self.app_layer.print_kpis()
        
        # Calculate and print layer-specific KPIs
        self.print_layer_kpis()
        
    def print_layer_kpis(self):
        """Print KPIs for each network layer"""
        print("\n" + "="*60)
        print("LAYER-SPECIFIC KEY PERFORMANCE INDICATORS")
        print("="*60)
        
        layers = [
            self.app_layer.layer_kpi,
            self.transport_layer.layer_kpi,
            self.network_layer.layer_kpi,
            self.datalink_layer.layer_kpi,
            self.physical_layer.layer_kpi
        ]
        
        for layer_kpi in layers:
            layer_kpi.calculate()
            print(f"\n[{layer_kpi.layer_name}]")
            print(f"  Packets Processed:      {layer_kpi.packets_processed}")
            print(f"  Errors:                 {layer_kpi.errors}")
            print(f"  Error Rate:             {layer_kpi.error_rate:.2f}%")
            print(f"  Total Time:             {layer_kpi.total_time*1000:.2f} ms")
            print(f"  Avg Time per Packet:    {layer_kpi.avg_time_per_packet*1000:.4f} ms")
        
        # Additional Physical Layer metrics
        if self.physical_layer.ber_values:
            avg_ber = np.mean(self.physical_layer.ber_values)
            print(f"\n[Physical Layer - Advanced Metrics]")
            print(f"  Average BER:            {avg_ber:.6e}")
            print(f"  BER Range:              {np.min(self.physical_layer.ber_values):.6e} to {np.max(self.physical_layer.ber_values):.6e}")
            print(f"  SNR (dB):               {self.config.snr_db}")
        
        print("\n" + "="*60)
        
    def plot_results(self):
        """Visualize simulation results"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Network Protocol Simulation - KPI Analysis', fontsize=16, fontweight='bold')
        
        kpis = self.app_layer.kpis
        
        # Plot 1: Packet Statistics
        ax1 = axes[0, 0]
        categories = ['Sent', 'Received', 'Lost']
        values = [self.sent_packets, self.received_packets, 
                 self.sent_packets - self.received_packets]
        colors = ['#2ecc71', '#3498db', '#e74c3c']
        ax1.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Number of Packets')
        ax1.set_title('Packet Transmission Statistics')
        ax1.grid(axis='y', alpha=0.3)
        
        # Plot 2: Latency Distribution
        ax2 = axes[0, 1]
        if self.latencies:
            ax2.hist(np.array(self.latencies) * 1000, bins=20, color='#9b59b6', 
                    alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Latency (ms)')
            ax2.set_ylabel('Frequency')
            ax2.set_title(f'Latency Distribution (Avg: {kpis["latency"]:.2f} ms)')
            ax2.grid(axis='y', alpha=0.3)
        
        # Plot 3: KPI Summary
        ax3 = axes[1, 0]
        kpi_names = ['Throughput\n(Mbps)', 'Latency\n(ms)', 'Packet Loss\n(%)', 
                     'Jitter\n(ms)', 'Success Rate\n(%)']
        kpi_values = [kpis['throughput'], kpis['latency'], kpis['packet_loss'], 
                     kpis['jitter'], kpis['success_rate']]
        colors = ['#1abc9c', '#f39c12', '#e74c3c', '#34495e', '#2ecc71']
        
        bars = ax3.barh(kpi_names, kpi_values, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Value')
        ax3.set_title('Key Performance Indicators')
        ax3.grid(axis='x', alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, kpi_values):
            ax3.text(value, bar.get_y() + bar.get_height()/2, f'{value:.2f}', 
                    ha='left', va='center', fontweight='bold')
        
        # Plot 4: Success Rate Pie Chart
        ax4 = axes[1, 1]
        success_count = self.received_packets
        failed_count = self.sent_packets - self.received_packets
        
        # Ensure we have valid data for pie chart
        if success_count > 0 or failed_count > 0:
            success_data = [max(1, success_count), max(1, failed_count)]
            labels = [f'Success\n({kpis["success_rate"]:.1f}%)', 
                     f'Failed\n({100-kpis["success_rate"]:.1f}%)']
            colors = ['#2ecc71', '#e74c3c']
            ax4.pie(success_data, labels=labels, colors=colors, autopct='%d', 
                   startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
            ax4.set_title('Transmission Success Rate')
        else:
            ax4.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)
            ax4.set_title('Transmission Success Rate')
        
        plt.tight_layout()
        plt.savefig('./simulation_results.png', dpi=300, bbox_inches='tight')
        print("\n[Visualization] Results saved to 'simulation_results.png'")
        plt.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print(" NETWORK PROTOCOL SIMULATION - JoMaRe ASSIGNMENT")
    print(" IoT Temperature Monitoring System")
    print(" DOS to KPI Improvement Implementation")
    print("="*60)
    print("\n📡 APPLICATION: IoT Temperature Sensor Network")
    print("   Sensor Node (1) → Central Server (5)")
    print("   Monitoring: Server Room Temperature & Humidity")
    print("="*60)
    
    # Configuration
    config = NetworkConfig(
        num_nodes=6,
        packet_size=1024,
        num_packets=50,  # Simulate 50 sensor readings
        snr_db=15.0,     # Signal-to-Noise Ratio
        bandwidth=10e6,
        distance=100.0
    )
    
    # Create simulator
    simulator = NetworkSimulator(config)
    
    # Run simulation from Node 1 to Node 5 (as per diagram)
    simulator.simulate_transmission(source_node=1, dest_node=5)
    
    # Visualize results
    simulator.plot_results()
    
    print("\n" + "="*60)
    print(" SIMULATION COMPLETED SUCCESSFULLY")
    print("="*60)
    print("\nFiles generated:")
    print("  - simulation_results.png (visualization)")
    print("\nLast date: 1/5/26 ✓")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()