# AI Translator API Documentation

Complete API reference for AI Translator REST endpoints.

## Overview

This document provides comprehensive API documentation for AI Translator's RESTful API. All API endpoints require session-based authentication. Login through the web interface to establish a session before making API calls.

## Base URL

```
http://localhost:5000
```

## Authentication

All API endpoints require session-based authentication. Login through the web interface at `/login` to establish an authenticated session.

## API Endpoints

### System Status

#### GET /api/status

Returns current system status and translation progress.

**Response:**
```json
{
  "status": "idle|processing|error",
  "progress": 75.5,
  "current_file": "/path/to/video.mp4",
  "total_files": 10,
  "files_done": 7,
  "is_running": true,
  "log_tail": "Latest log entries..."
}
```

### Media Files Management

#### GET /api/files

Returns paginated list of media files with filtering options.

**Parameters:**
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 24)
- `search` (string): Search query
- `media_type` (string): Filter by type ('movie', 'tv')
- `status` (string): Filter by status ('translated', 'untranslated', 'all')

**Response:**
```json
{
  "files": [
    {
      "id": 1,
      "title": "Movie Title",
      "file_path": "/path/to/movie.mp4",
      "poster_url": "http://example.com/poster.jpg",
      "media_type": "movie",
      "translation_status": "translated",
      "file_size": 1073741824,
      "duration": 7200,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 24,
  "pages": 5
}
```

### System Monitoring

#### GET /api/system-monitor-stats

Returns real-time system resource statistics.

**Response:**
```json
{
  "cpu": {
    "usage": 45.2,
    "cores": 8,
    "frequency": 2400
  },
  "memory": {
    "total": 16777216,
    "used": 8388608,
    "available": 8388608,
    "percent": 50.0
  },
  "disk": {
    "total": 1073741824000,
    "used": 536870912000,
    "free": 536870912000,
    "percent": 50.0
  },
  "gpu": [
    {
      "id": 0,
      "name": "NVIDIA RTX 4090",
      "memory_total": 24576,
      "memory_used": 8192,
      "utilization": 75,
      "temperature": 65
    }
  ]
}
```

### Log Management

#### GET /api/get_log

Retrieves system or translation logs.

**Parameters:**
- `log_type` (string): Type of log ('system' or 'translation')
- `limit` (int): Maximum number of entries (default: 100)

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "timestamp": "2025-01-01T12:00:00Z",
      "level": "INFO",
      "message": "Translation completed successfully",
      "details": "Additional log details"
    }
  ],
  "total": 500,
  "log_type": "system"
}
```

#### POST /api/clear_log

Clears all log entries of specified type.

**Request Body:**
```json
{
  "log_type": "system"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Logs cleared successfully"
}
```

### Translation Operations

#### POST /api/translation_logs

Retrieves translation-specific log entries.

**Response:**
```json
{
  "logs": [
    {
      "id": 1,
      "file_path": "/path/to/video.mp4",
      "file_name": "movie.mp4",
      "status": "completed",
      "progress": 100.0,
      "error_message": null,
      "started_at": "2025-01-01T12:00:00Z",
      "completed_at": "2025-01-01T12:30:00Z"
    }
  ]
}
```

### Notifications

#### GET /api/notifications

Returns list of system notifications.

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "title": "Translation Complete",
      "message": "Movie translation finished successfully",
      "type": "success",
      "read": false,
      "created_at": "2025-01-01T12:00:00Z"
    }
  ],
  "unread_count": 5
}
```

#### GET /api/notifications/count

Returns count of unread notifications.

**Response:**
```json
{
  "count": 5
}
```

#### PUT /api/notifications/<id>/read

Marks a notification as read.

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

### Database Administration

#### GET /api/database/stats

Returns database statistics and information.

**Response:**
```json
{
  "tables": [
    {
      "name": "media_files",
      "row_count": 1250,
      "size": "15.2 MB"
    },
    {
      "name": "translation_logs",
      "row_count": 3500,
      "size": "8.7 MB"
    }
  ],
  "total_size": "45.8 MB",
  "database_version": "PostgreSQL 14.9"
}
```

#### GET /api/database/tables

Returns list of database tables with details.

**Response:**
```json
{
  "tables": [
    {
      "name": "media_files",
      "columns": [
        {"name": "id", "type": "integer", "nullable": false},
        {"name": "title", "type": "varchar", "nullable": true},
        {"name": "file_path", "type": "text", "nullable": false}
      ]
    }
  ]
}
```

#### POST /api/database/query

Executes a SQL query against the database.

**Request Body:**
```json
{
  "query": "SELECT COUNT(*) FROM media_files WHERE translation_status = 'completed'"
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {"count": 450}
  ],
  "rows_affected": 1,
  "execution_time": 0.025
}
```

### GPU Management

#### GET /api/gpu/status

Returns GPU status and allocation information.

**Response:**
```json
{
  "gpus": [
    {
      "id": 0,
      "name": "NVIDIA RTX 4090",
      "memory_total": 24576,
      "memory_used": 8192,
      "memory_free": 16384,
      "utilization": 75,
      "temperature": 65,
      "power_draw": 350.5,
      "allocated_services": ["whisper", "ollama"]
    }
  ],
  "allocation": {
    "whisper_gpu": 0,
    "ollama_gpu": 0
  }
}
```

#### POST /api/gpu/allocate

Allocates GPUs to specific services.

**Request Body:**
```json
{
  "whisper_gpu": 0,
  "ollama_gpu": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "GPU allocation updated successfully",
  "allocation": {
    "whisper_gpu": 0,
    "ollama_gpu": 1
  }
}
```

### Media Services Integration

#### GET /api/media-services/status

Returns status of all configured media services.

**Response:**
```json
{
  "services": [
    {
      "type": "plex",
      "name": "Plex Media Server",
      "status": "connected",
      "url": "http://localhost:32400",
      "last_sync": "2025-01-01T12:00:00Z",
      "media_count": 1250
    },
    {
      "type": "radarr",
      "name": "Radarr Movie Manager",
      "status": "connected",
      "url": "http://localhost:7878",
      "last_sync": "2025-01-01T11:30:00Z",
      "media_count": 450
    }
  ]
}
```

#### POST /api/media-services/test/<service_type>

Tests connection to a specific media service.

**Response:**
```json
{
  "success": true,
  "service_type": "plex",
  "status": "connected",
  "message": "Connection successful",
  "server_info": {
    "name": "My Plex Server",
    "version": "1.32.0",
    "libraries": 5
  }
}
```

#### POST /api/media-services/sync/<service_type>

Syncs media from a specific service.

**Response:**
```json
{
  "success": true,
  "service_type": "radarr",
  "synced_files": 25,
  "message": "Sync completed successfully"
}
```

### User Preferences

#### GET /api/user/theme

Returns current user theme preference.

**Response:**
```json
{
  "theme": "dark"
}
```

#### POST /api/user/theme

Updates user theme preference.

**Request Body:**
```json
{
  "theme": "dark"
}
```

**Response:**
```json
{
  "success": true,
  "theme": "dark"
}
```

#### GET /api/user/language

Returns current user language preference.

**Response:**
```json
{
  "language": "ar"
}
```

#### POST /api/user/language

Updates user language preference.

**Request Body:**
```json
{
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "language": "en"
}
```

### Action Endpoints

#### POST /action/start-batch

Starts batch translation process.

**Response:**
```json
{
  "success": true,
  "message": "Batch translation started",
  "task_id": "batch_translate_123"
}
```

#### POST /action/stop

Stops current translation process.

**Response:**
```json
{
  "success": true,
  "message": "Translation process stopped"
}
```

#### POST /action/sync-library

Syncs media library from configured services.

**Response:**
```json
{
  "success": true,
  "message": "Library sync started",
  "task_id": "sync_library_456"
}
```

#### POST /action/scan-translation-status

Scans all media files and updates translation status.

**Response:**
```json
{
  "success": true,
  "message": "Translation status scan started",
  "task_id": "scan_status_789"
}
```

### File Browser

#### GET /api/browse-folders

Browse filesystem folders for path selection.

**Parameters:**
- `path` (string): Current directory path (default: "/")

**Response:**
```json
{
  "current_path": "/mnt/media",
  "folders": [
    {
      "name": "movies",
      "path": "/mnt/media/movies",
      "type": "directory"
    },
    {
      "name": "tv",
      "path": "/mnt/media/tv", 
      "type": "directory"
    }
  ],
  "parent_path": "/mnt"
}
```

## Error Handling

All API endpoints return standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (not logged in)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a JSON object with error details:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": "Additional error details"
}
```

## Rate Limiting

API endpoints are not currently rate-limited, but it's recommended to avoid excessive requests to prevent server overload.

## WebSocket Support

The application supports real-time updates through WebSocket connections for:
- Translation progress updates
- System status changes
- New notifications

Connect to: `ws://localhost:5000/ws`

## Examples

### Python Example

```python
import requests

# Login first
session = requests.Session()
login_data = {'username': 'admin', 'password': 'your_strong_password'}
session.post('http://localhost:5000/login', data=login_data)

# Get system status
response = session.get('http://localhost:5000/api/status')
status = response.json()
print(f"System status: {status['status']}")

# Start batch translation
response = session.post('http://localhost:5000/action/start-batch')
print(f"Batch started: {response.json()['success']}")
```

### JavaScript Example

```javascript
// Get system status
fetch('/api/status')
  .then(response => response.json())
  .then(data => {
    console.log('System status:', data.status);
    console.log('Progress:', data.progress + '%');
  });

// Start batch translation
fetch('/action/start-batch', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  }
})
.then(response => response.json())
.then(data => {
  console.log('Batch translation started:', data.success);
});
```

## Changelog

- **v2.2.1**: Added GPU management endpoints, enhanced media services API
- **v2.2.0**: Added database administration endpoints, improved error handling
- **v2.1.0**: Initial API documentation, basic CRUD operations