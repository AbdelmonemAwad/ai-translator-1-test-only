"""
Remote Storage Service for AI Translator
خدمة التخزين البعيد للترجمان الآلي
"""

import os
import subprocess
import socket
from typing import Dict, Any, Optional

def test_remote_connection(protocol: str, host: str, username: str, password: str, path: str, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Test connection to remote storage system
    اختبار الاتصال بنظام التخزين البعيد
    """
    try:
        if protocol.lower() == 'ssh':
            return test_ssh_connection(host, username, password, path, port or 22)
        elif protocol.lower() == 'smb':
            return test_smb_connection(host, username, password, path, port or 445)
        elif protocol.lower() == 'ftp':
            return test_ftp_connection(host, username, password, path, port or 21)
        elif protocol.lower() == 'nfs':
            return test_nfs_connection(host, path, port or 2049)
        else:
            return {
                'success': False,
                'error': f'Unsupported protocol: {protocol}',
                'details': 'Supported protocols: SSH, SMB, FTP, NFS'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Connection test failed: {str(e)}',
            'details': 'Unable to test remote connection'
        }

def test_ssh_connection(host: str, username: str, password: str, path: str, port: int) -> Dict[str, Any]:
    """Test SSH connection"""
    try:
        # Test basic connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result != 0:
            return {
                'success': False,
                'error': f'Cannot connect to {host}:{port}',
                'details': 'SSH port is not accessible'
            }
        
        return {
            'success': True,
            'message': f'SSH connection to {host}:{port} successful',
            'details': f'Remote path: {path}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'SSH connection failed: {str(e)}',
            'details': 'Check host, port, and network connectivity'
        }

def test_smb_connection(host: str, username: str, password: str, path: str, port: int) -> Dict[str, Any]:
    """Test SMB/CIFS connection"""
    try:
        # Test basic connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result != 0:
            return {
                'success': False,
                'error': f'Cannot connect to {host}:{port}',
                'details': 'SMB port is not accessible'
            }
        
        return {
            'success': True,
            'message': f'SMB connection to {host}:{port} successful',
            'details': f'Share path: {path}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'SMB connection failed: {str(e)}',
            'details': 'Check host, credentials, and share path'
        }

def test_ftp_connection(host: str, username: str, password: str, path: str, port: int) -> Dict[str, Any]:
    """Test FTP connection"""
    try:
        # Test basic connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result != 0:
            return {
                'success': False,
                'error': f'Cannot connect to {host}:{port}',
                'details': 'FTP port is not accessible'
            }
        
        return {
            'success': True,
            'message': f'FTP connection to {host}:{port} successful',
            'details': f'Remote path: {path}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'FTP connection failed: {str(e)}',
            'details': 'Check host, credentials, and path'
        }

def test_nfs_connection(host: str, path: str, port: int) -> Dict[str, Any]:
    """Test NFS connection"""
    try:
        # Test basic connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result != 0:
            return {
                'success': False,
                'error': f'Cannot connect to {host}:{port}',
                'details': 'NFS port is not accessible'
            }
        
        return {
            'success': True,
            'message': f'NFS connection to {host}:{port} successful',
            'details': f'Export path: {path}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'NFS connection failed: {str(e)}',
            'details': 'Check host, export path, and NFS service'
        }

def setup_remote_mount(protocol: str, host: str, username: str, password: str, 
                      remote_path: str, local_path: str, port: Optional[int] = None) -> Dict[str, Any]:
    """
    Setup remote storage mount
    إعداد تركيب التخزين البعيد
    """
    try:
        # Create local mount point if it doesn't exist
        os.makedirs(local_path, exist_ok=True)
        
        if protocol.lower() == 'smb':
            return setup_smb_mount(host, username, password, remote_path, local_path)
        elif protocol.lower() == 'nfs':
            return setup_nfs_mount(host, remote_path, local_path)
        else:
            return {
                'success': False,
                'error': f'Mount setup not supported for protocol: {protocol}',
                'details': 'Supported mount protocols: SMB, NFS'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Mount setup failed: {str(e)}',
            'details': 'Unable to setup remote mount'
        }

def setup_smb_mount(host: str, username: str, password: str, remote_path: str, local_path: str) -> Dict[str, Any]:
    """Setup SMB/CIFS mount"""
    try:
        mount_cmd = [
            'sudo', 'mount', '-t', 'cifs',
            f'//{host}/{remote_path}',
            local_path,
            '-o', f'username={username},password={password},uid=1000,gid=1000,iocharset=utf8'
        ]
        
        result = subprocess.run(mount_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': f'SMB mount successful: {local_path}',
                'details': f'Mounted //{host}/{remote_path} to {local_path}'
            }
        else:
            return {
                'success': False,
                'error': f'Mount failed: {result.stderr}',
                'details': 'Check credentials and share permissions'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'SMB mount setup failed: {str(e)}',
            'details': 'Ensure cifs-utils is installed'
        }

def setup_nfs_mount(host: str, remote_path: str, local_path: str) -> Dict[str, Any]:
    """Setup NFS mount"""
    try:
        mount_cmd = [
            'sudo', 'mount', '-t', 'nfs',
            f'{host}:{remote_path}',
            local_path
        ]
        
        result = subprocess.run(mount_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': f'NFS mount successful: {local_path}',
                'details': f'Mounted {host}:{remote_path} to {local_path}'
            }
        else:
            return {
                'success': False,
                'error': f'Mount failed: {result.stderr}',
                'details': 'Check NFS export and permissions'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'NFS mount setup failed: {str(e)}',
            'details': 'Ensure nfs-common is installed'
        }

def get_mount_status() -> Dict[str, Any]:
    """Get current mount status"""
    try:
        result = subprocess.run(['mount'], capture_output=True, text=True)
        mounts = []
        
        for line in result.stdout.split('\n'):
            if any(fs_type in line for fs_type in ['cifs', 'nfs', 'ftp']):
                mounts.append(line.strip())
        
        return {
            'success': True,
            'mounts': mounts,
            'count': len(mounts)
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to get mount status: {str(e)}',
            'mounts': []
        }

def unmount_remote_storage(local_path: str) -> Dict[str, Any]:
    """Unmount remote storage"""
    try:
        result = subprocess.run(['sudo', 'umount', local_path], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return {
                'success': True,
                'message': f'Successfully unmounted {local_path}'
            }
        else:
            return {
                'success': False,
                'error': f'Unmount failed: {result.stderr}'
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unmount failed: {str(e)}'
        }