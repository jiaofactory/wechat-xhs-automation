"""
WeChat Official Account Authentication Module
微信公众号认证模块
"""

import time
import json
import base64
import hashlib
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlencode


class WeChatAuth:
    """微信认证管理器"""
    
    API_BASE = "https://api.weixin.qq.com/cgi-bin"
    MP_BASE = "https://mp.weixin.qq.com"
    
    def __init__(self, config: Dict[str, Any]):
        self.app_id = config.get("app_id")
        self.app_secret = config.get("app_secret")
        self.token = config.get("token")
        self.encoding_aes_key = config.get("encoding_aes_key")
        self.auth_method = config.get("auth_method", "api")
        
        self.access_token: Optional[str] = None
        self.token_expire_time: int = 0
        
    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        获取微信access_token
        
        Args:
            force_refresh: 强制刷新token
            
        Returns:
            access_token或None
        """
        # 检查现有token是否有效
        if not force_refresh and self.access_token:
            if time.time() < self.token_expire_time - 300:  # 提前5分钟刷新
                return self.access_token
        
        # 请求新token
        url = f"{self.API_BASE}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if "access_token" in data:
                self.access_token = data["access_token"]
                expires_in = data.get("expires_in", 7200)
                self.token_expire_time = time.time() + expires_in
                return self.access_token
            else:
                print(f"[WeChatAuth] 获取token失败: {data.get('errmsg')}")
                return None
                
        except Exception as e:
            print(f"[WeChatAuth] 请求异常: {e}")
            return None
    
    def refresh_token(self) -> bool:
        """
        刷新access_token
        
        Returns:
            是否刷新成功
        """
        token = self.get_access_token(force_refresh=True)
        return token is not None
    
    def validate_credentials(self) -> bool:
        """
        验证凭证是否有效
        
        Returns:
            凭证是否有效
        """
        token = self.get_access_token()
        if not token:
            return False
            
        # 调用简单API验证token
        url = f"{self.API_BASE}/getcallbackip"
        params = {"access_token": token}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            return "ip_list" in data
        except Exception as e:
            print(f"[WeChatAuth] 验证失败: {e}")
            return False
    
    def get_server_ips(self) -> list:
        """
        获取微信服务器IP列表
        
        Returns:
            IP地址列表
        """
        token = self.get_access_token()
        if not token:
            return []
            
        url = f"{self.API_BASE}/getcallbackip"
        params = {"access_token": token}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            return data.get("ip_list", [])
        except Exception as e:
            print(f"[WeChatAuth] 获取IP列表失败: {e}")
            return []
    
    def verify_signature(self, signature: str, timestamp: str, nonce: str, 
                         echo_str: Optional[str] = None) -> bool:
        """
        验证微信服务器签名
        
        Args:
            signature: 微信传入的签名
            timestamp: 时间戳
            nonce: 随机数
            echo_str: 验证时的echostr
            
        Returns:
            签名是否有效
        """
        tmp_list = [self.token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = "".join(tmp_list)
        
        hashcode = hashlib.sha1(tmp_str.encode()).hexdigest()
        return hashcode == signature
    
    def generate_jsapi_signature(self, jsapi_ticket: str, noncestr: str, 
                                  timestamp: int, url: str) -> str:
        """
        生成JS-SDK签名
        
        Args:
            jsapi_ticket: JSAPI ticket
            noncestr: 随机字符串
            timestamp: 时间戳
            url: 当前网页URL
            
        Returns:
            签名字符串
        """
        data = {
            "jsapi_ticket": jsapi_ticket,
            "noncestr": noncestr,
            "timestamp": str(timestamp),
            "url": url
        }
        
        string1 = urlencode(sorted(data.items()))
        return hashlib.sha1(string1.encode()).hexdigest()
    
    def get_jsapi_ticket(self) -> Optional[str]:
        """
        获取JSAPI ticket
        
        Returns:
            ticket字符串或None
        """
        token = self.get_access_token()
        if not token:
            return None
            
        url = f"{self.API_BASE}/ticket/getticket"
        params = {
            "access_token": token,
            "type": "jsapi"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if data.get("errcode") == 0:
                return data.get("ticket")
            else:
                print(f"[WeChatAuth] 获取ticket失败: {data}")
                return None
                
        except Exception as e:
            print(f"[WeChatAuth] 请求异常: {e}")
            return None


class WeChatWebAuth:
    """微信网页版认证（用于个人号）"""
    
    def __init__(self):
        self.session = requests.Session()
        self.uuid: Optional[str] = None
        self.redirect_url: Optional[str] = None
        self.skey: Optional[str] = None
        self.wxsid: Optional[str] = None
        self.wxuin: Optional[str] = None
        self.pass_ticket: Optional[str] = None
        self.device_id = "e" + str(int(time.time()))
        
    def get_qr_uuid(self) -> Optional[str]:
        """
        获取二维码UUID
        
        Returns:
            UUID字符串
        """
        url = "https://login.wx.qq.com/jslogin"
        params = {
            "appid": "wx782c26e4c19acffb",
            "fun": "new",
            "lang": "zh_CN",
            "_": int(time.time() * 1000)
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            text = response.text
            
            if "window.QRLogin.code = 200" in text:
                self.uuid = text.split('"')[1]
                return self.uuid
            else:
                print(f"[WeChatWebAuth] 获取UUID失败: {text}")
                return None
                
        except Exception as e:
            print(f"[WeChatWebAuth] 请求异常: {e}")
            return None
    
    def get_qr_code_url(self) -> Optional[str]:
        """
        获取二维码URL
        
        Returns:
            二维码图片URL
        """
        if not self.uuid:
            self.get_qr_uuid()
            
        if self.uuid:
            return f"https://login.weixin.qq.com/l/{self.uuid}"
        return None
    
    def check_login_status(self) -> Dict[str, Any]:
        """
        检查登录状态
        
        Returns:
            状态信息字典
        """
        if not self.uuid:
            return {"status": "error", "message": "No UUID"}
            
        url = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login"
        params = {
            "tip": "0",
            "uuid": self.uuid,
            "_": int(time.time() * 1000)
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            text = response.text
            
            if "window.code=200" in text:
                # 登录成功
                redirect_match = text.split('redirect_uri="')[1].split('"')[0]
                self.redirect_url = redirect_match + "&fun=new&version=v2"
                return {"status": "success", "redirect_url": self.redirect_url}
                
            elif "window.code=201" in text:
                # 已扫码，等待确认
                return {"status": "scanned"}
                
            elif "window.code=408" in text:
                # 二维码过期
                return {"status": "expired"}
                
            else:
                return {"status": "waiting"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def complete_login(self) -> bool:
        """
        完成登录流程
        
        Returns:
            是否登录成功
        """
        if not self.redirect_url:
            return False
            
        try:
            response = self.session.get(self.redirect_url, timeout=30)
            
            # 解析返回数据
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            self.skey = root.find("skey").text if root.find("skey") is not None else None
            self.wxsid = root.find("wxsid").text if root.find("wxsid") is not None else None
            self.wxuin = root.find("wxuin").text if root.find("wxuin") is not None else None
            self.pass_ticket = root.find("pass_ticket").text if root.find("pass_ticket") is not None else None
            
            return all([self.skey, self.wxsid, self.wxuin])
            
        except Exception as e:
            print(f"[WeChatWebAuth] 登录完成失败: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """
        检查是否已登录
        
        Returns:
            登录状态
        """
        return all([self.skey, self.wxsid, self.wxuin])
    
    def get_base_request(self) -> Dict[str, Any]:
        """
        获取基础请求参数
        
        Returns:
            基础参数字典
        """
        return {
            "Uin": int(self.wxuin) if self.wxuin else 0,
            "Sid": self.wxsid or "",
            "Skey": self.skey or "",
            "DeviceID": self.device_id
        }
