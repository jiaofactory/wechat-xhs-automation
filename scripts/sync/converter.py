"""
Content Converter Module
内容格式转换模块

Handles conversion between WeChat article format and XiaoHongShu note format
处理微信公众号文章和小红书笔记之间的格式转换
"""

import re
from typing import Dict, Any, List
from html import unescape


class ContentConverter:
    """内容格式转换器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化转换器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.max_xhs_title = self.config.get("max_xhs_title_length", 20)
        self.max_xhs_content = self.config.get("max_xhs_content_length", 1000)
        self.auto_summarize = self.config.get("auto_summarize_long_content", True)
        
    def wechat_to_xhs(self, article_content: str, article_title: str = "") -> Dict[str, Any]:
        """
        将微信公众号文章转换为小红书笔记格式
        
        Args:
            article_content: 微信文章内容（HTML）
            article_title: 微信文章标题
            
        Returns:
            小红书格式的内容字典
        """
        # 提取纯文本
        text_content = self._html_to_text(article_content)
        
        # 生成小红书标题
        xhs_title = self._generate_xhs_title(article_title, text_content)
        
        # 转换内容格式
        xhs_content = self._convert_wechat_to_xhs_format(text_content)
        
        # 生成分割符分隔的文本（适合小红书）
        formatted_content = self._format_for_xhs(xhs_content)
        
        # 提取推荐标签
        suggested_tags = self._extract_tags(text_content)
        
        return {
            "title": xhs_title,
            "content": formatted_content,
            "original_title": article_title,
            "suggested_tags": suggested_tags,
            "content_length": len(formatted_content),
            "needs_truncation": len(formatted_content) > self.max_xhs_content
        }
    
    def xhs_to_wechat(self, note_title: str, note_content: str, 
                     images: List[str]) -> Dict[str, Any]:
        """
        将小红书笔记转换为微信公众号文章格式
        
        Args:
            note_title: 小红书标题
            note_content: 小红书内容
            images: 图片列表
            
        Returns:
            微信格式的内容字典
        """
        # 小红书内容转微信格式
        wechat_content = self._convert_xhs_to_wechat_format(note_content)
        
        # 添加标签为话题
        wechat_content = self._add_tags_as_topics(wechat_content)
        
        # 生成微信标题（可以更长）
        wechat_title = note_title if len(note_title) > 10 else f"{note_title} | 精彩分享"
        
        return {
            "title": wechat_title,
            "content": wechat_content,
            "digest": self._generate_digest(wechat_content),
            "images": images
        }
    
    def _html_to_text(self, html: str) -> str:
        """
        将HTML转换为纯文本
        
        Args:
            html: HTML字符串
            
        Returns:
            纯文本
        """
        # 移除script和style
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        
        # 转换常见HTML标签
        html = re.sub(r'<br\s*/?>', '\n', html)
        html = re.sub(r'<p[^>]*>', '\n', html)
        html = re.sub(r'</p>', '', html)
        html = re.sub(r'<div[^>]*>', '\n', html)
        html = re.sub(r'</div>', '', html)
        html = re.sub(r'<li[^>]*>', '\n• ', html)
        html = re.sub(r'</li>', '', html)
        
        # 移除其他标签
        html = re.sub(r'<[^>]+>', '', html)
        
        # 解码HTML实体
        text = unescape(html)
        
        # 清理多余空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text
    
    def _generate_xhs_title(self, original_title: str, content: str) -> str:
        """
        生成小红书风格的标题
        
        Args:
            original_title: 原标题
            content: 内容
            
        Returns:
            小红书标题
        """
        # 如果原标题较短，直接使用
        if len(original_title) <= self.max_xhs_title:
            return original_title
            
        # 截断原标题
        truncated = original_title[:self.max_xhs_title]
        
        # 添加小红书常见前缀/后缀增加吸引力
        prefixes = ["必看！", "超实用", "干货", "分享"]
        suffixes = ["✨", "💡", "🔥", "👍"]
        
        import random
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        # 组合新标题
        max_len = self.max_xhs_title - len(prefix) - len(suffix) - 2
        return f"{prefix}{truncated[:max_len]}{suffix}"
    
    def _convert_wechat_to_xhs_format(self, content: str) -> str:
        """
        将微信格式内容转换为小红书格式
        
        Args:
            content: 微信内容
            
        Returns:
            小红书格式内容
        """
        lines = content.split('\n')
        xhs_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 转换标题行为小红书样式
            if line.startswith('【') and line.endswith('】'):
                line = f"📌 {line[1:-1]}"
            elif line.startswith('#') or line.startswith('＃'):
                # 已经是标签格式
                pass
            elif len(line) < 15 and '：' in line:
                # 可能是小标题
                line = f"▶ {line}"
                
            xhs_lines.append(line)
            
        return '\n\n'.join(xhs_lines)
    
    def _format_for_xhs(self, content: str) -> str:
        """
        为小红书格式化内容
        
        Args:
            content: 内容
            
        Returns:
            格式化后内容
        """
        # 添加段落分隔（小红书常用空行分隔）
        paragraphs = content.split('\n\n')
        formatted = []
        
        for i, para in enumerate(paragraphs):
            formatted.append(para)
            # 每隔几段添加一个表情符号分隔
            if i < len(paragraphs) - 1 and i % 3 == 2:
                formatted.append("✨✨✨")
                
        result = '\n\n'.join(formatted)
        
        # 如果内容太长，进行摘要
        if len(result) > self.max_xhs_content and self.auto_summarize:
            result = self._summarize_content(result)
            
        return result
    
    def _summarize_content(self, content: str, max_length: int = 800) -> str:
        """
        摘要长内容
        
        Args:
            content: 内容
            max_length: 最大长度
            
        Returns:
            摘要后内容
        """
        if len(content) <= max_length:
            return content
            
        # 简单摘要：保留开头和结尾，中间用...连接
        # 更高级的可以使用NLP库如transformers
        
        head_len = max_length // 2
        tail_len = max_length // 4
        
        head = content[:head_len]
        tail = content[-tail_len:]
        
        return f"{head}\n\n...（内容较长，建议查看完整版）\n\n{tail}"
    
    def _extract_tags(self, content: str) -> List[str]:
        """
        从内容中提取推荐标签
        
        Args:
            content: 内容
            
        Returns:
            标签列表
        """
        # 小红书常见分类标签
        common_tags = {
            "美食": ["吃", "美食", "餐厅", "好吃", "味道", "料理", "烹饪"],
            "旅行": ["旅行", "旅游", "景点", "风景", "打卡", "目的地", "攻略"],
            "美妆": ["美妆", "化妆", "护肤", "口红", "粉底", "眼影", "穿搭"],
            "生活": ["生活", "日常", "分享", "好物", "推荐", "体验"],
            "时尚": ["时尚", "穿搭", "潮流", "OOTD", "搭配", "衣服"],
            "摄影": ["拍照", "摄影", "相机", "修图", "滤镜", "构图"],
            "读书": ["读书", "书籍", "阅读", "书单", "学习", "成长"],
            "家居": ["家居", "装修", "家具", "布置", "收纳", "装饰"],
            "职场": ["职场", "工作", "面试", "简历", "提升", "技能"],
            "健康": ["健康", "运动", "健身", "瑜伽", "减肥", "养生"]
        }
        
        found_tags = []
        content_lower = content.lower()
        
        for tag, keywords in common_tags.items():
            for keyword in keywords:
                if keyword in content_lower:
                    found_tags.append(tag)
                    break
                    
        # 去重并限制数量
        unique_tags = list(dict.fromkeys(found_tags))
        return unique_tags[:5]  # 最多5个标签
    
    def _convert_xhs_to_wechat_format(self, content: str) -> str:
        """
        将小红书格式转换为微信公众号格式
        
        Args:
            content: 小红书内容
            
        Returns:
            微信格式内容
        """
        # 移除小红书常用分隔符
        content = re.sub(r'[✨🔥💡👍]+', '', content)
        
        # 将小红书的分段转换为微信HTML段落
        lines = content.split('\n\n')
        html_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 转换小标题
            if line.startswith('📌') or line.startswith('▶'):
                html_lines.append(f"<h3>{line}</h3>")
            # 转换列表项
            elif line.startswith('•') or line.startswith('-'):
                html_lines.append(f"<li>{line[1:].strip()}</li>")
            else:
                html_lines.append(f"<p>{line}</p>")
                
        return '\n'.join(html_lines)
    
    def _add_tags_as_topics(self, content: str, tags: List[str] = None) -> str:
        """
        在内容末尾添加标签作为话题
        
        Args:
            content: 内容
            tags: 标签列表
            
        Returns:
            添加标签后的内容
        """
        if not tags:
            return content
            
        # 添加话题标签
        topic_section = "<p><strong>相关话题：</strong></p>"
        topic_section += "<p>" + " ".join([f"#{tag}" for tag in tags]) + "</p>"
        
        return content + "\n" + topic_section
    
    def _generate_digest(self, content: str, max_len: int = 120) -> str:
        """
        生成文章摘要
        
        Args:
            content: 内容
            max_len: 最大长度
            
        Returns:
            摘要
        """
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', content)
        text = text.replace('\n', ' ').strip()
        
        if len(text) <= max_len:
            return text
            
        return text[:max_len] + "..."


class HashtagGenerator:
    """标签生成器"""
    
    # 小红书热门标签库
    POPULAR_TAGS = {
        "通用": ["生活", "分享", "日常", "好物", "推荐"],
        "美食": ["美食", "探店", "吃货", "打卡", "美味", "食谱", " cooking"],
        "旅行": ["旅行", "旅游", "打卡", "攻略", "风景", "目的地", "周末去哪儿"],
        "美妆": ["美妆", "护肤", "化妆", "好物", "测评", "教程"],
        "穿搭": ["穿搭", "OOTD", "时尚", "搭配", "衣服", "潮流"],
        "家居": ["家居", "装修", "好物", "收纳", "布置", "生活"],
        "学习": ["学习", "读书", "成长", "干货", "方法", "提升"],
        "职场": ["职场", "工作", "打工人", "技巧", "经验", "面试"]
    }
    
    @classmethod
    def suggest_tags(cls, content: str, category: str = "通用") -> List[str]:
        """
        根据内容推荐标签
        
        Args:
            content: 内容
            category: 分类
            
        Returns:
            推荐标签列表
        """
        tags = []
        
        # 从分类获取基础标签
        base_tags = cls.POPULAR_TAGS.get(category, cls.POPULAR_TAGS["通用"])
        
        # 匹配内容中出现的热门标签
        for tag in base_tags:
            if tag in content:
                tags.append(tag)
                
        # 补充通用热门标签
        if len(tags) < 5:
            for tag in cls.POPULAR_TAGS["通用"]:
                if tag not in tags:
                    tags.append(tag)
                if len(tags) >= 5:
                    break
                    
        return tags[:5]
    
    @classmethod
    def format_for_platform(cls, tags: List[str], platform: str = "xhs") -> str:
        """
        将标签格式化为平台特定格式
        
        Args:
            tags: 标签列表
            platform: 平台（xhs或wechat）
            
        Returns:
            格式化后的标签字符串
        """
        if platform == "xhs":
            # 小红书格式：#标签1 #标签2
            return " ".join([f"#{tag}" for tag in tags])
        else:
            # 微信公众号格式：话题标签
            return " ".join([f"#{tag}" for tag in tags])
