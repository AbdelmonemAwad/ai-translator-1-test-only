#!/usr/bin/env python3
"""
Advanced System Monitor for AI Translator
Automatically detects and manages all system components including GPUs, CPU, RAM, Storage
"""

import subprocess
import json
import re
import psutil
import platform
import shutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class GPUInfo:
    """GPU information container"""
    id: int
    name: str
    memory_total: int  # MB
    memory_used: int   # MB
    memory_free: int   # MB
    utilization: int   # Percentage
    temperature: int   # Celsius
    power_draw: float  # Watts
    power_limit: float # Watts
    driver_version: str
    cuda_version: str
    performance_score: int  # 0-100 calculated score

@dataclass
class CPUInfo:
    """CPU information container"""
    name: str
    architecture: str
    cores_physical: int
    cores_logical: int
    frequency_current: float  # GHz
    frequency_max: float     # GHz
    utilization: float       # Percentage
    temperature: Optional[float]  # Celsius
    cache_l1: Optional[str]
    cache_l2: Optional[str]
    cache_l3: Optional[str]

@dataclass
class MemoryInfo:
    """Memory information container"""
    total: float         # GB
    available: float     # GB
    used: float         # GB
    percentage: float   # Percentage
    swap_total: float   # GB
    swap_used: float    # GB
    speed: Optional[str] # MHz
    type: Optional[str]  # DDR4, DDR5, etc.

@dataclass
class StorageInfo:
    """Storage device information"""
    device: str
    mountpoint: str
    filesystem: str
    total: float        # GB
    used: float        # GB
    free: float        # GB
    percentage: float  # Percentage
    device_type: str   # SSD, HDD, NVMe
    read_speed: Optional[float]  # MB/s
    write_speed: Optional[float] # MB/s

@dataclass
class NetworkInfo:
    """Network interface information"""
    interface: str
    ip_address: str
    netmask: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    speed: Optional[str]  # Mbps
    status: str          # up, down

@dataclass
class SystemInfo:
    """Complete system information container"""
    hostname: str
    os_name: str
    os_version: str
    kernel_version: str
    uptime: int         # seconds
    boot_time: float    # timestamp
    cpu: CPUInfo
    memory: MemoryInfo
    gpus: List[GPUInfo]
    storage: List[StorageInfo]
    network: List[NetworkInfo]
    load_average: List[float]  # 1, 5, 15 minute averages


class SystemMonitor:
    """Advanced system monitoring and hardware detection"""
    
    def __init__(self):
        self.system_info: Optional[SystemInfo] = None
        self.last_refresh = 0
        self.refresh_interval = 5  # seconds
        self.refresh_system_info()
    
    def get_complete_system_info(self) -> Optional[SystemInfo]:
        """Get complete system information with auto-refresh"""
        current_time = time.time()
        if current_time - self.last_refresh > self.refresh_interval:
            self.refresh_system_info()
        return self.system_info
    
    def refresh_system_info(self) -> bool:
        """Refresh all system information"""
        try:
            # Get basic system info
            hostname = platform.node()
            os_name = platform.system()
            os_version = platform.release()
            kernel_version = platform.version()
            
            # Get uptime and boot time
            boot_time = psutil.boot_time()
            uptime = int(time.time() - boot_time)
            
            # Get load average (Unix only)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]
            
            # Collect all component information
            cpu_info = self._get_cpu_info()
            memory_info = self._get_memory_info()
            gpu_info = self._get_all_gpus()
            storage_info = self._get_storage_info()
            network_info = self._get_network_info()
            
            self.system_info = SystemInfo(
                hostname=hostname,
                os_name=os_name,
                os_version=os_version,
                kernel_version=kernel_version,
                uptime=uptime,
                boot_time=boot_time,
                cpu=cpu_info,
                memory=memory_info,
                gpus=gpu_info,
                storage=storage_info,
                network=network_info,
                load_average=load_avg
            )
            
            self.last_refresh = time.time()
            return True
            
        except Exception as e:
            print(f"Error refreshing system info: {e}")
            return False
    
    def _get_cpu_info(self) -> CPUInfo:
        """Get detailed CPU information"""
        try:
            # CPU name and architecture
            cpu_name = self._get_cpu_name()
            architecture = platform.machine()
            
            # Core counts
            cores_physical = psutil.cpu_count(logical=False) or 1
            cores_logical = psutil.cpu_count(logical=True) or 1
            
            # Frequencies
            freq = psutil.cpu_freq()
            freq_current = freq.current / 1000 if freq else 0.0  # Convert to GHz
            freq_max = freq.max / 1000 if freq and freq.max else 0.0
            
            # CPU utilization
            utilization = psutil.cpu_percent(interval=1)
            
            # Temperature (if available)
            temperature = self._get_cpu_temperature()
            
            # Cache info (basic detection)
            cache_info = self._get_cpu_cache_info()
            
            return CPUInfo(
                name=cpu_name,
                architecture=architecture,
                cores_physical=cores_physical,
                cores_logical=cores_logical,
                frequency_current=freq_current,
                frequency_max=freq_max,
                utilization=utilization,
                temperature=temperature,
                cache_l1=cache_info.get('L1'),
                cache_l2=cache_info.get('L2'),
                cache_l3=cache_info.get('L3')
            )
            
        except Exception as e:
            print(f"Error getting CPU info: {e}")
            return CPUInfo("Unknown", "Unknown", 1, 1, 0.0, 0.0, 0.0, None, None, None, None)
    
    def _get_memory_info(self) -> MemoryInfo:
        """Get detailed memory information"""
        try:
            # Virtual memory
            mem = psutil.virtual_memory()
            total_gb = round(mem.total / (1024**3), 1)
            available_gb = round(mem.available / (1024**3), 1)
            used_gb = round(mem.used / (1024**3), 1)
            percentage = mem.percent
            
            # Swap memory
            swap = psutil.swap_memory()
            swap_total_gb = round(swap.total / (1024**3), 1)
            swap_used_gb = round(swap.used / (1024**3), 1)
            
            # Memory type and speed (try to detect from /proc/meminfo or dmidecode)
            mem_type, mem_speed = self._get_memory_specs()
            
            return MemoryInfo(
                total=total_gb,
                available=available_gb,
                used=used_gb,
                percentage=percentage,
                swap_total=swap_total_gb,
                swap_used=swap_used_gb,
                speed=mem_speed,
                type=mem_type
            )
            
        except Exception as e:
            print(f"Error getting memory info: {e}")
            return MemoryInfo(0, 0, 0, 0.0, 0, 0, None, None)
    
    def _get_storage_info(self) -> List[StorageInfo]:
        """Get information about all storage devices"""
        storage_devices = []
        
        try:
            # Get disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    # Skip special filesystems
                    if partition.fstype in ['', 'tmpfs', 'devtmpfs', 'squashfs']:
                        continue
                    
                    # Get disk usage
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = round(usage.total / (1024**3), 1)
                    used_gb = round(usage.used / (1024**3), 1)
                    free_gb = round(usage.free / (1024**3), 1)
                    percentage = (used_gb / total_gb * 100) if total_gb > 0 else 0
                    
                    # Detect device type
                    device_type = self._detect_storage_type(partition.device)
                    
                    # Get I/O stats (if available)
                    read_speed, write_speed = self._get_disk_io_speed(partition.device)
                    
                    storage_devices.append(StorageInfo(
                        device=partition.device,
                        mountpoint=partition.mountpoint,
                        filesystem=partition.fstype,
                        total=total_gb,
                        used=used_gb,
                        free=free_gb,
                        percentage=percentage,
                        device_type=device_type,
                        read_speed=read_speed,
                        write_speed=write_speed
                    ))
                    
                except (PermissionError, OSError):
                    continue
                    
        except Exception as e:
            print(f"Error getting storage info: {e}")
            
        return storage_devices
    
    def _get_network_info(self) -> List[NetworkInfo]:
        """Get information about network interfaces"""
        network_interfaces = []
        
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for interface_name, addresses in interfaces.items():
                # Skip loopback and virtual interfaces
                if interface_name.startswith(('lo', 'docker', 'br-', 'veth')):
                    continue
                
                # Get IPv4 address
                ipv4_addr = None
                netmask = None
                
                for addr in addresses:
                    if addr.family == 2:  # AF_INET (IPv4)
                        ipv4_addr = addr.address
                        netmask = addr.netmask
                        break
                
                if not ipv4_addr:
                    continue
                
                # Get interface stats
                interface_stats = stats.get(interface_name)
                interface_io = io_counters.get(interface_name)
                
                status = "up" if interface_stats and interface_stats.isup else "down"
                speed = f"{interface_stats.speed} Mbps" if interface_stats and interface_stats.speed else None
                
                bytes_sent = interface_io.bytes_sent if interface_io else 0
                bytes_recv = interface_io.bytes_recv if interface_io else 0
                packets_sent = interface_io.packets_sent if interface_io else 0
                packets_recv = interface_io.packets_recv if interface_io else 0
                
                network_interfaces.append(NetworkInfo(
                    interface=interface_name,
                    ip_address=ipv4_addr,
                    netmask=netmask or "255.255.255.0",
                    bytes_sent=bytes_sent,
                    bytes_recv=bytes_recv,
                    packets_sent=packets_sent,
                    packets_recv=packets_recv,
                    speed=speed,
                    status=status
                ))
                
        except Exception as e:
            print(f"Error getting network info: {e}")
            
        return network_interfaces

    def _get_all_gpus(self) -> List[GPUInfo]:
        """Get information about all GPUs using existing GPUManager"""
        gpu_manager = GPUManager()
        return gpu_manager.gpus

    def _get_cpu_name(self) -> str:
        """Get CPU name from /proc/cpuinfo or other sources"""
        try:
            # Try /proc/cpuinfo first (Linux)
            if platform.system() == "Linux":
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            return line.split(':')[1].strip()
            
            # Fallback to platform info
            return platform.processor() or "Unknown CPU"
            
        except Exception:
            return "Unknown CPU"

    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature if available"""
        try:
            # Try sensors from psutil (requires lm-sensors on Linux)
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Look for coretemp (Intel) or k10temp (AMD)
                    for name, entries in temps.items():
                        if name in ['coretemp', 'k10temp', 'cpu_thermal']:
                            for entry in entries:
                                if entry.current:
                                    return entry.current
            return None
        except Exception:
            return None

    def _get_cpu_cache_info(self) -> Dict[str, str]:
        """Get CPU cache information"""
        cache_info = {}
        try:
            if platform.system() == "Linux":
                # Try to read from /sys/devices/system/cpu/cpu0/cache/
                import os
                for level in ['index0', 'index1', 'index2', 'index3']:
                    cache_path = f'/sys/devices/system/cpu/cpu0/cache/{level}'
                    if os.path.exists(cache_path):
                        try:
                            with open(f'{cache_path}/level', 'r') as f:
                                level_num = f.read().strip()
                            with open(f'{cache_path}/size', 'r') as f:
                                size = f.read().strip()
                            cache_info[f'L{level_num}'] = size
                        except Exception:
                            continue
        except Exception:
            pass
        return cache_info

    def _get_memory_specs(self) -> tuple:
        """Get memory type and speed"""
        try:
            # Try dmidecode if available
            result = subprocess.run(['dmidecode', '-t', 'memory'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                output = result.stdout
                mem_type = None
                mem_speed = None
                
                for line in output.split('\n'):
                    if 'Type:' in line and 'DDR' in line:
                        mem_type = line.split(':')[1].strip()
                    elif 'Speed:' in line and 'MHz' in line:
                        mem_speed = line.split(':')[1].strip()
                
                return mem_type, mem_speed
        except Exception:
            pass
        
        return None, None

    def _detect_storage_type(self, device: str) -> str:
        """Detect storage device type (SSD, HDD, NVMe)"""
        try:
            device_name = device.replace('/dev/', '')
            
            # Check if it's NVMe
            if 'nvme' in device_name:
                return 'NVMe'
            
            # Try to read rotational flag (Linux)
            if platform.system() == "Linux":
                # Extract base device name (remove partition numbers)
                base_device = re.sub(r'\d+$', '', device_name)
                rotational_path = f'/sys/block/{base_device}/queue/rotational'
                
                try:
                    with open(rotational_path, 'r') as f:
                        rotational = f.read().strip()
                        return 'HDD' if rotational == '1' else 'SSD'
                except Exception:
                    pass
            
            # Fallback detection based on device name patterns
            if any(pattern in device_name for pattern in ['sd', 'hd']):
                return 'HDD'  # Assume HDD for SATA/IDE
            elif 'nvme' in device_name:
                return 'NVMe'
            else:
                return 'Unknown'
                
        except Exception:
            return 'Unknown'

    def _get_disk_io_speed(self, device: str) -> tuple:
        """Get disk I/O speeds (placeholder for now)"""
        # This would require benchmarking or historical data
        # For now, return None values
        return None, None

    def format_uptime(self, uptime_seconds: int) -> str:
        """Format uptime in human-readable format"""
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def format_bytes(self, bytes_value: float) -> str:
        """Format bytes in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f} PB"


class GPUManager:
    """Manages GPU detection, monitoring, and allocation for AI services"""
    
    def __init__(self):
        self.gpus: List[GPUInfo] = []
        self.refresh_gpu_info()
    
    def refresh_gpu_info(self) -> bool:
        """Refresh GPU information from nvidia-smi"""
        try:
            # Check if nvidia-smi is available
            result = subprocess.run(['nvidia-smi', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return False
            
            # Get detailed GPU information
            cmd = [
                'nvidia-smi',
                '--query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu,power.draw,power.limit,driver_version',
                '--format=csv,noheader,nounits'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False
            
            self.gpus = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 10:
                        try:
                            gpu = GPUInfo(
                                id=int(parts[0]),
                                name=parts[1],
                                memory_total=int(parts[2]),
                                memory_used=int(parts[3]),
                                memory_free=int(parts[4]),
                                utilization=int(parts[5]) if parts[5] != '[Not Supported]' else 0,
                                temperature=int(parts[6]) if parts[6] != '[Not Supported]' else 0,
                                power_draw=float(parts[7]) if parts[7] != '[Not Supported]' else 0.0,
                                power_limit=float(parts[8]) if parts[8] != '[Not Supported]' else 0.0,
                                driver_version=parts[9],
                                cuda_version=self._get_cuda_version(),
                                performance_score=self._calculate_performance_score(parts[1], int(parts[2]), int(parts[5]) if parts[5] != '[Not Supported]' else 0)
                            )
                            self.gpus.append(gpu)
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing GPU info: {e}")
                            continue
            
            return len(self.gpus) > 0
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _get_cuda_version(self) -> str:
        """Get CUDA version"""
        try:
            result = subprocess.run(['nvcc', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Extract version from output
                match = re.search(r'release (\d+\.\d+)', result.stdout)
                return match.group(1) if match else 'Unknown'
        except:
            pass
        
        # Try nvidia-smi for CUDA version
        try:
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                match = re.search(r'CUDA Version: (\d+\.\d+)', result.stdout)
                return match.group(1) if match else 'Unknown'
        except:
            pass
        
        return 'Unknown'
    
    def _calculate_performance_score(self, name: str, memory_mb: int, utilization: int) -> int:
        """Calculate performance score (0-100) based on GPU specifications"""
        score = 0
        
        # Memory score (40% weight)
        if memory_mb >= 24000:  # 24GB+
            score += 40
        elif memory_mb >= 16000:  # 16GB+
            score += 35
        elif memory_mb >= 12000:  # 12GB+
            score += 30
        elif memory_mb >= 8000:   # 8GB+
            score += 25
        elif memory_mb >= 6000:   # 6GB+
            score += 20
        elif memory_mb >= 4000:   # 4GB+
            score += 15
        else:
            score += 10
        
        # GPU tier score (40% weight)
        name_lower = name.lower()
        if any(x in name_lower for x in ['rtx 4090', 'rtx 4080', 'a100', 'h100']):
            score += 40
        elif any(x in name_lower for x in ['rtx 4070', 'rtx 3090', 'rtx 3080', 'a40']):
            score += 35
        elif any(x in name_lower for x in ['rtx 4060', 'rtx 3070', 'rtx 2080']):
            score += 30
        elif any(x in name_lower for x in ['rtx 3060', 'rtx 2070', 'gtx 1080']):
            score += 25
        elif any(x in name_lower for x in ['gtx 1070', 'gtx 1660']):
            score += 20
        else:
            score += 15
        
        # Current utilization penalty (20% weight)
        if utilization < 10:
            score += 20
        elif utilization < 30:
            score += 15
        elif utilization < 50:
            score += 10
        elif utilization < 70:
            score += 5
        # Heavy utilization gets 0 additional points
        
        return min(score, 100)
    
    def get_available_gpus(self) -> List[Dict[str, Any]]:
        """Get list of available GPUs with their information"""
        self.refresh_gpu_info()
        
        gpu_list = []
        for gpu in self.gpus:
            gpu_list.append({
                'id': gpu.id,
                'name': gpu.name,
                'memory_total': gpu.memory_total,
                'memory_used': gpu.memory_used,
                'memory_free': gpu.memory_free,
                'memory_total_gb': round(gpu.memory_total / 1024, 1),
                'memory_used_gb': round(gpu.memory_used / 1024, 1),
                'memory_free_gb': round(gpu.memory_free / 1024, 1),
                'utilization': gpu.utilization,
                'temperature': gpu.temperature,
                'power_draw': gpu.power_draw,
                'power_limit': gpu.power_limit,
                'driver_version': gpu.driver_version,
                'cuda_version': gpu.cuda_version,
                'performance_score': gpu.performance_score,
                'status': self._get_gpu_status(gpu),
                'recommended_for': self._get_service_recommendation(gpu)
            })
        
        # Sort by performance score (best first)
        gpu_list.sort(key=lambda x: x['performance_score'], reverse=True)
        return gpu_list
    
    def _get_gpu_status(self, gpu: GPUInfo) -> str:
        """Get GPU status description"""
        if gpu.utilization > 80:
            return 'مشغول بكثافة / Heavy Load'
        elif gpu.utilization > 50:
            return 'مشغول متوسط / Moderate Load'
        elif gpu.utilization > 20:
            return 'مشغول قليل / Light Load'
        else:
            return 'متاح / Available'
    
    def _get_service_recommendation(self, gpu: GPUInfo) -> List[str]:
        """Get service recommendations for this GPU"""
        recommendations = []
        
        # High-end GPUs suitable for both services
        if gpu.performance_score >= 80:
            recommendations = ['Ollama (Translation)', 'Whisper (Speech-to-Text)']
        # Mid-range GPUs better for one primary service
        elif gpu.performance_score >= 60:
            if gpu.memory_total >= 12000:
                recommendations = ['Ollama (Translation)']
            else:
                recommendations = ['Whisper (Speech-to-Text)']
        # Lower-end GPUs
        else:
            recommendations = ['Whisper (Speech-to-Text)']
        
        return recommendations
    
    def get_optimal_allocation(self) -> Dict[str, Optional[int]]:
        """Get optimal GPU allocation for services"""
        available_gpus = self.get_available_gpus()
        
        if not available_gpus:
            return {'ollama': None, 'whisper': None}
        
        if len(available_gpus) == 1:
            # Single GPU - use for both services
            return {
                'ollama': available_gpus[0]['id'],
                'whisper': available_gpus[0]['id']
            }
        
        # Multiple GPUs - allocate best to Ollama, second best to Whisper
        allocation = {}
        
        # Sort by performance score and availability
        suitable_for_ollama = [gpu for gpu in available_gpus if gpu['memory_total_gb'] >= 8]
        suitable_for_whisper = [gpu for gpu in available_gpus if gpu['memory_total_gb'] >= 4]
        
        # Allocate Ollama to best suitable GPU
        if suitable_for_ollama:
            allocation['ollama'] = suitable_for_ollama[0]['id']
        else:
            allocation['ollama'] = available_gpus[0]['id']
        
        # Allocate Whisper to different GPU if possible
        whisper_candidates = [gpu for gpu in suitable_for_whisper if gpu['id'] != allocation['ollama']]
        if whisper_candidates:
            allocation['whisper'] = whisper_candidates[0]['id']
        else:
            allocation['whisper'] = allocation['ollama']  # Share GPU if only one available
        
        return allocation
    
    def get_gpu_info(self, gpu_id: int) -> Optional[Dict[str, Any]]:
        """Get information for specific GPU"""
        available_gpus = self.get_available_gpus()
        for gpu in available_gpus:
            if gpu['id'] == gpu_id:
                return gpu
        return None
    
    def is_nvidia_available(self) -> bool:
        """Check if NVIDIA GPUs are available"""
        return len(self.gpus) > 0


# Global GPU manager instance
gpu_manager = GPUManager()


def get_gpu_environment_variables(service: str, gpu_id: Optional[int]) -> Dict[str, str]:
    """Get environment variables for GPU allocation"""
    if gpu_id is not None:
        return {
            'CUDA_VISIBLE_DEVICES': str(gpu_id),
            'NVIDIA_VISIBLE_DEVICES': str(gpu_id)
        }
    else:
        return {
            'CUDA_VISIBLE_DEVICES': '',
            'NVIDIA_VISIBLE_DEVICES': ''
        }


if __name__ == "__main__":
    # Test the GPU manager
    manager = GPUManager()
    print("Available GPUs:")
    for gpu in manager.get_available_gpus():
        print(f"GPU {gpu['id']}: {gpu['name']} ({gpu['memory_total_gb']}GB)")
        print(f"  Status: {gpu['status']}")
        print(f"  Score: {gpu['performance_score']}/100")
        print(f"  Recommended for: {', '.join(gpu['recommended_for'])}")
        print()
    
    print("Optimal allocation:")
    allocation = manager.get_optimal_allocation()
    print(f"Ollama: GPU {allocation['ollama']}")
    print(f"Whisper: GPU {allocation['whisper']}")