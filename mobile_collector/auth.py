"""
Microsoft认证模块

使用OAuth 2.0协议进行Microsoft账户认证，获取访问令牌。
"""

import json
import os
import time
from typing import Dict, Optional
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import msal


class MicrosoftAuthenticator:
    """Microsoft认证器"""
    
    TOKEN_CACHE_FILE = '.token_cache.json'
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scopes: list):
        """
        初始化认证器
        
        Args:
            client_id: Microsoft应用程序ID
            client_secret: Microsoft应用程序密钥
            redirect_uri: 重定向URI
            scopes: 请求的权限范围
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        
        # 创建MSAL应用程序实例
        self.app = msal.ConfidentialClientApplication(
            client_id,
            authority="https://login.microsoftonline.com/common",
            client_credential=client_secret,
        )
        
        self._token_cache = self._load_token_cache()
    
    def _load_token_cache(self) -> Dict:
        """从文件加载令牌缓存"""
        cache_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            self.TOKEN_CACHE_FILE
        )
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"警告: 无法加载令牌缓存: {e}")
        
        return {}
    
    def _save_token_cache(self, token_data: Dict):
        """保存令牌缓存到文件"""
        self._token_cache = token_data
        cache_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            self.TOKEN_CACHE_FILE
        )
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            # 设置文件权限为仅所有者可读写
            os.chmod(cache_file, 0o600)
        except Exception as e:
            print(f"警告: 无法保存令牌缓存: {e}")
    
    def get_auth_url(self) -> str:
        """
        获取认证URL
        
        Returns:
            认证URL字符串
        """
        auth_url = self.app.get_authorization_request_url(
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        return auth_url
    
    def authenticate(self) -> bool:
        """
        执行完整的认证流程
        
        Returns:
            True 如果认证成功，否则 False
        """
        print("正在启动认证流程...")
        
        # 获取认证URL
        auth_url = self.get_auth_url()
        print(f"\n请在浏览器中打开以下URL进行认证：")
        print(f"\n{auth_url}\n")
        
        # 尝试自动打开浏览器
        try:
            webbrowser.open(auth_url)
            print("已在浏览器中打开认证页面")
        except:
            print("无法自动打开浏览器，请手动复制上述URL")
        
        # 启动本地服务器接收回调
        auth_code = self._start_callback_server()
        
        if not auth_code:
            print("错误: 未获取到授权码")
            return False
        
        # 使用授权码获取令牌
        return self.get_token_from_code(auth_code)
    
    def _start_callback_server(self) -> Optional[str]:
        """启动本地服务器接收OAuth回调"""
        auth_code = None
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code
                
                # 解析URL获取授权码
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                
                if 'code' in params:
                    auth_code = params['code'][0]
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<html><body><h1>Authentication successful!</h1><p>You can close this window now.</p></body></html>')
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<html><body><h1>Authentication failed!</h1></body></html>')
            
            def log_message(self, format, *args):
                pass  # 禁用日志输出
        
        # 从redirect_uri解析端口
        parsed_uri = urlparse(self.redirect_uri)
        port = parsed_uri.port or 8000
        
        try:
            server = HTTPServer(('localhost', port), CallbackHandler)
            print(f"等待认证回调（端口 {port}）...")
            server.timeout = 120  # 2分钟超时
            server.handle_request()
        except Exception as e:
            print(f"错误: 无法启动回调服务器: {e}")
            return None
        
        return auth_code
    
    def get_token_from_code(self, code: str) -> bool:
        """
        使用授权码获取访问令牌
        
        Args:
            code: 授权码
            
        Returns:
            True 如果成功获取令牌，否则 False
        """
        try:
            result = self.app.acquire_token_by_authorization_code(
                code,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            if "access_token" in result:
                self._save_token_cache(result)
                print("认证成功！")
                return True
            else:
                error = result.get("error", "未知错误")
                error_desc = result.get("error_description", "")
                print(f"认证失败: {error} - {error_desc}")
                return False
                
        except Exception as e:
            print(f"获取令牌时出错: {e}")
            return False
    
    def get_access_token(self) -> Optional[str]:
        """
        获取有效的访问令牌（自动刷新如果需要）
        
        Returns:
            访问令牌字符串，如果无法获取则返回 None
        """
        # 首先尝试从缓存获取令牌
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(
                scopes=self.scopes,
                account=accounts[0]
            )
            if result and "access_token" in result:
                return result["access_token"]
        
        # 如果缓存中有refresh_token，尝试刷新
        if "refresh_token" in self._token_cache:
            try:
                result = self.app.acquire_token_by_refresh_token(
                    self._token_cache["refresh_token"],
                    scopes=self.scopes
                )
                if result and "access_token" in result:
                    self._save_token_cache(result)
                    return result["access_token"]
            except Exception as e:
                print(f"刷新令牌失败: {e}")
        
        # 如果都失败了，需要重新认证
        print("令牌已过期，请重新认证")
        return None
    
    def is_authenticated(self) -> bool:
        """
        检查是否已认证
        
        Returns:
            True 如果已认证且令牌有效，否则 False
        """
        return self.get_access_token() is not None
