# 微信小红书自动化管理工具

**WeChat + XiaoHongShu Automation Skill**

一站式管理中国两大社交平台，一次发布，全平台触达！

---

## 🎯 功能概述

这个Skill提供**微信公众号**和**小红书**的完整自动化管理——中国两大最强内容平台。

### 适用人群
- 🇨🇳 中国自媒体人和内容创作者
- 🏢 MCN机构（多账号管理）
- 🌏 海外华人创作者（面向国内受众）
- 💼 品牌方（建立中国社交 presence）

---

## ✨ 核心功能

### 1. 微信公众号自动化
- ✅ 自动登录和会话管理
- ✅ 文章抓取和管理
- ✅ 图文消息自动发布
- ✅ 定时发布功能
- ✅ 数据分析（阅读量、点赞数、分享数）

### 2. 小红书自动化
- ✅ 自动登录和Cookie管理
- ✅ 笔记抓取和备份
- ✅ 图文/视频笔记发布
- ✅ 定时发布（支持时区）
- ✅ 数据监控（曝光、点赞、收藏、关注）

### 3. 双平台同步
- ✅ 一键同步：公众号文章 → 小红书笔记
- ✅ 自动格式转换（微信风格 → 小红书风格）
- ✅ 图片自动优化和尺寸调整
- ✅ 智能标签推荐

### 4. 管理控制台
- ✅ 安全凭证存储（加密）
- ✅ 发布计划管理
- ✅ 批量操作
- ✅ 完整操作日志

---

## 🚀 快速上手（10分钟出效果）

### 步骤1：安装Skill
```bash
clawhub install wechat-xhs-automation
```

### 步骤2：配置账号
```bash
cp config.example.json config.json
# 编辑 config.json 填入你的账号信息
```

### 步骤3：测试连接
```python
from wechat_xhs_automation import WeChatManager, XHSManager

# 测试微信
wc = WeChatManager()
print(wc.test_login())

# 测试小红书
xhs = XHSManager()
print(xhs.test_login())
```

### 步骤4：发布第一条内容
```python
from wechat_xhs_automation import CrossPlatformSync

# 跨平台发布
sync = CrossPlatformSync()
sync.publish_wechat_to_xhs(
    article_url="https://mp.weixin.qq.com/s/...",
    xhs_title="你的小红书标题",
    xhs_tags=["生活方式", "好物分享"]
)
```

---

## 📁 文件结构

```
wechat-xhs-automation/
├── SKILL.md                    # 英文文档
├── README.md                   # 中文文档（本文件）
├── config.example.json         # 配置示例
├── requirements.txt            # Python依赖
├── scripts/
│   ├── wechat/                # 微信模块
│   │   ├── auth.py            # 登录认证
│   │   ├── publisher.py       # 文章发布
│   │   ├── analytics.py       # 数据分析
│   │   └── scheduler.py       # 定时发布
│   ├── xiaohongshu/           # 小红书模块
│   │   ├── auth.py            # 登录认证
│   │   ├── publisher.py       # 笔记发布
│   │   ├── analytics.py       # 数据监控
│   │   └── scheduler.py       # 定时发布
│   ├── sync/                  # 同步模块
│   │   ├── converter.py       # 格式转换
│   │   ├── image_processor.py # 图片处理
│   │   └── sync_engine.py     # 同步引擎
│   └── utils/                 # 工具模块
│       ├── config.py          # 配置管理
│       ├── crypto.py          # 加密工具
│       ├── logger.py          # 日志系统
│       └── helpers.py         # 通用工具
├── examples/                  # 示例代码
│   ├── basic_publish.py       # 基础发布
│   ├── batch_sync.py          # 批量同步
│   └── analytics_report.py    # 分析报告
└── tests/                     # 测试文件
    └── test_basic.py
```

---

## 🔧 配置说明

### config.json 结构

```json
{
  "wechat": {
    "app_id": "你的微信AppID",
    "app_secret": "你的微信AppSecret",
    "token": "你的微信Token",
    "encoding_aes_key": "你的加密密钥"
  },
  "xiaohongshu": {
    "phone": "+86138xxxxxxxx",
    "password": "加密后的密码",
    "device_id": "自动生成"
  },
  "sync": {
    "default_tags": ["生活", "分享"],
    "auto_convert_format": true,
    "image_quality": 85
  },
  "scheduler": {
    "timezone": "Asia/Shanghai",
    "retry_attempts": 3,
    "retry_delay": 300
  }
}
```

### 安全说明
- 所有凭证使用AES-256加密存储
- 设备指纹随机化，保护账号安全
- 会话Token自动刷新
- 内置IP轮换支持

---

## 📖 使用示例

### 示例1：获取微信公众号文章
```python
from scripts.wechat import WeChatManager

wc = WeChatManager()
articles = wc.get_article_list(offset=0, count=10)

for article in articles:
    print(f"标题: {article['title']}")
    print(f"阅读量: {article['read_num']}")
    print(f"点赞数: {article['like_num']}")
```

### 示例2：发布小红书笔记
```python
from scripts.xiaohongshu import XHSManager

xhs = XHSManager()
xhs.publish_note(
    title="发现上海的隐藏宝藏！✨",
    content="今天发现了一个超棒的地方...",
    images=["/path/to/image1.jpg", "/path/to/image2.jpg"],
    tags=["上海探店", "生活方式", "周末去哪"]
)
```

### 示例3：双平台同步
```python
from scripts.sync import CrossPlatformSync

sync = CrossPlatformSync()

# 将特定微信文章同步到小红书
result = sync.sync_article_to_xhs(
    article_id="你的文章ID",
    custom_title="优化后的小红书标题",
    add_tags=["热门", "推荐"]
)

print(f"已同步至: {result['xhs_url']}")
```

### 示例4：定时发布
```python
from scripts.utils import Scheduler
from datetime import datetime, timedelta

scheduler = Scheduler()

# 定时明天早上9:00发布
publish_time = datetime.now() + timedelta(days=1)
publish_time = publish_time.replace(hour=9, minute=0)

scheduler.schedule_xhs_note(
    title="早安灵感 ☀️",
    content="...",
    images=["..."],
    publish_at=publish_time
)
```

---

## 🔐 认证方式

### 微信公众号

**方式A：微信公众号API（订阅号/服务号）**
- 需要：AppID, AppSecret
- 适合：有API权限的公众号
- 稳定性：⭐⭐⭐⭐⭐

**方式B：微信网页版**
- 需要：扫码登录（一次性）
- 适合：个人号、快速测试
- 稳定性：⭐⭐⭐⭐

### 小红书

**方式A：手机号+密码**
- 需要：手机号、密码
- 自动处理：设备注册、短信验证
- 稳定性：⭐⭐⭐⭐⭐

**方式B：Cookie会话**
- 需要：从浏览器导出的Cookie
- 适合：高级用户、多账号管理
- 稳定性：⭐⭐⭐⭐

---

## 📊 数据分析与报告

### 微信可用指标
- `read_num`: 文章阅读量
- `like_num`: 点赞数
- `share_num`: 分享数
- `comment_num`: 评论数
- `fav_num`: 收藏数

### 小红书可用指标
- `impressions`: 笔记曝光量
- `likes`: 点赞数
- `collects`: 收藏数
- `comments`: 评论数
- `follows`: 笔记带来的新关注

### 生成报告
```python
from scripts.utils import ReportGenerator

reporter = ReportGenerator()
report = reporter.generate_weekly_report(
    start_date="2024-01-01",
    end_date="2024-01-07"
)

reporter.export_to_pdf(report, "weekly_report.pdf")
```

---

## ⚙️ 高级功能

### 1. 批量操作
```python
# 同时发布10篇文章到双平台
sync.batch_sync(
    article_ids=["id1", "id2", ...],
    schedule_spread=True,  # 错峰发布
    spread_hours=48
)
```

### 2. 智能内容转换
- 自动将长文章摘要成小红书风格
- 将微信格式转换为小红书格式
- 根据内容自动生成标签
- 推荐最佳发布时间

### 3. 图片处理
- 自动调整平台所需尺寸
- 可选添加水印
- 压缩优化，加速上传
- 自动生成缩略图

### 4. 代理与IP管理
```python
# 内置代理支持
config = {
    "proxy": {
        "enabled": True,
        "type": "rotating_residential",
        "endpoint": "http://proxy.provider.com:8080"
    }
}
```

---

## 🛠️ 故障排除

### 常见问题

**Q: 微信登录失败，提示"session expired"**
A: 运行 `wc.refresh_token()` 或重新扫码登录

**Q: 小红书图片上传失败**
A: 检查图片大小（最大20MB）、格式（JPG/PNG）、尺寸

**Q: 定时发布未执行**
A: 检查时区设置，确认调度守护进程正在运行

**Q: 平台限制频率**
A: 启用内置频率限制，操作间添加延迟

### 调试模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 所有HTTP请求将被记录
wc = WeChatManager(debug=True)
```

---

## 📚 API参考

### WeChatManager

| 方法 | 参数 | 返回值 |
|------|------|--------|
| `login()` | - | `bool` |
| `get_article_list()` | `offset, count` | `List[Article]` |
| `publish_article()` | `title, content, images` | `Article` |
| `get_analytics()` | `article_id` | `Analytics` |
| `delete_article()` | `article_id` | `bool` |

### XHSManager

| 方法 | 参数 | 返回值 |
|------|------|--------|
| `login()` | - | `bool` |
| `get_note_list()` | `offset, count` | `List[Note]` |
| `publish_note()` | `title, content, images, tags` | `Note` |
| `get_note_stats()` | `note_id` | `Stats` |
| `delete_note()` | `note_id` | `bool` |

### CrossPlatformSync

| 方法 | 参数 | 返回值 |
|------|------|--------|
| `sync_article_to_xhs()` | `article_id, options` | `SyncResult` |
| `sync_note_to_wechat()` | `note_id, options` | `SyncResult` |
| `batch_sync()` | `article_ids, options` | `List[SyncResult]` |

---

## 🤝 贡献

欢迎贡献代码！需要帮助的领域：
- 🌐 多语言支持
- 📱 移动端App集成
- 🤖 AI驱动的内容优化
- 📊 高级分析仪表板

---

## 📜 许可证

MIT许可证 - 个人和商业使用免费。

**免责声明**：本工具仅供合法内容管理使用。用户必须遵守微信和小红书的服务条款。

---

## 🔗 链接

- ClawHub: https://clawhub.ai/wechat-xhs-automation
- 文档: https://docs.clawhub.ai/wechat-xhs
- 问题反馈: https://github.com/clawhub/wechat-xhs-automation/issues

---

**用心打造 ❤️ 服务中国创作者经济**

*让内容创作更简单，让跨平台运营更高效*
