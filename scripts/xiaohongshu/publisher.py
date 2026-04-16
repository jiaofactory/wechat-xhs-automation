"""
XiaoHongShu Publisher Module
小红书发布模块
"""

import json
import time
import requests
import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class XHSNote:
    """小红书笔记数据结构"""
    title: str
    content: str
    images: List[str]
    video: Optional[str] = None
    tags: List[str] = None
    location: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class XHSPublisher:
    """小红书笔记发布器"""
    
    API_BASE = "https://edith.xiaohongshu.com"
    
    def __init__(self, auth_manager):
        """
        初始化发布器
        
        Args:
            auth_manager: XHSAuth实例
        """
        self.auth = auth_manager
        
    def _make_request(self, method: str, endpoint: str, 
                     data: Optional[Dict] = None,
                     files: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            method: 请求方法
            endpoint: API端点
            data: 请求数据
            files: 文件数据
            
        Returns:
            响应数据
        """
        if not self.auth.is_logged_in:
            print("[XHSPublisher] 未登录")
            return {}
            
        url = f"{self.API_BASE}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.auth.session.get(url, params=data, timeout=30)
            elif method.upper() == "POST":
                if files:
                    response = self.auth.session.post(url, data=data, files=files, timeout=60)
                else:
                    response = self.auth.session.post(url, json=data, timeout=30)
            else:
                return {}
                
            return response.json()
            
        except Exception as e:
            print(f"[XHSPublisher] 请求异常: {e}")
            return {}
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """
        上传图片
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            图片URL或None
        """
        if not os.path.exists(image_path):
            print(f"[XHSPublisher] 图片不存在: {image_path}")
            return None
            
        endpoint = "/api/sns/web/v1/upload"
        
        try:
            with open(image_path, "rb") as f:
                files = {"file": f}
                result = self._make_request("POST", endpoint, files=files)
                
                if result.get("success"):
                    data = result.get("data", {})
                    url = data.get("url") or data.get("filepath")
                    print(f"[XHSPublisher] 图片上传成功: {os.path.basename(image_path)}")
                    return url
                else:
                    print(f"[XHSPublisher] 上传失败: {result.get('msg')}")
                    return None
                    
        except Exception as e:
            print(f"[XHSPublisher] 上传异常: {e}")
            return None
    
    def upload_video(self, video_path: str) -> Optional[str]:
        """
        上传视频
        
        Args:
            video_path: 本地视频路径
            
        Returns:
            视频URL或None
        """
        if not os.path.exists(video_path):
            print(f"[XHSPublisher] 视频不存在: {video_path}")
            return None
            
        # 视频上传需要分片处理
        endpoint = "/api/sns/web/v1/upload/video"
        
        try:
            with open(video_path, "rb") as f:
                files = {"file": f}
                result = self._make_request("POST", endpoint, files=files)
                
                if result.get("success"):
                    data = result.get("data", {})
                    url = data.get("url") or data.get("filepath")
                    print(f"[XHSPublisher] 视频上传成功: {os.path.basename(video_path)}")
                    return url
                else:
                    print(f"[XHSPublisher] 视频上传失败: {result.get('msg')}")
                    return None
                    
        except Exception as e:
            print(f"[XHSPublisher] 视频上传异常: {e}")
            return None
    
    def publish_note(self, note: XHSNote) -> Optional[Dict[str, Any]]:
        """
        发布图文笔记
        
        Args:
            note: 笔记数据对象
            
        Returns:
            发布结果或None
        """
        # 先上传所有图片
        uploaded_images = []
        for img_path in note.images:
            url = self.upload_image(img_path)
            if url:
                uploaded_images.append(url)
                
        if not uploaded_images:
            print("[XHSPublisher] 没有成功上传的图片")
            return None
            
        # 构建发布数据
        endpoint = "/api/sns/web/v1/note/post"
        
        # 处理标签
        hashtags = " ".join([f"#{tag}" for tag in note.tags])
        full_content = f"{note.content}\n\n{hashtags}".strip()
        
        # 构建请求数据
        data = {
            "title": note.title,
            "desc": full_content,
            "type": "normal",
            "pics": uploaded_images,
            "cover": uploaded_images[0] if uploaded_images else None,
            "ats": [],
            "topics": [{"name": tag} for tag in note.tags],
            "setting": {
                "private": False,
                "comment": True
            }
        }
        
        if note.location:
            data["location"] = {"name": note.location}
            
        try:
            result = self._make_request("POST", endpoint, data=data)
            
            if result.get("success"):
                note_data = result.get("data", {})
                note_id = note_data.get("note_id") or note_data.get("id")
                print(f"[XHSPublisher] 笔记发布成功: {note_id}")
                return {
                    "note_id": note_id,
                    "title": note.title,
                    "url": f"https://www.xiaohongshu.com/discovery/item/{note_id}",
                    "status": "published"
                }
            else:
                print(f"[XHSPublisher] 发布失败: {result.get('msg')}")
                return None
                
        except Exception as e:
            print(f"[XHSPublisher] 发布异常: {e}")
            return None
    
    def publish_video_note(self, title: str, content: str, 
                          video_path: str,
                          cover_image: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          location: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        发布视频笔记
        
        Args:
            title: 标题
            content: 内容
            video_path: 视频路径
            cover_image: 封面图路径
            tags: 标签列表
            location: 位置信息
            
        Returns:
            发布结果或None
        """
        # 上传视频
        video_url = self.upload_video(video_path)
        if not video_url:
            return None
            
        # 上传封面图
        cover_url = None
        if cover_image:
            cover_url = self.upload_image(cover_image)
            
        # 构建发布数据
        endpoint = "/api/sns/web/v1/note/post"
        
        hashtags = " ".join([f"#{tag}" for tag in (tags or [])])
        full_content = f"{content}\n\n{hashtags}".strip()
        
        data = {
            "title": title,
            "desc": full_content,
            "type": "video",
            "video": video_url,
            "cover": cover_url or video_url,
            "ats": [],
            "topics": [{"name": tag} for tag in (tags or [])],
            "setting": {
                "private": False,
                "comment": True
            }
        }
        
        if location:
            data["location"] = {"name": location}
            
        try:
            result = self._make_request("POST", endpoint, data=data)
            
            if result.get("success"):
                note_data = result.get("data", {})
                note_id = note_data.get("note_id") or note_data.get("id")
                print(f"[XHSPublisher] 视频笔记发布成功: {note_id}")
                return {
                    "note_id": note_id,
                    "title": title,
                    "url": f"https://www.xiaohongshu.com/discovery/item/{note_id}",
                    "status": "published"
                }
            else:
                print(f"[XHSPublisher] 视频发布失败: {result.get('msg')}")
                return None
                
        except Exception as e:
            print(f"[XHSPublisher] 视频发布异常: {e}")
            return None
    
    def delete_note(self, note_id: str) -> bool:
        """
        删除笔记
        
        Args:
            note_id: 笔记ID
            
        Returns:
            是否删除成功
        """
        endpoint = "/api/sns/web/v1/note/delete"
        
        data = {"note_id": note_id}
        
        try:
            result = self._make_request("POST", endpoint, data=data)
            
            if result.get("success"):
                print(f"[XHSPublisher] 笔记已删除: {note_id}")
                return True
            else:
                print(f"[XHSPublisher] 删除失败: {result.get('msg')}")
                return False
                
        except Exception as e:
            print(f"[XHSPublisher] 删除异常: {e}")
            return False
    
    def edit_note(self, note_id: str, 
                  title: Optional[str] = None,
                  content: Optional[str] = None,
                  tags: Optional[List[str]] = None) -> bool:
        """
        编辑笔记
        
        Args:
            note_id: 笔记ID
            title: 新标题
            content: 新内容
            tags: 新标签
            
        Returns:
            是否编辑成功
        """
        endpoint = "/api/sns/web/v1/note/edit"
        
        # 先获取原笔记信息
        original = self.get_note_detail(note_id)
        if not original:
            print("[XHSPublisher] 无法获取原笔记信息")
            return False
            
        # 构建编辑数据
        data = {
            "note_id": note_id,
            "title": title or original.get("title", ""),
            "desc": content or original.get("desc", ""),
            "topics": [{"name": tag} for tag in (tags or original.get("topics", []))],
            "setting": original.get("setting", {"private": False, "comment": True})
        }
        
        try:
            result = self._make_request("POST", endpoint, data=data)
            
            if result.get("success"):
                print(f"[XHSPublisher] 笔记已编辑: {note_id}")
                return True
            else:
                print(f"[XHSPublisher] 编辑失败: {result.get('msg')}")
                return False
                
        except Exception as e:
            print(f"[XHSPublisher] 编辑异常: {e}")
            return False
    
    def get_note_detail(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        获取笔记详情
        
        Args:
            note_id: 笔记ID
            
        Returns:
            笔记详情或None
        """
        endpoint = f"/api/sns/web/v1/feed"
        
        data = {"note_id": note_id}
        
        try:
            result = self._make_request("GET", endpoint, data=data)
            
            if result.get("success"):
                return result.get("data", {})
            else:
                return None
                
        except Exception as e:
            print(f"[XHSPublisher] 获取详情异常: {e}")
            return None
    
    def save_as_draft(self, note: XHSNote) -> Optional[str]:
        """
        保存为草稿
        
        Args:
            note: 笔记数据
            
        Returns:
            草稿ID或None
        """
        # 上传图片
        uploaded_images = []
        for img_path in note.images:
            url = self.upload_image(img_path)
            if url:
                uploaded_images.append(url)
                
        endpoint = "/api/sns/web/v1/note/draft/save"
        
        hashtags = " ".join([f"#{tag}" for tag in note.tags])
        full_content = f"{note.content}\n\n{hashtags}".strip()
        
        data = {
            "title": note.title,
            "desc": full_content,
            "type": "normal",
            "pics": uploaded_images,
            "cover": uploaded_images[0] if uploaded_images else None,
            "topics": [{"name": tag} for tag in note.tags],
            "is_draft": True
        }
        
        try:
            result = self._make_request("POST", endpoint, data=data)
            
            if result.get("success"):
                draft_id = result.get("data", {}).get("draft_id")
                print(f"[XHSPublisher] 草稿已保存: {draft_id}")
                return draft_id
            else:
                print(f"[XHSPublisher] 保存草稿失败: {result.get('msg')}")
                return None
                
        except Exception as e:
            print(f"[XHSPublisher] 保存草稿异常: {e}")
            return None
