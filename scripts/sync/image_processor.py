"""
Image Processor Module
图片处理模块

Handles image optimization for WeChat and XiaoHongShu platforms
处理微信和小红书平台的图片优化
"""

import os
import io
from typing import Optional, Tuple, List, Dict, Any
from PIL import Image, ImageDraw, ImageFont, ImageEnhance


class ImageProcessor:
    """图片处理器"""
    
    # 平台推荐尺寸
    DIMENSIONS = {
        "wechat_cover": (900, 500),  # 微信公众号封面
        "wechat_content": (1080, 1920),  # 公众号正文图片
        "xhs_note": (1080, 1440),  # 小红书笔记图片（3:4）
        "xhs_square": (1080, 1080),  # 小红书正方形
        "xhs_story": (1080, 1920),  # 小红书故事/视频封面
    }
    
    # 文件大小限制（MB）
    SIZE_LIMITS = {
        "wechat": 5,  # 微信5MB
        "xhs": 20,  # 小红书20MB
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化处理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.quality = self.config.get("image_quality", 85)
        self.max_dimension = self.config.get("max_image_dimension", 1440)
        
        # 水印设置
        watermark_config = self.config.get("watermark", {})
        self.watermark_enabled = watermark_config.get("enabled", False)
        self.watermark_text = watermark_config.get("text", "")
        self.watermark_position = watermark_config.get("position", "bottom_right")
        self.watermark_opacity = watermark_config.get("opacity", 0.5)
        
    def process_for_wechat(self, image_path: str, 
                          image_type: str = "content") -> Optional[str]:
        """
        处理图片用于微信公众号
        
        Args:
            image_path: 原始图片路径
            image_type: 图片类型（cover或content）
            
        Returns:
            处理后图片路径或None
        """
        try:
            # 打开图片
            with Image.open(image_path) as img:
                # 转换为RGB（处理RGBA）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                    
                # 调整尺寸
                target_size = self.DIMENSIONS.get(f"wechat_{image_type}", (1080, 1920))
                img = self._resize_image(img, target_size)
                
                # 添加水印
                if self.watermark_enabled:
                    img = self._add_watermark(img)
                    
                # 压缩并保存
                output_path = self._generate_output_path(image_path, "wechat")
                self._save_with_compression(img, output_path, "wechat")
                
                return output_path
                
        except Exception as e:
            print(f"[ImageProcessor] 处理微信图片失败: {e}")
            return None
    
    def process_for_xhs(self, image_path: str, 
                       ratio: str = "3:4") -> Optional[str]:
        """
        处理图片用于小红书
        
        Args:
            image_path: 原始图片路径
            ratio: 图片比例（3:4或1:1）
            
        Returns:
            处理后图片路径或None
        """
        try:
            with Image.open(image_path) as img:
                # 转换为RGB
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                    
                # 选择目标尺寸
                if ratio == "1:1":
                    target_size = self.DIMENSIONS["xhs_square"]
                else:
                    target_size = self.DIMENSIONS["xhs_note"]
                    
                # 调整尺寸
                img = self._resize_for_xhs(img, target_size)
                
                # 添加水印
                if self.watermark_enabled:
                    img = self._add_watermark(img)
                    
                # 保存
                output_path = self._generate_output_path(image_path, "xhs")
                self._save_with_compression(img, output_path, "xhs")
                
                return output_path
                
        except Exception as e:
            print(f"[ImageProcessor] 处理小红书图片失败: {e}")
            return None
    
    def process_batch(self, image_paths: List[str], 
                     platform: str = "xhs") -> List[str]:
        """
        批量处理图片
        
        Args:
            image_paths: 图片路径列表
            platform: 目标平台
            
        Returns:
            处理后图片路径列表
        """
        processed = []
        
        for img_path in image_paths:
            if platform == "wechat":
                result = self.process_for_wechat(img_path)
            else:
                result = self.process_for_xhs(img_path)
                
            if result:
                processed.append(result)
                
        return processed
    
    def _resize_image(self, img: Image.Image, 
                     target_size: Tuple[int, int]) -> Image.Image:
        """
        调整图片尺寸
        
        Args:
            img: 图片对象
            target_size: 目标尺寸
            
        Returns:
            调整后的图片
        """
        # 计算缩放比例
        target_width, target_height = target_size
        
        # 按比例缩放
        img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        
        return img
    
    def _resize_for_xhs(self, img: Image.Image, 
                       target_size: Tuple[int, int]) -> Image.Image:
        """
        调整为小红书格式（支持裁剪）
        
        Args:
            img: 图片对象
            target_size: 目标尺寸
            
        Returns:
            调整后的图片
        """
        target_width, target_height = target_size
        target_ratio = target_width / target_height
        
        # 获取原图尺寸
        img_width, img_height = img.size
        img_ratio = img_width / img_height
        
        # 如果比例不匹配，进行智能裁剪
        if abs(img_ratio - target_ratio) > 0.01:
            if img_ratio > target_ratio:
                # 图片太宽，裁剪宽度
                new_width = int(img_height * target_ratio)
                left = (img_width - new_width) // 2
                img = img.crop((left, 0, left + new_width, img_height))
            else:
                # 图片太高，裁剪高度
                new_height = int(img_width / target_ratio)
                top = (img_height - new_height) // 3  # 从1/3处裁剪
                img = img.crop((0, top, img_width, top + new_height))
                
        # 调整大小
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        return img
    
    def _add_watermark(self, img: Image.Image) -> Image.Image:
        """
        添加水印
        
        Args:
            img: 图片对象
            
        Returns:
            添加水印后的图片
        """
        if not self.watermark_text:
            return img
            
        # 创建水印图层
        watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark)
        
        # 计算字体大小
        width, height = img.size
        font_size = max(int(min(width, height) * 0.03), 20)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        # 计算文字位置
        bbox = draw.textbbox((0, 0), self.watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        padding = 20
        if self.watermark_position == "bottom_right":
            x = width - text_width - padding
            y = height - text_height - padding
        elif self.watermark_position == "bottom_left":
            x = padding
            y = height - text_height - padding
        elif self.watermark_position == "top_right":
            x = width - text_width - padding
            y = padding
        else:  # top_left
            x = padding
            y = padding
            
        # 绘制半透明文字
        alpha = int(255 * self.watermark_opacity)
        draw.text((x, y), self.watermark_text, font=font, 
                 fill=(255, 255, 255, alpha))
        
        # 合并图层
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, watermark)
        img = img.convert('RGB')
        
        return img
    
    def _save_with_compression(self, img: Image.Image, 
                               output_path: str, 
                               platform: str) -> bool:
        """
        保存图片并进行压缩控制
        
        Args:
            img: 图片对象
            output_path: 输出路径
            platform: 目标平台
            
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            # 获取大小限制
            size_limit_mb = self.SIZE_LIMITS.get(platform, 5)
            size_limit_bytes = size_limit_mb * 1024 * 1024
            
            # 尝试保存
            quality = self.quality
            
            while quality > 30:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                size = buffer.tell()
                
                if size <= size_limit_bytes:
                    # 保存到文件
                    with open(output_path, 'wb') as f:
                        f.write(buffer.getvalue())
                    return True
                    
                # 降低质量再试
                quality -= 10
                
            # 如果质量降到30还是太大，强制保存
            img.save(output_path, format='JPEG', quality=30, optimize=True)
            return True
            
        except Exception as e:
            print(f"[ImageProcessor] 保存失败: {e}")
            return False
    
    def _generate_output_path(self, original_path: str, 
                              platform: str) -> str:
        """
        生成输出路径
        
        Args:
            original_path: 原始路径
            platform: 目标平台
            
        Returns:
            输出路径
        """
        base, ext = os.path.splitext(original_path)
        return f"{base}_{platform}_processed.jpg"
    
    def create_collage(self, image_paths: List[str], 
                      layout: str = "grid") -> Optional[str]:
        """
        创建拼贴图
        
        Args:
            image_paths: 图片路径列表
            layout: 布局方式（grid, vertical, horizontal）
            
        Returns:
            拼贴图路径或None
        """
        try:
            images = [Image.open(p) for p in image_paths[:9]]  # 最多9张
            
            if layout == "grid":
                # 网格布局
                count = len(images)
                if count <= 2:
                    cols, rows = count, 1
                elif count <= 4:
                    cols, rows = 2, 2
                elif count <= 6:
                    cols, rows = 3, 2
                else:
                    cols, rows = 3, 3
                    
                cell_width = 1080 // cols
                cell_height = 1440 // rows
                
                collage = Image.new('RGB', (1080, 1440), (255, 255, 255))
                
                for i, img in enumerate(images):
                    row = i // cols
                    col = i % cols
                    
                    img = img.resize((cell_width, cell_height), 
                                   Image.Resampling.LANCZOS)
                    collage.paste(img, (col * cell_width, row * cell_height))
                    
            elif layout == "vertical":
                # 垂直拼接
                total_height = sum(img.height for img in images)
                max_width = max(img.width for img in images)
                
                collage = Image.new('RGB', (max_width, total_height), 
                                  (255, 255, 255))
                y = 0
                for img in images:
                    collage.paste(img, (0, y))
                    y += img.height
                    
            else:  # horizontal
                # 水平拼接
                total_width = sum(img.width for img in images)
                max_height = max(img.height for img in images)
                
                collage = Image.new('RGB', (total_width, max_height), 
                                  (255, 255, 255))
                x = 0
                for img in images:
                    collage.paste(img, (x, 0))
                    x += img.width
                    
            # 保存
            output_path = "collage_output.jpg"
            collage.save(output_path, quality=self.quality)
            
            return output_path
            
        except Exception as e:
            print(f"[ImageProcessor] 创建拼贴图失败: {e}")
            return None
    
    def enhance_image(self, image_path: str, 
                     brightness: float = 1.0,
                     contrast: float = 1.0,
                     sharpness: float = 1.0) -> Optional[str]:
        """
        增强图片效果
        
        Args:
            image_path: 图片路径
            brightness: 亮度（1.0为原值）
            contrast: 对比度
            sharpness: 锐度
            
        Returns:
            处理后图片路径或None
        """
        try:
            with Image.open(image_path) as img:
                # 调整亮度
                if brightness != 1.0:
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(brightness)
                    
                # 调整对比度
                if contrast != 1.0:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(contrast)
                    
                # 调整锐度
                if sharpness != 1.0:
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(sharpness)
                    
                # 保存
                output_path = self._generate_output_path(image_path, "enhanced")
                img.save(output_path, quality=self.quality)
                
                return output_path
                
        except Exception as e:
            print(f"[ImageProcessor] 增强图片失败: {e}")
            return None
