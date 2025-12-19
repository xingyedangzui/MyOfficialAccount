# -*- coding: utf-8 -*-
"""
智谱 AI 单独测试脚本
"""

import requests
import time

# 智谱配置
ZHIPU_API_KEY = '3261c9ce585444aea9dda0f2e24caecb.ZudI1qxPltRY3lwJ'
ZHIPU_API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'


def test_zhipu_http():
    """使用 HTTP 方式测试智谱"""
    print('=' * 50)
    print('测试方式: HTTP 请求')
    print('=' * 50)

    headers = {'Authorization': f'Bearer {ZHIPU_API_KEY}', 'Content-Type': 'application/json'}

    data = {
        'model': 'glm-4-flash',  # 免费模型
        'messages': [{'role': 'user', 'content': '你好，请用一句话介绍自己'}],
        'max_tokens': 100,
        'temperature': 0.7,
        'stream': False,
    }

    print(f'请求 URL: {ZHIPU_API_URL}')
    print(f'请求模型: {data["model"]}')
    print(f'请求内容: {data["messages"][0]["content"]}')
    print('-' * 50)

    start_time = time.time()
    try:
        print('发送请求中...')
        response = requests.post(ZHIPU_API_URL, headers=headers, json=data, timeout=30)
        elapsed = time.time() - start_time

        print(f'响应状态码: {response.status_code}')
        print(f'响应时间: {elapsed:.2f} 秒')
        print('-' * 50)

        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f'✅ 成功! AI 回复: {content}')
            return True
        else:
            print(f'❌ 失败! 响应内容: {response.text}')
            return False
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f'❌ 超时! 等待了 {elapsed:.2f} 秒')
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f'❌ 异常! {type(e).__name__}: {e}')
        print(f'耗时: {elapsed:.2f} 秒')
        return False


def test_zhipu_sdk():
    """使用 SDK 方式测试智谱"""
    print('\n' + '=' * 50)
    print('测试方式: 官方 SDK (zai)')
    print('=' * 50)

    try:
        from zai import ZhipuAiClient

        print('✅ SDK 导入成功')
    except ImportError as e:
        print(f'❌ SDK 导入失败: {e}')
        print('请运行: pip install zai sniffio')
        return False

    messages = [{'role': 'user', 'content': '你好，请用一句话介绍自己'}]

    print(f'请求模型: glm-4-flash')
    print(f'请求内容: {messages[0]["content"]}')
    print('-' * 50)

    start_time = time.time()
    try:
        print('发送请求中...')
        client = ZhipuAiClient(api_key=ZHIPU_API_KEY)
        response = client.chat.completions.create(
            model='glm-4-flash',
            messages=messages,
            max_tokens=100,
            temperature=0.7,
            stream=False,
        )
        elapsed = time.time() - start_time

        print(f'响应时间: {elapsed:.2f} 秒')
        print('-' * 50)

        content = response.choices[0].message.content
        print(f'✅ 成功! AI 回复: {content}')
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f'❌ 异常! {type(e).__name__}: {e}')
        print(f'耗时: {elapsed:.2f} 秒')
        return False


if __name__ == '__main__':
    print('智谱 AI 连接测试')
    print('API Key:', ZHIPU_API_KEY[:20] + '...')
    print()

    # 测试 HTTP 方式
    http_ok = test_zhipu_http()

    # 测试 SDK 方式
    sdk_ok = test_zhipu_sdk()

    # 总结
    print('\n' + '=' * 50)
    print('测试结果汇总')
    print('=' * 50)
    print(f'HTTP 方式: {"✅ 成功" if http_ok else "❌ 失败"}')
    print(f'SDK 方式:  {"✅ 成功" if sdk_ok else "❌ 失败"}')
