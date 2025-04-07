# AIVANE: 基于自然语言的跨平台AI自动化助手

[English](README_en.md) | 简体中文

<p align="center">
  <img src="assets/logo.png" alt="AIVANE Logo" width="200"/>
</p>

<div align="center">
  
[![GitHub stars](https://img.shields.io/github/stars/taiyouqu/aivane)](https://github.com/taiyouqu/aivane/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/taiyouqu/aivane)](https://github.com/taiyouqu/aivane/network/members)
[![GitHub license](https://img.shields.io/github/license/taiyouqu/aivane)](https://github.com/taiyouqu/aivane/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/taiyouqu/aivane)](https://github.com/taiyouqu/aivane/issues)

</div>

## 📑 项目概述

AIVANE是一个强大的AI+RPA(机器人流程自动化)工具，允许用户通过自然语言命令控制网页、手机和Windows桌面应用程序。AIVANE结合了大型语言模型的理解能力和RPA的自动化能力，能够理解复杂指令并将其转化为精确的自动化操作。

### 主要特点

- 🔍 **自然语言控制**：直接用自然语言描述您想要完成的任务
- 💻 **跨平台支持**：支持Web浏览器、Windows桌面和移动设备
- 🤖 **智能流程自动化**：AI理解您的意图并自动执行相应操作
- 🔄 **适应性强**：能够处理界面变化和未预期情况
- 🛠️ **可扩展**：易于集成新功能和支持新应用

## 📌 目录

- [演示](#-演示)
- [快速开始](#-快速开始)
- [安装指南](#-安装指南)
- [使用方法](#-使用方法)
- [项目结构](#-项目结构)
- [技术架构](#-技术架构)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)
- [联系我们](#-联系我们)

## 🎬 演示

### Web浏览器自动化

[演示视频即将上线]

### Windows桌面应用自动化

[演示视频即将上线]

### 移动设备自动化

[演示视频即将上线]

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows 10/11 (桌面自动化)
- Android设备 (移动自动化)
- 现代Web浏览器 (Web自动化)

### 安装

```bash
# 克隆仓库
git clone https://github.com/taiyouqu/aivane.git
cd aivane

# 安装依赖
pip install -r requirements.txt

# 配置API密钥(如适用)
cp config.example.py config.py
# 编辑config.py设置您的API密钥
```

## 📦 安装指南

### Web自动化

Web自动化基于Playwright，需要安装浏览器驱动：

```bash
python -m playwright install
```

### Windows桌面自动化

Windows自动化依赖于PyAutoGUI和UI自动化库：

```bash
pip install pyautogui pywinauto
```

### 移动设备自动化

Android设备自动化需要ADB工具：

1. 下载并安装[Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. 确保ADB在您的PATH中或指定ADB路径
3. 在手机上启用USB调试并允许计算机连接

```bash
python -m aivane.mobile.setup --adb_path /path/to/adb
```

## 🔧 使用方法

### 基本用法

```python
from aivane import AIVANE

# 初始化AIVANE
agent = AIVANE()

# 执行自然语言命令
agent.execute("在浏览器中搜索'人工智能最新进展'并保存第一篇文章为PDF")
```

### 命令行界面

```bash
# 基本命令
python -m aivane --command "打开记事本并写入'Hello World'"

# 设备指定
python -m aivane --device web --command "登录GitHub并查看我的项目"
python -m aivane --device windows --command "打开Excel并创建销售报表"
python -m aivane --device mobile --command "打开微信并发送消息给张三"
```

## 📂 项目结构

```
aivane/
├── core/                   # 核心模块
│   ├── ai_engine.py        # AI理解和决策引擎
│   ├── executor.py         # 命令执行器
│   └── utils.py            # 通用工具函数
├── web/                    # Web自动化模块
│   ├── browser.py          # 浏览器控制
│   └── actions.py          # Web操作集合
├── windows/                # Windows自动化模块
│   ├── desktop.py          # 桌面应用控制
│   └── actions.py          # Windows操作集合
├── mobile/                 # 移动设备自动化模块
│   ├── device.py           # 移动设备控制
│   └── actions.py          # 移动操作集合
├── examples/               # 示例脚本
├── tests/                  # 测试代码
├── docs/                   # 文档
├── assets/                 # 图片、图标等资源
├── config.example.py       # 示例配置文件
├── requirements.txt        # 项目依赖
└── setup.py                # 安装脚本
```

## 🔌 技术架构

AIVANE基于以下技术构建：

- **自然语言处理**：使用大型语言模型理解用户意图
- **计算机视觉**：用于识别屏幕元素和界面组件
- **RPA框架**：执行精确的自动化操作
- **启发式学习**：通过用户反馈不断优化操作策略

### 架构图

```
用户指令 → NLP理解 → 任务分解 → 操作规划 → 执行动作 → 结果验证
           ↑                               ↓
           └───────── 反馈学习 ────────────┘
```

## 👥 贡献指南

我们欢迎社区贡献！如果您想参与项目开发，请遵循以下步骤：

1. Fork该仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建一个Pull Request

详细贡献指南请参阅[CONTRIBUTING.md](CONTRIBUTING.md)文件。

## 📄 许可证

该项目采用MIT许可证 - 详情请参阅[LICENSE](LICENSE)文件。

## 📞 联系我们

- 项目问题：[GitHub Issues](https://github.com/taiyouqu/aivane/issues)

---

<div align="center">
  <sub>构建于❤️之上，为自动化而生</sub>
</div>
