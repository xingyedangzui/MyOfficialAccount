# 微信公众号 AI 功能配置指南

## 🎉 功能介绍

本项目已接入免费的AI对话功能，用户在微信公众号中发送任意消息，如果不匹配特定命令，将会自动调用AI生成智能回复。

### 支持的免费AI服务

| 服务 | 免费额度 | 特点 | 推荐指数 |
|------|---------|------|---------|
| **SiliconFlow (硅基流动)** | 每日免费额度充足 | 国内服务，速度快 | ⭐⭐⭐⭐⭐ |
| **DeepSeek** | 注册送免费额度 | 国产大模型，效果好 | ⭐⭐⭐⭐⭐ |
| **通义千问** | 每月免费额度 | 阿里云，稳定可靠 | ⭐⭐⭐⭐ |
| **智谱 ChatGLM** | 每月免费额度 | 清华技术，中文友好 | ⭐⭐⭐⭐ |
| **讯飞星火** | Lite版免费 | 语音技术强 | ⭐⭐⭐ |

## 🚀 快速开始

### 推荐方案：配置 SiliconFlow (最简单)

1. 访问 https://siliconflow.cn/ 注册账号
2. 登录后进入「API密钥」页面
3. 创建一个新的 API Key
4. 打开 `script/ai_service.py` 文件
5. 找到 `SILICONFLOW_API_KEY = ''` 这一行
6. 将获取的 API Key 填入引号中：
   ```python
   SILICONFLOW_API_KEY = 'sk-xxxxxxxxxxxxxxxxxx'
   ```
7. 保存文件，重启服务即可

### 备选方案：配置 DeepSeek

1. 访问 https://platform.deepseek.com/ 注册账号
2. 进入「API Keys」页面创建密钥
3. 打开 `script/ai_service.py` 文件
4. 找到 `DEEPSEEK_API_KEY = ''` 这一行
5. 填入你的 API Key

### 多服务配置（推荐）

为了提高可用性，建议配置多个AI服务。系统会按优先级自动选择：

```python
# AI服务优先级配置（按顺序尝试）
AI_SERVICE_PRIORITY = ['siliconflow', 'deepseek', 'qwen', 'zhipu', 'spark']
```

## 📝 配置示例

编辑 `script/ai_service.py` 文件：

```python
# SiliconFlow 免费 API (硅基流动，每日免费额度)
SILICONFLOW_API_KEY = 'sk-your-siliconflow-key-here'

# 免费的 DeepSeek API (有免费额度)
DEEPSEEK_API_KEY = 'sk-your-deepseek-key-here'

# 通义千问配置 (阿里云百炼平台免费额度)
QWEN_API_KEY = 'sk-your-qwen-key-here'

# 智谱 ChatGLM 配置 (每月有免费额度)
ZHIPU_API_KEY = 'your-zhipu-key-here'

# 讯飞星火配置 (免费版 Spark Lite)
SPARK_APPID = 'your-appid'
SPARK_API_KEY = 'your-api-key'
SPARK_API_SECRET = 'your-api-secret'
```

## 🔧 高级配置

### 自定义AI人设

修改 `script/ai_service.py` 中的 `AI_SYSTEM_PROMPT`：

```python
AI_SYSTEM_PROMPT = """你是「源源和娇娇的家」微信公众号的智能助手，名叫"小源"。

你的特点：
- 性格温暖、活泼、有趣
- 回复简洁但不失温度，每次回复控制在150字以内
- 喜欢使用适当的emoji表情
...
"""
```

### 调整超时时间

微信公众号要求5秒内响应，默认超时设置为4秒：

```python
AI_REQUEST_TIMEOUT = 4  # 秒
```

### 对话历史长度

```python
MAX_HISTORY_LENGTH = 10  # 保留最近10轮对话
```

## 🎮 用户使用方式

- **AI对话**：直接发送任意消息
- **重置对话**：发送「新对话」「清除对话」「重置对话」

## ❓ 常见问题

### Q: AI没有回复？

1. 检查是否正确配置了至少一个 API Key
2. 检查网络连接是否正常
3. 查看服务器日志中的 `[AI]` 相关信息

### Q: 回复太慢/超时？

1. 微信公众号要求5秒内响应
2. 建议使用国内服务（SiliconFlow、DeepSeek）
3. 可以适当减少 `MAX_HISTORY_LENGTH`

### Q: 免费额度用完了？

1. 配置多个服务作为备份
2. 系统会自动切换到其他可用服务
3. 如果所有服务都不可用，会返回预设的备用回复

### Q: 如何测试配置是否成功？

运行测试脚本：
```bash
cd script
python ai_service.py
```

## 📊 各服务申请地址

| 服务 | 申请地址 |
|------|---------|
| SiliconFlow | https://siliconflow.cn/ |
| DeepSeek | https://platform.deepseek.com/ |
| 通义千问 | https://bailian.console.aliyun.com/ |
| 智谱 ChatGLM | https://open.bigmodel.cn/ |
| 讯飞星火 | https://xinghuo.xfyun.cn/ |

## 🔒 安全建议

1. **不要将 API Key 提交到公开仓库**
2. 建议使用环境变量存储敏感信息
3. 定期检查 API 使用量，防止超额

## 📞 技术支持

如有问题，请查看服务器日志或联系开发者。
