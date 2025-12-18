# -*- coding: utf-8 -*-
"""
天气推送功能测试脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'script'))

from scheduler import weather_push_scheduler, test_push_now
from wechat_push_service import wechat_push_service
from data_manager import user_data_manager


def test_access_token():
    """测试获取access_token"""
    print('=' * 50)
    print('测试获取微信access_token...')
    print('=' * 50)

    token = wechat_push_service._get_access_token()
    if token:
        print(f'✅ access_token获取成功: {token[:20]}...')
    else:
        print('❌ access_token获取失败')

    return token is not None


def test_send_message(openid, message='这是一条测试消息'):
    """测试发送消息"""
    print('=' * 50)
    print(f'测试向用户 {openid[:8]}... 发送消息')
    print('=' * 50)

    success = wechat_push_service.send_text_message(openid, message)
    if success:
        print('✅ 消息发送成功')
    else:
        print('❌ 消息发送失败')

    return success


def test_weather_push_single(openid, city_name='北京'):
    """测试向单个用户推送天气"""
    print('=' * 50)
    print(f'测试向用户 {openid[:8]}... 推送{city_name}天气')
    print('=' * 50)

    success = weather_push_scheduler.push_weather_to_user(openid, city_name, city_name)
    if success:
        print('✅ 天气推送成功')
    else:
        print('❌ 天气推送失败')

    return success


def test_weather_push_all():
    """测试向所有订阅用户推送天气（立即执行）"""
    print('=' * 50)
    print('测试向所有订阅用户推送天气...')
    print('=' * 50)

    test_push_now()


def show_subscribers():
    """显示所有订阅天气推送的用户"""
    print('=' * 50)
    print('天气推送订阅用户列表')
    print('=' * 50)

    subscribers = user_data_manager.get_weather_push_subscribers()
    if not subscribers:
        print('暂无订阅用户')
        return

    for i, openid in enumerate(subscribers, 1):
        user_city = user_data_manager.get_user_weather_city(openid)
        city_name = user_city['city_name'] if user_city else '未设置'
        vip_info = user_data_manager.get_vip_info(openid)
        vip_id = vip_info.get('vip_id', 'N/A') if vip_info else 'N/A'
        print(f'{i}. {vip_id} | {openid[:8]}... | 城市: {city_name}')

    print(f'\n共 {len(subscribers)} 位用户订阅了天气推送')


def show_vip_users():
    """显示所有VIP用户"""
    print('=' * 50)
    print('VIP用户列表')
    print('=' * 50)

    vip_users = user_data_manager.get_all_vip_users()
    if not vip_users:
        print('暂无VIP用户')
        return

    for i, (openid, info) in enumerate(vip_users.items(), 1):
        vip_id = info.get('vip_id', 'N/A')
        weather_push = '✅' if info.get('weather_push_enabled') else '❌'
        print(f'{i}. {vip_id} | {openid[:8]}... | 天气推送: {weather_push}')

    print(f'\n共 {len(vip_users)} 位VIP用户')


def show_menu():
    """显示菜单"""
    print('\n' + '=' * 50)
    print('天气推送功能测试菜单')
    print('=' * 50)
    print('1. 测试获取access_token')
    print('2. 查看订阅用户列表')
    print('3. 查看VIP用户列表')
    print('4. 测试向所有订阅用户推送天气')
    print('5. 测试向指定用户发送消息')
    print('6. 测试向指定用户推送天气')
    print('0. 退出')
    print('=' * 50)


def main():
    """主函数"""
    while True:
        show_menu()
        choice = input('请选择操作: ').strip()

        if choice == '0':
            print('再见！')
            break
        elif choice == '1':
            test_access_token()
        elif choice == '2':
            show_subscribers()
        elif choice == '3':
            show_vip_users()
        elif choice == '4':
            confirm = input('确认向所有订阅用户推送天气？(y/n): ').strip().lower()
            if confirm == 'y':
                test_weather_push_all()
        elif choice == '5':
            openid = input('请输入用户openid: ').strip()
            message = input('请输入消息内容（回车使用默认）: ').strip()
            if openid:
                test_send_message(openid, message or '这是一条测试消息')
            else:
                print('openid不能为空')
        elif choice == '6':
            openid = input('请输入用户openid: ').strip()
            city = input('请输入城市名称（回车使用北京）: ').strip() or '北京'
            if openid:
                test_weather_push_single(openid, city)
            else:
                print('openid不能为空')
        else:
            print('无效选择')

        input('\n按回车继续...')


if __name__ == '__main__':
    main()
