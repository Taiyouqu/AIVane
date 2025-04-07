# AIVANE: Cross-Platform AI Automation Assistant Powered by Natural Language

English | [简体中文](README.md)

<p align="center">
  <img src="assets/logo.png" alt="AIVANE Logo" width="200"/>
</p>

<div align="center">
  
[![GitHub stars](https://img.shields.io/github/stars/taiyouqu/aivane)](https://github.com/taiyouqu/aivane/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/taiyouqu/aivane)](https://github.com/taiyouqu/aivane/network/members)
[![GitHub license](https://img.shields.io/github/license/taiyouqu/aivane)](https://github.com/taiyouqu/aivane/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/taiyouqu/aivane)](https://github.com/taiyouqu/aivane/issues)

</div>

## 📑 Project Overview

AIVANE is a powerful AI+RPA (Robotic Process Automation) tool that allows users to control web browsers, mobile devices, and Windows desktop applications through natural language commands. AIVANE combines the understanding capabilities of large language models with the automation capabilities of RPA to understand complex instructions and transform them into precise automated operations.

### Key Features

- 🔍 **Natural Language Control**: Directly describe the tasks you want to accomplish in natural language
- 💻 **Cross-Platform Support**: Works with web browsers, Windows desktop, and mobile devices
- 🤖 **Intelligent Process Automation**: AI understands your intent and automatically executes corresponding operations
- 🔄 **Highly Adaptive**: Capable of handling interface changes and unexpected situations
- 🛠️ **Extensible**: Easy to integrate new features and support for new applications

## 📌 Table of Contents

- [Demos](#-demos)
- [Quick Start](#-quick-start)
- [Installation Guide](#-installation-guide)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technical Architecture](#-technical-architecture)
- [Contribution Guidelines](#-contribution-guidelines)
- [License](#-license)
- [Contact Us](#-contact-us)

## 🎬 Demos

### Web Browser Automation

[Demo videos coming soon]

### Windows Desktop Application Automation

[Demo videos coming soon]

### Mobile Device Automation

[Demo videos coming soon]

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Windows 10/11 (for desktop automation)
- Android device (for mobile automation)
- Modern web browser (for web automation)

### Installation

```bash
# Clone the repository
git clone https://github.com/taiyouqu/aivane.git
cd aivane

# Install dependencies
pip install -r requirements.txt

# Configure API keys (if applicable)
cp config.example.py config.py
# Edit config.py to set your API keys
```

## 📦 Installation Guide

### Web Automation

Web automation is based on Playwright and requires browser drivers:

```bash
python -m playwright install
```

### Windows Desktop Automation

Windows automation relies on PyAutoGUI and UI automation libraries:

```bash
pip install pyautogui pywinauto
```

### Mobile Device Automation

Android device automation requires ADB tools:

1. Download and install [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. Make sure ADB is in your PATH or specify the ADB path
3. Enable USB debugging on your phone and allow computer connection

```bash
python -m aivane.mobile.setup --adb_path /path/to/adb
```

## 🔧 Usage

### Basic Usage

```python
from aivane import AIVANE

# Initialize AIVANE
agent = AIVANE()

# Execute natural language command
agent.execute("Search for 'latest AI advancements' in the browser and save the first article as PDF")
```

### Command Line Interface

```bash
# Basic command
python -m aivane --command "Open Notepad and write 'Hello World'"

# Device specification
python -m aivane --device web --command "Log in to GitHub and check my projects"
python -m aivane --device windows --command "Open Excel and create a sales report"
python -m aivane --device mobile --command "Open WeChat and send a message to John"
```

## 📂 Project Structure

```
aivane/
├── core/                   # Core modules
│   ├── ai_engine.py        # AI understanding and decision engine
│   ├── executor.py         # Command executor
│   └── utils.py            # Common utility functions
├── web/                    # Web automation module
│   ├── browser.py          # Browser control
│   └── actions.py          # Web operation collection
├── windows/                # Windows automation module
│   ├── desktop.py          # Desktop application control
│   └── actions.py          # Windows operation collection
├── mobile/                 # Mobile device automation module
│   ├── device.py           # Mobile device control
│   └── actions.py          # Mobile operation collection
├── examples/               # Example scripts
├── tests/                  # Test code
├── docs/                   # Documentation
├── assets/                 # Images, icons and other resources
├── config.example.py       # Example configuration file
├── requirements.txt        # Project dependencies
└── setup.py                # Installation script
```

## 🔌 Technical Architecture

AIVANE is built on the following technologies:

- **Natural Language Processing**: Using large language models to understand user intent
- **Computer Vision**: For identifying screen elements and interface components
- **RPA Frameworks**: Executing precise automation operations
- **Heuristic Learning**: Continuously optimizing operation strategies through user feedback

### Architecture Diagram

```
User Instruction → NLP Understanding → Task Decomposition → Operation Planning → Execute Actions → Result Verification
                    ↑                                                            ↓
                    └────────────────── Feedback Learning ───────────────────────┘
```

## 👥 Contribution Guidelines

We welcome community contributions! If you want to participate in project development, please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

For detailed contribution guidelines, please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact Us

- Project Issues: [GitHub Issues](https://github.com/taiyouqu/aivane/issues)

---

<div align="center">
  <sub>Built with ❤️, born for automation</sub>
</div> 
