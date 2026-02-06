# Browser-use Server (LXC Deploy)

A lightweight, LXC-ready server implementation of [Browser-use](https://github.com/browser-use/browser-use), providing an HTTP API to control a headless browser with LLMs (DeepSeek, Qwen, OpenAI).

> **Note:** This project was purely developed via Agentic coding.

## Features

- **FastAPI Server**: Simple HTTP interface for browser automation.
- **Multi-Model Support**: Works with DeepSeek, Qwen (Alibaba Cloud), OpenAI, and any OpenAI-compatible API.
- **Headless & Secure**: Configured to run in LXC containers (Debian 13) with `--no-sandbox` support.
- **Vision Capable**: Supports multimodal models (like Qwen-VL) for visual web interaction.
- **Logging**: Integrated `loguru` logging with rotation.
- **One-Line Installer**: Easy deployment.

## Installation

Run this command in your fresh Debian 13 LXC container:

```bash
wget -O system_install.sh https://raw.githubusercontent.com/derLars/Browser-use-LXC-deploy/main/system_install.sh
bash system_install.sh
```

This will:
1. Install system dependencies (Python, Git, Playwright deps).
2. Clone this repository.
3. Set up a virtual environment.
4. Install Python packages and Playwright browsers.
5. Setup and start a systemd service (`browser-use.service`).

## Usage

The server runs on port **8000** and accepts POST requests at `/browse`.

### Example: DeepSeek Chat

```bash
curl -X POST "http://<LXC_IP>:8000/browse" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://www.google.com",
           "task": "Find the stock price of AAPL",
           "api_key": "YOUR_DEEPSEEK_API_KEY",
           "model": "deepseek-chat"
         }'
```

### Example: Qwen3-VL (Alibaba Cloud) with Vision

```bash
curl -X POST "http://<LXC_IP>:8000/browse" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://www.reddit.com",
           "task": "Describe the first image on the page",
           "api_key": "YOUR_ALIBABA_KEY",
           "model": "qwen-vl-plus",
           "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
           "use_vision": true
         }'
```

### Example: OpenAI GPT-4o

```bash
curl -X POST "http://<LXC_IP>:8000/browse" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://news.ycombinator.com",
           "task": "Summarize the top story",
           "api_key": "YOUR_OPENAI_KEY",
           "model": "gpt-4o",
           "use_vision": true
         }'
```

## Logs

Application logs are stored in `logs/server.log` (inside the installation directory) with rotation policies (10MB size limit, 10 days retention).

To view live service logs:
```bash
journalctl -u browser-use.service -f
```
