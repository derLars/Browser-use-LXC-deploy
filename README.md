# Browser-use Server

A production-ready FastAPI server implementation of [Browser-use](https://github.com/browser-use/browser-use), providing an HTTP API to control a headless browser with LLMs for automated web interaction tasks.

> **Note:** This project was purely developed via Agentic coding.

## 🚀 Quick Start

```bash
wget -O system_install.sh https://raw.githubusercontent.com/derLars/Browser-use-LXC-deploy/main/system_install.sh
bash system_install.sh
```

The server will be running on port **8000** after installation completes.

## ✨ Features

- 🎯 **FastAPI Server**: Simple HTTP interface for browser automation
- 🤖 **Multi-Model Support**: DeepSeek, Qwen (Alibaba Cloud), OpenAI, and any OpenAI-compatible API
- 🐧 **LXC Optimized**: Configured for Debian 13 containers with `--no-sandbox` support
- 👁️ **Vision Capable**: Supports multimodal models (like Qwen-VL, GPT-4o) for visual web interaction
- 📊 **Production Ready**: Systemd service, logging with rotation, and automatic restart
- ⚡ **One-Line Installer**: Automated deployment with zero manual configuration
- 🔒 **Headless & Secure**: Runs without GUI in secure container environments

## 🔧 System Requirements

- **OS**: Debian 13 (Trixie) or compatible Linux distribution
- **Container**: LXC container (or bare-metal)
- **Python**: 3.9+ (automatically installed)
- **RAM**: 2GB minimum (4GB+ recommended for vision models)
- **Disk**: 2GB free space for dependencies and browsers
- **Network**: Internet connection for API access

## 📦 What's Included

- `server.py` - FastAPI application with browser automation endpoints
- `requirements.txt` - Python dependencies
- `system_install.sh` - Automated installation and service setup script

## 🎯 Supported LLM Providers

| Provider | Base URL | Vision Support | Example Models |
|----------|----------|----------------|----------------|
| DeepSeek | `https://api.deepseek.com/v1` | ✅ | deepseek-chat, deepseek-reasoner |
| Qwen (Alibaba) | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | ✅ | qwen-vl-plus, qwen-turbo |
| OpenAI | `https://api.openai.com/v1` | ✅ | gpt-4o, gpt-4-turbo |
| Custom | Your endpoint | Depends | Any OpenAI-compatible API |

## ⚙️ API Usage

The server runs on port **8000** and accepts POST requests at `/browse`.

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | Starting URL for the browser |
| `task` | string | ✅ | - | Task description for the LLM agent |
| `api_key` | string | ✅ | - | API key for the LLM provider |
| `model` | string | ❌ | `deepseek-chat` | Model identifier |
| `base_url` | string | ❌ | `https://api.deepseek.com/v1` | API endpoint URL |
| `use_vision` | boolean | ❌ | `false` | Enable vision capabilities |
| `timeout` | integer | ❌ | `900` | Request timeout in seconds (15 minutes) |
| `max_steps` | integer | ❌ | `100` | Maximum agent steps to prevent infinite loops |

### Example 1: DeepSeek Chat

```bash
curl -X POST "http://<LXC_IP>:8000/browse" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://www.google.com",
           "task": "Find the current stock price of AAPL",
           "api_key": "YOUR_DEEPSEEK_API_KEY",
           "model": "deepseek-chat"
         }'
```

### Example 2: Qwen3-VL (Vision)

```bash
curl -X POST "http://<LXC_IP>:8000/browse" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://www.reddit.com",
           "task": "Describe the first image you see on the page",
           "api_key": "YOUR_ALIBABA_KEY",
           "model": "qwen-vl-plus",
           "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
           "use_vision": true
         }'
```

### Example 3: OpenAI GPT-4o

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

### Example 4: Complex Task with DeepSeek Reasoner

```bash
curl -X POST "http://<LXC_IP>:8000/browse" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://www.amazon.com",
           "task": "Search for wireless headphones under $100, find the top rated one, and tell me its price and rating",
           "api_key": "YOUR_DEEPSEEK_API_KEY",
           "model": "deepseek-reasoner"
         }'
```

### Example 5: Long-Running Task with Custom Timeout

```bash
curl -X POST "http://<LXC_IP>:8000/browse" \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://example.com/complex-page",
           "task": "Extract all data from multiple pages",
           "api_key": "YOUR_API_KEY",
           "model": "deepseek-chat",
           "timeout": 1800,
           "max_steps": 150
         }'
```

> **Note:** For n8n users, ensure your HTTP Request node timeout is set higher than the server timeout parameter (e.g., 1000000ms for 16+ minutes).

## 📋 Installation Details

The `system_install.sh` script performs the following:

1. ✅ Installs system dependencies (Python, Git, Playwright deps)
2. ✅ Clones or updates the repository to `/opt/browser-use-server`
3. ✅ Creates Python virtual environment
4. ✅ Installs Python packages from `requirements.txt`
5. ✅ Installs Playwright Chromium browser with dependencies
6. ✅ Configures systemd service (`browser-use.service`)
7. ✅ Enables and starts the service automatically

### Updating Existing Installations

If you already have the server installed and want to update to get the timeout fixes:

```bash
# Re-run the installation script (it will update automatically)
cd /opt/browser-use-server
git pull
bash system_install.sh
```

Or manually update:

```bash
# Pull latest changes
cd /opt/browser-use-server
git pull

# Update dependencies (if needed)
./venv/bin/pip install -r requirements.txt

# Restart the service
systemctl restart browser-use.service

# Verify the service is running
systemctl status browser-use.service
```

## 🔍 Monitoring

### Service Status
```bash
systemctl status browser-use.service
```

### Real-time Logs
```bash
journalctl -u browser-use.service -f
```

### Application Logs
```bash
tail -f /opt/browser-use-server/logs/server.log
```

### Test Server Health
```bash
curl http://localhost:8000/docs
```

## 🐛 Troubleshooting

### Common Issues

**Service won't start:**
```bash
systemctl status browser-use.service
journalctl -u browser-use.service -n 50
```

**Playwright browser issues in LXC:**
- The `--no-sandbox` flag is automatically configured
- Ensure your LXC container has sufficient privileges
- Check for missing system dependencies

**API key errors:**
- Verify your API key is correct
- Check the `base_url` matches your provider
- Ensure the model name is valid for your provider

**Vision not working:**
- Set `use_vision: true` in the request
- Ensure the model supports vision (e.g., qwen-vl-plus, gpt-4o)
- Check that the page contains images to process

**Task timeout errors:**
- The default timeout is 15 minutes (900 seconds)
- For longer tasks, increase the `timeout` parameter in your request
- Check server logs to see if the agent started execution: `journalctl -u browser-use.service -f`
- For n8n users: Set HTTP Request node timeout higher than server timeout
  - Example: Server timeout 900s → n8n timeout 1000000ms (16+ minutes)

**Agent reaches max_steps:**
- Default is 100 steps to prevent infinite loops
- Increase `max_steps` parameter if your task requires more browser actions
- Consider breaking complex tasks into smaller subtasks

### Service Management

**Restart the service:**
```bash
systemctl restart browser-use.service
```

**Stop the service:**
```bash
systemctl stop browser-use.service
```

**View service logs:**
```bash
journalctl -u browser-use.service --since "1 hour ago"
```

**Manual start (for debugging):**
```bash
cd /opt/browser-use-server
./venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
```

## 📊 Logging Configuration

Application logs are stored in `/opt/browser-use-server/logs/server.log` with:

- **Rotation**: 10MB file size limit
- **Retention**: 10 days
- **Level**: INFO (includes errors, warnings, and info messages)
- **Features**: Backtrace and diagnostic information enabled

## 🌟 What Makes This Special?

### Agentic Development
This entire project was developed using AI-powered agentic coding, demonstrating:
- Clean, production-ready code architecture
- Comprehensive error handling and logging
- Automated deployment and service management
- Multi-provider LLM integration

### LXC Optimization
Unlike standard browser automation setups, this server is specifically optimized for:
- Running in unprivileged LXC containers
- Headless operation without display dependencies
- Secure sandbox configuration for containerized environments
- Minimal resource footprint

### Production Features
- **Systemd Integration**: Automatic startup and restart on failure
- **Structured Logging**: Rotated logs with proper retention policies
- **Clean API Design**: RESTful endpoints with clear request/response patterns
- **Error Handling**: Comprehensive error messages and status codes
- **Extensibility**: Easy to add new LLM providers via OpenAI-compatible interface

## 📝 License

This project uses the [Browser-use](https://github.com/browser-use/browser-use) framework. Please refer to the Browser-use repository for licensing information.

The server implementation is open source and available for use in your projects.

## 🤝 Contributing

Contributions are welcome! This project is specifically optimized for:
- LXC containers and containerized environments
- Multi-provider LLM integration
- Production deployments with systemd
- Headless browser automation

Feel free to submit issues or pull requests.

## 🔗 Links

- **GitHub**: [derLars/Browser-use-LXC-deploy](https://github.com/derLars/Browser-use-LXC-deploy)
- **Browser-use Framework**: [browser-use/browser-use](https://github.com/browser-use/browser-use)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **Playwright Documentation**: [playwright.dev](https://playwright.dev/)

## 💡 Use Cases

- **Web Scraping**: Extract data from complex, JavaScript-heavy websites
- **Automated Testing**: Test web applications with natural language instructions
- **Research**: Gather information from multiple sources automatically
- **Content Monitoring**: Track changes on websites over time
- **Form Automation**: Fill out forms and submit data programmatically
- **Visual Analysis**: Use vision models to understand page layouts and content

---

**Status**: Production Ready  
**Tested On**: Debian 13 (Trixie) LXC Container  
**Last Updated**: February 6, 2026
