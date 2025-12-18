# -*- coding: utf-8 -*-
"""
天气API连通性测试脚本
用于测试各个天气API是否能正常访问
"""

import requests
import time
import sys
import os

# 添加项目根目录和script目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 上一级目录（项目根目录）
script_dir = os.path.join(project_root, 'script')

# 将script目录添加到Python路径
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import consts


def test_wttr_in():
    """测试 wttr.in 免费天气API"""
    print('=' * 50)
    print('测试 wttr.in API...')
    print('=' * 50)

    try:
        url = 'https://wttr.in/Beijing?format=j1'
        start_time = time.time()
        response = requests.get(url, timeout=15, headers={'Accept-Language': 'zh-CN'})
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            current = data.get('current_condition', [{}])[0]
            temp = current.get('temp_C', 'N/A')
            weather_desc = current.get('lang_zh', [{}])
            if weather_desc:
                weather_desc = weather_desc[0].get('value', 'N/A')
            else:
                weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')

            print(f'✅ wttr.in API 正常!')
            print(f'   响应时间: {elapsed:.2f}秒')
            print(f'   北京天气: {weather_desc}, 温度: {temp}°C')
            return True
        else:
            print(f'❌ wttr.in API 返回错误: HTTP {response.status_code}')
            return False

    except requests.exceptions.Timeout:
        print(f'❌ wttr.in API 超时 (>15秒)')
        return False
    except requests.exceptions.ConnectionError as e:
        print(f'❌ wttr.in API 连接失败: {str(e)}')
        return False
    except Exception as e:
        print(f'❌ wttr.in API 异常: {str(e)}')
        return False


def test_qweather(api_key=None):
    """测试和风天气API"""
    print('\n' + '=' * 50)
    print('测试和风天气 API...')
    print('=' * 50)

    if not api_key:
        # 尝试从 consts 读取
        try:
            api_key = consts.WEATHER_API_KEY
        except:
            pass

    if not api_key or api_key == 'YOUR_API_KEY':
        print('⚠️ 未配置和风天气API密钥，跳过测试')
        print('   请在 consts.py 中设置 WEATHER_API_KEY')
        return None

    try:
        # 测试实时天气接口
        url = 'https://devapi.qweather.com/v7/weather/now'
        params = {
            'location': '101010100',  # 北京
            'key': api_key,
        }

        start_time = time.time()
        response = requests.get(url, params=params, timeout=10)
        elapsed = time.time() - start_time

        data = response.json()
        code = data.get('code')

        if code == '200':
            now = data.get('now', {})
            temp = now.get('temp', 'N/A')
            text = now.get('text', 'N/A')

            print(f'✅ 和风天气 API 正常!')
            print(f'   响应时间: {elapsed:.2f}秒')
            print(f'   北京天气: {text}, 温度: {temp}°C')
            return True
        else:
            error_messages = {
                '400': '请求错误',
                '401': 'API密钥无效或过期',
                '402': '超过访问次数限制',
                '403': '无访问权限',
                '404': '查询的数据不存在',
                '429': '请求过于频繁',
                '500': '服务器内部错误',
            }
            error_msg = error_messages.get(code, f'未知错误码 {code}')
            print(f'❌ 和风天气 API 返回错误: {error_msg}')
            return False

    except requests.exceptions.Timeout:
        print(f'❌ 和风天气 API 超时')
        return False
    except requests.exceptions.ConnectionError as e:
        print(f'❌ 和风天气 API 连接失败: {str(e)}')
        return False
    except Exception as e:
        print(f'❌ 和风天气 API 异常: {str(e)}')
        return False


def test_gaode_weather(api_key=None):
    """测试高德天气API（备选方案）"""
    print('\n' + '=' * 50)
    print('测试高德天气 API...')
    print('=' * 50)

    if not api_key:
        print('⚠️ 未配置高德天气API密钥，跳过测试')
        print('   高德天气API申请地址: https://lbs.amap.com/')
        return None

    try:
        url = 'https://restapi.amap.com/v3/weather/weatherInfo'
        params = {
            'city': '110000',  # 北京
            'key': api_key,
            'extensions': 'base',
        }

        start_time = time.time()
        response = requests.get(url, params=params, timeout=10)
        elapsed = time.time() - start_time

        data = response.json()

        if data.get('status') == '1':
            lives = data.get('lives', [{}])[0]
            temp = lives.get('temperature', 'N/A')
            weather = lives.get('weather', 'N/A')

            print(f'✅ 高德天气 API 正常!')
            print(f'   响应时间: {elapsed:.2f}秒')
            print(f'   北京天气: {weather}, 温度: {temp}°C')
            return True
        else:
            print(f'❌ 高德天气 API 返回错误: {data.get("info", "未知错误")}')
            return False

    except Exception as e:
        print(f'❌ 高德天气 API 异常: {str(e)}')
        return False


def test_network_connectivity():
    """测试基本网络连通性"""
    print('=' * 50)
    print('测试基本网络连通性...')
    print('=' * 50)

    test_urls = [
        ('百度', 'https://www.baidu.com'),
        ('GitHub', 'https://github.com'),
        ('和风天气', 'https://devapi.qweather.com'),
    ]

    for name, url in test_urls:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start_time
            print(f'✅ {name}: 可访问 ({elapsed:.2f}秒)')
        except requests.exceptions.Timeout:
            print(f'❌ {name}: 超时')
        except requests.exceptions.ConnectionError:
            print(f'❌ {name}: 连接失败')
        except Exception as e:
            print(f'❌ {name}: {str(e)}')


def main():
    """主测试函数"""
    print('\n' + '🌤️ 天气API连通性测试' + '\n')

    # 1. 测试基本网络
    test_network_connectivity()

    # 2. 测试 wttr.in
    wttr_ok = test_wttr_in()

    # 3. 测试和风天气
    qweather_ok = test_qweather(consts.WEATHER_API_KEY)

    # 4. 测试高德天气（如果有配置的话）
    # gaode_ok = test_gaode_weather("你的高德API密钥")

    # 总结
    print('\n' + '=' * 50)
    print('📊 测试结果总结')
    print('=' * 50)

    if wttr_ok:
        print('✅ wttr.in: 可用 (免费，无需密钥)')
    else:
        print('❌ wttr.in: 不可用')

    if qweather_ok is None:
        print('⚠️ 和风天气: 未配置密钥')
    elif qweather_ok:
        print('✅ 和风天气: 可用')
    else:
        print('❌ 和风天气: 不可用')

    # 建议
    print('\n💡 建议:')
    if wttr_ok:
        print('   - wttr.in 可用，可以作为免费天气源')
    elif qweather_ok:
        print('   - 建议使用和风天气API')
    else:
        print('   - 所有天气API都不可用，请检查网络或API配置')
        print('   - 可以考虑申请高德天气API: https://lbs.amap.com/')


if __name__ == '__main__':
    main()
