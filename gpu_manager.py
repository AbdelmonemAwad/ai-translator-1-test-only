#!/usr/bin/env python3
"""
GPU Management System for AI Translator
Automatically detects and manages GPU allocation for Whisper and Ollama services
"""

import subprocess
import json
import re
import psutil
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


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