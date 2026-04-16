# WeChat + XiaoHongShu Automation Skill

中文名称：微信小红书自动化管理工具

**Automate your content across China's top two social platforms. Publish once, reach everywhere.**

---

## 🎯 What This Skill Does

This skill provides complete automation for managing **WeChat Official Accounts** and **XiaoHongShu (Little Red Book)** — China's two most powerful content platforms.

### For Who?
- 🇨🇳 Chinese content creators and self-media operators
- 🏢 MCN agencies managing multiple accounts
- 🌏 Overseas Chinese creators targeting mainland audience
- 💼 Brands building presence in China

---

## ✨ Core Features

### 1. WeChat Official Account Automation
- ✅ Auto-login and session management
- ✅ Article fetching and management
- ✅ Rich media post publishing (text + images)
- ✅ Scheduled publishing
- ✅ Analytics: reads, likes, shares, comments

### 2. XiaoHongShu Automation
- ✅ Auto-login and cookie management
- ✅ Note fetching and backup
- ✅ Image + video note publishing
- ✅ Scheduled publishing with timezone support
- ✅ Analytics: impressions, likes, collections, follows

### 3. Cross-Platform Sync
- ✅ One-click sync: WeChat Article → XiaoHongShu Note
- ✅ Auto format conversion (WeChat → XHS style)
- ✅ Image optimization and resizing
- ✅ Hashtag auto-suggestion

### 4. Management Dashboard
- ✅ Secure credential storage (encrypted)
- ✅ Publishing schedule management
- ✅ Batch operations
- ✅ Full operation logging

---

## 🚀 Quick Start (10 Minutes to First Post)

### Step 1: Install the Skill
```bash
clawhub install wechat-xhs-automation
```

### Step 2: Configure Your Accounts
```bash
cp config.example.json config.json
# Edit config.json with your credentials
```

### Step 3: Test Connection
```python
from wechat_xhs_automation import WeChatManager, XHSManager

# Test WeChat
wc = WeChatManager()
print(wc.test_login())

# Test XiaoHongShu
xhs = XHSManager()
print(xhs.test_login())
```

### Step 4: Publish Your First Post
```python
# Cross-platform publish
sync = CrossPlatformSync()
sync.publish_wechat_to_xhs(
    article_url="https://mp.weixin.qq.com/s/...",
    xhs_title="Your XHS Title",
    xhs_tags=[" lifestyle", "tips"]
)
```

---

## 📁 File Structure

```
wechat-xhs-automation/
├── SKILL.md                    # This documentation
├── README.md                   # Chinese documentation
├── config.example.json         # Example configuration
├── requirements.txt            # Python dependencies
├── scripts/
│   ├── wechat/
│   │   ├── __init__.py
│   │   ├── auth.py            # WeChat login & auth
│   │   ├── publisher.py       # Article publishing
│   │   ├── analytics.py       # Data analytics
│   │   └── scheduler.py       # Scheduled publishing
│   ├── xiaohongshu/
│   │   ├── __init__.py
│   │   ├── auth.py            # XHS login & auth
│   │   ├── publisher.py       # Note publishing
│   │   ├── analytics.py       # Data monitoring
│   │   └── scheduler.py       # Scheduled publishing
│   ├── sync/
│   │   ├── __init__.py
│   │   ├── converter.py       # Format conversion
│   │   ├── image_processor.py # Image optimization
│   │   └── sync_engine.py     # Sync orchestration
│   └── utils/
│       ├── __init__.py
│       ├── config.py          # Config management
│       ├── crypto.py          # Encryption utilities
│       ├── logger.py          # Logging system
│       └── helpers.py         # Common utilities
├── examples/
│   ├── basic_publish.py       # Basic publishing example
│   ├── batch_sync.py          # Batch sync example
│   └── analytics_report.py    # Analytics example
└── tests/
    └── test_basic.py          # Unit tests
```

---

## 🔧 Configuration

### config.json Structure

```json
{
  "wechat": {
    "app_id": "your_wechat_app_id",
    "app_secret": "your_wechat_app_secret",
    "token": "your_wechat_token",
    "encoding_aes_key": "your_encoding_key"
  },
  "xiaohongshu": {
    "phone": "+86138xxxxxxxx",
    "password": "encrypted_password",
    "device_id": "auto_generated"
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

### Security Notes
- All credentials are encrypted using AES-256
- Device fingerprints are randomized for safety
- Session tokens auto-refresh
- IP rotation support included

---

## 📖 Usage Examples

### Example 1: Fetch WeChat Articles
```python
from scripts.wechat import WeChatManager

wc = WeChatManager()
articles = wc.get_article_list(offset=0, count=10)

for article in articles:
    print(f"Title: {article['title']}")
    print(f"Reads: {article['read_num']}")
    print(f"Likes: {article['like_num']}")
```

### Example 2: Publish to XiaoHongShu
```python
from scripts.xiaohongshu import XHSManager

xhs = XHSManager()
xhs.publish_note(
    title="Discovering hidden gems in Shanghai! ✨",
    content="今天发现了一个超棒的地方...",
    images=["/path/to/image1.jpg", "/path/to/image2.jpg"],
    tags=["上海探店", "生活方式", "周末去哪"]
)
```

### Example 3: Cross-Platform Sync
```python
from scripts.sync import CrossPlatformSync

sync = CrossPlatformSync()

# Sync specific WeChat article to XHS
result = sync.sync_article_to_xhs(
    article_id="your_article_id",
    custom_title="Optimized XHS Title",
    add_tags=["热门", "推荐"]
)

print(f"Synced to: {result['xhs_url']}")
```

### Example 4: Scheduled Publishing
```python
from scripts.utils import Scheduler
from datetime import datetime, timedelta

scheduler = Scheduler()

# Schedule for tomorrow at 9:00 AM
publish_time = datetime.now() + timedelta(days=1)
publish_time = publish_time.replace(hour=9, minute=0)

scheduler.schedule_xhs_note(
    title="Morning inspiration ☀️",
    content="...",
    images=["..."],
    publish_at=publish_time
)
```

---

## 🔐 Authentication Methods

### WeChat Official Account

**Option A: WeChat MP Account (订阅号/服务号)**
- Requires: AppID, AppSecret
- Best for: Official accounts with API access
- Stability: ⭐⭐⭐⭐⭐

**Option B: WeChat Web Interface**
- Requires: QR code scan (one-time)
- Best for: Personal accounts, quick testing
- Stability: ⭐⭐⭐⭐

### XiaoHongShu

**Option A: Phone + Password**
- Requires: Phone number, password
- Auto handles: Device registration, SMS verification
- Stability: ⭐⭐⭐⭐⭐

**Option B: Cookie Session**
- Requires: Exported cookies from browser
- Best for: Advanced users, multiple accounts
- Stability: ⭐⭐⭐⭐

---

## 📊 Analytics & Reporting

### WeChat Metrics Available
- `read_num`: Article reads
- `like_num`: Likes
- `share_num`: Shares
- `comment_num`: Comments
- `fav_num`: Favorites

### XiaoHongShu Metrics Available
- `impressions`: Note impressions
- `likes`: Like count
- `collects`: Collections
- `comments`: Comments
- `follows`: New followers from note

### Generate Report
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

## ⚙️ Advanced Features

### 1. Batch Operations
```python
# Publish 10 articles across both platforms
sync.batch_sync(
    article_ids=["id1", "id2", ...],
    schedule_spread=True,  # Spread posts over time
    spread_hours=48
)
```

### 2. Smart Content Conversion
- Auto-summarizes long WeChat articles for XHS
- Converts WeChat formatting to XHS style
- Auto-generates hashtags from content
- Suggests optimal posting times

### 3. Image Processing
- Auto-resizes for platform requirements
- Adds watermarks (optional)
- Compresses for faster upload
- Generates thumbnails

### 4. Proxy & IP Management
```python
# Built-in proxy support
config = {
    "proxy": {
        "enabled": True,
        "type": " rotating_residential",
        "endpoint": "http://proxy.provider.com:8080"
    }
}
```

---

## 🛠️ Troubleshooting

### Common Issues

**Q: WeChat login fails with "session expired"**
A: Run `wc.refresh_token()` or re-authenticate with QR code

**Q: XHS image upload fails**
A: Check image size (max 20MB), format (JPG/PNG), and dimensions

**Q: Scheduled posts not publishing**
A: Verify timezone setting, check scheduler daemon is running

**Q: Rate limited by platform**
A: Enable built-in rate limiting, add delays between operations

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# All HTTP requests will be logged
wc = WeChatManager(debug=True)
```

---

## 📚 API Reference

### WeChatManager

| Method | Parameters | Returns |
|--------|------------|---------|
| `login()` | - | `bool` |
| `get_article_list()` | `offset, count` | `List[Article]` |
| `publish_article()` | `title, content, images` | `Article` |
| `get_analytics()` | `article_id` | `Analytics` |
| `delete_article()` | `article_id` | `bool` |

### XHSManager

| Method | Parameters | Returns |
|--------|------------|---------|
| `login()` | - | `bool` |
| `get_note_list()` | `offset, count` | `List[Note]` |
| `publish_note()` | `title, content, images, tags` | `Note` |
| `get_note_stats()` | `note_id` | `Stats` |
| `delete_note()` | `note_id` | `bool` |

### CrossPlatformSync

| Method | Parameters | Returns |
|--------|------------|---------|
| `sync_article_to_xhs()` | `article_id, options` | `SyncResult` |
| `sync_note_to_wechat()` | `note_id, options` | `SyncResult` |
| `batch_sync()` | `article_ids, options` | `List[SyncResult]` |

---

## 🤝 Contributing

Contributions welcome! Areas needing help:
- 🌐 Multi-language support
- 📱 Mobile app integration
- 🤖 AI-powered content optimization
- 📊 Advanced analytics dashboards

---

## 📜 License

MIT License - Free for personal and commercial use.

**Disclaimer**: This tool is for legitimate content management only. Users must comply with WeChat and XiaoHongShu Terms of Service.

---

## 🔗 Links

- ClawHub: https://clawhub.ai/wechat-xhs-automation
- Documentation: https://docs.clawhub.ai/wechat-xhs
- Issues: https://github.com/clawhub/wechat-xhs-automation/issues

---

**Built with ❤️ for China's creator economy**

*让内容创作更简单，让跨平台运营更高效*
