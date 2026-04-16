"""
XiaoHongShu Analytics Module
小红书数据分析模块
"""

import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class NoteStats:
    """笔记统计数据"""
    note_id: str
    title: str
    impressions: int  # 曝光量
    likes: int  # 点赞数
    collects: int  # 收藏数
    comments: int  # 评论数
    shares: int  # 分享数
    follows: int  # 新增关注
    
    @property
    def engagement(self) -> int:
        """总互动数"""
        return self.likes + self.collects + self.comments + self.shares
    
    @property
    def engagement_rate(self) -> float:
        """互动率"""
        if self.impressions == 0:
            return 0.0
        return self.engagement / self.impressions


@dataclass
class AccountStats:
    """账号统计数据"""
    followers: int  # 粉丝数
    following: int  # 关注数
    notes_count: int  # 笔记数
    total_likes: int  # 总获赞
    total_collects: int  # 总收藏


class XHSAnalytics:
    """小红书数据分析器"""
    
    API_BASE = "https://edith.xiaohongshu.com"
    
    def __init__(self, auth_manager):
        """
        初始化分析器
        
        Args:
            auth_manager: XHSAuth实例
        """
        self.auth = auth_manager
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送API请求
        
        Args:
            endpoint: API端点
            params: 查询参数
            
        Returns:
            响应数据
        """
        if not self.auth.is_logged_in:
            return {}
            
        url = f"{self.API_BASE}{endpoint}"
        
        try:
            response = self.auth.session.get(url, params=params, timeout=30)
            return response.json()
        except Exception as e:
            print(f"[XHSAnalytics] 请求异常: {e}")
            return {}
    
    def get_account_stats(self) -> Optional[AccountStats]:
        """
        获取账号统计数据
        
        Returns:
            账号统计数据
        """
        # 获取用户信息
        user_info = self.auth.get_user_info()
        if not user_info:
            return None
            
        # 获取笔记列表统计
        endpoint = "/api/sns/web/v1/user/notes"
        params = {"num": 1, "cursor": ""}
        
        result = self._make_request(endpoint, params)
        
        if result.get("success"):
            data = result.get("data", {})
            notes_count = data.get("total", 0)
            
            return AccountStats(
                followers=user_info.get("followers", 0),
                following=user_info.get("following", 0),
                notes_count=notes_count,
                total_likes=user_info.get("likes", 0),
                total_collects=user_info.get("collects", 0)
            )
            
        return None
    
    def get_note_stats(self, note_id: str) -> Optional[NoteStats]:
        """
        获取单篇笔记的统计数据
        
        Args:
            note_id: 笔记ID
            
        Returns:
            笔记统计数据
        """
        endpoint = f"/api/sns/web/v1/feed"
        params = {"note_id": note_id}
        
        result = self._make_request(endpoint, params)
        
        if result.get("success"):
            data = result.get("data", {})
            note = data.get("note", {})
            
            interact_info = note.get("interact_info", {})
            
            return NoteStats(
                note_id=note_id,
                title=note.get("title", ""),
                impressions=interact_info.get("share_count", 0),  # 使用分享数估算曝光
                likes=interact_info.get("liked_count", 0),
                collects=interact_info.get("collected_count", 0),
                comments=interact_info.get("comment_count", 0),
                shares=interact_info.get("share_count", 0),
                follows=interact_info.get("followed_count", 0)
            )
            
        return None
    
    def get_notes_list(self, page_size: int = 20, 
                      cursor: str = "") -> Dict[str, Any]:
        """
        获取笔记列表
        
        Args:
            page_size: 每页数量
            cursor: 分页游标
            
        Returns:
            笔记列表数据
        """
        endpoint = "/api/sns/web/v1/user/notes"
        params = {
            "num": page_size,
            "cursor": cursor
        }
        
        return self._make_request(endpoint, params)
    
    def get_all_notes_with_stats(self) -> List[NoteStats]:
        """
        获取所有笔记及其统计数据
        
        Returns:
            笔记统计列表
        """
        all_notes = []
        cursor = ""
        
        while True:
            result = self.get_notes_list(page_size=20, cursor=cursor)
            
            if not result.get("success"):
                break
                
            data = result.get("data", {})
            notes = data.get("notes", [])
            
            if not notes:
                break
                
            for note in notes:
                note_id = note.get("id")
                if note_id:
                    stats = NoteStats(
                        note_id=note_id,
                        title=note.get("title", ""),
                        impressions=0,
                        likes=note.get("likes", 0),
                        collects=note.get("collects", 0),
                        comments=note.get("comments", 0),
                        shares=note.get("shares", 0),
                        follows=0
                    )
                    all_notes.append(stats)
                    
            # 更新游标
            cursor = data.get("cursor", "")
            if not cursor:
                break
                
        return all_notes
    
    def get_recent_notes_stats(self, days: int = 7) -> List[NoteStats]:
        """
        获取最近发布的笔记统计
        
        Args:
            days: 最近多少天
            
        Returns:
            笔记统计列表
        """
        all_notes = self.get_all_notes_with_stats()
        
        # 筛选最近发布的笔记
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_notes = []
        for note in all_notes:
            # 这里假设能通过某种方式获取发布时间
            # 实际实现需要根据API返回的数据
            recent_notes.append(note)
            
        return recent_notes
    
    def get_trending_tags(self, category: str = "all") -> List[Dict[str, Any]]:
        """
        获取热门标签
        
        Args:
            category: 分类（all, fashion, food, travel等）
            
        Returns:
            热门标签列表
        """
        endpoint = "/api/sns/web/v1/search/trending"
        params = {"category": category}
        
        result = self._make_request(endpoint, params)
        
        if result.get("success"):
            return result.get("data", {}).get("queries", [])
        return []
    
    def get_recommended_tags(self, keyword: str) -> List[str]:
        """
        获取推荐标签
        
        Args:
            keyword: 关键词
            
        Returns:
            推荐标签列表
        """
        endpoint = "/api/sns/web/v1/search/tag"
        params = {"keyword": keyword}
        
        result = self._make_request(endpoint, params)
        
        if result.get("success"):
            tags = result.get("data", {}).get("tags", [])
            return [tag.get("name", "") for tag in tags if tag.get("name")]
        return []
    
    def generate_performance_report(self, days: int = 30) -> Dict[str, Any]:
        """
        生成表现报告
        
        Args:
            days: 统计天数
            
        Returns:
            报告数据字典
        """
        # 获取账号统计
        account = self.get_account_stats()
        
        # 获取笔记列表
        notes = self.get_all_notes_with_stats()
        recent_notes = notes[:30] if len(notes) > 30 else notes
        
        # 计算汇总数据
        total_likes = sum(n.likes for n in recent_notes)
        total_collects = sum(n.collects for n in recent_notes)
        total_comments = sum(n.comments for n in recent_notes)
        total_shares = sum(n.shares for n in recent_notes)
        
        # 找出最佳表现笔记
        top_notes = sorted(recent_notes, key=lambda x: x.likes + x.collects, reverse=True)[:5]
        
        # 计算平均表现
        avg_likes = total_likes / max(len(recent_notes), 1)
        avg_collects = total_collects / max(len(recent_notes), 1)
        
        return {
            "period": f"最近{days}天",
            "account_overview": {
                "followers": account.followers if account else 0,
                "following": account.following if account else 0,
                "total_notes": account.notes_count if account else 0,
                "total_likes": account.total_likes if account else 0
            },
            "content_performance": {
                "notes_analyzed": len(recent_notes),
                "total_likes": total_likes,
                "total_collects": total_collects,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "avg_likes_per_note": round(avg_likes, 2),
                "avg_collects_per_note": round(avg_collects, 2)
            },
            "top_performing_notes": [
                {
                    "note_id": n.note_id,
                    "title": n.title[:50] + "..." if len(n.title) > 50 else n.title,
                    "likes": n.likes,
                    "collects": n.collects,
                    "engagement": n.engagement
                }
                for n in top_notes
            ],
            "engagement_summary": {
                "total_engagement": total_likes + total_collects + total_comments + total_shares,
                "likes_ratio": round(total_likes / max(total_likes + total_collects, 1), 2),
                "collects_ratio": round(total_collects / max(total_likes + total_collects, 1), 2)
            }
        }
    
    def track_note_over_time(self, note_id: str, 
                            track_hours: int = 72) -> List[Dict[str, Any]]:
        """
        追踪笔记数据变化（模拟，实际需定时采集）
        
        Args:
            note_id: 笔记ID
            track_hours: 追踪小时数
            
        Returns:
            数据变化记录
        """
        # 获取当前数据
        current = self.get_note_stats(note_id)
        
        if not current:
            return []
            
        return [{
            "timestamp": datetime.now().isoformat(),
            "impressions": current.impressions,
            "likes": current.likes,
            "collects": current.collects,
            "comments": current.comments,
            "shares": current.shares
        }]
    
    def compare_notes_performance(self, note_ids: List[str]) -> List[Dict[str, Any]]:
        """
        对比多篇笔记的表现
        
        Args:
            note_ids: 笔记ID列表
            
        Returns:
            对比结果
        """
        comparison = []
        
        for note_id in note_ids:
            stats = self.get_note_stats(note_id)
            if stats:
                comparison.append({
                    "note_id": stats.note_id,
                    "title": stats.title[:30] + "..." if len(stats.title) > 30 else stats.title,
                    "impressions": stats.impressions,
                    "likes": stats.likes,
                    "collects": stats.collects,
                    "comments": stats.comments,
                    "engagement_rate": round(stats.engagement_rate, 4)
                })
                
        # 按互动率排序
        comparison.sort(key=lambda x: x["engagement_rate"], reverse=True)
        return comparison
    
    def export_analytics_to_csv(self, filename: str = "xhs_analytics.csv") -> bool:
        """
        导出分析数据到CSV
        
        Args:
            filename: 输出文件名
            
        Returns:
            是否导出成功
        """
        import csv
        
        notes = self.get_all_notes_with_stats()
        
        if not notes:
            print("[XHSAnalytics] 无数据可导出")
            return False
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Note ID', 'Title', 'Likes', 'Collects', 
                                'Comments', 'Shares', 'Total Engagement'])
                
                for note in notes:
                    writer.writerow([
                        note.note_id,
                        note.title,
                        note.likes,
                        note.collects,
                        note.comments,
                        note.shares,
                        note.engagement
                    ])
                    
            print(f"[XHSAnalytics] 数据已导出至: {filename}")
            return True
            
        except Exception as e:
            print(f"[XHSAnalytics] 导出失败: {e}")
            return False
