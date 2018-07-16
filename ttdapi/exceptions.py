import requests

class TTDClientError(Exception):
    """Base exception for this library"""

class TTDApiError(TTDClientError):
    """All api business errors"""
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response', None)
        super().__init__(*args, **kwargs)

class TTDApiPermissionsError(TTDApiError):
    """raise on 401"""
