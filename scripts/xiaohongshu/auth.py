"""
XiaoHongShu (Little Red Book) Authentication Module
小红书认证模块
"""

import re
import json
import time
import hashlib
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode, parse_qs, urlparse


class XHSAuth:
    """小红书认证管理器"""
    
    API_BASE = "https://edith.xiaohongshu.com"
    WEB_BASE = "https://www.xiaohongshu.com"
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化认证器
        
        Args:
            config: 配置字典，包含phone, password等
        """
        self.phone = config.get("phone")
        self.password = config.get("password")
        self.device_id = config.get("device_id") or self._generate_device_id()
        self.user_agent = config.get(
            "user_agent", 
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "X-Sign": "",
            "X-Timestamp": "",
            "X-Device-Id": self.device_id
        })
        
        self.user_info: Optional[Dict[str, Any]] = None
        self.cookies: Dict[str, str] = {}
        self.is_logged_in = False
        
    def _generate_device_id(self) -> str:
        """生成设备ID"""
        import uuid
        return str(uuid.uuid4()).replace("-", "")[:16]
    
    def _generate_sign(self, params: Dict[str, Any], data: Optional[str] = None) -> str:
        """
        生成API签名
        
        Args:
            params: URL参数
            data: 请求体数据
            
        Returns:
            签名字符串
        """
        # 小红书签名算法（简化版）
        sorted_params = sorted(params.items())
        param_str = urlencode(sorted_params)
        
        if data:
            param_str += data
            
        # 添加密钥（实际使用需要逆向获取）
        secret = "your_secret_key_here"
        sign_str = param_str + secret
        
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def _update_sign_headers(self, params: Dict[str, Any], data: Optional[str] = None):
        """更新签名头"""
        timestamp = str(int(time.time()))
        self.session.headers["X-Timestamp"] = timestamp
        
        sign_params = {**params, "timestamp": timestamp, "deviceId": self.device_id}
        sign = self._generate_sign(sign_params, data)
        self.session.headers["X-Sign"] = sign
    
    def send_sms_code(self, phone: Optional[str] = None) -> bool:
        """
        发送短信验证码
        
        Args:
            phone: 手机号（默认使用配置中的手机号）
            
        Returns:
            是否发送成功
        """
        phone = phone or self.phone
        if not phone:
            print("[XHSAuth] 未提供手机号")
            return False
            
        url = f"{self.API_BASE}/api/sns/send_code"
        
        params = {
            "zone": "86",
            "phone": phone,
            "type": "login"
        }
        
        self._update_sign_headers(params)
        
        try:
            response = self.session.post(url, data=params, timeout=30)
            data = response.json()
            
            if data.get("success"):
                print(f"[XHSAuth] 验证码已发送至 {phone}")
                return True
            else:
                print(f"[XHSAuth] 发送失败: {data.get('msg')}")
                return False
                
        except Exception as e:
            print(f"[XHSAuth] 请求异常: {e}")
            return False
    
    def login_with_sms(self, phone: str, sms_code: str) -> bool:
        """
        使用短信验证码登录
        
        Args:
            phone: 手机号
            sms_code: 短信验证码
            
        Returns:
            是否登录成功
        """
        url = f"{self.API_BASE}/api/sns/login"
        
        params = {
            "phone": phone,
            "code": sms_code,
            "zone": "86"
        }
        
        self._update_sign_headers(params)
        
        try:
            response = self.session.post(url, data=params, timeout=30)
            data = response.json()
            
            if data.get("success"):
                self.user_info = data.get("data", {})
                self.is_logged_in = True
                self.cookies = dict(self.session.cookies)
                print(f"[XHSAuth] 登录成功: {self.user_info.get('nickname', 'Unknown')}")
                return True
            else:
                print(f"[XHSAuth] 登录失败: {data.get('msg')}")
                return False
                
        except Exception as e:
            print(f"[XHSAuth] 登录异常: {e}")
            return False
    
    def login_with_password(self, phone: Optional[str] = None, 
                           password: Optional[str] = None) -> bool:
        """
        使用密码登录
        
        Args:
            phone: 手机号
            password: 密码
            
        Returns:
            是否登录成功
        """
        phone = phone or self.phone
        password = password or self.password
        
        if not phone or not password:
            print("[XHSAuth] 缺少手机号或密码")
            return False
            
        # 小红书密码登录需要处理加密
        # 这里使用简化版流程，实际可能需要滑块验证
        
        url = f"{self.API_BASE}/api/sns/login"
        
        params = {
            "phone": phone,
            "password": password,
            "zone": "86"
        }
        
        self._update_sign_headers(params)
        
        try:
            response = self.session.post(url, data=params, timeout=30)
            data = response.json()
            
            if data.get("success"):
                self.user_info = data.get("data", {})
                self.is_logged_in = True
                self.cookies = dict(self.session.cookies)
                print(f"[XHSAuth] 登录成功: {self.user_info.get('nickname', 'Unknown')}")
                return True
            else:
                # 可能需要验证码或其他验证
                error_msg = data.get("msg", "")
                if "验证码" in error_msg or "captcha" in error_msg.lower():
                    print("[XHSAuth] 需要验证码处理")
                    return self._handle_captcha(data)
                else:
                    print(f"[XHSAuth] 登录失败: {error_msg}")
                    return False
                
        except Exception as e:
            print(f"[XHSAuth] 登录异常: {e}")
            return False
    
    def _handle_captcha(self, data: Dict[str, Any]) -> bool:
        """
        处理验证码
        
        Args:
            data: 包含验证码信息的响应数据
            
        Returns:
            是否处理成功
        """
        # 这里可以集成captcha-solver Skill
        print("[XHSAuth] 检测到验证码，需要手动处理或使用captcha-solver")
        return False
    
    def login_with_cookies(self, cookies: Dict[str, str]) -> bool:
        """
        使用Cookie登录
        
        Args:
            cookies: Cookie字典
            
        Returns:
            是否登录成功
        """
        self.session.cookies.update(cookies)
        self.cookies = cookies
        
        # 验证登录状态
        if self.check_login_status():
            self.is_logged_in = True
            print("[XHSAuth] Cookie登录成功")
            return True
        else:
            print("[XHSAuth] Cookie已失效")
            return False
    
    def check_login_status(self) -> bool:
        """
        检查登录状态
        
        Returns:
            是否已登录
        """
        url = f"{self.API_BASE}/api/sns/user/info"
        
        params = {}
        self._update_sign_headers(params)
        
        try:
            response = self.session.get(url, timeout=30)
            data = response.json()
            
            if data.get("success") and data.get("data"):
                self.user_info = data.get("data", {})
                return True
            else:
                return False
                
        except Exception as e:
            print(f"[XHSAuth] 检查状态异常: {e}")
            return False
    
    def refresh_login(self) -> bool:
        """
        刷新登录状态
        
        Returns:
            是否刷新成功
        """
        if self.cookies:
            # 尝试使用现有cookie
            return self.login_with_cookies(self.cookies)
        elif self.phone and self.password:
            # 重新登录
            return self.login_with_password()
        else:
            print("[XHSAuth] 无法刷新登录：缺少凭证")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        获取用户信息
        
        Returns:
            用户信息字典
        """
        if not self.is_logged_in:
            return None
            
        return self.user_info
    
    def get_cookies(self) -> Dict[str, str]:
        """
        获取当前Cookies
        
        Returns:
            Cookie字典
        """
        return dict(self.session.cookies)
    
    def logout(self) -> bool:
        """
        登出
        
        Returns:
            是否登出成功
        """
        url = f"{self.API_BASE}/api/sns/logout"
        
        try:
            response = self.session.post(url, timeout=30)
            self.is_logged_in = False
            self.user_info = None
            self.cookies = {}
            self.session.cookies.clear()
            print("[XHSAuth] 已登出")
            return True
            
        except Exception as e:
            print(f"[XHSAuth] 登出异常: {e}")
            return False


class XHSWebAuth:
    """小红书网页版认证"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        
        self.qr_url: Optional[str] = None
        self.qr_key: Optional[str] = None
        self.is_logged_in = False
        
    def get_qr_code(self) -> Optional[str]:
        """
        获取二维码
        
        Returns:
            二维码图片URL
        """
        url = f"https://www.xiaohongshu.com/web-login/captcha"
        
        try:
            response = self.session.get(url, timeout=30)
            # 解析二维码数据
            # 实际实现需要逆向网页登录流程
            
            print("[XHSWebAuth] 请访问小红书网页版手动登录后导出Cookie")
            return None
            
        except Exception as e:
            print(f"[XHSWebAuth] 获取二维码异常: {e}")
            return None
    
    def check_qr_status(self) -> Dict[str, Any]:
        """
        检查二维码扫描状态
        
        Returns:
            状态信息
        """
        # 实现二维码状态检查
        return {"status": "waiting"}
    
    def import_cookies_from_browser(self, cookie_string: str) -> bool:
        """
        从浏览器导入Cookie
        
        Args:
            cookie_string: Cookie字符串（从浏览器开发者工具复制）
            
        Returns:
            是否导入成功
        """
        try:
            # 解析Cookie字符串
            cookies = {}
            for item in cookie_string.split(";"):
                if "=" in item:
                    key, value = item.strip().split("=", 1)
                    cookies[key] = value
                    
            self.session.cookies.update(cookies)
            
            # 验证登录状态
            test_url = "https://www.xiaohongshu.com/api/sns/web/v1/user/selfinfo"
            response = self.session.get(test_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.is_logged_in = True
                    print("[XHSWebAuth] Cookie导入成功")
                    return True
                    
            print("[XHSWebAuth] Cookie无效或已过期")
            return False
            
        except Exception as e:
            print(f"[XHSWebAuth] 导入Cookie异常: {e}")
            return False
