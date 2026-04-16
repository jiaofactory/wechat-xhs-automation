"""
WeChat Scheduler Module
微信公众号定时发布模块
"""

import json
import time
import threading
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import schedule


@dataclass
class ScheduledJob:
    """定时任务数据结构"""
    job_id: str
    job_type: str  # 'article', 'text', 'batch'
    scheduled_time: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    data: Dict[str, Any]
    created_at: str
    executed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WeChatScheduler:
    """微信公众号定时发布调度器"""
    
    def __init__(self, publisher, storage_path: str = "./data/wechat_scheduler.json"):
        """
        初始化调度器
        
        Args:
            publisher: WeChatPublisher实例
            storage_path: 任务存储路径
        """
        self.publisher = publisher
        self.storage_path = storage_path
        self.jobs: Dict[str, ScheduledJob] = {}
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        # 加载已保存的任务
        self._load_jobs()
        
    def _load_jobs(self):
        """从存储加载任务"""
        import os
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for job_id, job_data in data.items():
                        self.jobs[job_id] = ScheduledJob(**job_data)
            except Exception as e:
                print(f"[WeChatScheduler] 加载任务失败: {e}")
                
    def _save_jobs(self):
        """保存任务到存储"""
        import os
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                data = {job_id: asdict(job) for job_id, job in self.jobs.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WeChatScheduler] 保存任务失败: {e}")
    
    def _generate_job_id(self) -> str:
        """生成任务ID"""
        import uuid
        return f"wc_job_{uuid.uuid4().hex[:12]}"
    
    def schedule_article(self, article_data: Dict[str, Any], 
                        publish_at: datetime) -> str:
        """
        定时发布图文消息
        
        Args:
            article_data: 文章数据
            publish_at: 发布时间
            
        Returns:
            任务ID
        """
        job_id = self._generate_job_id()
        
        job = ScheduledJob(
            job_id=job_id,
            job_type="article",
            scheduled_time=publish_at.isoformat(),
            status="pending",
            data=article_data,
            created_at=datetime.now().isoformat()
        )
        
        with self.lock:
            self.jobs[job_id] = job
            self._save_jobs()
            
        # 添加到schedule
        schedule.every().day.at(publish_at.strftime("%H:%M")).do(
            self._execute_article_job, job_id
        ).tag(job_id)
        
        print(f"[WeChatScheduler] 文章已定时: {job_id} at {publish_at}")
        return job_id
    
    def schedule_text(self, content: str, publish_at: datetime,
                     group_id: Optional[str] = None) -> str:
        """
        定时发布文本消息
        
        Args:
            content: 文本内容
            publish_at: 发布时间
            group_id: 分组ID
            
        Returns:
            任务ID
        """
        job_id = self._generate_job_id()
        
        job = ScheduledJob(
            job_id=job_id,
            job_type="text",
            scheduled_time=publish_at.isoformat(),
            status="pending",
            data={"content": content, "group_id": group_id},
            created_at=datetime.now().isoformat()
        )
        
        with self.lock:
            self.jobs[job_id] = job
            self._save_jobs()
            
        schedule.every().day.at(publish_at.strftime("%H:%M")).do(
            self._execute_text_job, job_id
        ).tag(job_id)
        
        print(f"[WeChatScheduler] 文本已定时: {job_id} at {publish_at}")
        return job_id
    
    def _execute_article_job(self, job_id: str):
        """
        执行文章发布任务
        
        Args:
            job_id: 任务ID
        """
        job = self.jobs.get(job_id)
        if not job or job.status != "pending":
            return schedule.CancelJob
            
        with self.lock:
            job.status = "running"
            job.executed_at = datetime.now().isoformat()
            self._save_jobs()
            
        try:
            # 发布文章
            from .publisher import WeChatArticle
            
            article_data = job.data
            article = WeChatArticle(**article_data)
            
            # 上传封面图
            if article.thumb_media_id:
                pass  # 已有封面图ID
            elif article_data.get("thumb_image_path"):
                thumb_id = self.publisher.upload_thumb_media(
                    article_data["thumb_image_path"]
                )
                article.thumb_media_id = thumb_id or ""
                
            # 创建并发布
            media_id = self.publisher.create_article(article)
            
            if media_id:
                msg_id = self.publisher.publish_article(media_id)
                
                with self.lock:
                    job.status = "completed"
                    job.result = {"media_id": media_id, "msg_id": msg_id}
                    self._save_jobs()
                    
                print(f"[WeChatScheduler] 文章发布成功: {msg_id}")
            else:
                raise Exception("Failed to create article")
                
        except Exception as e:
            with self.lock:
                job.status = "failed"
                job.error = str(e)
                self._save_jobs()
                
            print(f"[WeChatScheduler] 文章发布失败: {e}")
            
        return schedule.CancelJob
    
    def _execute_text_job(self, job_id: str):
        """
        执行文本发布任务
        
        Args:
            job_id: 任务ID
        """
        job = self.jobs.get(job_id)
        if not job or job.status != "pending":
            return schedule.CancelJob
            
        with self.lock:
            job.status = "running"
            job.executed_at = datetime.now().isoformat()
            self._save_jobs()
            
        try:
            content = job.data.get("content", "")
            group_id = job.data.get("group_id")
            
            msg_id = self.publisher.publish_simple_text(content, group_id)
            
            with self.lock:
                job.status = "completed"
                job.result = {"msg_id": msg_id}
                self._save_jobs()
                
            print(f"[WeChatScheduler] 文本发布成功: {msg_id}")
            
        except Exception as e:
            with self.lock:
                job.status = "failed"
                job.error = str(e)
                self._save_jobs()
                
            print(f"[WeChatScheduler] 文本发布失败: {e}")
            
        return schedule.CancelJob
    
    def cancel_job(self, job_id: str) -> bool:
        """
        取消定时任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            是否取消成功
        """
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return False
                
            if job.status in ["completed", "failed"]:
                return False
                
            job.status = "cancelled"
            self._save_jobs()
            
        # 从schedule中移除
        schedule.clear(job_id)
        
        print(f"[WeChatScheduler] 任务已取消: {job_id}")
        return True
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务状态字典
        """
        job = self.jobs.get(job_id)
        if job:
            return asdict(job)
        return None
    
    def list_jobs(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有任务
        
        Args:
            status: 筛选状态
            
        Returns:
            任务列表
        """
        jobs = []
        for job in self.jobs.values():
            if status is None or job.status == status:
                jobs.append(asdict(job))
                
        # 按时间排序
        jobs.sort(key=lambda x: x["scheduled_time"])
        return jobs
    
    def start_scheduler(self):
        """启动调度器"""
        if self.running:
            return
            
        self.running = True
        
        def run_schedule():
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        self.scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        self.scheduler_thread.start()
        
        print("[WeChatScheduler] 调度器已启动")
        
    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        schedule.clear()
        print("[WeChatScheduler] 调度器已停止")
        
    def get_pending_jobs_count(self) -> int:
        """
        获取待执行任务数量
        
        Returns:
            待执行任务数
        """
        return sum(1 for job in self.jobs.values() if job.status == "pending")
