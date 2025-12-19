# -*- coding: utf-8 -*-
"""
讯飞星火 API 测试脚本
测试 Spark X1.5 深度推理模型
"""

import requests
import json

# ==================== 配置 ==================== #
SPARK_API_KEY = '54b74d8c45a30f8eb4787cc1a3feb608'
SPARK_API_SECRET = 'MWRjMjQzMmFlZjVkNGIxYzhiNzhjZDBh'
SPARK_API_URL = 'https://spark-api-open.xf-yun.com/v2/chat/completions'
SPARK_MODEL = 'spark-x'  # Spark X1.5 深度推理模型

# ==================== 测试函数 ==================== #


def test_spark_api():
    """测试讯飞星火 API"""
    print('=' * 50)
    print('讯飞星火 API 测试')
    print('=' * 50)
    print(f'API URL: {SPARK_API_URL}')
    print(f'Model: {SPARK_MODEL}')
    print()

    # 认证格式: Bearer APIKey:APISecret
    headers = {
        'Authorization': f'Bearer {SPARK_API_KEY}:{SPARK_API_SECRET}',
        'Content-Type': 'application/json',
    }

    # 测试消息
    messages = [{'role': 'user', 'content': '你好，请介绍一下你自己'}]

    data = {
        'model': SPARK_MODEL,
        'messages': messages,
        'max_tokens': 300,
        'temperature': 0.7,
        'stream': False,
    }

    print('请求参数:')
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print()

    try:
        print('正在发送请求...')
        response = requests.post(SPARK_API_URL, headers=headers, json=data, timeout=30)

        print(f'响应状态码: {response.status_code}')
        print()

        if response.status_code == 200:
            result = response.json()
            print('响应内容:')
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print()

            # 检查业务错误码
            if result.get('code') and result.get('code') != 0:
                print(f'❌ 业务错误: code={result.get("code")}, message={result.get("message")}')
                return False

            # 提取回复内容
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if content:
                print('=' * 50)
                print('✅ 测试成功！')
                print('=' * 50)
                print(f'AI回复: {content}')

                # 显示 Token 使用情况
                usage = result.get('usage', {})
                if usage:
                    print()
                    print('Token 使用情况:')
                    print(f'  - 输入 Token: {usage.get("prompt_tokens", "N/A")}')
                    print(f'  - 输出 Token: {usage.get("completion_tokens", "N/A")}')
                    print(f'  - 总计 Token: {usage.get("total_tokens", "N/A")}')

                return True
            else:
                print('❌ 响应内容为空')
                return False
        else:
            print(f'❌ 请求失败: {response.status_code}')
            print(f'错误信息: {response.text}')
            return False

    except requests.exceptions.Timeout:
        print('❌ 请求超时 (30秒)')
        return False
    except Exception as e:
        print(f'❌ 请求异常: {e}')
        return False


def test_spark_conversation():
    """测试多轮对话"""
    print()
    print('=' * 50)
    print('多轮对话测试')
    print('=' * 50)

    headers = {
        'Authorization': f'Bearer {SPARK_API_KEY}:{SPARK_API_SECRET}',
        'Content-Type': 'application/json',
    }

    # 多轮对话
    conversations = [
        '我叫小明',
        '你还记得我的名字吗？',
    ]

    messages = []

    for user_input in conversations:
        messages.append({'role': 'user', 'content': user_input})

        data = {
            'model': SPARK_MODEL,
            'messages': messages,
            'max_tokens': 300,
            'temperature': 0.7,
            'stream': False,
        }

        try:
            response = requests.post(SPARK_API_URL, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

                print(f'用户: {user_input}')
                print(f'AI: {content}')
                print()

                # 将 AI 回复加入历史
                messages.append({'role': 'assistant', 'content': content})
            else:
                print(f'❌ 请求失败: {response.status_code}')
                return False

        except Exception as e:
            print(f'❌ 异常: {e}')
            return False

    print('✅ 多轮对话测试完成')
    return True


if __name__ == '__main__':
    # 运行测试
    success = test_spark_api()

    if success:
        test_spark_conversation()

    print()
    print('=' * 50)
    print('测试结束')
    print('=' * 50)
