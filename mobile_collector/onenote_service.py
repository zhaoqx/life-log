"""
OneNote服务模块

提供OneNote笔记本和页面的操作功能。
"""

import requests
from typing import Optional, Dict, List


class OneNoteService:
    """OneNote服务类"""
    
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, authenticator):
        """
        初始化OneNote服务
        
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
            "Content-Type": "application/json"
        }
    
    def list_notebooks(self) -> List[Dict]:
        """
        列出所有笔记本
        
        Returns:
            笔记本列表
        """
        url = f"{self.GRAPH_API_ENDPOINT}/me/onenote/notebooks"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"获取笔记本列表失败: {e}")
            raise
    
    def get_default_notebook(self) -> Optional[Dict]:
        """
        获取默认笔记本（第一个笔记本）
        
        Returns:
            笔记本信息字典，如果没有笔记本则返回 None
        """
        notebooks = self.list_notebooks()
        return notebooks[0] if notebooks else None
    
    def list_sections(self, notebook_id: str) -> List[Dict]:
        """
        列出指定笔记本的所有分区
        
        Args:
            notebook_id: 笔记本ID
            
        Returns:
            分区列表
        """
        url = f"{self.GRAPH_API_ENDPOINT}/me/onenote/notebooks/{notebook_id}/sections"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get('value', [])
        except requests.exceptions.RequestException as e:
            print(f"获取分区列表失败: {e}")
            raise
    
    def create_page(
        self, 
        title: str, 
        content: str,
        notebook_id: Optional[str] = None,
        section_id: Optional[str] = None
    ) -> Dict:
        """
        创建OneNote页面
        
        Args:
            title: 页面标题
            content: 页面内容（纯文本，将被转换为HTML）
            notebook_id: 笔记本ID（可选）
            section_id: 分区ID（可选，如果提供则notebook_id被忽略）
            
        Returns:
            创建的页面信息
        """
        # 如果没有指定section_id，则使用默认笔记本的第一个分区
        if not section_id:
            if not notebook_id:
                notebook = self.get_default_notebook()
                if not notebook:
                    raise Exception("没有可用的笔记本，请先在OneNote中创建笔记本")
                notebook_id = notebook['id']
            
            sections = self.list_sections(notebook_id)
            if not sections:
                raise Exception(f"笔记本 {notebook_id} 中没有分区，请先创建分区")
            section_id = sections[0]['id']
        
        # 构建HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <meta name="created" content="{self._get_current_time()}" />
        </head>
        <body>
            <h1>{title}</h1>
            <div>{self._text_to_html(content)}</div>
        </body>
        </html>
        """
        
        url = f"{self.GRAPH_API_ENDPOINT}/me/onenote/sections/{section_id}/pages"
        
        headers = self._get_headers()
        headers["Content-Type"] = "application/xhtml+xml"
        
        try:
            response = requests.post(url, headers=headers, data=html_content.encode('utf-8'))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"创建页面失败: {e}")
            if hasattr(e.response, 'text'):
                print(f"错误详情: {e.response.text}")
            raise
    
    def _text_to_html(self, text: str) -> str:
        """将纯文本转换为HTML（保留换行）"""
        # 转义HTML特殊字符
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        
        # 将换行转换为<br>
        text = text.replace('\n', '<br/>')
        
        return text
    
    def _get_current_time(self) -> str:
        """获取当前时间的ISO格式字符串"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
    
    def get_page(self, page_id: str) -> Dict:
        """
        获取页面信息
        
        Args:
            page_id: 页面ID
            
        Returns:
            页面信息
        """
        url = f"{self.GRAPH_API_ENDPOINT}/me/onenote/pages/{page_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取页面失败: {e}")
            raise
