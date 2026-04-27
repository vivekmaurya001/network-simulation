

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
class NodeAddress:
    """Node addressing information"""
    node_id: int
    ip_address: str
    mac_address: str
    
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
    
class TransportLayer:
    """Transport Layer - Creates packets with headers"""
    
    def __init__(self):
        self.source_port = 8080
        self.dest_port = 9090
        
    def create_packet(self, data: bytes, seq_num: int) -> TransportPacket:
        """Create transport layer packet"""
        checksum = self._calculate_checksum(data)
        packet = TransportPacket(
            source_port=self.source_port,
            dest_port=self.dest_port,
            sequence_num=seq_num,
            payload=data,
            checksum=checksum,
            timestamp=time.time()
        )
        print(f"  [Transport] Created packet #{seq_num} with checksum {checksum}")
        return packet
    
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
    """Network Layer - Adds IP addressing and routing"""
    
    def __init__(self):
        self.routing_table = {
            1: [2, 4],  # Node 1 can reach nodes 2 and 4
            2: [1, 3],  # Node 2 can reach nodes 1 and 3
            3: [2, 5],  # Node 3 can reach nodes 2 and 5
            4: [1, 5],  # Node 4 can reach nodes 1 and 5
            5: [3, 4],  # Node 5 can reach nodes 3 and 4
            6: [1]      # Node 6 can reach node 1
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
        source_ip = self.node_addresses[source_node].ip_address
        dest_ip = self.node_addresses[dest_node].ip_address
        
        packet = NetworkPacket(
            source_ip=source_ip,
            dest_ip=dest_ip,
            ttl=64,
            transport_packet=transport_packet
        )
        print(f"  [Network] Added IP header: {source_ip} -> {dest_ip}")
        return packet
    
    def find_path(self, source: int, dest: int) -> List[int]:
        """Find routing path using BFS"""
        if source == dest:
            return [source]
        
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
        
    def create_frame(self, network_packet: NetworkPacket, 
                     source_node: int, dest_node: int) -> Frame:
        """Create data link frame (packet to frame conversion)"""
        source_mac = self.network_layer.node_addresses[source_node].mac_address
        dest_mac = self.network_layer.node_addresses[dest_node].mac_address
        
        # Calculate CRC
        crc = self._calculate_crc(network_packet)
        
        frame = Frame(
            source_mac=source_mac,
            dest_mac=dest_mac,
            network_packet=network_packet,
            crc=crc
        )
        print(f"  [DataLink] Created frame: {source_mac} -> {dest_mac}")
        return frame
    
    def _calculate_crc(self, network_packet: NetworkPacket) -> int:
        """Calculate CRC checksum"""
        data = network_packet.transport_packet.payload
        return sum(data) % 2**16
    
    def verify_frame(self, frame: Frame) -> bool:
        """Verify frame integrity"""
        calculated_crc = self._calculate_crc(frame.network_packet)
        return calculated_crc == frame.crc

# ============================================================================
# LAYER 1: PHYSICAL LAYER
# ============================================================================

class PhysicalLayer:
    """Physical Layer - Converts to signals and simulates AWGN channel"""
    
    def __init__(self, config: NetworkConfig):
        self.config = config
        
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
            data = self.app_layer.generate_data(packet_id)
            
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
            
            # Step 2: Transport Layer - Create packet
            transport_packet = self.transport_layer.create_packet(data, packet_id)
            
            # Step 3 & 4: Network Layer - Add addressing and select path
            network_packet = self.network_layer.add_network_header(
                transport_packet, source_node, dest_node
            )
            
            # Simulate transmission through each hop in path
            success = True
            for i in range(len(path) - 1):
                current_node = path[i]
                next_node = path[i + 1]
                
                print(f"\n  Hop {i+1}: Node {current_node} -> Node {next_node}")
                
                # Step 5: Data Link Layer - Create frame
                frame = self.datalink_layer.create_frame(
                    network_packet, current_node, next_node
                )
                
                # Step 6: Physical Layer - Convert to signal
                signal = self.physical_layer.frame_to_signal(frame)
                
                # Step 7: Transmit through AWGN channel
                received_signal = self.physical_layer.transmit_through_awgn(signal)
                
                # Step 8: Receive and demodulate
                received_frame, hop_success = self.physical_layer.signal_to_frame(
                    received_signal, frame
                )
                
                if not hop_success:
                    success = False
                    break
                
                # Verify frame
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
        
        # Calculate and display KPIs
        self.app_layer.calculate_kpis(
            self.sent_packets, self.received_packets, 
            self.latencies, start_time, end_time
        )
        self.app_layer.print_kpis()
        
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
        success_data = [self.received_packets, self.sent_packets - self.received_packets]
        labels = [f'Success\n({kpis["success_rate"]:.1f}%)', 
                 f'Failed\n({100-kpis["success_rate"]:.1f}%)']
        colors = ['#2ecc71', '#e74c3c']
        ax4.pie(success_data, labels=labels, colors=colors, autopct='%d', 
               startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
        ax4.set_title('Transmission Success Rate')
        
        plt.tight_layout()
        plt.savefig('./simulation_results.png', dpi=300, bbox_inches='tight')
        print("\n[Visualization] Results saved to 'simulation_results.png'")
        plt.show()

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