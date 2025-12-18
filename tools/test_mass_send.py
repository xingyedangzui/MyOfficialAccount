# -*- coding: utf-8 -*-
"""
测试群发天气图文消息
注意：订阅号每天只能群发1条消息，请谨慎测试！
"""

import sys
import os

# 将script目录添加到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'script'))

from scheduler import mass_send_scheduler, test_mass_send_now
from wechat_push_service import wechat_push_service
import consts


def test_get_access_token():
    """测试获取access_token"""
    print('\n===== 测试获取access_token =====')
    token = wechat_push_service._get_access_token()
    if token:
        print(f'✅ 获取access_token成功!')
        print(f'   access_token: {token}')
        return True
    else:
        print('❌ 获取access_token失败')
        return False


def test_upload_image():
    """测试上传封面图片"""
    print('\n===== 测试上传封面图片 =====')

    image_path = getattr(consts, 'MASS_SEND_WEATHER_IMAGE_PATH', '')

    # 处理相对路径
    if not os.path.isabs(image_path):
        image_path = os.path.join(os.path.dirname(__file__), '..', 'script', image_path)

    if not image_path:
        print('❌ 未配置封面图片路径 MASS_SEND_WEATHER_IMAGE_PATH')
        return None

    if not os.path.exists(image_path):
        print(f'❌ 封面图片不存在: {image_path}')
        print('请将封面图片放到 script/data/weather_cover.jpg')
        return None

    print(f'正在上传: {image_path}')
    media_id = wechat_push_service.upload_permanent_image(image_path)

    if media_id:
        print(f'✅ 上传成功! media_id: {media_id}')
        print(f'\n💡 请将此media_id配置到consts.py的MASS_SEND_THUMB_MEDIA_ID')
        return media_id
    else:
        print('❌ 上传失败')
        return None


def test_get_materials():
    """测试获取素材列表"""
    print('\n===== 测试获取素材列表 =====')

    # 获取图片素材列表
    print('\n📷 图片素材:')
    result = wechat_push_service.get_material_list('image', 0, 5)
    if result:
        print(f'总数: {result.get("total_count", 0)}')
        for item in result.get('item', []):
            media_id = item.get('media_id', '')
            name = item.get('name', '未命名')
            print(f'  - media_id: {media_id}')
            print(f'    名称: {name}')
            print()
    else:
        print('  (无法获取)')

    # 获取图文素材列表
    print('\n📰 图文素材:')
    result = wechat_push_service.get_material_list('news', 0, 5)
    if result:
        print(f'总数: {result.get("total_count", 0)}')
        for item in result.get('item', []):
            media_id = item.get('media_id', '')
            content = item.get('content', {})
            articles = content.get('news_item', [])
            title = articles[0].get('title', '无标题') if articles else '无标题'
            print(f'  - media_id: {media_id}')
            print(f'    标题: {title}')
            print()
    else:
        print('  (无法获取)')


def test_create_news_material():
    """测试创建图文素材（不群发）"""
    print('\n===== 测试创建图文素材 =====')

    # 检查封面图片media_id
    thumb_media_id = getattr(consts, 'MASS_SEND_THUMB_MEDIA_ID', '')

    if not thumb_media_id:
        print('❌ 未配置封面图片media_id')
        print('请先运行 test_upload_image() 上传图片获取media_id')
        return None

    # 生成测试内容
    from datetime import datetime
    from weather_service import weather_service, get_clothing_advice

    city_name = consts.MASS_SEND_WEATHER_CITY
    print(f'正在获取{city_name}天气...')

    # 使用底层的weather_service获取天气数据字典
    weather_info = weather_service.get_weather(city_name)
    if not weather_info or not weather_info.get('success'):
        print('❌ 获取天气失败')
        print(f'   返回信息: {weather_info}')
        return None

    # 天气数据在 'now' 字段下
    now_data = weather_info.get('now', {})
    temp = now_data.get('temp', 'N/A')
    feel_temp = now_data.get('feels_like', temp)
    weather_desc = now_data.get('text', '')
    humidity = now_data.get('humidity', 'N/A')
    wind_dir = now_data.get('wind_dir', '')
    wind_scale = now_data.get('wind_scale', '')

    # 获取穿衣建议并格式化为字符串
    advice = get_clothing_advice(int(temp) if temp != 'N/A' else 20, weather_desc)
    clothing_advice = f'{advice["emoji"]} {advice["level"]}：{advice["clothes"]}。{advice["tip"]}'
    if advice.get('extra_tips'):
        clothing_advice += ' ' + ' '.join(advice['extra_tips'])

    today = datetime.now().strftime('%Y年%m月%d日')
    weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][datetime.now().weekday()]

    # 生成HTML内容
    html_content = consts.MASS_SEND_WEATHER_HTML.format(
        date=today,
        weekday=weekday,
        city=city_name,
        temp=temp,
        feel_temp=feel_temp,
        weather=weather_desc,
        humidity=humidity,
        wind_dir=wind_dir,
        wind_scale=wind_scale,
        clothing_advice=clothing_advice,
    )

    # 生成标题
    title_date = datetime.now().strftime('%m月%d日')
    title = consts.MASS_SEND_WEATHER_TITLE.format(date=title_date, city=city_name)

    print(f'标题: {title}')
    print(f'天气: {weather_desc}, {temp}°C')

    # 创建图文素材
    print('\n正在创建图文素材...')
    news_media_id = wechat_push_service.add_news_material(
        title=title,
        thumb_media_id=thumb_media_id,
        content=html_content,
        author=getattr(consts, 'MASS_SEND_AUTHOR', ''),
        digest=getattr(consts, 'MASS_SEND_DIGEST', f'{city_name}今日天气播报'),
        show_cover_pic=1,
    )

    if news_media_id:
        print(f'✅ 图文素材创建成功! media_id: {news_media_id}')
        return news_media_id
    else:
        print('❌ 图文素材创建失败')
        return None


def do_mass_send():
    """
    执行群发（危险操作！）
    ⚠️ 注意：订阅号每天只能群发1条消息！
    """
    print('\n' + '=' * 50)
    print('⚠️  警告：您即将执行群发操作！')
    print('⚠️  订阅号每天只能群发1条消息！')
    print('=' * 50)

    confirm = input("\n确认群发吗？输入 'YES' 继续: ")
    if confirm != 'YES':
        print('已取消')
        return

    print('\n开始执行群发...')
    result = test_mass_send_now()

    if result:
        print('\n✅ 群发成功！')
    else:
        print('\n❌ 群发失败，请检查日志')


def main():
    """主菜单"""
    print('\n' + '=' * 50)
    print('   天气群发功能测试工具')
    print('=' * 50)

    while True:
        print('\n请选择测试项目:')
        print('1. 测试获取access_token')
        print('2. 测试上传封面图片')
        print('3. 查看素材列表')
        print('4. 测试创建图文素材（不群发）')
        print('5. 🚨 执行群发（危险操作）')
        print('0. 退出')

        choice = input('\n请输入选项: ').strip()

        if choice == '1':
            test_get_access_token()
        elif choice == '2':
            test_upload_image()
        elif choice == '3':
            test_get_materials()
        elif choice == '4':
            test_create_news_material()
        elif choice == '5':
            do_mass_send()
        elif choice == '0':
            print('再见！')
            break
        else:
            print('无效选项，请重新输入')


if __name__ == '__main__':
    main()
