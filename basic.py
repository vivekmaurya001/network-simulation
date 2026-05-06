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
    num_packets: int = 50
    snr_db: float = 15.0  # Signal-to-Noise Ratio in dB
    bandwidth: float = 10e6  # 10 MHz
    distance: float = 100.0  # meters between nodes
    
@dataclass
class NodeAddress:
    """Node addressing information"""
    node_id: int
    ip_address: str
    mac_address: str

# ============================================================================
# PER-LAYER METRICS TRACKING
# ============================================================================

class LayerMetrics:
    """Track KPI and QoS metrics for each network layer"""
    
    def __init__(self, layer_name: str):
        self.layer_name = layer_name
        self.processing_times = []
        self.success_count = 0
        self.failure_count = 0
        self.total_bytes_in = 0
        self.total_bytes_out = 0
        self.errors_detected = 0
        self.errors_corrected = 0
        self.start_time = 0
        self.total_time = 0
        
    def record_operation(self, processing_time: float, success: bool, bytes_in: int, bytes_out: int, errors: int = 0):
        """Record a single operation"""
        self.processing_times.append(processing_time)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.total_bytes_in += bytes_in
        self.total_bytes_out += bytes_out
        self.errors_detected += errors
        
    def start_timer(self):
        """Start timing for cumulative operations"""
        self.start_time = time.time()
        
    def stop_timer(self):
        """Stop timing"""
        self.total_time = time.time() - self.start_time
        
    # KPI Calculations
    def get_throughput_mbps(self) -> float:
        """Calculate throughput in Mbps"""
        if self.total_time > 0:
            return (self.total_bytes_out * 8) / (self.total_time * 1e6)
        return 0.0
    
    def get_avg_processing_time_ms(self) -> float:
        """Average processing time in milliseconds"""
        if self.processing_times:
            return np.mean(self.processing_times) * 1000
        return 0.0
    
    def get_success_rate(self) -> float:
        """Success rate percentage"""
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 100.0
    
    def get_error_rate(self) -> float:
        """Error detection rate percentage"""
        total = self.success_count + self.failure_count
        return (self.errors_detected / total * 100) if total > 0 else 0.0
    
    def get_overhead_percentage(self) -> float:
        """Protocol overhead percentage"""
        if self.total_bytes_in > 0:
            overhead = self.total_bytes_out - self.total_bytes_in
            return (overhead / self.total_bytes_in * 100) if overhead > 0 else 0.0
        return 0.0
    
    # QoS Calculations
    def get_qos_reliability(self) -> float:
        """QoS Reliability (0-100)"""
        return self.get_success_rate()
    
    def get_qos_efficiency(self) -> float:
        """QoS Efficiency - how well layer performs without overhead"""
        overhead = self.get_overhead_percentage()
        error_rate = self.get_error_rate()
        return max(0, 100 - overhead - error_rate)
    
    def get_qos_performance(self) -> float:
        """QoS Performance based on processing speed"""
        avg_time = self.get_avg_processing_time_ms()
        # Lower processing time = better performance
        # Normalize: <1ms=100, >100ms=0
        if avg_time < 1:
            return 100.0
        elif avg_time > 100:
            return 0.0
        else:
            return 100 - avg_time
    
    def get_qos_overall(self) -> float:
        """Overall QoS score (weighted average)"""
        reliability = self.get_qos_reliability() * 0.4
        efficiency = self.get_qos_efficiency() * 0.3
        performance = self.get_qos_performance() * 0.3
        return reliability + efficiency + performance
    
    def get_all_metrics(self) -> dict:
        """Get all KPI and QoS metrics"""
        return {
            'layer_name': self.layer_name,
            'kpi': {
                'throughput_mbps': round(self.get_throughput_mbps(), 3),
                'avg_processing_time_ms': round(self.get_avg_processing_time_ms(), 3),
                'success_rate_percent': round(self.get_success_rate(), 2),
                'error_rate_percent': round(self.get_error_rate(), 2),
                'overhead_percent': round(self.get_overhead_percentage(), 2),
                'total_operations': self.success_count + self.failure_count,
                'successful_operations': self.success_count,
                'failed_operations': self.failure_count,
                'bytes_processed': self.total_bytes_out
            },
            'qos': {
                'reliability': round(self.get_qos_reliability(), 2),
                'efficiency': round(self.get_qos_efficiency(), 2),
                'performance': round(self.get_qos_performance(), 2),
                'overall_score': round(self.get_qos_overall(), 2)
            }
        }

# ============================================================================
# LAYER 5: APPLICATION LAYER
# ============================================================================

class ApplicationLayer:
    """
    Application Layer - IoT Temperature Monitoring System
    """
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.metrics = LayerMetrics("Application Layer")
        self.sensor_id = "TEMP_SENSOR_001"
        self.location = "Server_Room_A"
        self.kpis = {
            'throughput': 0.0,
            'latency': 0.0,
            'packet_loss': 0.0,
            'jitter': 0.0,
            'success_rate': 0.0
        }
        
    def generate_data(self, packet_id: int) -> bytes:
        """Generate IoT sensor data with timing"""
        start_time = time.time()
        
        # Generate realistic sensor data
        temperature = 20.0 + np.random.uniform(-2, 8)
        humidity = 50.0 + np.random.uniform(-20, 20)
        timestamp = time.time()
        
        sensor_data = {
            'sensor_id': self.sensor_id,
            'location': self.location,
            'temperature_celsius': round(temperature, 2),
            'humidity_percent': round(humidity, 2),
            'timestamp': timestamp,
            'packet_number': packet_id,
            'alert': 'HIGH_TEMP' if temperature > 26 else 'NORMAL'
        }
        
        data_str = json.dumps(sensor_data)
        padding_needed = self.config.packet_size - len(data_str)
        if padding_needed > 0:
            data_str += ' ' * padding_needed
        
        data_bytes = data_str.encode()[:self.config.packet_size]
        
        # Record metrics
        processing_time = time.time() - start_time
        self.metrics.record_operation(processing_time, True, 0, len(data_bytes), 0)
        
        return data_bytes
    
    def calculate_kpis(self, sent_packets: int, received_packets: int, 
                       latencies: List[float], start_time: float, end_time: float) -> dict:
        """Calculate Key Performance Indicators"""
        total_time = end_time - start_time
        
        self.kpis['throughput'] = (received_packets * self.config.packet_size * 8 / total_time) / 1e6 if total_time > 0 else 0
        self.kpis['latency'] = np.mean(latencies) * 1000 if latencies else 0
        self.kpis['packet_loss'] = ((sent_packets - received_packets) / sent_packets * 100) if sent_packets > 0 else 0
        self.kpis['jitter'] = np.std(latencies) * 1000 if len(latencies) > 1 else 0
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
    
class TransportLayer:
    """Transport Layer - Creates packets with headers"""
    
    def __init__(self):
        self.source_port = 8080
        self.dest_port = 9090
        self.metrics = LayerMetrics("Transport Layer")
        
    def create_packet(self, data: bytes, seq_num: int) -> TransportPacket:
        """Create transport layer packet"""
        start_time = time.time()
        
        checksum = self._calculate_checksum(data)
        packet = TransportPacket(
            source_port=self.source_port,
            dest_port=self.dest_port,
            sequence_num=seq_num,
            payload=data,
            checksum=checksum,
            timestamp=time.time()
        )
        
        # Calculate overhead (header size)
        header_size = 24  # ports(4) + seq(4) + checksum(4) + timestamp(8) + other(4)
        
        processing_time = time.time() - start_time
        self.metrics.record_operation(processing_time, True, len(data), len(data) + header_size, 0)
        
        print(f"  [Transport] Created packet #{seq_num} with checksum {checksum}")
        return packet
    
    def _calculate_checksum(self, data: bytes) -> int:
        """Simple checksum calculation"""
        return sum(data) % 65536
    
    def verify_packet(self, packet: TransportPacket) -> bool:
        """Verify packet integrity"""
        start_time = time.time()
        calculated = self._calculate_checksum(packet.payload)
        success = calculated == packet.checksum
        
        processing_time = time.time() - start_time
        errors = 0 if success else 1
        self.metrics.record_operation(processing_time, success, len(packet.payload), len(packet.payload), errors)
        
        return success

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
    """Network Layer - Adds IP addressing and routing"""
    
    def __init__(self):
        self.metrics = LayerMetrics("Network Layer")
        self.routing_table = {
            1: [2, 4],
            2: [1, 3],
            3: [2, 5],
            4: [1, 5],
            5: [3, 4],
            6: [1]
        }
        self.node_addresses = {
            1: NodeAddress(1, "192.168.1.1", "00:00:00:00:00:01"),
            2: NodeAddress(2, "192.168.1.2", "00:00:00:00:00:02"),
            3: NodeAddress(3, "192.168.1.3", "00:00:00:00:00:03"),
            4: NodeAddress(4, "192.168.1.4", "00:00:00:00:00:04"),
            5: NodeAddress(5, "192.168.1.5", "00:00:00:00:00:05"),
            6: NodeAddress(6, "192.168.1.6", "00:00:00:00:00:06"),
        }
    
    def add_network_header(self, transport_packet: TransportPacket, 
                          source_node: int, dest_node: int) -> NetworkPacket:
        """Add network layer addressing"""
        start_time = time.time()
        
        source_ip = self.node_addresses[source_node].ip_address
        dest_ip = self.node_addresses[dest_node].ip_address
        
        packet = NetworkPacket(
            source_ip=source_ip,
            dest_ip=dest_ip,
            ttl=64,
            transport_packet=transport_packet
        )
        
        # IP header size
        header_size = 20  # Standard IP header
        payload_size = len(transport_packet.payload)
        
        processing_time = time.time() - start_time
        self.metrics.record_operation(processing_time, True, payload_size, payload_size + header_size, 0)
        
        print(f"  [Network] Added IP header: {source_ip} -> {dest_ip}")
        return packet
    
    def find_path(self, source: int, dest: int) -> List[int]:
        """Find routing path using BFS"""
        start_time = time.time()
        
        if source == dest:
            return [source]
        
        visited = set()
        queue = [(source, [source])]
        
        while queue:
            node, path = queue.pop(0)
            if node == dest:
                processing_time = time.time() - start_time
                self.metrics.record_operation(processing_time, True, 0, 0, 0)
                return path
            
            if node in visited:
                continue
            visited.add(node)
            
            for neighbor in self.routing_table.get(node, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        processing_time = time.time() - start_time
        self.metrics.record_operation(processing_time, False, 0, 0, 1)
        return []

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
    """Data Link Layer - Creates frames with MAC addresses"""
    
    def __init__(self, network_layer: NetworkLayer):
        self.network_layer = network_layer
        self.metrics = LayerMetrics("Data Link Layer")
        
    def create_frame(self, network_packet: NetworkPacket, 
                     source_node: int, dest_node: int) -> Frame:
        """Create data link frame (packet to frame conversion)"""
        start_time = time.time()
        
        source_mac = self.network_layer.node_addresses[source_node].mac_address
        dest_mac = self.network_layer.node_addresses[dest_node].mac_address
        
        crc = self._calculate_crc(network_packet)
        
        frame = Frame(
            source_mac=source_mac,
            dest_mac=dest_mac,
            network_packet=network_packet,
            crc=crc
        )
        
        # Frame header size
        header_size = 18  # MAC addresses (12) + CRC (4) + control (2)
        payload_size = len(network_packet.transport_packet.payload)
        
        processing_time = time.time() - start_time
        self.metrics.record_operation(processing_time, True, payload_size, payload_size + header_size, 0)
        
        print(f"  [DataLink] Created frame: {source_mac} -> {dest_mac}")
        return frame
    
    def _calculate_crc(self, network_packet: NetworkPacket) -> int:
        """Calculate CRC checksum"""
        data = network_packet.transport_packet.payload
        return sum(data) % 2**16
    
    def verify_frame(self, frame: Frame) -> bool:
        """Verify frame integrity"""
        start_time = time.time()
        calculated_crc = self._calculate_crc(frame.network_packet)
        success = calculated_crc == frame.crc
        
        processing_time = time.time() - start_time
        errors = 0 if success else 1
        payload_size = len(frame.network_packet.transport_packet.payload)
        self.metrics.record_operation(processing_time, success, payload_size, payload_size, errors)
        
        return success

# ============================================================================
# LAYER 1: PHYSICAL LAYER
# ============================================================================

class PhysicalLayer:
    """Physical Layer - Converts to signals and simulates AWGN channel"""
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        self.metrics = LayerMetrics("Physical Layer")
        self.ber_values = []
        
    def frame_to_signal(self, frame: Frame) -> np.ndarray:
        """Convert frame to physical signal (bits)"""
        start_time = time.time()
        
        data = frame.network_packet.transport_packet.payload
        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        signal = 2 * bits - 1  # BPSK modulation
        
        processing_time = time.time() - start_time
        self.metrics.record_operation(processing_time, True, len(data), len(signal), 0)
        
        print(f"  [Physical] Converted to {len(signal)} bits signal")
        return signal.astype(float)
    
    def transmit_through_awgn(self, signal: np.ndarray) -> np.ndarray:
        """Simulate AWGN (Additive White Gaussian Noise) channel"""
        start_time = time.time()
        
        signal_power = np.mean(signal ** 2)
        snr_linear = 10 ** (self.config.snr_db / 10)
        noise_power = signal_power / snr_linear
        
        noise = np.sqrt(noise_power) * np.random.randn(len(signal))
        received_signal = signal + noise
        
        processing_time = time.time() - start_time
        self.metrics.record_operation(processing_time, True, len(signal), len(received_signal), 0)
        
        print(f"  [Physical] Transmitted through AWGN channel (SNR={self.config.snr_db} dB)")
        return received_signal
    
    def signal_to_frame(self, received_signal: np.ndarray, original_frame: Frame) -> Tuple[Frame, bool]:
        """Demodulate signal back to frame"""
        start_time = time.time()
        
        bits = (received_signal > 0).astype(np.uint8)
        num_bytes = len(bits) // 8
        byte_data = np.packbits(bits[:num_bytes * 8])
        
        ber = self._calculate_ber(received_signal)
        self.ber_values.append(ber)
        
        success = True
        if np.random.random() < ber * 100:
            success = False
            print(f"  [Physical] Frame corrupted (BER={ber:.6f})")
        else:
            print(f"  [Physical] Frame received successfully (BER={ber:.6f})")
        
        processing_time = time.time() - start_time
        errors = 0 if success else 1
        self.metrics.record_operation(processing_time, success, len(received_signal), num_bytes, errors)
        
        return original_frame, success
    
    def _calculate_ber(self, received_signal: np.ndarray) -> float:
        """Calculate Bit Error Rate"""
        snr_linear = 10 ** (self.config.snr_db / 10)
        from scipy.special import erfc
        ber = 0.5 * erfc(np.sqrt(snr_linear))
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
        
    def simulate_transmission(self, source_node: int, dest_node: int):
        """Simulate complete network transmission"""
        print("\n" + "="*60)
        print(f"STARTING IoT SENSOR TRANSMISSION")
        print(f"Temperature Sensor (Node {source_node}) → Monitoring Server (Node {dest_node})")
        print("="*60)
        
        path = self.network_layer.find_path(source_node, dest_node)
        print(f"\n[Routing] Path selected: {' -> '.join(map(str, path))}")
        
        if not path:
            print("ERROR: No path found!")
            return
        
        # Start timers for each layer
        self.app_layer.metrics.start_timer()
        self.transport_layer.metrics.start_timer()
        self.network_layer.metrics.start_timer()
        self.datalink_layer.metrics.start_timer()
        self.physical_layer.metrics.start_timer()
        
        start_time = time.time()
        
        for packet_id in range(self.config.num_packets):
            print(f"\n{'─'*60}")
            print(f"PACKET {packet_id + 1}/{self.config.num_packets}")
            print(f"{'─'*60}")
            
            packet_start = time.time()
            
            # Application Layer
            data = self.app_layer.generate_data(packet_id)
            try:
                sensor_reading = json.loads(data.decode().strip())
                print(f"[Application] IoT Sensor Data Generated:")
                print(f"  └─ Sensor: {sensor_reading['sensor_id']} at {sensor_reading['location']}")
                print(f"  └─ Temperature: {sensor_reading['temperature_celsius']}°C")
                print(f"  └─ Humidity: {sensor_reading['humidity_percent']}%")
                print(f"  └─ Status: {sensor_reading['alert']}")
            except:
                print(f"[Application] Generated {len(data)} bytes of sensor data")
            
            # Transport Layer
            transport_packet = self.transport_layer.create_packet(data, packet_id)
            
            # Network Layer
            network_packet = self.network_layer.add_network_header(
                transport_packet, source_node, dest_node
            )
            
            # Simulate transmission through each hop
            success = True
            for i in range(len(path) - 1):
                current_node = path[i]
                next_node = path[i + 1]
                
                print(f"\n  Hop {i+1}: Node {current_node} -> Node {next_node}")
                
                # Data Link Layer
                frame = self.datalink_layer.create_frame(
                    network_packet, current_node, next_node
                )
                
                # Physical Layer
                signal = self.physical_layer.frame_to_signal(frame)
                received_signal = self.physical_layer.transmit_through_awgn(signal)
                received_frame, hop_success = self.physical_layer.signal_to_frame(
                    received_signal, frame
                )
                
                if not hop_success:
                    success = False
                    break
                
                if not self.datalink_layer.verify_frame(received_frame):
                    success = False
                    print(f"  [DataLink] CRC check failed!")
                    break
            
            self.sent_packets += 1
            
            if success:
                self.received_packets += 1
                packet_latency = time.time() - packet_start
                self.latencies.append(packet_latency)
                print(f"\n✓ Packet {packet_id} delivered successfully!")
            else:
                print(f"\n✗ Packet {packet_id} lost during transmission")
        
        end_time = time.time()
        
        # Stop timers
        self.app_layer.metrics.stop_timer()
        self.transport_layer.metrics.stop_timer()
        self.network_layer.metrics.stop_timer()
        self.datalink_layer.metrics.stop_timer()
        self.physical_layer.metrics.stop_timer()
        
        # Calculate KPIs
        self.app_layer.calculate_kpis(
            self.sent_packets, self.received_packets, 
            self.latencies, start_time, end_time
        )
        self.app_layer.print_kpis()
        
        # Print per-layer metrics
        self.print_layer_metrics()
        
    def print_layer_metrics(self):
        """Print detailed per-layer KPI and QoS metrics"""
        print("\n" + "="*80)
        print("PER-LAYER KPI AND QOS METRICS")
        print("="*80)
        
        layers = [
            self.app_layer.metrics,
            self.transport_layer.metrics,
            self.network_layer.metrics,
            self.datalink_layer.metrics,
            self.physical_layer.metrics
        ]
        
        for layer_metrics in layers:
            metrics = layer_metrics.get_all_metrics()
            
            print(f"\n┌{'─'*78}┐")
            print(f"│ {metrics['layer_name']:^76} │")
            print(f"├{'─'*78}┤")
            
            # KPI Section
            print(f"│ {'KPI METRICS':^76} │")
            print(f"├{'─'*38}┬{'─'*39}┤")
            kpi = metrics['kpi']
            print(f"│ Throughput:           {kpi['throughput_mbps']:>10.3f} Mbps │ Operations:        {kpi['total_operations']:>10} │")
            print(f"│ Avg Processing Time:  {kpi['avg_processing_time_ms']:>10.3f} ms   │ Successful:        {kpi['successful_operations']:>10} │")
            print(f"│ Success Rate:         {kpi['success_rate_percent']:>10.2f} %    │ Failed:            {kpi['failed_operations']:>10} │")
            print(f"│ Error Rate:           {kpi['error_rate_percent']:>10.2f} %    │ Bytes Processed:   {kpi['bytes_processed']:>10} │")
            print(f"│ Protocol Overhead:    {kpi['overhead_percent']:>10.2f} %    │                               │")
            
            # QoS Section
            print(f"├{'─'*78}┤")
            print(f"│ {'QoS METRICS':^76} │")
            print(f"├{'─'*38}┬{'─'*39}┤")
            qos = metrics['qos']
            print(f"│ Reliability:          {qos['reliability']:>10.2f} %    │ Performance:       {qos['performance']:>10.2f} %    │")
            print(f"│ Efficiency:           {qos['efficiency']:>10.2f} %    │ Overall QoS Score: {qos['overall_score']:>10.2f} %    │")
            print(f"└{'─'*38}┴{'─'*39}┘")
        
        
    def plot_results(self):
        """Visualize simulation results including per-layer metrics"""
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        fig.suptitle('Network Protocol Simulation - Comprehensive KPI & QoS Analysis', 
                     fontsize=16, fontweight='bold')
        
        kpis = self.app_layer.kpis
        
        # Plot 1: Packet Statistics
        ax1 = fig.add_subplot(gs[0, 0])
        categories = ['Sent', 'Received', 'Lost']
        values = [self.sent_packets, self.received_packets, 
                 self.sent_packets - self.received_packets]
        colors = ['#2ecc71', '#3498db', '#e74c3c']
        ax1.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Number of Packets')
        ax1.set_title('Packet Transmission Statistics')
        ax1.grid(axis='y', alpha=0.3)
        
        # Plot 2: Latency Distribution
        ax2 = fig.add_subplot(gs[0, 1])
        if self.latencies:
            ax2.hist(np.array(self.latencies) * 1000, bins=20, color='#9b59b6', 
                    alpha=0.7, edgecolor='black')
            ax2.set_xlabel('Latency (ms)')
            ax2.set_ylabel('Frequency')
            ax2.set_title(f'Latency Distribution (Avg: {kpis["latency"]:.2f} ms)')
            ax2.grid(axis='y', alpha=0.3)
        
        # Plot 3: Overall KPI Summary
        ax3 = fig.add_subplot(gs[0, 2])
        kpi_names = ['Throughput\n(Mbps)', 'Latency\n(ms)', 'Packet Loss\n(%)', 'Success Rate\n(%)']
        kpi_values = [kpis['throughput'], kpis['latency'], kpis['packet_loss'], kpis['success_rate']]
        colors = ['#1abc9c', '#f39c12', '#e74c3c', '#2ecc71']
        bars = ax3.barh(kpi_names, kpi_values, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Value')
        ax3.set_title('Overall KPIs')
        ax3.grid(axis='x', alpha=0.3)
        for bar, value in zip(bars, kpi_values):
            ax3.text(value, bar.get_y() + bar.get_height()/2, f'{value:.2f}', 
                    ha='left', va='center', fontweight='bold')
        
        # Plot 4: Per-Layer Throughput
        ax4 = fig.add_subplot(gs[1, 0])
        layers = ['App', 'Transport', 'Network', 'DataLink', 'Physical']
        throughputs = [
            self.app_layer.metrics.get_throughput_mbps(),
            self.transport_layer.metrics.get_throughput_mbps(),
            self.network_layer.metrics.get_throughput_mbps(),
            self.datalink_layer.metrics.get_throughput_mbps(),
            self.physical_layer.metrics.get_throughput_mbps()
        ]
        ax4.bar(layers, throughputs, color='#3498db', alpha=0.7, edgecolor='black')
        ax4.set_ylabel('Throughput (Mbps)')
        ax4.set_title('Per-Layer Throughput')
        ax4.grid(axis='y', alpha=0.3)
        ax4.tick_params(axis='x', rotation=45)
        
        # Plot 5: Per-Layer Processing Time
        ax5 = fig.add_subplot(gs[1, 1])
        processing_times = [
            self.app_layer.metrics.get_avg_processing_time_ms(),
            self.transport_layer.metrics.get_avg_processing_time_ms(),
            self.network_layer.metrics.get_avg_processing_time_ms(),
            self.datalink_layer.metrics.get_avg_processing_time_ms(),
            self.physical_layer.metrics.get_avg_processing_time_ms()
        ]
        ax5.bar(layers, processing_times, color='#f39c12', alpha=0.7, edgecolor='black')
        ax5.set_ylabel('Avg Processing Time (ms)')
        ax5.set_title('Per-Layer Processing Time')
        ax5.grid(axis='y', alpha=0.3)
        ax5.tick_params(axis='x', rotation=45)
        
        # Plot 6: Per-Layer Success Rate
        ax6 = fig.add_subplot(gs[1, 2])
        success_rates = [
            self.app_layer.metrics.get_success_rate(),
            self.transport_layer.metrics.get_success_rate(),
            self.network_layer.metrics.get_success_rate(),
            self.datalink_layer.metrics.get_success_rate(),
            self.physical_layer.metrics.get_success_rate()
        ]
        ax6.bar(layers, success_rates, color='#2ecc71', alpha=0.7, edgecolor='black')
        ax6.set_ylabel('Success Rate (%)')
        ax6.set_title('Per-Layer Success Rate')
        ax6.set_ylim([0, 105])
        ax6.grid(axis='y', alpha=0.3)
        ax6.tick_params(axis='x', rotation=45)
        
        # Plot 7: QoS Comparison Across Layers
        ax7 = fig.add_subplot(gs[2, :2])
        qos_metrics = ['Reliability', 'Efficiency', 'Performance', 'Overall']
        x = np.arange(len(layers))
        width = 0.2
        
        reliability = [self.app_layer.metrics.get_qos_reliability(),
                      self.transport_layer.metrics.get_qos_reliability(),
                      self.network_layer.metrics.get_qos_reliability(),
                      self.datalink_layer.metrics.get_qos_reliability(),
                      self.physical_layer.metrics.get_qos_reliability()]
        
        efficiency = [self.app_layer.metrics.get_qos_efficiency(),
                     self.transport_layer.metrics.get_qos_efficiency(),
                     self.network_layer.metrics.get_qos_efficiency(),
                     self.datalink_layer.metrics.get_qos_efficiency(),
                     self.physical_layer.metrics.get_qos_efficiency()]
        
        performance = [self.app_layer.metrics.get_qos_performance(),
                      self.transport_layer.metrics.get_qos_performance(),
                      self.network_layer.metrics.get_qos_performance(),
                      self.datalink_layer.metrics.get_qos_performance(),
                      self.physical_layer.metrics.get_qos_performance()]
        
        overall = [self.app_layer.metrics.get_qos_overall(),
                  self.transport_layer.metrics.get_qos_overall(),
                  self.network_layer.metrics.get_qos_overall(),
                  self.datalink_layer.metrics.get_qos_overall(),
                  self.physical_layer.metrics.get_qos_overall()]
        
        ax7.bar(x - 1.5*width, reliability, width, label='Reliability', color='#3498db', alpha=0.8)
        ax7.bar(x - 0.5*width, efficiency, width, label='Efficiency', color='#2ecc71', alpha=0.8)
        ax7.bar(x + 0.5*width, performance, width, label='Performance', color='#f39c12', alpha=0.8)
        ax7.bar(x + 1.5*width, overall, width, label='Overall QoS', color='#e74c3c', alpha=0.8)
        
        ax7.set_ylabel('QoS Score (%)')
        ax7.set_title('QoS Metrics Comparison Across All Layers')
        ax7.set_xticks(x)
        ax7.set_xticklabels(layers)
        ax7.legend()
        ax7.grid(axis='y', alpha=0.3)
        ax7.set_ylim([0, 105])
        
        # Plot 8: Protocol Overhead by Layer
        ax8 = fig.add_subplot(gs[2, 2])
        overheads = [
            self.app_layer.metrics.get_overhead_percentage(),
            self.transport_layer.metrics.get_overhead_percentage(),
            self.network_layer.metrics.get_overhead_percentage(),
            self.datalink_layer.metrics.get_overhead_percentage(),
            self.physical_layer.metrics.get_overhead_percentage()
        ]
        ax8.bar(layers, overheads, color='#e67e22', alpha=0.7, edgecolor='black')
        ax8.set_ylabel('Protocol Overhead (%)')
        ax8.set_title('Protocol Overhead by Layer')
        ax8.grid(axis='y', alpha=0.3)
        ax8.tick_params(axis='x', rotation=45)
        
        plt.savefig('simulation_results_with_layer_kpi.png', 
                    dpi=300, bbox_inches='tight')

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print(" NETWORK PROTOCOL SIMULATION - JoMaRe ASSIGNMENT")
    print(" IoT Temperature Monitoring System")
    print(" WITH PER-LAYER KPI AND QOS METRICS")
    print(" DOS to KPI Improvement Implementation")
    print("="*60)
    print("\n📡 APPLICATION: IoT Temperature Sensor Network")
    print("   Sensor Node (1) → Central Server (5)")
    print("   Monitoring: Server Room Temperature & Humidity")
    print("="*60)
    
    config = NetworkConfig(
        num_nodes=6,
        packet_size=1024,
        num_packets=50,
        snr_db=15.0,
        bandwidth=10e6,
        distance=100.0
    )
    
    simulator = NetworkSimulator(config)
    simulator.simulate_transmission(source_node=1, dest_node=5)
    simulator.plot_results()
    

if __name__ == "__main__":
    main()