# -*- coding: utf-8 -*-
# 数据持久化管理模块

import json
import os
from typing import Any, Dict, Optional
from threading import Lock


class JSONDataManager:
    """JSON数据持久化管理器"""

    def __init__(self, data_dir: str = 'data'):
        """
        初始化数据管理器

        Args:
            data_dir: 数据存储目录，默认为项目根目录下的data文件夹
        """
        # 获取项目根目录
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.project_root, data_dir)

        # 确保数据目录存在
        self._ensure_data_dir()

        # 线程锁，确保文件操作的线程安全
        self._lock = Lock()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            print(f'创建数据目录: {self.data_dir}')

    def _get_file_path(self, filename: str) -> str:
        """获取完整的文件路径"""
        if not filename.endswith('.json'):
            filename += '.json'
        return os.path.join(self.data_dir, filename)

    def _save_data_internal(self, filename: str, data: Any, indent: int = 2) -> bool:
        """内部保存方法，不加锁"""
        try:
            file_path = self._get_file_path(filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            print(f'数据已保存到: {file_path}')
            return True
        except Exception as e:
            print(f'保存数据失败 {filename}: {str(e)}')
            return False

    def _load_data_internal(self, filename: str, default_value: Any = None) -> Any:
        """内部加载方法，不加锁"""
        try:
            file_path = self._get_file_path(filename)
            if not os.path.exists(file_path):
                print(f'文件不存在: {file_path}，返回默认值')
                return default_value

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f'数据已从 {file_path} 加载')
            return data
        except Exception as e:
            print(f'加载数据失败 {filename}: {str(e)}')
            return default_value

    def save_data(self, filename: str, data: Any, indent: int = 2) -> bool:
        """
        保存数据到JSON文件

        Args:
            filename: 文件名（不需要包含.json后缀）
            data: 要保存的数据
            indent: JSON格式化缩进

        Returns:
            bool: 保存是否成功
        """
        with self._lock:
            return self._save_data_internal(filename, data, indent)

    def load_data(self, filename: str, default_value: Any = None) -> Any:
        """
        从JSON文件加载数据

        Args:
            filename: 文件名（不需要包含.json后缀）
            default_value: 文件不存在时返回的默认值

        Returns:
            Any: 加载的数据，文件不存在时返回default_value
        """
        with self._lock:
            return self._load_data_internal(filename, default_value)

    def update_data(self, filename: str, update_func, default_value: Any = None) -> bool:
        """
        更新JSON文件中的数据

        Args:
            filename: 文件名
            update_func: 更新函数，接收当前数据作为参数，返回更新后的数据
            default_value: 文件不存在时的默认值

        Returns:
            bool: 更新是否成功
        """
        try:
            with self._lock:
                current_data = self._load_data_internal(filename, default_value)
                updated_data = update_func(current_data)
                return self._save_data_internal(filename, updated_data)
        except Exception as e:
            print(f'更新数据失败 {filename}: {str(e)}')
            return False

    def delete_file(self, filename: str) -> bool:
        """
        删除JSON文件

        Args:
            filename: 文件名

        Returns:
            bool: 删除是否成功
        """
        try:
            with self._lock:
                file_path = self._get_file_path(filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f'文件已删除: {file_path}')
                    return True
                else:
                    print(f'文件不存在: {file_path}')
                    return False
        except Exception as e:
            print(f'删除文件失败 {filename}: {str(e)}')
            return False

    def list_files(self) -> list:
        """
        列出所有JSON文件

        Returns:
            list: JSON文件名列表（不包含.json后缀）
        """
        try:
            files = []
            if os.path.exists(self.data_dir):
                for filename in os.listdir(self.data_dir):
                    if filename.endswith('.json'):
                        files.append(filename[:-5])  # 移除.json后缀
            return files
        except Exception as e:
            print(f'列出文件失败: {str(e)}')
            return []


class UserDataManager:
    """用户数据管理器 - 专门用于管理微信用户数据"""

    def __init__(self):
        self.data_manager = JSONDataManager()
        self.users_file = 'users'
        self.user_messages_file = 'user_messages'
        self.statistics_file = 'statistics'
        self.vip_users_file = 'vip_users'  # VIP用户数据文件
        self.user_sessions_file = 'user_sessions'  # 用户会话状态文件（验证、菜谱录入等）
        self.recipes_file = 'recipes'  # 菜谱数据文件
        self.recipe_notifications_file = 'recipe_notifications'  # 菜谱通知记录文件

    def save_user_info(self, openid: str, user_info: Dict) -> bool:
        """
        保存用户信息

        Args:
            openid: 用户的openid
            user_info: 用户信息字典

        Returns:
            bool: 保存是否成功
        """

        def update_users(current_users):
            if current_users is None:
                current_users = {}

            # 添加时间戳
            import time

            user_info['last_update'] = time.time()
            user_info['last_update_str'] = time.strftime('%Y-%m-%d %H:%M:%S')

            current_users[openid] = user_info
            return current_users

        return self.data_manager.update_data(self.users_file, update_users, {})

    def get_user_info(self, openid: str) -> Optional[Dict]:
        """
        获取用户信息

        Args:
            openid: 用户的openid

        Returns:
            Dict: 用户信息，不存在时返回None
        """
        users = self.data_manager.load_data(self.users_file, {})
        return users.get(openid)

    def record_user_message(self, openid: str, message_type: str, content: str) -> bool:
        """
        记录用户消息

        Args:
            openid: 用户openid
            message_type: 消息类型（text, image等）
            content: 消息内容

        Returns:
            bool: 记录是否成功
        """

        def update_messages(current_messages):
            if current_messages is None:
                current_messages = {}

            if openid not in current_messages:
                current_messages[openid] = []

            import time

            message_record = {
                'type': message_type,
                'content': content,
                'timestamp': time.time(),
                'time_str': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

            current_messages[openid].append(message_record)

            # 只保留最近100条消息
            if len(current_messages[openid]) > 100:
                current_messages[openid] = current_messages[openid][-100:]

            return current_messages

        return self.data_manager.update_data(self.user_messages_file, update_messages, {})

    def get_user_messages(self, openid: str, limit: int = 10) -> list:
        """
        获取用户消息历史

        Args:
            openid: 用户openid
            limit: 返回消息数量限制

        Returns:
            list: 消息历史列表
        """
        all_messages = self.data_manager.load_data(self.user_messages_file, {})
        user_messages = all_messages.get(openid, [])
        return user_messages[-limit:] if limit > 0 else user_messages

    def update_statistics(self, event_type: str) -> bool:
        """
        更新统计数据

        Args:
            event_type: 事件类型（如：subscribe, unsubscribe, text_message等）

        Returns:
            bool: 更新是否成功
        """

        def update_stats(current_stats):
            if current_stats is None:
                current_stats = {}

            import time

            today = time.strftime('%Y-%m-%d')

            # 初始化今日统计
            if 'daily' not in current_stats:
                current_stats['daily'] = {}
            if today not in current_stats['daily']:
                current_stats['daily'][today] = {}

            # 初始化总统计
            if 'total' not in current_stats:
                current_stats['total'] = {}

            # 更新统计
            current_stats['daily'][today][event_type] = (
                current_stats['daily'][today].get(event_type, 0) + 1
            )
            current_stats['total'][event_type] = current_stats['total'].get(event_type, 0) + 1

            # 只保留最近30天的数据
            import datetime

            cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime(
                '%Y-%m-%d'
            )
            dates_to_remove = [date for date in current_stats['daily'].keys() if date < cutoff_date]
            for date in dates_to_remove:
                del current_stats['daily'][date]

            return current_stats

        return self.data_manager.update_data(self.statistics_file, update_stats, {})

    def get_statistics(self) -> Dict:
        """
        获取统计数据

        Returns:
            Dict: 统计数据
        """
        return self.data_manager.load_data(self.statistics_file, {})

    # ==================== VIP用户管理功能 ==================== #

    def _generate_vip_id(self) -> str:
        """
        生成专属VIP ID

        Returns:
            str: 格式化的VIP ID，如 VIP-0001
        """
        vip_users = self.data_manager.load_data(self.vip_users_file, {})
        next_number = len(vip_users) + 1
        return f'VIP-{next_number:04d}'

    def verify_and_save_vip(self, openid: str) -> Dict:
        """
        验证暗号并保存VIP用户信息

        Args:
            openid: 用户的openid

        Returns:
            Dict: 包含验证结果的字典
                  - is_new: bool, 是否是新VIP用户
                  - vip_id: str, VIP ID
                  - verify_time: str, 验证时间
        """
        import time

        # 检查是否已经是VIP用户
        existing_vip = self.get_vip_info(openid)
        if existing_vip:
            return {
                'is_new': False,
                'vip_id': existing_vip['vip_id'],
                'verify_time': existing_vip['verify_time_str'],
            }

        # 生成新的VIP信息
        vip_id = self._generate_vip_id()
        current_time = time.time()
        verify_time_str = time.strftime('%Y-%m-%d %H:%M:%S')

        vip_info = {
            'openid': openid,
            'vip_id': vip_id,
            'verify_time': current_time,
            'verify_time_str': verify_time_str,
            'status': 'active',
            'privileges': ['basic'],  # 可以后续扩展权限
        }

        # 保存VIP信息
        def update_vip_users(current_vip_users):
            if current_vip_users is None:
                current_vip_users = {}
            current_vip_users[openid] = vip_info
            return current_vip_users

        success = self.data_manager.update_data(self.vip_users_file, update_vip_users, {})

        if success:
            # 同时更新用户基本信息中的VIP状态
            user_info = self.get_user_info(openid) or {}
            user_info['vip_status'] = 'vip'
            user_info['vip_id'] = vip_id
            user_info['vip_verify_time'] = verify_time_str
            self.save_user_info(openid, user_info)

            # 更新统计
            self.update_statistics('vip_verification')

            print(f'新VIP用户注册成功: {openid} -> {vip_id}')

        return {'is_new': True, 'vip_id': vip_id, 'verify_time': verify_time_str}

    def get_vip_info(self, openid: str) -> Optional[Dict]:
        """
        获取VIP用户信息

        Args:
            openid: 用户的openid

        Returns:
            Dict: VIP用户信息，不存在时返回None
        """
        vip_users = self.data_manager.load_data(self.vip_users_file, {})
        return vip_users.get(openid)

    def is_vip_user(self, openid: str) -> bool:
        """
        检查用户是否是VIP

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否是VIP用户
        """
        vip_info = self.get_vip_info(openid)
        return vip_info is not None and vip_info.get('status') == 'active'

    def get_all_vip_users(self) -> Dict:
        """
        获取所有VIP用户列表

        Returns:
            Dict: 所有VIP用户信息
        """
        return self.data_manager.load_data(self.vip_users_file, {})

    def get_vip_count(self) -> int:
        """
        获取VIP用户数量

        Returns:
            int: VIP用户总数
        """
        vip_users = self.data_manager.load_data(self.vip_users_file, {})
        return len(vip_users)

    def delete_user_data(self, openid: str) -> bool:
        """
        删除用户所有相关数据（用于用户取消关注时清理）

        Args:
            openid: 用户的openid

        Returns:
            bool: 删除是否成功
        """
        print(f'开始删除用户 {openid} 的所有数据...')

        # 1. 删除用户基本信息
        def delete_from_users(users):
            if users and openid in users:
                del users[openid]
                print(f'已删除用户基本信息: {openid}')
            return users or {}

        self.data_manager.update_data(self.users_file, delete_from_users, {})

        # 2. 删除用户消息记录
        def delete_from_messages(messages):
            if messages and openid in messages:
                del messages[openid]
                print(f'已删除用户消息记录: {openid}')
            return messages or {}

        self.data_manager.update_data(self.user_messages_file, delete_from_messages, {})

        # 3. 删除VIP信息
        def delete_from_vip(vip_users):
            if vip_users and openid in vip_users:
                del vip_users[openid]
                print(f'已删除用户VIP信息: {openid}')
            return vip_users or {}

        self.data_manager.update_data(self.vip_users_file, delete_from_vip, {})

        # 4. 删除用户会话状态
        def delete_from_sessions(sessions):
            if sessions and openid in sessions:
                del sessions[openid]
                print(f'已删除用户会话状态: {openid}')
            return sessions or {}

        self.data_manager.update_data(self.user_sessions_file, delete_from_sessions, {})

        # 5. 删除菜谱通知
        def delete_from_notifications(notifications):
            if notifications and openid in notifications:
                del notifications[openid]
                print(f'已删除用户菜谱通知: {openid}')
            return notifications or {}

        self.data_manager.update_data(self.recipe_notifications_file, delete_from_notifications, {})

        print(f'用户 {openid} 的所有数据已删除')
        return True

    # ==================== 用户会话状态管理 ==================== #

    def set_user_session_state(self, openid: str, state: str, extra_data: Dict = None) -> bool:
        """
        设置用户会话状态

        Args:
            openid: 用户的openid
            state: 会话状态
            extra_data: 额外数据

        Returns:
            bool: 是否成功
        """
        import time

        def update_sessions(current_sessions):
            if current_sessions is None:
                current_sessions = {}

            session_data = {
                'state': state,
                'start_time': time.time(),
                'start_time_str': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            if extra_data:
                session_data.update(extra_data)

            current_sessions[openid] = session_data
            return current_sessions

        return self.data_manager.update_data(self.user_sessions_file, update_sessions, {})

    def get_user_session_state(self, openid: str) -> Optional[Dict]:
        """
        获取用户会话状态

        Args:
            openid: 用户的openid

        Returns:
            Dict: 会话状态信息，不存在时返回None
        """
        sessions = self.data_manager.load_data(self.user_sessions_file, {})
        return sessions.get(openid)

    def clear_user_session_state(self, openid: str) -> bool:
        """
        清除用户会话状态

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否成功
        """

        def update_sessions(current_sessions):
            if current_sessions is None:
                current_sessions = {}
            if openid in current_sessions:
                del current_sessions[openid]
            return current_sessions

        return self.data_manager.update_data(self.user_sessions_file, update_sessions, {})

    # ==================== 菜谱管理功能 ==================== #

    def add_recipe(self, openid: str, recipe_content: str, category: str = None) -> Dict:
        """
        添加菜谱

        Args:
            openid: 用户的openid
            recipe_content: 菜谱内容
            category: 菜谱分类 ('meat' 或 'veg')

        Returns:
            Dict: 包含添加结果的字典
                  - success: bool, 是否成功
                  - recipe_id: int, 菜谱ID
                  - recipe_name: str, 菜谱名称
        """
        import time

        # 解析菜谱内容，提取菜名（取第一行或全部内容作为菜名）
        lines = recipe_content.strip().split('\n')
        recipe_name = lines[0].strip()

        # 如果菜名包含冒号，取冒号后面的内容
        if '：' in recipe_name:
            recipe_name = recipe_name.split('：', 1)[1].strip()
        elif ':' in recipe_name:
            recipe_name = recipe_name.split(':', 1)[1].strip()

        # 获取用户VIP信息用于显示创建者
        vip_info = self.get_vip_info(openid)
        creator_name = vip_info['vip_id'] if vip_info else openid[:8]

        def update_recipes(current_recipes):
            if current_recipes is None:
                current_recipes = {'list': [], 'next_id': 1}

            recipe_id = current_recipes.get('next_id', 1)

            recipe = {
                'id': recipe_id,
                'name': recipe_name,
                'content': recipe_content,
                'category': category,  # 新增分类字段
                'creator_openid': openid,
                'creator_name': creator_name,
                'create_time': time.time(),
                'create_time_str': time.strftime('%Y-%m-%d %H:%M:%S'),
            }

            current_recipes['list'].append(recipe)
            current_recipes['next_id'] = recipe_id + 1

            return current_recipes

        success = self.data_manager.update_data(
            self.recipes_file, update_recipes, {'list': [], 'next_id': 1}
        )

        if success:
            # 记录新菜谱通知（用于通知其他VIP用户）
            self._record_new_recipe_notification(openid, recipe_name)
            print(f'菜谱添加成功: {recipe_name} (分类: {category}) by {creator_name}')

        recipes = self.data_manager.load_data(self.recipes_file, {'list': [], 'next_id': 1})
        recipe_id = recipes['next_id'] - 1

        return {
            'success': success,
            'recipe_id': recipe_id,
            'recipe_name': recipe_name,
        }

    def _record_new_recipe_notification(self, creator_openid: str, recipe_name: str) -> bool:
        """
        记录新菜谱通知（用于通知其他VIP用户）

        Args:
            creator_openid: 创建者openid
            recipe_name: 菜谱名称

        Returns:
            bool: 是否成功
        """
        import time

        # 获取所有VIP用户，为他们记录通知
        vip_users = self.get_all_vip_users()

        def update_notifications(current_notifications):
            if current_notifications is None:
                current_notifications = {}

            for openid in vip_users.keys():
                # 不通知创建者自己
                if openid == creator_openid:
                    continue

                if openid not in current_notifications:
                    current_notifications[openid] = []

                current_notifications[openid].append(
                    {
                        'recipe_name': recipe_name,
                        'time': time.time(),
                        'time_str': time.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                )

            return current_notifications

        return self.data_manager.update_data(
            self.recipe_notifications_file, update_notifications, {}
        )

    def get_new_recipe_notifications(self, openid: str) -> list:
        """
        获取用户未读的新菜谱通知

        Args:
            openid: 用户的openid

        Returns:
            list: 新菜谱通知列表
        """
        notifications = self.data_manager.load_data(self.recipe_notifications_file, {})
        return notifications.get(openid, [])

    def clear_recipe_notifications(self, openid: str) -> bool:
        """
        清除用户的菜谱通知

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否成功
        """

        def update_notifications(current_notifications):
            if current_notifications is None:
                current_notifications = {}
            if openid in current_notifications:
                del current_notifications[openid]
            return current_notifications

        return self.data_manager.update_data(
            self.recipe_notifications_file, update_notifications, {}
        )

    def get_recipe_list(self) -> list:
        """
        获取菜谱列表

        Returns:
            list: 菜谱列表
        """
        recipes = self.data_manager.load_data(self.recipes_file, {'list': [], 'next_id': 1})
        return recipes.get('list', [])

    def get_recipe_by_index(self, index: int) -> Optional[Dict]:
        """
        通过序号获取菜谱（序号从1开始）

        Args:
            index: 菜谱序号（1开始）

        Returns:
            Dict: 菜谱信息，不存在时返回None
        """
        recipe_list = self.get_recipe_list()
        if 1 <= index <= len(recipe_list):
            return recipe_list[index - 1]
        return None

    def get_random_recipe(self) -> Optional[Dict]:
        """
        获取随机菜谱

        Returns:
            Dict: 随机菜谱信息，列表为空时返回None
        """
        import random

        recipe_list = self.get_recipe_list()
        if not recipe_list:
            return None
        return random.choice(recipe_list)

    def get_random_recipe_by_category(self, category: str) -> Optional[Dict]:
        """
        按分类获取随机菜谱

        Args:
            category: 菜谱分类 ('meat' 或 'veg')

        Returns:
            Dict: 随机菜谱信息，该分类为空时返回None
        """
        import random

        recipe_list = self.get_recipe_list()
        # 筛选指定分类的菜谱
        category_recipes = [r for r in recipe_list if r.get('category') == category]
        if not category_recipes:
            return None
        return random.choice(category_recipes)

    def get_random_recipe_pair(self) -> Dict:
        """
        获取一荤一素的随机菜谱组合

        Returns:
            Dict: 包含荤菜和素菜的字典
                  - meat: Dict 或 None, 随机荤菜
                  - veg: Dict 或 None, 随机素菜
                  - has_any: bool, 是否至少有一个菜谱
        """
        meat_recipe = self.get_random_recipe_by_category('meat')
        veg_recipe = self.get_random_recipe_by_category('veg')

        return {
            'meat': meat_recipe,
            'veg': veg_recipe,
            'has_any': meat_recipe is not None or veg_recipe is not None,
        }

    def get_recipe_count(self) -> int:
        """
        获取菜谱数量

        Returns:
            int: 菜谱数量
        """
        return len(self.get_recipe_list())

    # ==================== 用户偏好设置管理 ==================== #

    def set_user_weather_city(self, openid: str, city_name: str, city_pinyin: str = None) -> bool:
        """
        设置用户的天气城市偏好

        Args:
            openid: 用户的openid
            city_name: 城市名称（中文）
            city_pinyin: 城市拼音（用于API查询）

        Returns:
            bool: 是否成功
        """
        import time

        def update_users(current_users):
            if current_users is None:
                current_users = {}

            if openid not in current_users:
                current_users[openid] = {}

            current_users[openid]['weather_city'] = city_name
            current_users[openid]['weather_city_pinyin'] = city_pinyin or city_name
            current_users[openid]['weather_city_set_time'] = time.strftime('%Y-%m-%d %H:%M:%S')

            return current_users

        return self.data_manager.update_data(self.users_file, update_users, {})

    def get_user_weather_city(self, openid: str) -> Optional[Dict]:
        """
        获取用户的天气城市偏好

        Args:
            openid: 用户的openid

        Returns:
            Dict: 包含城市信息的字典，未设置时返回None
                  - city_name: str, 城市名称
                  - city_pinyin: str, 城市拼音
        """
        users = self.data_manager.load_data(self.users_file, {})
        user_info = users.get(openid, {})

        city_name = user_info.get('weather_city')
        if city_name:
            return {
                'city_name': city_name,
                'city_pinyin': user_info.get('weather_city_pinyin', city_name),
            }
        return None

    def clear_user_weather_city(self, openid: str) -> bool:
        """
        清除用户的天气城市偏好

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否成功
        """

        def update_users(current_users):
            if current_users is None:
                current_users = {}

            if openid in current_users:
                current_users[openid].pop('weather_city', None)
                current_users[openid].pop('weather_city_pinyin', None)
                current_users[openid].pop('weather_city_set_time', None)

            return current_users

        return self.data_manager.update_data(self.users_file, update_users, {})

    # ==================== 天气推送订阅管理 ==================== #

    def subscribe_weather_push(self, openid: str) -> bool:
        """
        订阅天气推送

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否成功
        """
        import time

        def update_vip_users(current_vip_users):
            if current_vip_users is None:
                current_vip_users = {}

            if openid in current_vip_users:
                current_vip_users[openid]['weather_push_enabled'] = True
                current_vip_users[openid]['weather_push_subscribe_time'] = time.strftime(
                    '%Y-%m-%d %H:%M:%S'
                )

            return current_vip_users

        return self.data_manager.update_data(self.vip_users_file, update_vip_users, {})

    def unsubscribe_weather_push(self, openid: str) -> bool:
        """
        取消订阅天气推送

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否成功
        """

        def update_vip_users(current_vip_users):
            if current_vip_users is None:
                current_vip_users = {}

            if openid in current_vip_users:
                current_vip_users[openid]['weather_push_enabled'] = False
                current_vip_users[openid].pop('weather_push_subscribe_time', None)

            return current_vip_users

        return self.data_manager.update_data(self.vip_users_file, update_vip_users, {})

    def is_weather_push_subscribed(self, openid: str) -> bool:
        """
        检查用户是否已订阅天气推送

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否已订阅
        """
        vip_info = self.get_vip_info(openid)
        if vip_info:
            return vip_info.get('weather_push_enabled', False)
        return False

    def get_weather_push_subscribers(self) -> list:
        """
        获取所有订阅天气推送的用户列表

        Returns:
            list: 订阅用户的openid列表
        """
        vip_users = self.get_all_vip_users()
        subscribers = []

        for openid, vip_info in vip_users.items():
            if vip_info.get('weather_push_enabled', False):
                subscribers.append(openid)

        return subscribers

    # ==================== 每日首次互动检测 ==================== #

    def is_first_interaction_today(self, openid: str) -> bool:
        """
        检查用户今日是否为首次互动

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否为今日首次互动
        """
        import time

        today = time.strftime('%Y-%m-%d')

        # 获取用户的每日互动记录
        daily_interactions = self.data_manager.load_data('daily_interactions', {})

        # 检查今天是否已有互动记录
        user_interactions = daily_interactions.get(openid, {})
        last_interaction_date = user_interactions.get('last_date', '')

        return last_interaction_date != today

    def record_daily_interaction(self, openid: str) -> bool:
        """
        记录用户今日的互动

        Args:
            openid: 用户的openid

        Returns:
            bool: 记录是否成功
        """
        import time

        today = time.strftime('%Y-%m-%d')

        def update_interactions(current_data):
            if current_data is None:
                current_data = {}

            # 更新用户的互动记录
            current_data[openid] = {
                'last_date': today,
                'last_time': time.strftime('%H:%M:%S'),
            }

            # 清理过期的记录（只保留今天的）
            # 避免数据文件无限增长
            keys_to_remove = []
            for uid, info in current_data.items():
                if info.get('last_date', '') != today:
                    keys_to_remove.append(uid)

            for uid in keys_to_remove:
                del current_data[uid]

            return current_data

        return self.data_manager.update_data('daily_interactions', update_interactions, {})

    def check_and_record_first_interaction(self, openid: str) -> bool:
        """
        检查并记录用户今日首次互动（原子操作）

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否为今日首次互动
        """
        is_first = self.is_first_interaction_today(openid)
        if is_first:
            self.record_daily_interaction(openid)
        return is_first

    # ==================== 签到积分系统 ==================== #

    def get_user_checkin_data(self, openid: str) -> Dict:
        """
        获取用户签到数据

        Args:
            openid: 用户的openid

        Returns:
            Dict: 用户签到数据
        """
        checkin_data = self.data_manager.load_data('checkin_data', {})
        return checkin_data.get(
            openid,
            {
                'total_points': 0,
                'total_checkins': 0,
                'consecutive_days': 0,
                'last_checkin_date': '',
                'checkin_history': [],
            },
        )

    def do_checkin(self, openid: str) -> Dict:
        """
        执行签到操作

        Args:
            openid: 用户的openid

        Returns:
            Dict: 签到结果
                - success: bool, 是否成功
                - is_already: bool, 今日是否已签到
                - points_earned: int, 本次获得积分
                - bonus_points: int, 连续签到奖励积分
                - total_points: int, 当前总积分
                - consecutive_days: int, 连续签到天数
                - is_vip_bonus: bool, 是否获得VIP双倍奖励
        """
        import time
        from datetime import datetime, timedelta

        today = time.strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        result = {
            'success': False,
            'is_already': False,
            'points_earned': 0,
            'bonus_points': 0,
            'total_points': 0,
            'consecutive_days': 0,
            'is_vip_bonus': False,
            'total_checkins': 0,
        }

        # 检查是否是VIP用户（VIP用户积分翻倍）
        is_vip = self.is_vip_user(openid)

        def update_checkin(current_data):
            nonlocal result

            if current_data is None:
                current_data = {}

            # 获取用户当前签到数据
            user_data = current_data.get(
                openid,
                {
                    'total_points': 0,
                    'total_checkins': 0,
                    'consecutive_days': 0,
                    'last_checkin_date': '',
                    'checkin_history': [],
                },
            )

            last_date = user_data.get('last_checkin_date', '')

            # 检查今日是否已签到
            if last_date == today:
                result['is_already'] = True
                result['total_points'] = user_data['total_points']
                result['consecutive_days'] = user_data['consecutive_days']
                result['total_checkins'] = user_data['total_checkins']
                return current_data

            # 计算连续签到天数
            if last_date == yesterday:
                # 连续签到
                consecutive_days = user_data.get('consecutive_days', 0) + 1
            else:
                # 断签，重新计算
                consecutive_days = 1

            # 基础积分
            base_points = 10

            # 连续签到奖励（每7天额外奖励）
            bonus_points = 0
            if consecutive_days % 7 == 0:
                bonus_points = 50  # 每满7天奖励50积分
            elif consecutive_days % 3 == 0:
                bonus_points = 20  # 每满3天奖励20积分

            # 连续签到加成（连续天数 * 2，最高20）
            streak_bonus = min(consecutive_days * 2, 20)
            base_points += streak_bonus

            # VIP双倍积分
            if is_vip:
                base_points *= 2
                bonus_points *= 2
                result['is_vip_bonus'] = True

            total_earned = base_points + bonus_points

            # 更新用户数据
            user_data['total_points'] = user_data.get('total_points', 0) + total_earned
            user_data['total_checkins'] = user_data.get('total_checkins', 0) + 1
            user_data['consecutive_days'] = consecutive_days
            user_data['last_checkin_date'] = today

            # 记录签到历史（只保留最近30条）
            if 'checkin_history' not in user_data:
                user_data['checkin_history'] = []

            user_data['checkin_history'].append(
                {
                    'date': today,
                    'time': time.strftime('%H:%M:%S'),
                    'points': total_earned,
                    'consecutive': consecutive_days,
                }
            )

            if len(user_data['checkin_history']) > 30:
                user_data['checkin_history'] = user_data['checkin_history'][-30:]

            current_data[openid] = user_data

            # 设置返回结果
            result['success'] = True
            result['points_earned'] = base_points
            result['bonus_points'] = bonus_points
            result['total_points'] = user_data['total_points']
            result['consecutive_days'] = consecutive_days
            result['total_checkins'] = user_data['total_checkins']

            return current_data

        self.data_manager.update_data('checkin_data', update_checkin, {})

        # 更新统计
        if result['success']:
            self.update_statistics('checkin')

        return result

    def get_points_ranking(self, limit: int = 10) -> list:
        """
        获取积分排行榜

        Args:
            limit: 返回数量限制

        Returns:
            list: 排行榜列表，每项包含 openid, display_name, total_points, total_checkins
        """
        checkin_data = self.data_manager.load_data('checkin_data', {})

        # 构建排行榜
        ranking = []
        for openid, data in checkin_data.items():
            # 获取VIP信息
            vip_info = self.get_vip_info(openid)
            # 使用昵称系统获取显示名称
            display_name = self.get_user_display_name(openid)

            ranking.append(
                {
                    'openid': openid,
                    'display_name': display_name,
                    'is_vip': vip_info is not None,
                    'total_points': data.get('total_points', 0),
                    'total_checkins': data.get('total_checkins', 0),
                    'consecutive_days': data.get('consecutive_days', 0),
                }
            )

        # 按积分降序排序
        ranking.sort(key=lambda x: x['total_points'], reverse=True)

        return ranking[:limit]

    def get_user_rank(self, openid: str) -> Dict:
        """
        获取用户在排行榜中的排名

        Args:
            openid: 用户的openid

        Returns:
            Dict: 包含排名信息
                - rank: int, 排名（从1开始）
                - total_users: int, 总参与人数
        """
        checkin_data = self.data_manager.load_data('checkin_data', {})

        if openid not in checkin_data:
            return {'rank': 0, 'total_users': len(checkin_data)}

        user_points = checkin_data[openid].get('total_points', 0)

        # 计算排名
        rank = 1
        for uid, data in checkin_data.items():
            if data.get('total_points', 0) > user_points:
                rank += 1

        return {'rank': rank, 'total_users': len(checkin_data)}

    def add_points(self, openid: str, points: int, reason: str = '') -> bool:
        """
        给用户增加积分（用于奖励等场景）

        Args:
            openid: 用户的openid
            points: 增加的积分（可以为负数扣除积分）
            reason: 原因说明

        Returns:
            bool: 是否成功
        """
        import time

        def update_checkin(current_data):
            if current_data is None:
                current_data = {}

            if openid not in current_data:
                current_data[openid] = {
                    'total_points': 0,
                    'total_checkins': 0,
                    'consecutive_days': 0,
                    'last_checkin_date': '',
                    'checkin_history': [],
                    'points_log': [],
                }

            user_data = current_data[openid]
            user_data['total_points'] = max(0, user_data.get('total_points', 0) + points)

            # 记录积分变动日志
            if 'points_log' not in user_data:
                user_data['points_log'] = []

            user_data['points_log'].append(
                {
                    'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'points': points,
                    'reason': reason,
                    'balance': user_data['total_points'],
                }
            )

            # 只保留最近50条日志
            if len(user_data['points_log']) > 50:
                user_data['points_log'] = user_data['points_log'][-50:]

            current_data[openid] = user_data
            return current_data

        return self.data_manager.update_data('checkin_data', update_checkin, {})

    def deduct_points(self, openid: str, points: int, reason: str = '') -> Dict:
        """
        扣除用户积分（用于兑换等场景）

        Args:
            openid: 用户的openid
            points: 扣除的积分（正数）
            reason: 原因说明

        Returns:
            Dict: 结果
                - success: bool, 是否成功
                - current_points: int, 当前余额
                - message: str, 消息
        """
        user_data = self.get_user_checkin_data(openid)
        current_points = user_data.get('total_points', 0)

        if current_points < points:
            return {
                'success': False,
                'current_points': current_points,
                'message': f'积分不足，当前积分：{current_points}，需要：{points}',
            }

        self.add_points(openid, -points, reason)

        return {
            'success': True,
            'current_points': current_points - points,
            'message': f'成功扣除{points}积分',
        }

    # ==================== 用户昵称管理 ==================== #

    def set_user_nickname(self, openid: str, nickname: str) -> bool:
        """
        设置用户昵称

        Args:
            openid: 用户的openid
            nickname: 昵称

        Returns:
            bool: 是否成功
        """
        import time

        def update_users(current_users):
            if current_users is None:
                current_users = {}

            if openid not in current_users:
                current_users[openid] = {}

            current_users[openid]['nickname'] = nickname
            current_users[openid]['nickname_set_time'] = time.strftime('%Y-%m-%d %H:%M:%S')

            return current_users

        success = self.data_manager.update_data(self.users_file, update_users, {})
        if success:
            print(f'用户 {openid} 昵称已设置为: {nickname}')
        return success

    def get_user_nickname(self, openid: str) -> str:
        """
        获取用户昵称

        Args:
            openid: 用户的openid

        Returns:
            str: 用户昵称，未设置时返回默认昵称
        """
        users = self.data_manager.load_data(self.users_file, {})
        user_info = users.get(openid, {})

        nickname = user_info.get('nickname')
        if nickname:
            return nickname

        # 如果没有设置昵称，检查是否是VIP用户
        vip_info = self.get_vip_info(openid)
        if vip_info:
            # VIP用户使用VIP-XXXX作为默认昵称
            return vip_info.get('vip_id', f'用户{openid[:6]}')

        # 普通用户使用默认昵称
        return f'用户{openid[:6]}'

    def get_user_display_name(self, openid: str) -> str:
        """
        获取用户显示名称（用于排行榜等场景）
        优先使用自定义昵称，其次使用VIP ID，最后使用默认名称

        Args:
            openid: 用户的openid

        Returns:
            str: 显示名称
        """
        return self.get_user_nickname(openid)

    def has_custom_nickname(self, openid: str) -> bool:
        """
        检查用户是否已设置自定义昵称

        Args:
            openid: 用户的openid

        Returns:
            bool: 是否已设置自定义昵称
        """
        users = self.data_manager.load_data(self.users_file, {})
        user_info = users.get(openid, {})
        return 'nickname' in user_info and user_info['nickname']


# 全局实例
data_manager = JSONDataManager()
user_data_manager = UserDataManager()
