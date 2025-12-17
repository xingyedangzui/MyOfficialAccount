# -*- coding: utf-8 -*-
# JSON数据持久化使用示例

from data_manager import data_manager, user_data_manager, JSONDataManager


def basic_usage_examples():
    """基础使用示例"""
    print('=== 基础JSON数据持久化示例 ===')

    # 1. 保存简单数据
    user_config = {'theme': 'dark', 'language': 'zh-CN', 'notifications': True, 'auto_reply': False}

    success = data_manager.save_data('config', user_config)
    print(f'保存配置: {"成功" if success else "失败"}')

    # 2. 读取数据
    loaded_config = data_manager.load_data('config')
    print(f'加载的配置: {loaded_config}')

    # 3. 更新数据
    def update_config(current_config):
        if current_config is None:
            current_config = {}
        current_config['auto_reply'] = True
        current_config['last_modified'] = '2024-12-16 14:50'
        return current_config

    success = data_manager.update_data('config', update_config)
    print(f'更新配置: {"成功" if success else "失败"}')

    # 4. 再次读取验证
    updated_config = data_manager.load_data('config')
    print(f'更新后的配置: {updated_config}')

    print()


def user_data_examples():
    """用户数据管理示例"""
    print('=== 用户数据管理示例 ===')

    # 模拟一些用户数据
    test_users = [
        {'openid': 'user001', 'nickname': '张三', 'subscribe_time': '2024-12-16'},
        {'openid': 'user002', 'nickname': '李四', 'subscribe_time': '2024-12-15'},
        {'openid': 'user003', 'nickname': '王五', 'subscribe_time': '2024-12-14'},
    ]

    # 1. 保存用户信息
    for user in test_users:
        openid = user['openid']
        user_info = {
            'nickname': user['nickname'],
            'subscribe_time': user['subscribe_time'],
            'status': 'active',
        }
        success = user_data_manager.save_user_info(openid, user_info)
        print(f'保存用户 {user["nickname"]}: {"成功" if success else "失败"}')

    # 2. 记录用户消息
    messages = [
        {'openid': 'user001', 'type': 'text', 'content': '你好'},
        {'openid': 'user001', 'type': 'text', 'content': '帮助'},
        {'openid': 'user002', 'type': 'image', 'content': '发送了一张图片'},
        {'openid': 'user003', 'type': 'text', 'content': '谢谢'},
    ]

    for msg in messages:
        success = user_data_manager.record_user_message(msg['openid'], msg['type'], msg['content'])
        print(f'记录消息 {msg["openid"]}: {"成功" if success else "失败"}')

    # 3. 获取用户信息
    user_info = user_data_manager.get_user_info('user001')
    print(f'用户user001信息: {user_info}')

    # 4. 获取用户消息历史
    messages = user_data_manager.get_user_messages('user001', limit=5)
    print(f'用户user001的消息历史: {messages}')

    # 5. 更新统计数据
    events = ['subscribe', 'text_message', 'text_message', 'image_message', 'unsubscribe']
    for event in events:
        user_data_manager.update_statistics(event)

    # 6. 获取统计数据
    stats = user_data_manager.get_statistics()
    print(f'统计数据: {stats}')

    print()


def advanced_usage_examples():
    """高级使用示例"""
    print('=== 高级使用示例 ===')

    # 创建专门的数据管理器实例
    logs_manager = JSONDataManager('logs')  # 存储在logs目录

    # 1. 保存日志数据
    import time

    log_entry = {
        'level': 'INFO',
        'message': '用户登录成功',
        'timestamp': time.time(),
        'user_id': 'user001',
    }

    # 使用更新函数来追加日志
    def append_log(current_logs):
        if current_logs is None:
            current_logs = []

        current_logs.append(log_entry)

        # 只保留最近1000条日志
        if len(current_logs) > 1000:
            current_logs = current_logs[-1000:]

        return current_logs

    success = logs_manager.update_data('app_logs', append_log)
    print(f'追加日志: {"成功" if success else "失败"}')

    # 2. 管理关键词回复规则
    reply_rules = {
        '你好': '你好！很高兴为您服务！',
        '帮助': "您可以发送以下内容:\n• 发送'你好'打招呼\n• 发送'帮助'查看帮助信息",
        '拜拜': '再见！期待下次与您交流！',
        '时间': '当前时间是: {time}',  # 支持动态替换
    }

    success = data_manager.save_data('reply_rules', reply_rules)
    print(f'保存回复规则: {"成功" if success else "失败"}')

    # 3. 加载并使用回复规则
    rules = data_manager.load_data('reply_rules', {})
    user_input = '你好'
    if user_input in rules:
        reply = rules[user_input]
        if '{time}' in reply:
            import time

            reply = reply.replace('{time}', time.strftime('%Y-%m-%d %H:%M:%S'))
        print(f"用户输入'{user_input}' -> 自动回复: {reply}")

    # 4. 列出所有数据文件
    files = data_manager.list_files()
    print(f'当前数据文件: {files}')

    print()


def integration_example():
    """集成到现有项目的示例"""
    print('=== 集成到微信公众号项目示例 ===')

    # 模拟处理用户关注事件
    def handle_subscribe_event(openid: str, event_data: dict):
        """处理用户关注事件"""
        # 保存用户信息
        user_info = {
            'status': 'subscribed',
            'subscribe_time': event_data.get('CreateTime', ''),
            'source': 'wechat',
        }

        success = user_data_manager.save_user_info(openid, user_info)
        if success:
            print(f'用户 {openid} 关注信息已保存')

        # 更新统计
        user_data_manager.update_statistics('subscribe')
        print('关注统计已更新')

    # 模拟处理文本消息
    def handle_text_message(openid: str, content: str):
        """处理文本消息"""
        # 记录消息
        user_data_manager.record_user_message(openid, 'text', content)

        # 更新统计
        user_data_manager.update_statistics('text_message')

        # 获取用户历史消息（可用于上下文理解）
        history = user_data_manager.get_user_messages(openid, limit=5)
        print(f'用户 {openid} 最近消息: {len(history)} 条')

        # 加载回复规则
        rules = data_manager.load_data('reply_rules', {})
        if content in rules:
            return rules[content]
        else:
            return f'收到您的消息: {content}'

    # 测试事件处理
    test_openid = 'test_user_001'

    # 模拟关注事件
    handle_subscribe_event(test_openid, {'CreateTime': '1702713000'})

    # 模拟文本消息
    reply1 = handle_text_message(test_openid, '你好')
    print(f'回复1: {reply1}')

    reply2 = handle_text_message(test_openid, '帮助')
    print(f'回复2: {reply2}')

    reply3 = handle_text_message(test_openid, '测试消息')
    print(f'回复3: {reply3}')


if __name__ == '__main__':
    print('JSON数据持久化示例演示')
    print('=' * 50)

    # 运行所有示例
    basic_usage_examples()
    user_data_examples()
    advanced_usage_examples()
    integration_example()

    print('示例演示完成！')
    print('\n数据文件已保存在项目的 data/ 目录下')
    print('日志文件已保存在项目的 logs/ 目录下')
