"""
WeChat Official Account Analytics Module
微信公众号数据分析模块
"""

import json
import time
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class ArticleStats:
    """文章统计数据"""
    msgid: str
    title: str
    int_page_read_user: int  # 图文页阅读人数
    int_page_read_count: int  # 图文页阅读次数
    ori_page_read_user: int  # 原文页阅读人数
    ori_page_read_count: int  # 原文页阅读次数
    share_user: int  # 分享人数
    share_count: int  # 分享次数
    add_to_fav_user: int  # 收藏人数
    add_to_fav_count: int  # 收藏次数
    
    @property
    def total_reads(self) -> int:
        """总阅读量"""
        return self.int_page_read_count + self.ori_page_read_count
    
    @property
    def engagement_rate(self) -> float:
        """互动率"""
        if self.int_page_read_count == 0:
            return 0.0
        return (self.share_count + self.add_to_fav_count) / self.int_page_read_count


@dataclass
class UserSummary:
    """用户增长数据"""
    date: str
    new_user: int  # 新增用户
    cancel_user: int  # 取消关注用户
    cumulate_user: int  # 累计用户
    
    @property
    def net_growth(self) -> int:
        """净增长"""
        return self.new_user - self.cancel_user


class WeChatAnalytics:
    """微信数据分析器"""
    
    API_BASE = "https://api.weixin.qq.com/datacube"
    
    def __init__(self, auth_manager):
        """
        初始化分析器
        
        Args:
            auth_manager: WeChatAuth实例
        """
        self.auth = auth_manager
        
    def _get_token_and_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取token并发送请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            响应数据
        """
        token = self.auth.get_access_token()
        if not token:
            return {}
            
        url = f"{self.API_BASE}/{endpoint}"
        params = {"access_token": token}
        
        try:
            response = requests.post(
                url,
                params=params,
                data=json.dumps(data),
                timeout=30
            )
            return response.json()
            
        except Exception as e:
            print(f"[WeChatAnalytics] 请求异常: {e}")
            return {}
    
    def get_user_summary(self, start_date: str, end_date: str) -> List[UserSummary]:
        """
        获取用户增长数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            用户增长数据列表
        """
        data = {
            "begin_date": start_date,
            "end_date": end_date
        }
        
        result = self._get_token_and_request("getusersummary", data)
        
        if "list" in result:
            return [
                UserSummary(
                    date=item.get("ref_date"),
                    new_user=item.get("new_user", 0),
                    cancel_user=item.get("cancel_user", 0),
                    cumulate_user=item.get("cumulate_user", 0)
                )
                for item in result["list"]
            ]
        return []
    
    def get_user_cumulate(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取累计用户数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            累计用户数据列表
        """
        data = {
            "begin_date": start_date,
            "end_date": end_date
        }
        
        return self._get_token_and_request("getusercumulate", data).get("list", [])
    
    def get_article_summary(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取图文群发每日数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            图文数据列表
        """
        data = {
            "begin_date": start_date,
            "end_date": end_date
        }
        
        return self._get_token_and_request("getarticlesummary", data).get("list", [])
    
    def get_article_total(self, start_date: str, end_date: str) -> List[ArticleStats]:
        """
        获取图文群发总数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            图文统计数据列表
        """
        data = {
            "begin_date": start_date,
            "end_date": end_date
        }
        
        result = self._get_token_and_request("getarticletotal", data)
        
        if "list" in result:
            stats_list = []
            for item in result["list"]:
                # 可能有多个统计时间点
                details = item.get("details", [])
                if details:
                    latest = details[-1]  # 取最新数据
                    stats_list.append(ArticleStats(
                        msgid=item.get("msgid", ""),
                        title=item.get("title", ""),
                        int_page_read_user=latest.get("int_page_read_user", 0),
                        int_page_read_count=latest.get("int_page_read_count", 0),
                        ori_page_read_user=latest.get("ori_page_read_user", 0),
                        ori_page_read_count=latest.get("ori_page_read_count", 0),
                        share_user=latest.get("share_user", 0),
                        share_count=latest.get("share_count", 0),
                        add_to_fav_user=latest.get("add_to_fav_user", 0),
                        add_to_fav_count=latest.get("add_to_fav_count", 0)
                    ))
            return stats_list
        return []
    
    def get_user_read(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取图文阅读统计数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            阅读统计数据
        """
        data = {
            "begin_date": start_date,
            "end_date": end_date
        }
        
        return self._get_token_and_request("getuserread", data).get("list", [])
    
    def get_user_share(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取图文分享转发数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            分享数据
        """
        data = {
            "begin_date": start_date,
            "end_date": end_date
        }
        
        return self._get_token_and_request("getusershare", data).get("list", [])
    
    def get_upstream_msg(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取消息发送概况数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            消息概况数据
        """
        data = {
            "begin_date": start_date,
            "end_date": end_date
        }
        
        return self._get_token_and_request("getupstreammsg", data).get("list", [])
    
    def get_interface_summary(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取接口分析数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            接口调用数据
        """
        data = {
            "begin_date": start_date,
            "end_date": end_date
        }
        
        return self._get_token_and_request("getinterfacesummary", data).get("list", [])
    
    def get_article_read_stats(self, article_msgid: str) -> Optional[ArticleStats]:
        """
        获取单篇文章的详细阅读数据
        
        Args:
            article_msgid: 文章消息ID
            
        Returns:
            文章统计数据
        """
        # 获取最近7天的数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        stats_list = self.get_article_total(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        for stats in stats_list:
            if article_msgid in stats.msgid:
                return stats
                
        return None
    
    def generate_weekly_report(self, week_start: Optional[str] = None) -> Dict[str, Any]:
        """
        生成周报数据
        
        Args:
            week_start: 周报开始日期 (YYYY-MM-DD)，默认为上周一
            
        Returns:
            周报数据字典
        """
        if week_start is None:
            # 计算上周一
            today = datetime.now()
            last_monday = today - timedelta(days=today.weekday() + 7)
            week_start = last_monday.strftime("%Y-%m-%d")
        
        start_date = datetime.strptime(week_start, "%Y-%m-%d")
        end_date = start_date + timedelta(days=6)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # 获取各项数据
        user_summary = self.get_user_summary(start_str, end_str)
        article_stats = self.get_article_total(start_str, end_str)
        user_reads = self.get_user_read(start_str, end_str)
        
        # 汇总数据
        total_new_users = sum(u.new_user for u in user_summary)
        total_cancel_users = sum(u.cancel_user for u in user_summary)
        net_growth = total_new_users - total_cancel_users
        
        total_reads = sum(a.total_reads for a in article_stats)
        total_shares = sum(a.share_count for a in article_stats)
        total_favs = sum(a.add_to_fav_count for a in article_stats)
        
        return {
            "period": f"{start_str} ~ {end_str}",
            "user_growth": {
                "new_followers": total_new_users,
                "unfollows": total_cancel_users,
                "net_growth": net_growth
            },
            "content_performance": {
                "total_reads": total_reads,
                "total_shares": total_shares,
                "total_favorites": total_favs,
                "article_count": len(article_stats),
                "avg_reads_per_article": total_reads // max(len(article_stats), 1)
            },
            "top_articles": [
                {
                    "title": a.title,
                    "reads": a.total_reads,
                    "shares": a.share_count,
                    "favs": a.add_to_fav_count
                }
                for a in sorted(article_stats, key=lambda x: x.total_reads, reverse=True)[:5]
            ],
            "daily_breakdown": [
                {
                    "date": u.date,
                    "new_users": u.new_user,
                    "net_growth": u.net_growth
                }
                for u in user_summary
            ]
        }
    
    def export_data_to_csv(self, data: List[Dict[str, Any]], 
                          filename: str = "wechat_analytics.csv") -> bool:
        """
        导出数据到CSV文件
        
        Args:
            data: 数据列表
            filename: 输出文件名
            
        Returns:
            是否导出成功
        """
        import csv
        
        if not data:
            print("[WeChatAnalytics] 无数据可导出")
            return False
            
        try:
            keys = data[0].keys() if isinstance(data[0], dict) else []
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
                
            print(f"[WeChatAnalytics] 数据已导出至: {filename}")
            return True
            
        except Exception as e:
            print(f"[WeChatAnalytics] 导出失败: {e}")
            return False
