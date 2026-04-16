# WeChat + XiaoHongShu Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://openclaw.ai)

> **Automate your content across China's top two social platforms. Publish once, reach everywhere.**

English | [中文](./README_CN.md)

## 🎯 What This Project Does

This is a comprehensive automation tool for managing **WeChat Official Accounts** and **XiaoHongShu (Little Red Book)** — China's two most powerful content platforms.

### For Who?
- 🇨🇳 Chinese content creators and self-media operators
- 🏢 MCN agencies managing multiple accounts
- 🌏 Overseas Chinese creators targeting mainland audience
- 💼 Brands building presence in China

## ✨ Core Features

### 1. WeChat Official Account Automation
- ✅ Auto-login and session management (API & Web)
- ✅ Article fetching and management
- ✅ Rich media post publishing (text + images)
- ✅ Scheduled publishing
- ✅ Analytics: reads, likes, shares, comments

### 2. XiaoHongShu Automation
- ✅ Auto-login and cookie management (Phone/SMS/Password)
- ✅ Note fetching and backup
- ✅ Image + video note publishing
- ✅ Scheduled publishing with timezone support
- ✅ Analytics: impressions, likes, collections, follows

### 3. Cross-Platform Sync 🚀
- ✅ **One-click sync**: WeChat Article → XiaoHongShu Note
- ✅ **Auto format conversion** (WeChat → XHS style)
- ✅ **Image optimization** and resizing
- ✅ **Hashtag auto-suggestion**
- ✅ **AI-powered content adaptation**

### 4. Management Dashboard
- ✅ Secure credential storage (AES-256 encrypted)
- ✅ Publishing schedule management
- ✅ Batch operations
- ✅ Full operation logging (Chinese)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenClaw installed
- WeChat Official Account or Web access
- XiaoHongShu account

### Installation

```bash
# Clone the repository
git clone https://github.com/jiaofactory/wechat-xhs-automation.git
cd wechat-xhs-automation

# Install dependencies
pip install -r requirements.txt

# Configure your accounts
cp config.example.json config.json
# Edit config.json with your credentials
```

### Usage Examples

#### 1. WeChat Article Management
```python
from scripts.wechat import WeChatManager

wc = WeChatManager()
articles = wc.get_article_list(offset=0, count=10)

for article in articles:
    print(f"Title: {article['title']}")
    print(f"Reads: {article['read_num']}")
```

#### 2. XiaoHongShu Publishing
```python
from scripts.xiaohongshu import XHSManager

xhs = XHSManager()
xhs.publish_note(
    title="Discovering hidden gems! ✨",
    content="Today I found an amazing place...",
    images=["/path/to/image1.jpg"],
    tags=["travel", "lifestyle", "shanghai"]
)
```

#### 3. Cross-Platform Sync (The Magic! 🎉)
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

## 📁 Project Structure

```
wechat-xhs-automation/
├── SKILL.md                    # OpenClaw Skill documentation
├── README.md                   # This file
├── README_CN.md               # Chinese documentation
├── LICENSE                     # MIT License
├── config.example.json         # Configuration template
├── requirements.txt            # Python dependencies
├── scripts/
│   ├── wechat/                # WeChat modules
│   │   ├── auth.py            # Authentication
│   │   ├── publisher.py       # Content publishing
│   │   ├── analytics.py       # Data analytics
│   │   └── scheduler.py       # Task scheduling
│   ├── xiaohongshu/           # XHS modules
│   │   ├── auth.py            # Authentication
│   │   ├── publisher.py       # Content publishing
│   │   ├── analytics.py       # Data monitoring
│   │   └── scheduler.py       # Task scheduling
│   ├── sync/                  # Sync modules
│   │   ├── converter.py       # Format conversion
│   │   ├── image_processor.py # Image optimization
│   │   └── sync_engine.py     # Sync orchestration
│   └── utils/                 # Utilities
│       ├── crypto.py          # Encryption
│       ├── logger.py          # Logging (Chinese)
│       └── config.py          # Configuration
├── examples/                   # Usage examples
└── tests/                      # Unit tests
```

## 🔐 Security

- **AES-256 encryption** for credential storage
- **Device fingerprint randomization** for safety
- **Session token auto-refresh**
- **IP rotation support** included
- **No hardcoded credentials** (ever!)

## 🛠️ Configuration

### WeChat Official Account

**Option A: API Access (Recommended)**
```json
{
  "wechat": {
    "app_id": "your_app_id",
    "app_secret": "your_app_secret",
    "token": "your_token",
    "encoding_aes_key": "your_key"
  }
}
```

**Option B: Web Interface**
- QR code scan (one-time setup)
- Suitable for personal accounts

### XiaoHongShu

**Option A: Phone + Password**
```json
{
  "xiaohongshu": {
    "phone": "+86138xxxxxxxx",
    "password": "encrypted_password"
  }
}
```

**Option B: Cookie Session**
- Export cookies from browser
- Suitable for multiple accounts

## 📊 Analytics & Reporting

### WeChat Metrics
- `read_num`: Article reads
- `like_num`: Likes
- `share_num`: Shares
- `comment_num`: Comments
- `fav_num`: Favorites

### XiaoHongShu Metrics
- `impressions`: Note impressions
- `likes`: Like count
- `collects`: Collections
- `comments`: Comments
- `follows`: New followers

## 🤝 Contributing

Contributions welcome! Areas needing help:
- 🌐 Multi-language support
- 📱 Mobile app integration
- 🤖 AI-powered content optimization
- 📊 Advanced analytics dashboards

## 📜 License

MIT License - Free for personal and commercial use.

**Disclaimer**: This tool is for legitimate content management only. Users must comply with WeChat and XiaoHongShu Terms of Service.

## 🔗 Links

- **GitHub**: https://github.com/jiaofactory/wechat-xhs-automation
- **ClawHub**: https://clawhub.ai/jiaofactory/wechat-xhs-automation
- **Documentation**: https://docs.clawhub.ai/wechat-xhs
- **Issues**: https://github.com/jiaofactory/wechat-xhs-automation/issues

## 💬 Support

- 📧 Email: 99.jiaojiao.99@gmail.com
- 💬 WeChat: JiaoFactory
- 🐦 Twitter: @JiaoFactory

---

**Built with ❤️ by Jiao Factory**

*Empowering creators to focus on content, not logistics.*
