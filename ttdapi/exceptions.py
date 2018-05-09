import requests

class TTDClientError(Exception):
    """Base exception for this library"""

class TTDApiError(TTDClientError):
    """All api business errors"""

class TTDApiPermissionsError(TTDApiError):
    """raise on 401"""
