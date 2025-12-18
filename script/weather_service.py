# -*- coding: utf-8 -*-
# 天气服务模块 - 获取天气信息并生成温馨提示
# 支持多个天气API自动切换：和风天气、wttr.in

import requests
import json
from datetime import datetime
import consts


class WeatherService:
    """天气服务类 - 使用和风天气API"""

    def __init__(self, api_key=None, location=None):
        """
        初始化天气服务

        Args:
            api_key: 和风天气API密钥（需要到 https://dev.qweather.com/ 注册获取）
            location: 城市代码，默认使用配置中的默认城市
        """
        self.api_key = api_key or consts.WEATHER_API_KEY
        self.location = location or consts.WEATHER_DEFAULT_CITY
        self.base_url = f'https://{consts.WEATHER_API_HOST}/v7'
        self.geo_url = f'https://{consts.WEATHER_API_HOST}/geo/v2'
        self.timeout = consts.WEATHER_API_TIMEOUT

    def get_weather(self, city=None):
        """
        获取指定城市的天气信息

        Args:
            city: 城市名称或城市代码，如果为None则使用默认城市

        Returns:
            dict: 天气信息字典，包含温度、天气状况、建议等
        """
        location = city if city else self.location

        # 如果传入的是城市名称，先查询城市代码
        if not location.isdigit():
            location = self._search_city(location)
            if not location:
                return {'success': False, 'error': '未找到该城市'}

        try:
            # 获取实时天气
            now_weather = self._get_now_weather(location)
            if not now_weather['success']:
                return now_weather

            # 获取今日天气预报（包含日出日落、紫外线等）
            daily_forecast = self._get_daily_forecast(location)

            # 获取生活指数
            indices = self._get_life_indices(location)

            # 组合天气信息
            weather_info = {
                'success': True,
                'city': now_weather.get('city', '未知'),
                'update_time': now_weather.get('update_time', ''),
                'now': now_weather.get('data', {}),
                'today': daily_forecast.get('data', {}),
                'indices': indices.get('data', {}),
            }

            return weather_info

        except Exception as e:
            print(f'获取天气信息失败: {str(e)}')
            return {'success': False, 'error': str(e)}

    def _search_city(self, city_name):
        """
        根据城市名称搜索城市代码

        Args:
            city_name: 城市名称

        Returns:
            str: 城市代码，未找到返回None
        """
        # 首先检查本地城市ID映射表（速度快，无需网络请求）
        if city_name in consts.WEATHER_CITY_ID_MAP:
            city_id = consts.WEATHER_CITY_ID_MAP[city_name]
            print(f'[QWeather] 使用本地映射: {city_name} -> {city_id}')
            return city_id

        # 本地没有找到，尝试调用GEO API
        try:
            # 和风天气GEO API（使用新的API Host）
            url = f'{self.geo_url}/city/lookup'
            params = {
                'location': city_name,
                'key': self.api_key,
            }

            print(f'[QWeather] 搜索城市: {city_name}, key={self.api_key[:8]}...')
            response = requests.get(url, params=params, timeout=self.timeout)

            print(
                f'[QWeather] 响应状态: {response.status_code}, 长度: {len(response.text) if response.text else 0}'
            )

            # 检查HTTP响应状态
            if response.status_code != 200:
                print(f'[QWeather] HTTP错误: {response.status_code}')
                if response.text:
                    print(f'[QWeather] 错误响应: {response.text[:200]}')
                return None

            # 检查响应内容是否为空
            if not response.text or len(response.text.strip()) == 0:
                print(f'[QWeather] 响应内容为空')
                return None

            data = response.json()
            api_code = data.get('code', 'unknown')
            print(f'[QWeather] API返回码: {api_code}')

            if api_code == '200' and data.get('location'):
                city_id = data['location'][0]['id']
                city_found = data['location'][0].get('name', city_name)
                print(f'[QWeather] 找到城市: {city_found} (ID: {city_id})')
                return city_id
            else:
                # 和风天气API错误码
                error_codes = {
                    '400': '请求错误',
                    '401': 'API密钥认证失败',
                    '402': '超过访问次数限制',
                    '403': '无访问权限',
                    '404': '未找到该城市',
                    '500': '服务器内部错误',
                }
                error_msg = error_codes.get(str(api_code), f'未知错误')
                print(f'[QWeather] 城市搜索失败: {api_code} - {error_msg}')
                return None
        except json.JSONDecodeError as e:
            print(f'[QWeather] JSON解析失败: {str(e)}')
            if response and response.text:
                print(f'[QWeather] 原始响应: {response.text[:200]}')
            return None
        except requests.exceptions.Timeout:
            print(f'[QWeather] 请求超时')
            return None
        except requests.exceptions.ConnectionError as e:
            print(f'[QWeather] 连接错误: {str(e)}')
            return None
        except Exception as e:
            print(f'[QWeather] 搜索城市异常: {str(e)}')
            return None

    def _get_now_weather(self, location):
        """获取实时天气"""
        try:
            url = f'{self.base_url}/weather/now'
            params = {
                'location': location,
                'key': self.api_key,
            }
            print(f'[QWeather] 获取实时天气: location={location}')
            response = requests.get(url, params=params, timeout=self.timeout)

            print(
                f'[QWeather] 天气API响应: status={response.status_code}, len={len(response.text) if response.text else 0}'
            )

            # 检查响应内容
            if not response.text or len(response.text.strip()) == 0:
                print(f'[QWeather] 天气API返回空内容')
                return {'success': False, 'error': '天气API返回空内容'}

            data = response.json()
            api_code = data.get('code', 'unknown')
            print(f'[QWeather] 天气API返回码: {api_code}')

            if api_code == '200':
                now = data.get('now', {})
                return {
                    'success': True,
                    'update_time': data.get('updateTime', ''),
                    'data': {
                        'temp': now.get('temp', 'N/A'),  # 温度
                        'feels_like': now.get('feelsLike', 'N/A'),  # 体感温度
                        'text': now.get('text', 'N/A'),  # 天气状况
                        'wind_dir': now.get('windDir', 'N/A'),  # 风向
                        'wind_scale': now.get('windScale', 'N/A'),  # 风力等级
                        'humidity': now.get('humidity', 'N/A'),  # 相对湿度
                        'precip': now.get('precip', '0'),  # 降水量
                        'vis': now.get('vis', 'N/A'),  # 能见度
                    },
                }
            else:
                return {'success': False, 'error': f'API返回错误: {data.get("code")}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_daily_forecast(self, location):
        """获取每日天气预报"""
        try:
            url = f'{self.base_url}/weather/3d'
            params = {
                'location': location,
                'key': self.api_key,
            }
            response = requests.get(url, params=params, timeout=self.timeout)
            data = response.json()

            if data.get('code') == '200' and data.get('daily'):
                today = data['daily'][0]
                return {
                    'success': True,
                    'data': {
                        'temp_max': today.get('tempMax', 'N/A'),  # 最高温度
                        'temp_min': today.get('tempMin', 'N/A'),  # 最低温度
                        'text_day': today.get('textDay', 'N/A'),  # 白天天气
                        'text_night': today.get('textNight', 'N/A'),  # 夜间天气
                        'sunrise': today.get('sunrise', ''),  # 日出时间
                        'sunset': today.get('sunset', ''),  # 日落时间
                        'uv_index': today.get('uvIndex', 'N/A'),  # 紫外线指数
                    },
                }
            return {'success': False, 'data': {}}
        except Exception as e:
            return {'success': False, 'error': str(e), 'data': {}}

    def _get_life_indices(self, location):
        """
        获取生活指数

        指数类型：
        1-运动指数, 2-洗车指数, 3-穿衣指数, 5-紫外线指数, 9-感冒指数, 15-交通指数
        """
        try:
            url = f'{self.base_url}/indices/1d'
            params = {
                'location': location,
                'key': self.api_key,
                'type': '1,2,3,5,9',  # 运动、洗车、穿衣、紫外线、感冒
            }
            response = requests.get(url, params=params, timeout=self.timeout)
            data = response.json()

            if data.get('code') == '200' and data.get('daily'):
                indices = {}
                for item in data['daily']:
                    index_type = item.get('type')
                    indices[index_type] = {
                        'name': item.get('name', ''),
                        'category': item.get('category', ''),
                        'text': item.get('text', ''),
                    }
                return {'success': True, 'data': indices}
            return {'success': False, 'data': {}}
        except Exception as e:
            return {'success': False, 'error': str(e), 'data': {}}

    def format_weather_reply(self, weather_info):
        """
        格式化天气信息为用户友好的回复

        Args:
            weather_info: get_weather() 返回的天气信息字典

        Returns:
            str: 格式化后的天气回复文本
        """
        if not weather_info.get('success'):
            return f'😢 获取天气信息失败：{weather_info.get("error", "未知错误")}\n\n请稍后再试~'

        now = weather_info.get('now', {})
        today = weather_info.get('today', {})
        indices = weather_info.get('indices', {})

        # 基本天气信息
        temp = now.get('temp', 'N/A')
        feels_like = now.get('feels_like', 'N/A')
        text = now.get('text', 'N/A')
        temp_max = today.get('temp_max', 'N/A')
        temp_min = today.get('temp_min', 'N/A')
        humidity = now.get('humidity', 'N/A')
        wind_dir = now.get('wind_dir', 'N/A')
        wind_scale = now.get('wind_scale', 'N/A')

        # 构建回复
        reply_parts = []

        # 天气概况
        reply_parts.append(f'🌤 今日天气\n')
        reply_parts.append(f'📍 当前天气：{text}')
        reply_parts.append(f'🌡 实时温度：{temp}°C（体感{feels_like}°C）')
        reply_parts.append(f'📊 温度范围：{temp_min}°C ~ {temp_max}°C')
        reply_parts.append(f'💧 相对湿度：{humidity}%')
        reply_parts.append(f'🌬 风力风向：{wind_dir} {wind_scale}级')

        # 温馨提示部分
        tips = self._generate_tips(weather_info)
        if tips:
            reply_parts.append(f'\n💡 温馨提示')
            reply_parts.extend(tips)

        # 穿衣建议
        dress_index = indices.get('3', {})
        if dress_index:
            reply_parts.append(f'\n👔 穿衣建议')
            reply_parts.append(f'{dress_index.get("category", "")}: {dress_index.get("text", "")}')

        # 更新时间
        update_time = weather_info.get('update_time', '')
        if update_time:
            try:
                dt = datetime.fromisoformat(update_time.replace('+08:00', ''))
                update_time = dt.strftime('%H:%M')
            except:
                pass
            reply_parts.append(f'\n⏰ 更新时间：{update_time}')

        return '\n'.join(reply_parts)

    def _generate_tips(self, weather_info):
        """
        根据天气信息生成温馨提示

        Args:
            weather_info: 天气信息字典

        Returns:
            list: 提示列表
        """
        tips = []
        now = weather_info.get('now', {})
        today = weather_info.get('today', {})
        indices = weather_info.get('indices', {})

        text = now.get('text', '').lower()
        temp = now.get('temp', '20')

        try:
            temp_val = int(temp)
        except:
            temp_val = 20

        # 降雨提示
        rain_keywords = ['雨', '雷', '阵雨', '暴雨', '小雨', '中雨', '大雨']
        if any(keyword in text for keyword in rain_keywords):
            tips.append('☔ 今天有雨，出门记得带伞！')

        # 降雪提示
        snow_keywords = ['雪', '暴雪', '小雪', '中雪', '大雪']
        if any(keyword in text for keyword in snow_keywords):
            tips.append('❄️ 今天有雪，注意保暖和路滑！')

        # 高温提示
        if temp_val >= 35:
            tips.append('🔥 高温预警！注意防暑降温，多喝水！')
        elif temp_val >= 30:
            tips.append('☀️ 天气较热，注意防晒补水！')

        # 低温提示
        if temp_val <= 0:
            tips.append('🥶 气温很低，注意保暖防冻！')
        elif temp_val <= 10:
            tips.append('🧥 天气较冷，多穿点衣服！')

        # 感冒指数
        cold_index = indices.get('9', {})
        if cold_index:
            category = cold_index.get('category', '')
            if '易发' in category or '极易' in category:
                tips.append(f'🤧 感冒{category}，注意增减衣物！')

        # 紫外线指数
        uv_index = indices.get('5', {})
        if uv_index:
            category = uv_index.get('category', '')
            if '强' in category or '很强' in category:
                tips.append(f'🧴 紫外线{category}，外出注意防晒！')

        # 风力提示
        wind_scale = now.get('wind_scale', '0')
        try:
            wind_val = int(wind_scale.split('-')[0] if '-' in wind_scale else wind_scale)
            if wind_val >= 6:
                tips.append('💨 风力较大，外出注意安全！')
        except:
            pass

        return tips


# 创建全局天气服务实例
# 注意：使用前需要设置正确的API密钥
weather_service = WeatherService()


def get_weather_reply(city=None):
    """
    获取天气回复的便捷函数

    Args:
        city: 城市名称，为None则使用默认城市

    Returns:
        str: 格式化后的天气回复
    """
    weather_info = weather_service.get_weather(city)
    return weather_service.format_weather_reply(weather_info)


# ============== 备选方案：使用免费的天气API ============== #
class FreeWeatherService:
    """
    免费天气服务（使用 wttr.in API）
    优点：无需API密钥，直接可用
    缺点：功能相对简单，没有生活指数
    """

    def __init__(self):
        self.timeout = consts.WEATHER_API_TIMEOUT

    def get_weather(self, city='Beijing'):
        """
        获取天气信息

        Args:
            city: 城市名称（英文或中文拼音）

        Returns:
            str: 天气信息回复
        """
        try:
            # wttr.in API
            url = f'https://wttr.in/{city}?format=j1'
            response = requests.get(url, timeout=self.timeout, headers={'Accept-Language': 'zh-CN'})
            data = response.json()

            current = data.get('current_condition', [{}])[0]
            weather_desc = current.get('lang_zh', [{}])
            if weather_desc:
                weather_desc = weather_desc[0].get(
                    'value', current.get('weatherDesc', [{}])[0].get('value', 'N/A')
                )
            else:
                weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')

            temp = current.get('temp_C', 'N/A')
            feels_like = current.get('FeelsLikeC', 'N/A')
            humidity = current.get('humidity', 'N/A')
            wind_speed = current.get('windspeedKmph', 'N/A')
            wind_dir = current.get('winddir16Point', 'N/A')

            # 今日预报
            weather_today = data.get('weather', [{}])[0]
            temp_max = weather_today.get('maxtempC', 'N/A')
            temp_min = weather_today.get('mintempC', 'N/A')

            # 构建回复
            reply = f"""🌤 今日天气

📍 当前天气：{weather_desc}
🌡 实时温度：{temp}°C（体感{feels_like}°C）
📊 温度范围：{temp_min}°C ~ {temp_max}°C
💧 相对湿度：{humidity}%
🌬 风速：{wind_speed}km/h"""

            # 生成穿衣建议
            clothing_advice = self._generate_clothing_advice(temp, weather_desc)
            reply += clothing_advice

            # 生成温馨提示
            tips = self._generate_tips(temp, weather_desc)
            if tips:
                reply += '\n\n💡 温馨提示\n' + '\n'.join(tips)

            return reply

        except Exception as e:
            print(f'获取天气失败: {str(e)}')
            return f'😢 获取天气信息失败，请稍后再试~'

    def _generate_clothing_advice(self, temp, weather_desc=''):
        """
        根据温度生成穿衣建议

        Args:
            temp: 温度字符串
            weather_desc: 天气描述

        Returns:
            str: 穿衣建议文本
        """
        try:
            temp_val = int(temp)
        except (ValueError, TypeError):
            temp_val = 20

        weather_lower = weather_desc.lower() if weather_desc else ''

        # 根据温度区间给出建议
        if temp_val >= 30:
            level = '炎热'
            clothes = '短袖、短裤/短裙、凉鞋'
            tip = '天气炎热，穿着清凉透气，注意防晒补水！'
            emoji = '🩳'
        elif temp_val >= 26:
            level = '热'
            clothes = '短袖、薄长裤/裙子'
            tip = '天气较热，穿着轻薄舒适即可。'
            emoji = '👕'
        elif temp_val >= 22:
            level = '舒适'
            clothes = '短袖/薄长袖、长裤'
            tip = '温度适宜，穿着舒适就好~'
            emoji = '👔'
        elif temp_val >= 18:
            level = '微凉'
            clothes = '长袖衬衫、薄外套、长裤'
            tip = '早晚微凉，建议带一件薄外套。'
            emoji = '🧥'
        elif temp_val >= 14:
            level = '凉'
            clothes = '卫衣/毛衣、外套、长裤'
            tip = '天气转凉，注意添加衣物。'
            emoji = '🧥'
        elif temp_val >= 10:
            level = '冷'
            clothes = '毛衣、厚外套/风衣、长裤'
            tip = '天气较冷，记得穿暖和些。'
            emoji = '🧣'
        elif temp_val >= 5:
            level = '寒冷'
            clothes = '厚毛衣、羽绒服/棉衣、保暖裤'
            tip = '天气寒冷，做好保暖措施！'
            emoji = '🧤'
        elif temp_val >= 0:
            level = '严寒'
            clothes = '羽绒服、保暖内衣、围巾手套帽子'
            tip = '气温很低，务必做好全身保暖！'
            emoji = '🧣'
        else:
            level = '极寒'
            clothes = '厚羽绒服、保暖内衣裤、围巾帽子手套'
            tip = '极度寒冷，减少外出，注意防寒！'
            emoji = '❄️'

        # 构建穿衣建议文本
        advice = f'\n\n👔 穿衣建议（{emoji} {level}）\n'
        advice += f'推荐穿着：{clothes}\n'
        advice += f'💡 {tip}'

        # 天气特殊情况补充
        if '雨' in weather_lower or 'rain' in weather_lower:
            advice += '\n☔ 有雨天气，建议穿防水外套'
        if '雪' in weather_lower or 'snow' in weather_lower:
            advice += '\n❄️ 有雪天气，穿防滑保暖鞋子'

        return advice

    def _generate_tips(self, temp, weather_desc=''):
        """
        生成温馨提示

        Args:
            temp: 温度
            weather_desc: 天气描述

        Returns:
            list: 提示列表
        """
        tips = []
        try:
            temp_val = int(temp)
        except (ValueError, TypeError):
            temp_val = 20

        weather_lower = weather_desc.lower() if weather_desc else ''

        # 降雨提示
        if '雨' in weather_lower or 'rain' in weather_lower:
            tips.append('☔ 今天有雨，出门记得带伞！')

        # 降雪提示
        if '雪' in weather_lower or 'snow' in weather_lower:
            tips.append('❄️ 今天有雪，注意路滑！')

        # 高温提示
        if temp_val >= 35:
            tips.append('🔥 高温预警！注意防暑降温，多喝水！')

        # 低温提示
        if temp_val <= 0:
            tips.append('🥶 气温很低，注意保暖防冻！')

        # 没有特殊提示时
        if not tips:
            tips.append('😊 今天天气不错，心情也要美美的！')

        return tips


# 创建免费天气服务实例（备选方案）
free_weather_service = FreeWeatherService()


def get_free_weather_reply(city='Beijing'):
    """使用免费API获取天气"""
    return free_weather_service.get_weather(city)


# ============== 穿衣建议生成器 ============== #
def get_clothing_advice(temp, weather_desc=''):
    """
    根据温度和天气状况生成穿衣建议

    Args:
        temp: 温度（摄氏度），可以是字符串或数字
        weather_desc: 天气描述（可选）

    Returns:
        dict: 包含穿衣建议的字典 {
            'level': 穿衣等级,
            'clothes': 推荐衣物,
            'tip': 温馨提示
        }
    """
    try:
        temp_val = int(temp) if isinstance(temp, str) else temp
    except (ValueError, TypeError):
        temp_val = 20  # 默认温度

    weather_lower = weather_desc.lower() if weather_desc else ''

    # 根据温度区间给出建议
    if temp_val >= 30:
        level = '炎热'
        clothes = '短袖、短裤/短裙、凉鞋'
        tip = '天气炎热，穿着清凉透气的衣物，注意防晒！'
        emoji = '🩳'
    elif temp_val >= 26:
        level = '热'
        clothes = '短袖、薄长裤/裙子'
        tip = '天气较热，穿着轻薄舒适即可。'
        emoji = '👕'
    elif temp_val >= 22:
        level = '舒适'
        clothes = '短袖/薄长袖、长裤'
        tip = '温度适宜，穿着舒适就好。'
        emoji = '👔'
    elif temp_val >= 18:
        level = '微凉'
        clothes = '长袖衬衫、薄外套、长裤'
        tip = '早晚微凉，建议带一件薄外套。'
        emoji = '🧥'
    elif temp_val >= 14:
        level = '凉'
        clothes = '卫衣/毛衣、外套、长裤'
        tip = '天气转凉，注意添加衣物。'
        emoji = '🧥'
    elif temp_val >= 10:
        level = '冷'
        clothes = '毛衣、厚外套/风衣、长裤'
        tip = '天气较冷，记得穿暖和些。'
        emoji = '🧣'
    elif temp_val >= 5:
        level = '寒冷'
        clothes = '厚毛衣、羽绒服/棉衣、保暖裤'
        tip = '天气寒冷，做好保暖措施！'
        emoji = '🧤'
    elif temp_val >= 0:
        level = '严寒'
        clothes = '羽绒服、保暖内衣、围巾手套帽子'
        tip = '气温很低，务必做好全身保暖！'
        emoji = '🧣'
    else:
        level = '极寒'
        clothes = '厚羽绒服、保暖内衣裤、围巾帽子手套、雪地靴'
        tip = '极度寒冷，减少外出，注意防寒保暖！'
        emoji = '❄️'

    # 根据天气状况附加建议
    extra_tips = []

    if '雨' in weather_lower or 'rain' in weather_lower:
        extra_tips.append('☔ 有雨，建议穿防水外套，带好雨伞')
    if '雪' in weather_lower or 'snow' in weather_lower:
        extra_tips.append('❄️ 有雪，穿防滑保暖的鞋子')
    if '风' in weather_lower or 'wind' in weather_lower:
        extra_tips.append('💨 风大，穿防风外套')
    if '晴' in weather_lower or 'sunny' in weather_lower or 'clear' in weather_lower:
        if temp_val >= 25:
            extra_tips.append('☀️ 阳光强烈，注意防晒')

    return {
        'level': level,
        'clothes': clothes,
        'tip': tip,
        'emoji': emoji,
        'extra_tips': extra_tips,
    }


def format_clothing_advice(temp, weather_desc=''):
    """
    格式化穿衣建议为用户友好的文本

    Args:
        temp: 温度
        weather_desc: 天气描述

    Returns:
        str: 格式化的穿衣建议文本
    """
    advice = get_clothing_advice(temp, weather_desc)

    parts = [
        f'\n👔 穿衣建议（{advice["emoji"]} {advice["level"]}）',
        f'推荐穿着：{advice["clothes"]}',
        f'💡 {advice["tip"]}',
    ]

    if advice['extra_tips']:
        parts.extend(advice['extra_tips'])

    return '\n'.join(parts)


# ============== 根据经纬度获取天气 ============== #
class LocationWeatherService:
    """
    基于位置的天气服务
    支持通过经纬度获取天气信息
    """

    def __init__(self):
        self.free_weather = FreeWeatherService()
        self.timeout = consts.WEATHER_API_TIMEOUT

    def get_weather_by_location(self, latitude, longitude, label=None):
        """
        根据经纬度获取天气信息

        Args:
            latitude: 纬度（Location_X）
            longitude: 经度（Location_Y）
            label: 地理位置标签（可选，用于显示）

        Returns:
            str: 天气信息回复
        """
        try:
            # 方案1：直接使用经纬度查询（wttr.in支持）
            location = f'{latitude},{longitude}'

            # 获取天气
            weather_reply = self._get_weather_by_coords(latitude, longitude)

            # 如果有地址标签，添加到回复中
            if label and weather_reply:
                # 在天气信息前添加位置信息
                location_header = f'📍 您的位置：{label}\n\n'
                weather_reply = location_header + weather_reply

            return weather_reply

        except Exception as e:
            print(f'根据位置获取天气失败: {str(e)}')
            return '😢 获取天气信息失败，请稍后再试~'

    def _get_weather_by_coords(self, latitude, longitude):
        """
        根据坐标获取天气（使用wttr.in）

        Args:
            latitude: 纬度
            longitude: 经度

        Returns:
            str: 天气信息
        """
        try:
            # wttr.in 支持直接使用经纬度查询
            url = f'https://wttr.in/{latitude},{longitude}?format=j1'
            response = requests.get(url, timeout=self.timeout, headers={'Accept-Language': 'zh-CN'})
            data = response.json()

            # 获取最近的地区信息
            nearest_area = data.get('nearest_area', [{}])[0]
            area_name = ''

            # 尝试获取城市名
            if nearest_area:
                # 优先使用中文名
                area_list = nearest_area.get('areaName', [{}])
                if area_list:
                    area_name = area_list[0].get('value', '')

                # 获取国家/地区
                country_list = nearest_area.get('country', [{}])
                country = country_list[0].get('value', '') if country_list else ''

                # 获取区域
                region_list = nearest_area.get('region', [{}])
                region = region_list[0].get('value', '') if region_list else ''

            current = data.get('current_condition', [{}])[0]

            # 天气描述
            weather_desc = current.get('lang_zh', [{}])
            if weather_desc:
                weather_desc = weather_desc[0].get(
                    'value', current.get('weatherDesc', [{}])[0].get('value', 'N/A')
                )
            else:
                weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')

            temp = current.get('temp_C', 'N/A')
            feels_like = current.get('FeelsLikeC', 'N/A')
            humidity = current.get('humidity', 'N/A')
            wind_speed = current.get('windspeedKmph', 'N/A')

            # 今日预报
            weather_today = data.get('weather', [{}])[0]
            temp_max = weather_today.get('maxtempC', 'N/A')
            temp_min = weather_today.get('mintempC', 'N/A')

            # 构建回复
            reply = f"""🌤 今日天气

📍 当前天气：{weather_desc}
🌡 实时温度：{temp}°C（体感{feels_like}°C）
📊 温度范围：{temp_min}°C ~ {temp_max}°C
💧 相对湿度：{humidity}%
🌬 风速：{wind_speed}km/h

💡 温馨提示"""

            # 生成提示
            tips = []
            try:
                temp_val = int(temp)
                if '雨' in weather_desc or 'rain' in weather_desc.lower():
                    tips.append('☔ 今天有雨，出门记得带伞！')
                if '雪' in weather_desc or 'snow' in weather_desc.lower():
                    tips.append('❄️ 今天有雪，注意保暖和路滑！')
                if temp_val >= 35:
                    tips.append('🔥 高温预警！注意防暑降温，多喝水！')
                elif temp_val >= 30:
                    tips.append('☀️ 天气较热，注意防晒补水！')
                if temp_val <= 0:
                    tips.append('🥶 气温很低，注意保暖防冻！')
                elif temp_val <= 10:
                    tips.append('🧥 天气较冷，多穿点衣服！')
            except:
                pass

            if tips:
                reply += '\n' + '\n'.join(tips)
            else:
                reply += '\n今天天气不错，心情也要美美的！'

            return reply

        except Exception as e:
            print(f'坐标天气查询失败: {str(e)}')
            # 如果经纬度查询失败，返回错误信息
            return None

    def parse_city_from_label(self, label):
        """
        从位置标签中解析城市名

        Args:
            label: 位置标签，如 "广东省深圳市南山区xxx"

        Returns:
            str: 城市名，如 "深圳"
        """
        if not label:
            return None

        # 常见城市关键词
        city_keywords = ['市', '区', '县']

        # 尝试从标签中提取城市
        for keyword in city_keywords:
            if keyword in label:
                # 找到关键词的位置
                idx = label.find(keyword)
                # 向前查找省份
                start = 0
                if '省' in label:
                    start = label.find('省') + 1
                elif '自治区' in label:
                    start = label.find('自治区') + 3

                city = label[start:idx]
                if city:
                    return city

        return None


# 创建位置天气服务实例
location_weather_service = LocationWeatherService()


def get_weather_by_location(latitude, longitude, label=None):
    """
    根据用户位置获取天气

    Args:
        latitude: 纬度
        longitude: 经度
        label: 位置标签（地址描述）

    Returns:
        str: 天气回复
    """
    return location_weather_service.get_weather_by_location(latitude, longitude, label)


# ============== 智能天气查询（多API自动切换） ============== #
class SmartWeatherService:
    """
    智能天气服务
    支持多个天气API自动切换，当一个API不可用时自动尝试下一个
    """

    def __init__(self):
        self.qweather = weather_service  # 和风天气
        self.wttr = free_weather_service  # wttr.in
        # API优先级，从配置读取
        self.api_priority = consts.WEATHER_API_PRIORITY

    def get_weather(self, city_name, city_pinyin=None):
        """
        智能获取天气信息，自动切换API

        Args:
            city_name: 城市名称（中文）
            city_pinyin: 城市拼音（可选，用于wttr.in）

        Returns:
            str: 天气信息回复
        """
        errors = []

        for api_name in self.api_priority:
            try:
                print(f'尝试使用 {api_name} API 获取天气...')

                if api_name == 'qweather':
                    result = self._try_qweather(city_name)
                elif api_name == 'wttr':
                    result = self._try_wttr(city_name, city_pinyin)
                else:
                    continue

                if result:
                    print(f'✅ {api_name} API 获取天气成功')
                    return result

            except Exception as e:
                error_msg = f'{api_name}: {str(e)}'
                errors.append(error_msg)
                print(f'❌ {api_name} API 失败: {str(e)}')
                continue

        # 所有API都失败
        print(f'所有天气API都失败: {errors}')
        return '😢 获取天气信息失败，请稍后再试~'

    def _try_qweather(self, city_name):
        """尝试使用和风天气API"""
        if not consts.WEATHER_API_KEY or consts.WEATHER_API_KEY == 'YOUR_API_KEY':
            print('和风天气API密钥未配置，跳过')
            return None

        try:
            weather_info = self.qweather.get_weather(city_name)
            if weather_info.get('success'):
                return self.qweather.format_weather_reply(weather_info)
            return None
        except Exception as e:
            print(f'和风天气API异常: {str(e)}')
            return None

    def _try_wttr(self, city_name, city_pinyin=None):
        """尝试使用wttr.in API"""
        try:
            query_city = city_pinyin if city_pinyin else self._get_city_pinyin(city_name)
            result = self.wttr.get_weather(query_city)
            if result and '获取天气信息失败' not in result:
                return result
            return None
        except Exception as e:
            print(f'wttr.in API异常: {str(e)}')
            return None

    def _get_city_pinyin(self, city_name):
        """将常见中文城市名转换为拼音"""
        return consts.WEATHER_CITY_PINYIN_MAP.get(city_name, city_name)


# 创建智能天气服务实例
smart_weather_service = SmartWeatherService()


def get_smart_weather_reply(city_name, city_pinyin=None):
    """
    智能获取天气回复（自动切换API）

    Args:
        city_name: 城市名称（中文）
        city_pinyin: 城市拼音（可选）

    Returns:
        str: 天气信息回复
    """
    return smart_weather_service.get_weather(city_name, city_pinyin)
