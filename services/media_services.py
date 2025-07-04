"""
Media Services Integration Manager
Handles integration with Plex, Jellyfin, Emby, Kodi, Radarr, and Sonarr
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

class MediaServiceBase:
    """Base class for all media service integrations"""
    
    def __init__(self, name: str, base_url: str, api_key: Optional[str] = None, 
                 username: Optional[str] = None, password: Optional[str] = None):
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.timeout = 10
        
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the service"""
        try:
            response = self.get_system_status()
            if response.get('success'):
                return {
                    'success': True,
                    'message': f'Successfully connected to {self.name}',
                    'version': response.get('version', 'Unknown'),
                    'status': 'online'
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to connect to {self.name}: {response.get("error", "Unknown error")}',
                    'status': 'offline'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection error: {str(e)}',
                'status': 'error'
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_system_status")
    
    def get_media_library(self) -> List[Dict[str, Any]]:
        """Get media library - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_media_library")

class PlexService(MediaServiceBase):
    """Plex Media Server integration"""
    
    def __init__(self, base_url: str, api_key: str):
        super().__init__("Plex", base_url, api_key=api_key)
        self.session.headers.update({'X-Plex-Token': api_key})
    
    def get_system_status(self) -> Dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}/identity")
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'version': data.get('version', 'Unknown'),
                    'name': data.get('friendlyName', 'Plex Server')
                }
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_media_library(self) -> List[Dict[str, Any]]:
        media_items = []
        try:
            # Get library sections
            response = self.session.get(f"{self.base_url}/library/sections")
            if response.status_code != 200:
                return media_items
            
            sections = response.json().get('MediaContainer', {}).get('Directory', [])
            
            for section in sections:
                if section.get('type') in ['movie', 'show']:
                    section_key = section.get('key')
                    section_response = self.session.get(
                        f"{self.base_url}/library/sections/{section_key}/all"
                    )
                    
                    if section_response.status_code == 200:
                        items = section_response.json().get('MediaContainer', {}).get('Metadata', [])
                        
                        for item in items:
                            media_item = {
                                'title': item.get('title', ''),
                                'year': item.get('year'),
                                'media_type': 'movie' if section.get('type') == 'movie' else 'episode',
                                'plex_id': item.get('ratingKey'),
                                'service_source': 'plex',
                                'poster_url': self._get_poster_url(item.get('thumb')),
                                'path': self._get_media_path(item)
                            }
                            media_items.append(media_item)
        
        except Exception as e:
            logging.error(f"Error fetching Plex library: {str(e)}")
        
        return media_items
    
    def _get_poster_url(self, thumb_path: str) -> Optional[str]:
        if thumb_path:
            return f"{self.base_url}{thumb_path}?X-Plex-Token={self.api_key}"
        return None
    
    def _get_media_path(self, item: Dict) -> Optional[str]:
        media = item.get('Media', [])
        if media and len(media) > 0:
            parts = media[0].get('Part', [])
            if parts and len(parts) > 0:
                return parts[0].get('file')
        return None

class JellyfinService(MediaServiceBase):
    """Jellyfin Media Server integration"""
    
    def __init__(self, base_url: str, api_key: str):
        super().__init__("Jellyfin", base_url, api_key=api_key)
        self.session.headers.update({'X-Emby-Token': api_key})
    
    def get_system_status(self) -> Dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}/System/Info")
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'version': data.get('Version', 'Unknown'),
                    'name': data.get('ServerName', 'Jellyfin Server')
                }
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_media_library(self) -> List[Dict[str, Any]]:
        media_items = []
        try:
            # Get library folders
            response = self.session.get(f"{self.base_url}/Library/VirtualFolders")
            if response.status_code != 200:
                return media_items
            
            folders = response.json()
            
            for folder in folders:
                if folder.get('CollectionType') in ['movies', 'tvshows']:
                    # Get items from this folder
                    params = {
                        'ParentId': folder.get('ItemId'),
                        'Recursive': 'true',
                        'IncludeItemTypes': 'Movie,Episode'
                    }
                    items_response = self.session.get(f"{self.base_url}/Items", params=params)
                    
                    if items_response.status_code == 200:
                        items = items_response.json().get('Items', [])
                        
                        for item in items:
                            media_item = {
                                'title': item.get('Name', ''),
                                'year': item.get('ProductionYear'),
                                'media_type': 'movie' if item.get('Type') == 'Movie' else 'episode',
                                'jellyfin_id': item.get('Id'),
                                'service_source': 'jellyfin',
                                'poster_url': self._get_poster_url(item.get('Id')),
                                'path': item.get('Path')
                            }
                            media_items.append(media_item)
        
        except Exception as e:
            logging.error(f"Error fetching Jellyfin library: {str(e)}")
        
        return media_items
    
    def _get_poster_url(self, item_id: str) -> Optional[str]:
        if item_id:
            return f"{self.base_url}/Items/{item_id}/Images/Primary?X-Emby-Token={self.api_key}"
        return None

class EmbyService(MediaServiceBase):
    """Emby Media Server integration"""
    
    def __init__(self, base_url: str, api_key: str):
        super().__init__("Emby", base_url, api_key=api_key)
        self.session.headers.update({'X-Emby-Token': api_key})
    
    def get_system_status(self) -> Dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}/System/Info")
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'version': data.get('Version', 'Unknown'),
                    'name': data.get('ServerName', 'Emby Server')
                }
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_media_library(self) -> List[Dict[str, Any]]:
        # Emby uses similar API to Jellyfin
        media_items = []
        try:
            response = self.session.get(f"{self.base_url}/Library/VirtualFolders")
            if response.status_code != 200:
                return media_items
            
            folders = response.json()
            
            for folder in folders:
                if folder.get('CollectionType') in ['movies', 'tvshows']:
                    params = {
                        'ParentId': folder.get('ItemId'),
                        'Recursive': 'true',
                        'IncludeItemTypes': 'Movie,Episode'
                    }
                    items_response = self.session.get(f"{self.base_url}/Items", params=params)
                    
                    if items_response.status_code == 200:
                        items = items_response.json().get('Items', [])
                        
                        for item in items:
                            media_item = {
                                'title': item.get('Name', ''),
                                'year': item.get('ProductionYear'),
                                'media_type': 'movie' if item.get('Type') == 'Movie' else 'episode',
                                'emby_id': item.get('Id'),
                                'service_source': 'emby',
                                'poster_url': self._get_poster_url(item.get('Id')),
                                'path': item.get('Path')
                            }
                            media_items.append(media_item)
        
        except Exception as e:
            logging.error(f"Error fetching Emby library: {str(e)}")
        
        return media_items
    
    def _get_poster_url(self, item_id: str) -> Optional[str]:
        if item_id:
            return f"{self.base_url}/Items/{item_id}/Images/Primary?X-Emby-Token={self.api_key}"
        return None

class RadarrService(MediaServiceBase):
    """Radarr integration"""
    
    def __init__(self, base_url: str, api_key: str):
        super().__init__("Radarr", base_url, api_key=api_key)
        self.session.headers.update({'X-Api-Key': api_key})
    
    def get_system_status(self) -> Dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}/api/v3/system/status")
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'version': data.get('version', 'Unknown'),
                    'name': f"Radarr v{data.get('version', 'Unknown')}"
                }
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_media_library(self) -> List[Dict[str, Any]]:
        media_items = []
        try:
            response = self.session.get(f"{self.base_url}/api/v3/movie")
            if response.status_code == 200:
                movies = response.json()
                
                for movie in movies:
                    if movie.get('hasFile', False):
                        media_item = {
                            'title': movie.get('title', ''),
                            'year': movie.get('year'),
                            'media_type': 'movie',
                            'radarr_id': movie.get('id'),
                            'tmdb_id': movie.get('tmdbId'),
                            'imdb_id': movie.get('imdbId'),
                            'service_source': 'radarr',
                            'poster_url': self._get_poster_url(movie.get('images', [])),
                            'path': movie.get('movieFile', {}).get('path') if movie.get('movieFile') else None
                        }
                        media_items.append(media_item)
        
        except Exception as e:
            logging.error(f"Error fetching Radarr library: {str(e)}")
        
        return media_items
    
    def _get_poster_url(self, images: List[Dict]) -> Optional[str]:
        for image in images:
            if image.get('coverType') == 'poster':
                return image.get('url')
        return None

class SonarrService(MediaServiceBase):
    """Sonarr integration"""
    
    def __init__(self, base_url: str, api_key: str):
        super().__init__("Sonarr", base_url, api_key=api_key)
        self.session.headers.update({'X-Api-Key': api_key})
    
    def get_system_status(self) -> Dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}/api/v3/system/status")
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'version': data.get('version', 'Unknown'),
                    'name': f"Sonarr v{data.get('version', 'Unknown')}"
                }
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_media_library(self) -> List[Dict[str, Any]]:
        media_items = []
        try:
            # Get all series
            series_response = self.session.get(f"{self.base_url}/api/v3/series")
            if series_response.status_code != 200:
                return media_items
            
            series_list = series_response.json()
            
            for series in series_list:
                # Get episodes for this series
                episodes_response = self.session.get(
                    f"{self.base_url}/api/v3/episode", 
                    params={'seriesId': series.get('id')}
                )
                
                if episodes_response.status_code == 200:
                    episodes = episodes_response.json()
                    
                    for episode in episodes:
                        if episode.get('hasFile', False):
                            media_item = {
                                'title': f"{series.get('title', '')} - S{episode.get('seasonNumber', 0):02d}E{episode.get('episodeNumber', 0):02d} - {episode.get('title', '')}",
                                'year': series.get('year'),
                                'media_type': 'episode',
                                'sonarr_id': episode.get('id'),
                                'tmdb_id': series.get('tmdbId'),
                                'imdb_id': series.get('imdbId'),
                                'service_source': 'sonarr',
                                'poster_url': self._get_poster_url(series.get('images', [])),
                                'path': episode.get('episodeFile', {}).get('path') if episode.get('episodeFile') else None
                            }
                            media_items.append(media_item)
        
        except Exception as e:
            logging.error(f"Error fetching Sonarr library: {str(e)}")
        
        return media_items
    
    def _get_poster_url(self, images: List[Dict]) -> Optional[str]:
        for image in images:
            if image.get('coverType') == 'poster':
                return image.get('url')
        return None

class MediaServicesManager:
    """Central manager for all media service integrations"""
    
    def __init__(self):
        self.services: Dict[str, MediaServiceBase] = {}
    
    def add_service(self, service_type: str, service: MediaServiceBase):
        """Add a media service"""
        self.services[service_type] = service
    
    def remove_service(self, service_type: str):
        """Remove a media service"""
        if service_type in self.services:
            del self.services[service_type]
    
    def test_service(self, service_type: str) -> Dict[str, Any]:
        """Test connection to a specific service"""
        if service_type not in self.services:
            return {
                'success': False,
                'message': f'Service {service_type} not configured',
                'status': 'not_configured'
            }
        
        return self.services[service_type].test_connection()
    
    def test_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Test connection to all configured services"""
        results = {}
        for service_type, service in self.services.items():
            results[service_type] = service.test_connection()
        return results
    
    def sync_service(self, service_type: str) -> Dict[str, Any]:
        """Sync media library from a specific service"""
        if service_type not in self.services:
            return {
                'success': False,
                'message': f'Service {service_type} not configured',
                'media_count': 0
            }
        
        try:
            media_items = self.services[service_type].get_media_library()
            return {
                'success': True,
                'message': f'Successfully synced {len(media_items)} items from {service_type}',
                'media_count': len(media_items),
                'media_items': media_items
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to sync {service_type}: {str(e)}',
                'media_count': 0
            }
    
    def sync_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Sync media library from all configured services"""
        results = {}
        for service_type in self.services:
            results[service_type] = self.sync_service(service_type)
        return results
    
    def get_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all configured services"""
        return self.test_all_services()

def create_service(service_type: str, base_url: str, api_key: Optional[str] = None, 
                  username: Optional[str] = None, password: Optional[str] = None) -> Optional[MediaServiceBase]:
    """Factory function to create media service instances"""
    service_classes = {
        'plex': PlexService,
        'jellyfin': JellyfinService,
        'emby': EmbyService,
        'radarr': RadarrService,
        'sonarr': SonarrService
    }
    
    if service_type not in service_classes:
        return None
    
    service_class = service_classes[service_type]
    
    # Different services have different authentication methods
    if service_type in ['plex', 'jellyfin', 'emby', 'radarr', 'sonarr']:
        return service_class(base_url, api_key)
    
    return None