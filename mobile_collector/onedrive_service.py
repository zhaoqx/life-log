"""
OneDrive服务模块

提供OneDrive文件上传和管理功能。
"""

import os
import requests
from typing import Optional, Dict, List


class OneDriveService:
    """OneDrive服务类"""
    
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, authenticator):
        """
        初始化OneDrive服务
        
        Args:
            authenticator: MicrosoftAuthenticator实例
        """
        self.authenticator = authenticator
    
    def _get_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        token = self.authenticator.get_access_token()
        if not token:
            raise Exception("未认证或令牌已过期，请先执行认证")
        
        return {
            "Authorization": f"Bearer {token}",
        }
    
    def list_files(self, folder_path: Optional[str] = None) -> List[Dict]:
        """
        列出文件夹中的文件
        
        Args:
            folder_path: 文件夹路径，如果为None则列出根目录
            
        Returns:
            文件列表
        """
        if folder_path:
            # 移除开头的斜杠
            folder_path = folder_path.lstrip('/')
            url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/{folder_path}:/children"
        else:
            url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root/children"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"列出文件失败: {e}")
            raise
    
    def create_folder(self, folder_path: str) -> Dict:
        """
        创建文件夹
        
        Args:
            folder_path: 文件夹路径（从根目录开始）
            
        Returns:
            创建的文件夹信息
        """
        folder_path = folder_path.lstrip('/')
        parts = folder_path.split('/')
        
        # 逐级创建文件夹
        current_path = ""
        folder_info = None
        
        for part in parts:
            parent_path = current_path if current_path else ""
            
            # 检查文件夹是否已存在
            try:
                if parent_path:
                    check_url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/{parent_path}/{part}"
                else:
                    check_url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/{part}"
                
                response = requests.get(check_url, headers=self._get_headers())
                if response.status_code == 200:
                    folder_info = response.json()
                    current_path = f"{parent_path}/{part}" if parent_path else part
                    continue
            except:
                pass
            
            # 创建文件夹
            if parent_path:
                url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/{parent_path}:/children"
            else:
                url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root/children"
            
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            
            data = {
                "name": part,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }
            
            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                folder_info = response.json()
                current_path = f"{parent_path}/{part}" if parent_path else part
            except requests.exceptions.RequestException as e:
                print(f"创建文件夹失败: {e}")
                raise
        
        return folder_info
    
    def upload_file(
        self, 
        file_path: str, 
        target_folder: Optional[str] = None,
        target_filename: Optional[str] = None
    ) -> Dict:
        """
        上传文件到OneDrive
        
        Args:
            file_path: 本地文件路径
            target_folder: 目标文件夹路径（从根目录开始），如果为None则上传到根目录
            target_filename: 目标文件名，如果为None则使用原文件名
            
        Returns:
            上传的文件信息
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 获取文件名
        filename = target_filename or os.path.basename(file_path)
        
        # 确保目标文件夹存在
        if target_folder:
            target_folder = target_folder.lstrip('/')
            self.create_folder(target_folder)
            upload_path = f"{target_folder}/{filename}"
        else:
            upload_path = filename
        
        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 构建上传URL
        url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/{upload_path}:/content"
        
        headers = self._get_headers()
        headers["Content-Type"] = "application/octet-stream"
        
        try:
            print(f"正在上传文件: {filename}...")
            response = requests.put(url, headers=headers, data=file_content)
            response.raise_for_status()
            print(f"文件上传成功: {filename}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"上传文件失败: {e}")
            if hasattr(e.response, 'text'):
                print(f"错误详情: {e.response.text}")
            raise
    
    def upload_files(
        self, 
        file_paths: List[str], 
        target_folder: Optional[str] = None
    ) -> List[Dict]:
        """
        批量上传文件
        
        Args:
            file_paths: 本地文件路径列表
            target_folder: 目标文件夹路径
            
        Returns:
            上传的文件信息列表
        """
        results = []
        
        for file_path in file_paths:
            try:
                result = self.upload_file(file_path, target_folder)
                results.append(result)
            except Exception as e:
                print(f"上传文件 {file_path} 失败: {e}")
                results.append({"error": str(e), "file": file_path})
        
        return results
    
    def get_file_info(self, file_path: str) -> Dict:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径（从根目录开始）
            
        Returns:
            文件信息
        """
        file_path = file_path.lstrip('/')
        url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/{file_path}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取文件信息失败: {e}")
            raise
