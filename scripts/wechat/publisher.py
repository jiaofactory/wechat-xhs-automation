"""
WeChat Official Account Publisher Module
微信公众号发布模块
"""

import json
import time
import requests
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass


@dataclass
class WeChatArticle:
    """微信文章数据结构"""
    title: str
    content: str
    author: str = ""
    digest: str = ""
    content_source_url: str = ""
    thumb_media_id: str = ""
    show_cover_pic: int = 1
    need_open_comment: int = 1
    only_fans_can_comment: int = 0


class WeChatPublisher:
    """微信文章发布器"""
    
    API_BASE = "https://api.weixin.qq.com/cgi-bin"
    
    def __init__(self, auth_manager):
        """
        初始化发布器
        
        Args:
            auth_manager: WeChatAuth实例
        """
        self.auth = auth_manager
        
    def upload_image(self, image_path: str) -> Optional[str]:
        """
        上传图片到微信素材库
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            media_id或None
        """
        token = self.auth.get_access_token()
        if not token:
            return None
            
        url = f"{self.API_BASE}/media/upload"
        params = {
            "access_token": token,
            "type": "image"
        }
        
        try:
            with open(image_path, "rb") as f:
                files = {"media": f}
                response = requests.post(url, params=params, files=files, timeout=60)
                data = response.json()
                
                if "media_id" in data:
                    return data["media_id"]
                else:
                    print(f"[WeChatPublisher] 上传图片失败: {data}")
                    return None
                    
        except Exception as e:
            print(f"[WeChatPublisher] 上传异常: {e}")
            return None
    
    def upload_news_image(self, image_path: str) -> Optional[str]:
        """
        上传图文消息内的图片（获取URL）
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            图片URL或None
        """
        token = self.auth.get_access_token()
        if not token:
            return None
            
        url = f"{self.API_BASE}/media/uploadimg"
        params = {"access_token": token}
        
        try:
            with open(image_path, "rb") as f:
                files = {"media": f}
                response = requests.post(url, params=params, files=files, timeout=60)
                data = response.json()
                
                if "url" in data:
                    return data["url"]
                else:
                    print(f"[WeChatPublisher] 上传图文图片失败: {data}")
                    return None
                    
        except Exception as e:
            print(f"[WeChatPublisher] 上传异常: {e}")
            return None
    
    def upload_thumb_media(self, image_path: str) -> Optional[str]:
        """
        上传缩略图（封面图）
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            thumb_media_id或None
        """
        token = self.auth.get_access_token()
        if not token:
            return None
            
        url = f"{self.API_BASE}/media/upload"
        params = {
            "access_token": token,
            "type": "thumb"
        }
        
        try:
            with open(image_path, "rb") as f:
                files = {"media": f}
                response = requests.post(url, params=params, files=files, timeout=60)
                data = response.json()
                
                if "thumb_media_id" in data:
                    return data["thumb_media_id"]
                elif "media_id" in data:
                    return data["media_id"]
                else:
                    print(f"[WeChatPublisher] 上传缩略图失败: {data}")
                    return None
                    
        except Exception as e:
            print(f"[WeChatPublisher] 上传异常: {e}")
            return None
    
    def create_article(self, article: WeChatArticle) -> Optional[str]:
        """
        创建图文消息素材
        
        Args:
            article: 文章数据对象
            
        Returns:
            media_id或None
        """
        token = self.auth.get_access_token()
        if not token:
            return None
            
        url = f"{self.API_BASE}/material/add_news"
        params = {"access_token": token}
        
        articles_data = {
            "articles": [{
                "title": article.title,
                "thumb_media_id": article.thumb_media_id,
                "author": article.author,
                "digest": article.digest,
                "show_cover_pic": article.show_cover_pic,
                "content": article.content,
                "content_source_url": article.content_source_url,
                "need_open_comment": article.need_open_comment,
                "only_fans_can_comment": article.only_fans_can_comment
            }]
        }
        
        try:
            response = requests.post(
                url, 
                params=params, 
                data=json.dumps(articles_data, ensure_ascii=False).encode("utf-8"),
                timeout=60
            )
            data = response.json()
            
            if "media_id" in data:
                return data["media_id"]
            else:
                print(f"[WeChatPublisher] 创建文章失败: {data}")
                return None
                
        except Exception as e:
            print(f"[WeChatPublisher] 创建异常: {e}")
            return None
    
    def preview_article(self, media_id: str, to_wxname: str) -> bool:
        """
        预览图文消息
        
        Args:
            media_id: 素材ID
            to_wxname: 接收预览的微信号
            
        Returns:
            是否发送成功
        """
        token = self.auth.get_access_token()
        if not token:
            return False
            
        url = f"{self.API_BASE}/message/mass/preview"
        params = {"access_token": token}
        
        data = {
            "touser": to_wxname,
            "mpnews": {
                "media_id": media_id
            },
            "msgtype": "mpnews"
        }
        
        try:
            response = requests.post(
                url,
                params=params,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                timeout=60
            )
            result = response.json()
            
            if result.get("errcode") == 0:
                return True
            else:
                print(f"[WeChatPublisher] 预览发送失败: {result}")
                return False
                
        except Exception as e:
            print(f"[WeChatPublisher] 预览异常: {e}")
            return False
    
    def publish_article(self, media_id: str, group_id: Optional[str] = None,
                       tag_id: Optional[int] = None, 
                       send_ignore_reprint: int = 0) -> Optional[str]:
        """
        群发图文消息
        
        Args:
            media_id: 素材ID
            group_id: 分组ID（按分组群发）
            tag_id: 标签ID（按标签群发）
            send_ignore_reprint: 是否忽略转载检查
            
        Returns:
            msg_id或None
        """
        token = self.auth.get_access_token()
        if not token:
            return None
            
        url = f"{self.API_BASE}/message/mass/sendall"
        params = {"access_token": token}
        
        # 构建filter
        if tag_id is not None:
            filter_data = {"is_to_all": False, "tag_id": tag_id}
        elif group_id is not None:
            filter_data = {"is_to_all": False, "group_id": group_id}
        else:
            filter_data = {"is_to_all": True}
            
        data = {
            "filter": filter_data,
            "mpnews": {
                "media_id": media_id
            },
            "msgtype": "mpnews",
            "send_ignore_reprint": send_ignore_reprint
        }
        
        try:
            response = requests.post(
                url,
                params=params,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                timeout=60
            )
            result = response.json()
            
            if "msg_id" in result:
                return result["msg_id"]
            else:
                print(f"[WeChatPublisher] 群发失败: {result}")
                return None
                
        except Exception as e:
            print(f"[WeChatPublisher] 群发异常: {e}")
            return None
    
    def delete_article(self, msg_id: str, article_idx: int = 0) -> bool:
        """
        删除群发消息
        
        Args:
            msg_id: 消息ID
            article_idx: 要删除的文章在图文消息中的位置，第一篇为0
            
        Returns:
            是否删除成功
        """
        token = self.auth.get_access_token()
        if not token:
            return False
            
        url = f"{self.API_BASE}/message/mass/delete"
        params = {"access_token": token}
        
        data = {
            "msg_id": msg_id,
            "article_idx": article_idx
        }
        
        try:
            response = requests.post(
                url,
                params=params,
                data=json.dumps(data),
                timeout=30
            )
            result = response.json()
            return result.get("errcode") == 0
            
        except Exception as e:
            print(f"[WeChatPublisher] 删除异常: {e}")
            return False
    
    def get_mass_status(self, msg_id: str) -> Dict[str, Any]:
        """
        查询群发消息状态
        
        Args:
            msg_id: 消息ID
            
        Returns:
            状态信息
        """
        token = self.auth.get_access_token()
        if not token:
            return {}
            
        url = f"{self.API_BASE}/message/mass/get"
        params = {"access_token": token}
        
        data = {"msg_id": msg_id}
        
        try:
            response = requests.post(
                url,
                params=params,
                data=json.dumps(data),
                timeout=30
            )
            return response.json()
            
        except Exception as e:
            print(f"[WeChatPublisher] 查询异常: {e}")
            return {}
    
    def publish_simple_text(self, content: str, 
                           group_id: Optional[str] = None) -> Optional[str]:
        """
        群发纯文本消息
        
        Args:
            content: 文本内容
            group_id: 分组ID
            
        Returns:
            msg_id或None
        """
        token = self.auth.get_access_token()
        if not token:
            return None
            
        url = f"{self.API_BASE}/message/mass/sendall"
        params = {"access_token": token}
        
        if group_id is not None:
            filter_data = {"is_to_all": False, "group_id": group_id}
        else:
            filter_data = {"is_to_all": True}
            
        data = {
            "filter": filter_data,
            "text": {"content": content},
            "msgtype": "text"
        }
        
        try:
            response = requests.post(
                url,
                params=params,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                timeout=60
            )
            result = response.json()
            
            if "msg_id" in result:
                return result["msg_id"]
            else:
                print(f"[WeChatPublisher] 文本群发失败: {result}")
                return None
                
        except Exception as e:
            print(f"[WeChatPublisher] 文本群发异常: {e}")
            return None
