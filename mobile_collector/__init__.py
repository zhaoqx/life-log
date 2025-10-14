"""
Mobile Collector - 手机信息采集到OneNote和OneDrive

这个包提供了将手机上的文章、文件和照片同步到Microsoft OneNote和OneDrive的功能。
"""

__version__ = '1.0.0'
__author__ = 'zhaoqx'

from .auth import MicrosoftAuthenticator
from .onenote_service import OneNoteService
from .onedrive_service import OneDriveService
from .config import Config

__all__ = [
    'MicrosoftAuthenticator',
    'OneNoteService',
    'OneDriveService',
    'Config',
]
