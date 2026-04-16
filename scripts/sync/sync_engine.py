"""
Sync Engine Module
双平台同步引擎

Orchestrates cross-platform content synchronization between
WeChat Official Accounts and XiaoHongShu
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SyncResult:
    """同步结果数据结构"""
    success: bool
    source_platform: str
    target_platform: str
    source_id: str
    target_id: Optional[str]
    target_url: Optional[str]
    message: str
    details: Dict[str, Any]
    synced_at: str


class CrossPlatformSync:
    """跨平台同步引擎"""
    
    def __init__(self, wechat_manager, xhs_manager, config: Dict[str, Any] = None):
        """
        初始化同步引擎
        
        Args:
            wechat_manager: 微信管理器实例
            xhs_manager: 小红书管理器实例
            config: 配置字典
        """
        self.wechat = wechat_manager
        self.xhs = xhs_manager
        self.config = config or {}
        
        # 导入子模块
        from .converter import ContentConverter, HashtagGenerator
        from .image_processor import ImageProcessor
        
        self.converter = ContentConverter(self.config)
        self.image_processor = ImageProcessor(self.config)
        self.hashtag_generator = HashtagGenerator()
        
    def sync_article_to_xhs(self, article_id: str, 
                            custom_title: Optional[str] = None,
                            add_tags: Optional[List[str]] = None,
                            auto_publish: bool = True) -> SyncResult:
        """
        将微信公众号文章同步到小红书
        
        Args:
            article_id: 微信文章ID或媒体ID
            custom_title: 自定义小红书标题
            add_tags: 额外添加的标签
            auto_publish: 是否自动发布（False则保存为草稿）
            
        Returns:
            同步结果
        """
        try:
            # 1. 获取微信文章内容
            # 注意：微信API不直接提供通过ID获取内容，这里需要实现文章内容获取逻辑
            article_data = self._fetch_wechat_article(article_id)
            
            if not article_data:
                return SyncResult(
                    success=False,
                    source_platform="wechat",
                    target_platform="xiaohongshu",
                    source_id=article_id,
                    target_id=None,
                    target_url=None,
                    message="无法获取微信文章内容",
                    details={},
                    synced_at=datetime.now().isoformat()
                )
                
            # 2. 转换内容格式
            converted = self.converter.wechat_to_xhs(
                article_data.get("content", ""),
                article_data.get("title", "")
            )
            
            # 3. 处理图片
            processed_images = []
            original_images = article_data.get("images", [])
            
            if original_images:
                processed_images = self.image_processor.process_batch(
                    original_images, platform="xhs"
                )
                
            # 4. 准备小红书笔记数据
            title = custom_title or converted["title"]
            content = converted["content"]
            
            # 合并标签
            tags = converted.get("suggested_tags", [])
            if add_tags:
                tags = list(dict.fromkeys(tags + add_tags))  # 去重
                
            # 5. 发布或保存草稿
            if auto_publish:
                from ..xiaohongshu.publisher import XHSNote
                
                note = XHSNote(
                    title=title,
                    content=content,
                    images=processed_images,
                    tags=tags
                )
                
                result = self.xhs.publish_note(note)
                
                if result:
                    return SyncResult(
                        success=True,
                        source_platform="wechat",
                        target_platform="xiaohongshu",
                        source_id=article_id,
                        target_id=result.get("note_id"),
                        target_url=result.get("url"),
                        message="同步成功",
                        details={
                            "title": title,
                            "tags": tags,
                            "image_count": len(processed_images)
                        },
                        synced_at=datetime.now().isoformat()
                    )
                else:
                    return SyncResult(
                        success=False,
                        source_platform="wechat",
                        target_platform="xiaohongshu",
                        source_id=article_id,
                        target_id=None,
                        target_url=None,
                        message="小红书发布失败",
                        details={},
                        synced_at=datetime.now().isoformat()
                    )
            else:
                # 保存为草稿
                from ..xiaohongshu.publisher import XHSNote
                
                note = XHSNote(
                    title=title,
                    content=content,
                    images=processed_images,
                    tags=tags
                )
                
                draft_id = self.xhs.save_as_draft(note)
                
                return SyncResult(
                    success=True,
                    source_platform="wechat",
                    target_platform="xiaohongshu",
                    source_id=article_id,
                    target_id=draft_id,
                    target_url=None,
                    message="已保存为草稿",
                    details={
                        "draft_id": draft_id,
                        "title": title,
                        "tags": tags
                    },
                    synced_at=datetime.now().isoformat()
                )
                
        except Exception as e:
            return SyncResult(
                success=False,
                source_platform="wechat",
                target_platform="xiaohongshu",
                source_id=article_id,
                target_id=None,
                target_url=None,
                message=f"同步异常: {str(e)}",
                details={"error": str(e)},
                synced_at=datetime.now().isoformat()
            )
    
    def sync_note_to_wechat(self, note_id: str,
                           custom_title: Optional[str] = None,
                           auto_publish: bool = False) -> SyncResult:
        """
        将小红书笔记同步到微信公众号
        
        Args:
            note_id: 小红书笔记ID
            custom_title: 自定义微信标题
            auto_publish: 是否自动发布（建议先预览）
            
        Returns:
            同步结果
        """
        try:
            # 1. 获取小红书笔记内容
            note_data = self._fetch_xhs_note(note_id)
            
            if not note_data:
                return SyncResult(
                    success=False,
                    source_platform="xiaohongshu",
                    target_platform="wechat",
                    source_id=note_id,
                    target_id=None,
                    target_url=None,
                    message="无法获取小红书笔记内容",
                    details={},
                    synced_at=datetime.now().isoformat()
                )
                
            # 2. 转换内容格式
            converted = self.converter.xhs_to_wechat(
                note_data.get("title", ""),
                note_data.get("content", ""),
                note_data.get("images", [])
            )
            
            # 3. 处理图片
            processed_images = []
            original_images = note_data.get("images", [])
            
            if original_images:
                processed_images = self.image_processor.process_batch(
                    original_images, platform="wechat"
                )
                
            # 4. 准备微信文章数据
            title = custom_title or converted["title"]
            content = converted["content"]
            digest = converted["digest"]
            
            # 5. 创建文章
            from ..wechat.publisher import WeChatArticle
            
            thumb_media_id = ""
            if processed_images:
                thumb_media_id = self.wechat.upload_thumb_media(
                    processed_images[0]
                ) or ""
                
            article = WeChatArticle(
                title=title,
                content=content,
                digest=digest,
                thumb_media_id=thumb_media_id,
                author=note_data.get("author", ""),
                content_source_url=note_data.get("url", "")
            )
            
            media_id = self.wechat.create_article(article)
            
            if not media_id:
                return SyncResult(
                    success=False,
                    source_platform="xiaohongshu",
                    target_platform="wechat",
                    source_id=note_id,
                    target_id=None,
                    target_url=None,
                    message="创建微信文章失败",
                    details={},
                    synced_at=datetime.now().isoformat()
                )
                
            # 6. 发布或返回素材ID
            if auto_publish:
                msg_id = self.wechat.publish_article(media_id)
                
                return SyncResult(
                    success=True,
                    source_platform="xiaohongshu",
                    target_platform="wechat",
                    source_id=note_id,
                    target_id=msg_id,
                    target_url=f"https://mp.weixin.qq.com/s/{msg_id}",
                    message="同步成功",
                    details={
                        "title": title,
                        "media_id": media_id,
                        "msg_id": msg_id
                    },
                    synced_at=datetime.now().isoformat()
                )
            else:
                return SyncResult(
                    success=True,
                    source_platform="xiaohongshu",
                    target_platform="wechat",
                    source_id=note_id,
                    target_id=media_id,
                    target_url=None,
                    message="已创建素材，请预览后发布",
                    details={
                        "media_id": media_id,
                        "title": title
                    },
                    synced_at=datetime.now().isoformat()
                )
                
        except Exception as e:
            return SyncResult(
                success=False,
                source_platform="xiaohongshu",
                target_platform="wechat",
                source_id=note_id,
                target_id=None,
                target_url=None,
                message=f"同步异常: {str(e)}",
                details={"error": str(e)},
                synced_at=datetime.now().isoformat()
            )
    
    def batch_sync(self, source_ids: List[str], 
                  source_platform: str = "wechat",
                  schedule_spread: bool = True,
                  spread_hours: int = 48) -> List[SyncResult]:
        """
        批量同步多篇内容
        
        Args:
            source_ids: 源内容ID列表
            source_platform: 源平台（wechat/xiaohongshu）
            schedule_spread: 是否错峰发布
            spread_hours: 错峰时间范围（小时）
            
        Returns:
            同步结果列表
        """
        results = []
        
        if schedule_spread:
            from datetime import timedelta
            
            interval = spread_hours / max(len(source_ids), 1)
            base_time = datetime.now()
            
            for i, source_id in enumerate(source_ids):
                if source_platform == "wechat":
                    # 先同步，但可能设置定时发布
                    result = self.sync_article_to_xhs(
                        source_id, 
                        auto_publish=False  # 保存为草稿，稍后定时
                    )
                    
                    # 设置定时发布
                    if result.success and result.target_id:
                        publish_time = base_time + timedelta(hours=i * interval)
                        # 调用定时发布功能
                        
                else:
                    result = self.sync_note_to_wechat(source_id, auto_publish=False)
                    
                results.append(result)
        else:
            for source_id in source_ids:
                if source_platform == "wechat":
                    result = self.sync_article_to_xhs(source_id)
                else:
                    result = self.sync_note_to_wechat(source_id)
                    
                results.append(result)
                
        return results
    
    def _fetch_wechat_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        获取微信文章内容
        
        注意：这需要额外的爬虫或API实现
        此处为简化版实现
        
        Args:
            article_id: 文章ID
            
        Returns:
            文章数据或None
        """
        # 实现文章内容获取逻辑
        # 可以通过数据库、缓存或网络请求获取
        
        # 示例返回结构
        return {
            "id": article_id,
            "title": "示例文章标题",
            "content": "<p>示例内容...</p>",
            "images": [],
            "author": "",
            "publish_time": ""
        }
    
    def _fetch_xhs_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        获取小红书笔记内容
        
        Args:
            note_id: 笔记ID
            
        Returns:
            笔记数据或None
        """
        # 使用小红书API获取笔记详情
        return self.xhs.get_note_detail(note_id)
    
    def validate_sync_readiness(self) -> Dict[str, Any]:
        """
        验证同步准备状态
        
        Returns:
            状态信息
        """
        wechat_ready = self.wechat.auth.validate_credentials()
        xhs_ready = self.xhs.auth.is_logged_in
        
        return {
            "ready": wechat_ready and xhs_ready,
            "wechat_connected": wechat_ready,
            "xiaohongshu_connected": xhs_ready,
            "timestamp": datetime.now().isoformat()
        }


class SyncScheduler:
    """同步调度器 - 处理定时同步任务"""
    
    def __init__(self, sync_engine: CrossPlatformSync):
        """
        初始化调度器
        
        Args:
            sync_engine: 同步引擎实例
        """
        self.engine = sync_engine
        self.scheduled_jobs: List[Dict[str, Any]] = []
        
    def schedule_sync(self, source_id: str, 
                     source_platform: str,
                     publish_at: datetime,
                     options: Dict[str, Any] = None) -> str:
        """
        安排定时同步
        
        Args:
            source_id: 源内容ID
            source_platform: 源平台
            publish_at: 发布时间
            options: 同步选项
            
        Returns:
            调度任务ID
        """
        import uuid
        
        job_id = f"sync_{uuid.uuid4().hex[:12]}"
        
        job = {
            "job_id": job_id,
            "source_id": source_id,
            "source_platform": source_platform,
            "scheduled_time": publish_at.isoformat(),
            "options": options or {},
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        self.scheduled_jobs.append(job)
        
        # 实际调度需要集成到系统定时任务中
        # 这里返回任务ID供后续查询
        
        return job_id
    
    def get_sync_history(self, limit: int = 50) -> List[SyncResult]:
        """
        获取同步历史
        
        Args:
            limit: 返回数量限制
            
        Returns:
            同步结果列表
        """
        # 从日志或数据库获取历史记录
        return []
