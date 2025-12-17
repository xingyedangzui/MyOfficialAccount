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


# 全局实例
data_manager = JSONDataManager()
user_data_manager = UserDataManager()
