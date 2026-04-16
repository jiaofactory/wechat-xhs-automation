"""
XiaoHongShu Scheduler Module
小红书定时发布模块
"""

import json
import time
import threading
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict
import schedule


@dataclass
class XHSScheduledJob:
    """小红书定时任务数据结构"""
    job_id: str
    job_type: str  # 'note', 'video', 'draft'
    scheduled_time: str
    status: str  # 'pending', 'running', 'completed', 'failed', 'cancelled'
    data: Dict[str, Any]
    created_at: str
    executed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class XHSScheduler:
    """小红书定时发布调度器"""
    
    def __init__(self, publisher, storage_path: str = "./data/xhs_scheduler.json"):
        """
        初始化调度器
        
        Args:
            publisher: XHSPublisher实例
            storage_path: 任务存储路径
        """
        self.publisher = publisher
        self.storage_path = storage_path
        self.jobs: Dict[str, XHSScheduledJob] = {}
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
                        self.jobs[job_id] = XHSScheduledJob(**job_data)
            except Exception as e:
                print(f"[XHSScheduler] 加载任务失败: {e}")
                
    def _save_jobs(self):
        """保存任务到存储"""
        import os
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                data = {job_id: asdict(job) for job_id, job in self.jobs.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[XHSScheduler] 保存任务失败: {e}")
    
    def _generate_job_id(self) -> str:
        """生成任务ID"""
        import uuid
        return f"xhs_job_{uuid.uuid4().hex[:12]}"
    
    def schedule_note(self, title: str, content: str, 
                     images: List[str],
                     tags: List[str],
                     publish_at: datetime,
                     location: Optional[str] = None) -> str:
        """
        定时发布图文笔记
        
        Args:
            title: 标题
            content: 内容
            images: 图片路径列表
            tags: 标签列表
            publish_at: 发布时间
            location: 位置信息
            
        Returns:
            任务ID
        """
        job_id = self._generate_job_id()
        
        job = XHSScheduledJob(
            job_id=job_id,
            job_type="note",
            scheduled_time=publish_at.isoformat(),
            status="pending",
            data={
                "title": title,
                "content": content,
                "images": images,
                "tags": tags,
                "location": location
            },
            created_at=datetime.now().isoformat()
        )
        
        with self.lock:
            self.jobs[job_id] = job
            self._save_jobs()
            
        # 添加到schedule
        schedule.every().day.at(publish_at.strftime("%H:%M")).do(
            self._execute_note_job, job_id
        ).tag(job_id)
        
        print(f"[XHSScheduler] 笔记已定时: {job_id} at {publish_at}")
        return job_id
    
    def schedule_video(self, title: str, content: str,
                      video_path: str,
                      cover_image: Optional[str],
                      tags: List[str],
                      publish_at: datetime,
                      location: Optional[str] = None) -> str:
        """
        定时发布视频笔记
        
        Args:
            title: 标题
            content: 内容
            video_path: 视频路径
            cover_image: 封面图路径
            tags: 标签列表
            publish_at: 发布时间
            location: 位置信息
            
        Returns:
            任务ID
        """
        job_id = self._generate_job_id()
        
        job = XHSScheduledJob(
            job_id=job_id,
            job_type="video",
            scheduled_time=publish_at.isoformat(),
            status="pending",
            data={
                "title": title,
                "content": content,
                "video_path": video_path,
                "cover_image": cover_image,
                "tags": tags,
                "location": location
            },
            created_at=datetime.now().isoformat()
        )
        
        with self.lock:
            self.jobs[job_id] = job
            self._save_jobs()
            
        schedule.every().day.at(publish_at.strftime("%H:%M")).do(
            self._execute_video_job, job_id
        ).tag(job_id)
        
        print(f"[XHSScheduler] 视频已定时: {job_id} at {publish_at}")
        return job_id
    
    def _execute_note_job(self, job_id: str):
        """
        执行笔记发布任务
        
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
            from .publisher import XHSNote
            
            note = XHSNote(
                title=job.data["title"],
                content=job.data["content"],
                images=job.data["images"],
                tags=job.data.get("tags", []),
                location=job.data.get("location")
            )
            
            result = self.publisher.publish_note(note)
            
            with self.lock:
                if result:
                    job.status = "completed"
                    job.result = result
                    print(f"[XHSScheduler] 笔记发布成功: {result.get('note_id')}")
                else:
                    job.status = "failed"
                    job.error = "Publish returned None"
                    print("[XHSScheduler] 笔记发布失败")
                self._save_jobs()
                
        except Exception as e:
            with self.lock:
                job.status = "failed"
                job.error = str(e)
                self._save_jobs()
            print(f"[XHSScheduler] 笔记发布异常: {e}")
            
        return schedule.CancelJob
    
    def _execute_video_job(self, job_id: str):
        """
        执行视频发布任务
        
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
            result = self.publisher.publish_video_note(
                title=job.data["title"],
                content=job.data["content"],
                video_path=job.data["video_path"],
                cover_image=job.data.get("cover_image"),
                tags=job.data.get("tags", []),
                location=job.data.get("location")
            )
            
            with self.lock:
                if result:
                    job.status = "completed"
                    job.result = result
                    print(f"[XHSScheduler] 视频发布成功: {result.get('note_id')}")
                else:
                    job.status = "failed"
                    job.error = "Video publish returned None"
                    print("[XHSScheduler] 视频发布失败")
                self._save_jobs()
                
        except Exception as e:
            with self.lock:
                job.status = "failed"
                job.error = str(e)
                self._save_jobs()
            print(f"[XHSScheduler] 视频发布异常: {e}")
            
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
                
            if job.status in ["completed", "failed", "cancelled"]:
                return False
                
            job.status = "cancelled"
            self._save_jobs()
            
        schedule.clear(job_id)
        
        print(f"[XHSScheduler] 任务已取消: {job_id}")
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
                
        jobs.sort(key=lambda x: x["scheduled_time"])
        return jobs
    
    def get_pending_jobs(self) -> List[Dict[str, Any]]:
        """
        获取所有待执行任务
        
        Returns:
            待执行任务列表
        """
        return self.list_jobs(status="pending")
    
    def start_scheduler(self):
        """启动调度器"""
        if self.running:
            return
            
        self.running = True
        
        def run_schedule():
            while self.running:
                schedule.run_pending()
                time.sleep(60)
                
        self.scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        self.scheduler_thread.start()
        
        print("[XHSScheduler] 调度器已启动")
        
    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            
        schedule.clear()
        print("[XHSScheduler] 调度器已停止")
