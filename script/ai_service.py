# -*- coding: utf-8 -*-
"""
AI 服务模块 - 为微信公众号提供免费AI对话能力

支持的免费AI服务：
1. 通义千问 (Qwen) - 阿里云百炼平台，每月免费额度
2. 智谱 ChatGLM - 新用户赠送500万Token
3. 讯飞星火 - 深度推理模型
4. SiliconFlow 硅基流动 - 每日免费额度

使用方法：
    from ai_service import get_ai_reply
    reply = get_ai_reply("你好，今天天气怎么样？")
"""

import requests
import time
import re
import threading
import sys
import os

# 添加项目根目录到路径，以便导入 configs 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置常量
from ai_consts import (
    # 通义千问
    QWEN_API_KEY,
    QWEN_API_URL,
    QWEN_MODEL,
    # 智谱
    ZHIPU_API_KEY,
    ZHIPU_API_URL,
    ZHIPU_MODEL,
    ZHIPU_SDK_AVAILABLE,
    # SiliconFlow
    SILICONFLOW_API_KEY,
    SILICONFLOW_API_URL,
    SILICONFLOW_MODEL,
    # 讯飞星火
    SPARK_APPID,
    SPARK_API_KEY,
    SPARK_API_SECRET,
    SPARK_API_URL,
    SPARK_MODEL,
    # 服务优先级
    AI_SERVICE_PRIORITY,
    AI_SERVICE_PRIORITY_TRANSLATE,
    # 请求配置
    AI_REQUEST_TIMEOUT,
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    # 对话历史配置
    MAX_HISTORY_LENGTH,
    CONVERSATION_EXPIRE_SECONDS,
    # 系统提示词
    AI_SYSTEM_PROMPT,
    AI_SYSTEM_PROMPT_TRANSLATE,
    # 意图识别配置
    TRANSLATE_KEYWORDS,
    TRANSLATE_PATTERNS,
    # 备用回复
    FALLBACK_REPLIES,
)

# 如果智谱 SDK 可用，则导入
if ZHIPU_SDK_AVAILABLE:
    from zai import ZhipuAiClient

# ==================== 对话历史管理 ==================== #


class ConversationManager:
    """用户对话历史管理器"""

    def __init__(self, max_history=MAX_HISTORY_LENGTH):
        self.conversations = {}  # {user_id: [messages]}
        self.max_history = max_history
        self._lock = threading.Lock()

    def add_message(self, user_id, role, content):
        """添加一条消息到对话历史"""
        with self._lock:
            if user_id not in self.conversations:
                self.conversations[user_id] = []

            self.conversations[user_id].append(
                {'role': role, 'content': content, 'timestamp': time.time()}
            )

            # 限制历史长度
            if len(self.conversations[user_id]) > self.max_history * 2:
                self.conversations[user_id] = self.conversations[user_id][-self.max_history * 2 :]

    def get_history(self, user_id):
        """获取用户的对话历史"""
        with self._lock:
            return self.conversations.get(user_id, []).copy()

    def clear_history(self, user_id):
        """清除用户的对话历史"""
        with self._lock:
            if user_id in self.conversations:
                del self.conversations[user_id]

    def cleanup_old_conversations(self, max_age_seconds=CONVERSATION_EXPIRE_SECONDS):
        """清理超时的对话"""
        current_time = time.time()
        with self._lock:
            users_to_remove = []
            for user_id, messages in self.conversations.items():
                if messages:
                    last_time = messages[-1].get('timestamp', 0)
                    if current_time - last_time > max_age_seconds:
                        users_to_remove.append(user_id)

            for user_id in users_to_remove:
                del self.conversations[user_id]


# 全局对话管理器
conversation_manager = ConversationManager()


# ==================== AI服务实现 ==================== #


def call_siliconflow_api(messages, timeout=AI_REQUEST_TIMEOUT):
    """
    调用 SiliconFlow (硅基流动) API - 免费额度充足

    Args:
        messages: 对话消息列表
        timeout: 超时时间

    Returns:
        str: AI回复内容，失败返回None
    """
    if not SILICONFLOW_API_KEY:
        print('[AI] SiliconFlow API Key 未配置')
        return None

    headers = {'Authorization': f'Bearer {SILICONFLOW_API_KEY}', 'Content-Type': 'application/json'}

    data = {
        'model': SILICONFLOW_MODEL,
        'messages': messages,
        'max_tokens': AI_MAX_TOKENS,
        'temperature': AI_TEMPERATURE,
        'stream': False,
    }

    try:
        response = requests.post(SILICONFLOW_API_URL, headers=headers, json=data, timeout=timeout)

        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                print(f'[AI] SiliconFlow 响应成功')
                return content.strip()
        else:
            print(f'[AI] SiliconFlow 请求失败: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'[AI] SiliconFlow 请求异常: {e}')

    return None


def call_qwen_api(messages, timeout=AI_REQUEST_TIMEOUT):
    """
    调用通义千问 API (OpenAI兼容模式)

    Args:
        messages: 对话消息列表
        timeout: 超时时间

    Returns:
        str: AI回复内容，失败返回None
    """
    if not QWEN_API_KEY:
        print('[AI] 通义千问 API Key 未配置')
        return None

    headers = {'Authorization': f'Bearer {QWEN_API_KEY}', 'Content-Type': 'application/json'}

    data = {
        'model': QWEN_MODEL,
        'messages': messages,
        'max_tokens': AI_MAX_TOKENS,
        'temperature': AI_TEMPERATURE,
        'stream': False,
    }

    try:
        response = requests.post(QWEN_API_URL, headers=headers, json=data, timeout=timeout)

        if response.status_code == 200:
            result = response.json()
            # OpenAI 兼容模式的响应格式
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                print(f'[AI] 通义千问 响应成功')
                return content.strip()
        else:
            print(f'[AI] 通义千问 请求失败: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'[AI] 通义千问 请求异常: {e}')

    return None


def call_zhipu_api(messages, timeout=AI_REQUEST_TIMEOUT):
    """
    调用智谱 ChatGLM API (使用官方 SDK)

    Args:
        messages: 对话消息列表
        timeout: 超时时间

    Returns:
        str: AI回复内容，失败返回None
    """
    if not ZHIPU_API_KEY:
        print('[AI] 智谱 API Key 未配置')
        return None

    # 优先使用官方 SDK
    if ZHIPU_SDK_AVAILABLE:
        try:
            client = ZhipuAiClient(api_key=ZHIPU_API_KEY)
            response = client.chat.completions.create(
                model=ZHIPU_MODEL,
                messages=messages,
                max_tokens=AI_MAX_TOKENS,
                temperature=AI_TEMPERATURE,
                stream=False,
            )
            content = response.choices[0].message.content
            if content:
                print('[AI] 智谱ChatGLM (SDK) 响应成功')
                return content.strip()
        except Exception as e:
            print(f'[AI] 智谱ChatGLM (SDK) 请求异常: {e}')
            # SDK 失败后尝试 HTTP 方式
            print('[AI] 尝试使用 HTTP 方式调用智谱...')

    # 备用: HTTP 方式调用
    headers = {'Authorization': f'Bearer {ZHIPU_API_KEY}', 'Content-Type': 'application/json'}

    data = {
        'model': ZHIPU_MODEL,
        'messages': messages,
        'max_tokens': AI_MAX_TOKENS,
        'temperature': AI_TEMPERATURE,
        'stream': False,
    }

    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=data, timeout=timeout)

        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                print('[AI] 智谱ChatGLM (HTTP) 响应成功')
                return content.strip()
        else:
            print(f'[AI] 智谱ChatGLM (HTTP) 请求失败: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'[AI] 智谱ChatGLM (HTTP) 请求异常: {e}')

    return None


def call_spark_api(messages, timeout=AI_REQUEST_TIMEOUT):
    """
    调用讯飞星火 API (Spark X1.5 - 300万Token额度)

    官方文档: https://www.xfyun.cn/doc/spark/HTTP调用文档.html
    认证方式: Bearer APIKey:APISecret

    Args:
        messages: 对话消息列表
        timeout: 超时时间

    Returns:
        str: AI回复内容，失败返回None
    """
    if not all([SPARK_API_KEY, SPARK_API_SECRET]):
        print('[AI] 讯飞星火 API 未完整配置')
        return None

    # 认证格式: Bearer APIKey:APISecret
    headers = {
        'Authorization': f'Bearer {SPARK_API_KEY}:{SPARK_API_SECRET}',
        'Content-Type': 'application/json',
    }

    data = {
        'model': SPARK_MODEL,
        'messages': messages,
        'max_tokens': AI_MAX_TOKENS,
        'temperature': AI_TEMPERATURE,
        'stream': False,
    }

    try:
        print(f'[AI] 正在调用讯飞星火 API...')
        response = requests.post(SPARK_API_URL, headers=headers, json=data, timeout=timeout)

        if response.status_code == 200:
            result = response.json()
            # 检查业务错误码
            if result.get('code') and result.get('code') != 0:
                print(
                    f'[AI] 讯飞星火 业务错误: code={result.get("code")}, message={result.get("message")}'
                )
                return None
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                print(f'[AI] 讯飞星火 响应成功')
                return content.strip()
            else:
                print(f'[AI] 讯飞星火 响应为空: {result}')
        else:
            print(f'[AI] 讯飞星火 请求失败: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'[AI] 讯飞星火 请求异常: {e}')

    return None


# ==================== 意图识别与智能路由 ==================== #


class UserIntent:
    """用户意图类型"""

    TRANSLATE = 'translate'  # 翻译需求
    CHAT = 'chat'  # 闲聊/问答
    UNKNOWN = 'unknown'  # 未知意图


def detect_user_intent(user_message):
    """
    识别用户意图

    Args:
        user_message: 用户消息

    Returns:
        str: 意图类型 (UserIntent.TRANSLATE / UserIntent.CHAT)
    """
    message_lower = user_message.lower()

    # 1. 关键词匹配
    for keyword in TRANSLATE_KEYWORDS:
        if keyword.lower() in message_lower:
            print(f'[AI] 检测到翻译意图 (关键词: {keyword})')
            return UserIntent.TRANSLATE

    # 2. 正则模式匹配
    for pattern in TRANSLATE_PATTERNS:
        if re.search(pattern, user_message, re.IGNORECASE):
            print(f'[AI] 检测到翻译意图 (模式匹配)')
            return UserIntent.TRANSLATE

    # 3. 特殊情况：纯外文内容（可能需要翻译）
    # 检查是否主要是外文字符
    non_chinese = len(re.findall(r'[a-zA-Z]', user_message))
    chinese = len(re.findall(r'[\u4e00-\u9fff]', user_message))

    # 如果外文字符占比很高，且有一定长度，可能是需要翻译
    if non_chinese > 10 and chinese < 5:
        print(f'[AI] 检测到翻译意图 (外文内容)')
        return UserIntent.TRANSLATE

    # 默认为聊天意图
    return UserIntent.CHAT


def get_service_priority_by_intent(intent):
    """
    根据用户意图获取AI服务优先级

    Args:
        intent: 用户意图类型

    Returns:
        list: AI服务优先级列表
    """
    if intent == UserIntent.TRANSLATE:
        return AI_SERVICE_PRIORITY_TRANSLATE
    else:
        return AI_SERVICE_PRIORITY


# ==================== 统一AI调用接口 ==================== #

# AI服务映射（仅保留免费服务）
AI_SERVICES = {
    'qwen': call_qwen_api,
    'zhipu': call_zhipu_api,
    'siliconflow': call_siliconflow_api,
    'spark': call_spark_api,
}


def get_ai_reply(user_message, user_id=None, use_history=True):
    """
    获取AI回复 - 根据用户意图智能选择AI服务

    Args:
        user_message: 用户消息
        user_id: 用户ID（用于保持对话上下文）
        use_history: 是否使用对话历史

    Returns:
        str: AI回复内容
    """
    # 1. 识别用户意图
    intent = detect_user_intent(user_message)

    # 2. 根据意图选择系统提示词
    if intent == UserIntent.TRANSLATE:
        system_prompt = AI_SYSTEM_PROMPT_TRANSLATE
        use_history = False  # 翻译任务不需要历史上下文
        print(f'[AI] 切换到翻译模式')
    else:
        system_prompt = AI_SYSTEM_PROMPT
        print(f'[AI] 使用聊天模式')

    # 3. 构建消息列表
    messages = [{'role': 'system', 'content': system_prompt}]

    # 添加对话历史（仅聊天模式）
    if use_history and user_id:
        history = conversation_manager.get_history(user_id)
        for msg in history[-MAX_HISTORY_LENGTH * 2 :]:
            messages.append({'role': msg['role'], 'content': msg['content']})

    # 添加当前用户消息
    messages.append({'role': 'user', 'content': user_message})

    # 4. 根据意图获取服务优先级
    service_priority = get_service_priority_by_intent(intent)
    print(f'[AI] 服务优先级: {service_priority}')

    # 5. 按优先级尝试各个AI服务
    for service_name in service_priority:
        if service_name not in AI_SERVICES:
            continue

        service_func = AI_SERVICES[service_name]
        print(f'[AI] 尝试使用 {service_name} 服务...')

        reply = service_func(messages)
        if reply:
            # 保存对话历史（仅聊天模式）
            if user_id and intent != UserIntent.TRANSLATE:
                conversation_manager.add_message(user_id, 'user', user_message)
                conversation_manager.add_message(user_id, 'assistant', reply)

            return reply

    # 所有服务都失败，返回默认回复
    print('[AI] 所有AI服务均不可用')
    return get_fallback_reply(user_message)


def get_fallback_reply(user_message):
    """
    AI服务不可用时的备用回复

    Args:
        user_message: 用户消息

    Returns:
        str: 备用回复
    """
    message_lower = user_message.lower()

    if any(word in message_lower for word in ['你好', 'hello', 'hi', '嗨']):
        return FALLBACK_REPLIES['greeting']

    if any(word in message_lower for word in ['谢谢', '感谢', 'thanks']):
        return FALLBACK_REPLIES['thanks']

    if any(word in message_lower for word in ['再见', '拜拜', 'bye']):
        return FALLBACK_REPLIES['goodbye']

    if any(word in message_lower for word in ['笑话', '开心', '无聊']):
        return FALLBACK_REPLIES['joke']

    if '?' in user_message or '？' in user_message:
        return FALLBACK_REPLIES['question']

    return FALLBACK_REPLIES['default']


def clear_user_conversation(user_id):
    """
    清除用户的对话历史

    Args:
        user_id: 用户ID
    """
    conversation_manager.clear_history(user_id)
    print(f'[AI] 已清除用户 {user_id[:8]}... 的对话历史')


def is_ai_enabled():
    """
    检查AI功能是否可用（至少配置了一个API Key）

    Returns:
        bool: 是否有可用的AI服务
    """
    return any(
        [
            QWEN_API_KEY,
            ZHIPU_API_KEY,
            SILICONFLOW_API_KEY,
            all([SPARK_APPID, SPARK_API_KEY, SPARK_API_SECRET]),
        ]
    )


# ==================== 测试代码 ==================== #

if __name__ == '__main__':
    print('=== AI服务测试 ===')
    print(f'AI功能是否可用: {is_ai_enabled()}')
    print()

    if is_ai_enabled():
        # 测试用例：不同意图
        test_cases = [
            # 聊天意图 -> 使用 zhipu/qwen
            ('你好，请介绍一下你自己', '聊天'),
            ('今天天气怎么样？', '聊天'),
            # 翻译意图 -> 使用 siliconflow 翻译模型
            ('帮我翻译：Hello World', '翻译'),
            ('把"人工智能"翻译成英文', '翻译'),
            ('I love programming, it makes me happy.', '翻译'),
            ('这句话用英语怎么说：我很开心', '翻译'),
        ]

        for message, expected_intent in test_cases:
            print(f'=' * 50)
            print(f'测试消息: {message}')
            print(f'期望意图: {expected_intent}')

            # 识别意图
            intent = detect_user_intent(message)
            print(f'识别意图: {intent}')

            # 获取回复
            reply = get_ai_reply(message, user_id='test_user_001')
            print(f'AI回复: {reply}')
            print()
    else:
        print('请先配置至少一个AI服务的API Key')
        print('推荐配置 SiliconFlow，注册即送免费额度')
        print('注册地址: https://siliconflow.cn/')
