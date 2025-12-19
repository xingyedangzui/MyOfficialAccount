# -*- coding: utf-8 -*-
# 微信消息处理模块

import hashlib
import web
import receive
from xml_templates import WeChatXMLTemplate
import consts
from data_manager import user_data_manager, data_manager
from weather_service import (
    get_free_weather_reply,
    get_weather_by_location,
    get_smart_weather_reply,
    smart_weather_service,
    get_clothing_advice,
)
from ai_service import get_ai_reply, clear_user_conversation, is_ai_enabled


class Handle(object):
    def __init__(self):
        pass

    def GET(self):
        """处理微信GET请求（服务器验证）"""
        try:
            data = web.input()
            if len(data) == 0:
                return 'hello, this is handle view'

            # 提取验证参数
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = consts.TOKEN  # 应该从配置文件读取

            print(f'微信服务器验证: signature={signature}, timestamp={timestamp}, nonce={nonce}')

            # 验证签名
            if self._validate_signature(signature, timestamp, nonce, token):
                print('签名验证成功')
                return echostr
            else:
                print('签名验证失败')
                return 'signature validation failed'

        except Exception as e:
            print(f'GET请求处理异常: {str(e)}')
            return 'error'

    def POST(self):
        """处理微信POST请求"""
        try:
            # 解析请求数据
            recMsg = self._parse_request_data()
            if not recMsg:
                return 'success'

            # 根据消息类型分发处理
            return self._dispatch_message(recMsg)

        except Exception as e:
            return self._handle_exception(e)

    def _parse_request_data(self):
        """解析微信请求数据"""
        try:
            webData = web.data()
            print('Handle Post webdata is:\n', webData)

            # 确保webData是字符串格式
            if isinstance(webData, bytes):
                webData = webData.decode('utf-8')

            # 解析XML消息
            return receive.parse_xml(webData)
        except Exception as e:
            print(f'解析请求数据异常: {str(e)}')
            return None

    def _dispatch_message(self, recMsg):
        """根据消息类型分发处理"""
        if isinstance(recMsg, receive.Msg):
            return self._handle_message(recMsg)
        elif isinstance(recMsg, receive.EventMsg):
            return self._handle_event(recMsg)
        else:
            print('不支持的消息类型：', getattr(recMsg, 'MsgType', 'Unknown'))
            return 'success'

    def _handle_message(self, recMsg):
        """处理普通消息"""
        msg_type = recMsg.MsgType

        if msg_type == consts.WeChatMsgType.TEXT:
            return self._handle_text_message(recMsg)
        elif msg_type == consts.WeChatMsgType.IMAGE:
            return self._handle_image_message(recMsg)
        elif msg_type == consts.WeChatMsgType.LOCATION:
            return self._handle_location_message(recMsg)
        else:
            print(f'不支持的消息类型: {msg_type}')
            return 'success'

    def _handle_event(self, recMsg):
        """处理事件消息"""
        event_type = recMsg.Event

        print(f'处理事件: {event_type}')
        print(f'用户OpenID: {recMsg.FromUserName}')

        if event_type == consts.WeChatEventType.SUBSCRIBE:
            return self._handle_subscribe_event(recMsg)
        elif event_type == consts.WeChatEventType.UNSUBSCRIBE:
            return self._handle_unsubscribe_event(recMsg)
        else:
            print(f'未处理的事件类型: {event_type}')
            return 'success'

    def _handle_exception(self, exception):
        """统一异常处理"""
        print(f'POST处理异常: {str(exception)}')
        import traceback

        traceback.print_exc()
        return 'success'  # 返回success避免微信重复推送

    def _handle_text_message(self, recMsg):
        """处理文本消息"""
        toUser = recMsg.FromUserName
        fromUser = recMsg.ToUserName
        user_content = str(recMsg.Content).strip()

        print(f'处理文本消息: 用户({toUser})发送: {user_content}')

        # 记录用户消息到数据库
        user_data_manager.record_user_message(toUser, 'text', user_content)

        # 更新统计数据
        user_data_manager.update_statistics('text_message')

        # 首先检查用户是否处于验证会话中
        verify_reply = self._handle_verify_session(toUser, user_content)
        if verify_reply:
            return self._create_text_response(toUser, fromUser, verify_reply)

        # 检查用户是否处于菜谱录入模式
        recipe_reply = self._handle_recipe_session(toUser, user_content)
        if recipe_reply:
            return self._create_text_response(toUser, fromUser, recipe_reply)

        # 检查用户是否处于天气城市设置模式
        weather_city_reply = self._handle_weather_city_session(toUser, user_content)
        if weather_city_reply:
            return self._create_text_response(toUser, fromUser, weather_city_reply)

        # 检查用户是否处于昵称设置模式
        nickname_reply = self._handle_nickname_session(toUser, user_content)
        if nickname_reply:
            return self._create_text_response(toUser, fromUser, nickname_reply)

        # 根据用户输入生成回复内容
        reply_content = self._generate_text_reply(toUser, user_content)

        # 检查是否有新菜谱通知需要附加
        reply_content = self._append_recipe_notification(toUser, reply_content)

        # 检查VIP用户每日首次互动，附加天气提醒
        reply_content = self._append_daily_weather_greeting(toUser, reply_content, user_content)

        return self._create_text_response(toUser, fromUser, reply_content)

    def _handle_verify_session(self, user_openid, user_content):
        """
        处理验证会话中的用户输入

        Args:
            user_openid: 用户的OpenID
            user_content: 用户发送的消息内容

        Returns:
            str: 如果用户在验证会话中返回验证结果消息，否则返回None
        """
        # 检查用户是否在验证会话中
        session = user_data_manager.get_user_session_state(user_openid)

        if not session or session.get('state') != consts.SessionState.WAITING_VERIFY:
            # 用户不在验证会话中，不处理
            return None

        # 检查会话是否过期
        import time

        if time.time() > session.get('expire_time', 0):
            # 会话已过期，清理会话
            user_data_manager.clear_user_session_state(user_openid)
            print(f'用户 {user_openid} 的验证会话已过期')
            return consts.SECRET_CODE_EXPIRED

        # 用户发送取消
        if user_content in ['取消', '退出', '返回']:
            user_data_manager.clear_user_session_state(user_openid)
            print(f'用户 {user_openid} 取消了验证')
            return consts.VERIFY_CANCELLED

        # 用户在验证会话中，检查输入的是否是正确的暗号
        if user_content == consts.SECRET_CODE:
            print(f'用户 {user_openid} 输入了正确的暗号')

            # 结束验证会话
            user_data_manager.clear_user_session_state(user_openid)

            # 调用VIP验证和保存
            result = user_data_manager.verify_and_save_vip(user_openid)

            if result['is_new']:
                # 新VIP用户
                reply = consts.VIP_WELCOME_MESSAGE.format(
                    vip_id=result['vip_id'], verify_time=result['verify_time']
                )
                print(f'新VIP用户验证成功: {user_openid} -> {result["vip_id"]}')
            else:
                # 已经是VIP用户
                reply = consts.ALREADY_VIP_MESSAGE.format(
                    vip_id=result['vip_id'], verify_time=result['verify_time']
                )
                print(f'用户 {user_openid} 已是VIP: {result["vip_id"]}')

            return reply
        else:
            # 暗号错误
            print(f'用户 {user_openid} 输入了错误的暗号: {user_content}')
            return consts.SECRET_CODE_WRONG

    def _generate_text_reply(self, user_openid, user_content):
        """根据用户输入生成回复内容"""
        # 统一转换为小写用于关键词匹配
        content_lower = user_content.lower()

        # ==================== 1. 自定义回复规则（最高优先级） ==================== #
        custom_reply = self._check_custom_reply_rules(user_content)
        if custom_reply:
            return custom_reply

        # ==================== 2. 精确匹配命令 ==================== #
        # 验证相关关键词
        if content_lower in consts.Commands.VERIFY_KEYWORDS:
            return self._handle_verify_keyword(user_openid)

        # 帮助菜单关键词
        if content_lower in consts.Commands.HELP_KEYWORDS:
            return consts.HELP_MESSAGE

        # 菜谱功能关键词
        if user_content == consts.Commands.RECIPE_MENU:
            return consts.RECIPE_MENU_MESSAGE
        if user_content == consts.Commands.RECIPE_VIEW_LIST:
            return self._handle_view_recipe_list(user_openid)
        if user_content == consts.Commands.RECIPE_ADD:
            return self._handle_start_recipe_input(user_openid)
        if user_content == consts.Commands.RECIPE_RANDOM:
            return self._handle_random_recipe()

        # 天气功能关键词
        if user_content in consts.Commands.WEATHER_KEYWORDS:
            return self._handle_weather_keyword(user_openid)

        # 更换天气城市关键词
        if user_content in consts.Commands.WEATHER_CHANGE_CITY:
            return self._handle_change_weather_city(user_openid)

        # 天气推送订阅相关命令
        if user_content in consts.WeatherPushCommands.SUBSCRIBE:
            return self._handle_weather_push_subscribe(user_openid)
        if user_content in consts.WeatherPushCommands.UNSUBSCRIBE:
            return self._handle_weather_push_unsubscribe(user_openid)
        if user_content in consts.WeatherPushCommands.STATUS:
            return self._handle_weather_push_status(user_openid)

        # 签到积分相关命令
        if user_content in consts.Commands.CHECKIN_KEYWORDS:
            return self._handle_checkin(user_openid)
        if user_content in consts.Commands.POINTS_KEYWORDS:
            return self._handle_my_points(user_openid)
        if user_content in consts.Commands.RANKING_KEYWORDS:
            return self._handle_points_ranking(user_openid)
        if user_content in consts.Commands.CHECKIN_HELP_KEYWORDS:
            return consts.CHECKIN_HELP

        # 昵称相关命令
        if user_content in consts.Commands.SET_NICKNAME_KEYWORDS:
            return self._handle_set_nickname(user_openid)
        if user_content in consts.Commands.MY_NICKNAME_KEYWORDS:
            return self._handle_my_nickname(user_openid)

        # ==================== 3. 前缀匹配命令 ==================== #
        # 快捷记录菜谱：记录菜谱 + 内容（如 "记录菜谱 红烧肉"）
        if user_content.startswith(consts.Commands.RECIPE_ADD_PREFIX):
            recipe_content = user_content[len(consts.Commands.RECIPE_ADD_PREFIX) :].strip()
            if recipe_content:
                return self._handle_quick_add_recipe(user_openid, recipe_content)

        # 菜谱详情：菜谱 + 序号（如 "菜谱 1"）
        if user_content.startswith(consts.Commands.RECIPE_DETAIL_PREFIX):
            recipe_detail = self._parse_recipe_detail_command(user_content)
            if recipe_detail:
                return recipe_detail

        # 指定城市天气：天气 + 城市名（如 "天气 上海"）
        if user_content.startswith(consts.Commands.WEATHER_PREFIX):
            city_name = user_content[len(consts.Commands.WEATHER_PREFIX) :].strip()
            if city_name:
                return self._handle_weather_query(city_name)

        # ==================== 4. 模糊匹配命令 ==================== #
        # 查看VIP信息
        if consts.Commands.VIP_INFO_KEYWORD in content_lower:
            return self._handle_vip_info_query(user_openid)

        # ==================== 5. 默认回复（最低优先级） ==================== #
        return self._generate_default_reply(user_openid, user_content, content_lower)

    def _check_custom_reply_rules(self, user_content):
        """
        检查自定义回复规则

        Args:
            user_content: 用户发送的消息内容

        Returns:
            str: 匹配到的自定义回复，否则返回 None
        """
        reply_rules = data_manager.load_data('reply_rules', {})
        if user_content not in reply_rules:
            return None

        reply = reply_rules[user_content]
        # 支持动态时间替换
        if '{time}' in reply:
            import time

            reply = reply.replace('{time}', time.strftime('%Y-%m-%d %H:%M:%S'))
        return reply

    def _parse_recipe_detail_command(self, user_content):
        """
        解析菜谱详情命令（菜谱 + 序号）

        Args:
            user_content: 用户发送的消息内容

        Returns:
            str: 菜谱详情回复，解析失败返回 None
        """
        parts = user_content.split()
        if len(parts) != 2:
            return None

        try:
            index = int(parts[1])
            return self._handle_view_recipe_detail(index)
        except ValueError:
            return None

    def _handle_vip_info_query(self, user_openid):
        """
        处理VIP信息查询

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: VIP信息回复
        """
        vip_info = user_data_manager.get_vip_info(user_openid)
        if not vip_info:
            return consts.NOT_VIP_MESSAGE

        status = '✅ 有效' if vip_info['status'] == 'active' else '❌ 无效'
        return consts.VIP_INFO_MESSAGE.format(
            vip_id=vip_info['vip_id'],
            verify_time=vip_info['verify_time_str'],
            status=status,
        )

    def _generate_default_reply(self, user_openid, user_content, content_lower):
        """
        生成默认回复 - 优先使用AI回复

        Args:
            user_openid: 用户的OpenID
            user_content: 用户发送的消息内容
            content_lower: 小写形式的消息内容

        Returns:
            str: 默认回复内容
        """
        is_vip = user_data_manager.is_vip_user(user_openid)
        vip_prefix = consts.VIP_PREFIX if is_vip else ''

        # 清除对话历史命令
        if content_lower in ('清除对话', '重置对话', '新对话', '清空对话'):
            clear_user_conversation(user_openid)
            return '🔄 对话已重置！我们可以开始新的话题啦~ 😊'

        # 尝试使用AI回复
        if is_ai_enabled():
            try:
                print(f'[AI] 为用户 {user_openid[:8]}... 生成AI回复')
                ai_reply = get_ai_reply(user_content, user_id=user_openid)
                if ai_reply:
                    # VIP用户添加前缀
                    if is_vip:
                        return f'{vip_prefix}\n{ai_reply}'
                    return ai_reply
            except Exception as e:
                print(f'[AI] AI回复异常: {e}')

        # AI不可用时的备用回复
        # 问候语回复
        if any(keyword in content_lower for keyword in consts.Commands.GREETING_KEYWORDS):
            return consts.HELLO_REPLY.format(vip_prefix=vip_prefix)

        # 通用默认回复
        return consts.DEFAULT_REPLY.format(vip_prefix=vip_prefix)

    # ==================== 菜谱功能处理方法 ==================== #

    def _handle_recipe_session(self, user_openid, user_content):
        """
        处理菜谱录入会话中的用户输入

        Args:
            user_openid: 用户的OpenID
            user_content: 用户发送的消息内容

        Returns:
            str: 如果用户在菜谱录入会话中返回处理结果消息，否则返回None
        """
        # 检查用户会话状态
        session = user_data_manager.get_user_session_state(user_openid)
        if not session:
            return None

        state = session.get('state')

        # 处理等待菜谱内容的状态
        if state == consts.SessionState.WAITING_RECIPE:
            return self._handle_waiting_recipe_content(user_openid, user_content)

        # 处理等待选择分类的状态
        if state == consts.SessionState.WAITING_RECIPE_CATEGORY:
            return self._handle_waiting_recipe_category(user_openid, user_content, session)

        return None

    def _handle_waiting_recipe_content(self, user_openid, user_content):
        """处理等待菜谱内容输入"""
        # 用户发送取消
        if user_content in consts.Commands.CANCEL_KEYWORDS:
            user_data_manager.clear_user_session_state(user_openid)
            print(f'用户 {user_openid} 取消了菜谱录入')
            return consts.RECIPE_INPUT_CANCELLED

        # 解析菜名（用于提示）
        lines = user_content.strip().split('\n')
        recipe_name = lines[0].strip()
        if '：' in recipe_name:
            recipe_name = recipe_name.split('：', 1)[1].strip()
        elif ':' in recipe_name:
            recipe_name = recipe_name.split(':', 1)[1].strip()

        # 保存菜谱内容到会话，等待用户选择分类
        user_data_manager.set_user_session_state(
            user_openid,
            consts.SessionState.WAITING_RECIPE_CATEGORY,
            {'recipe_content': user_content, 'recipe_name': recipe_name},
        )

        print(f'用户 {user_openid} 输入菜谱: {recipe_name}，等待选择分类')
        return consts.RECIPE_CATEGORY_PROMPT.format(recipe_name=recipe_name)

    def _handle_waiting_recipe_category(self, user_openid, user_content, session):
        """处理等待选择菜谱分类"""
        # 用户发送取消
        if user_content in consts.Commands.CANCEL_KEYWORDS:
            user_data_manager.clear_user_session_state(user_openid)
            print(f'用户 {user_openid} 取消了菜谱录入')
            return consts.RECIPE_INPUT_CANCELLED

        # 解析用户选择的分类
        category = consts.RecipeCategory.get_category_by_keyword(user_content)
        if not category:
            return consts.RECIPE_CATEGORY_INVALID

        # 获取之前保存的菜谱内容
        recipe_content = session.get('recipe_content', '')

        # 保存菜谱（带分类）
        result = user_data_manager.add_recipe(user_openid, recipe_content, category)

        # 清除会话状态
        user_data_manager.clear_user_session_state(user_openid)

        if result['success']:
            category_display = consts.RecipeCategory.get_display_name(category)
            print(f'用户 {user_openid} 成功添加菜谱: {result["recipe_name"]} (分类: {category})')
            return consts.RECIPE_ADD_SUCCESS_WITH_CATEGORY.format(
                recipe_name=result['recipe_name'], category=category_display
            )
        else:
            return consts.RECIPE_ADD_FAILED

    def _handle_start_recipe_input(self, user_openid):
        """
        开始菜谱录入流程（VIP专属）

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 检查是否是VIP用户
        if not user_data_manager.is_vip_user(user_openid):
            return consts.RECIPE_VIP_ONLY

        # 设置用户会话状态为等待菜谱输入
        user_data_manager.set_user_session_state(user_openid, consts.SessionState.WAITING_RECIPE)

        print(f'用户 {user_openid} 进入菜谱录入模式')
        return consts.RECIPE_INPUT_PROMPT

    def _handle_quick_add_recipe(self, user_openid, recipe_content):
        """
        快捷记录菜谱（VIP专属）

        支持两种格式：
        1. "记录菜谱 红烧肉" - 需要后续选择分类
        2. "记录菜谱 红烧肉 荤" - 一步完成记录

        Args:
            user_openid: 用户的OpenID
            recipe_content: 菜谱内容（可能包含分类）

        Returns:
            str: 回复消息
        """
        # 检查是否是VIP用户
        if not user_data_manager.is_vip_user(user_openid):
            return consts.RECIPE_VIP_ONLY

        # 尝试解析是否包含分类（最后一个词）
        parts = recipe_content.strip().split()
        category = None
        actual_content = recipe_content

        if len(parts) >= 2:
            # 检查最后一个词是否是分类关键词
            last_word = parts[-1]
            category = consts.RecipeCategory.get_category_by_keyword(last_word)
            if category:
                # 去掉最后的分类词，剩下的是菜谱内容
                actual_content = ' '.join(parts[:-1])

        # 解析菜名
        lines = actual_content.strip().split('\n')
        recipe_name = lines[0].strip()
        if '：' in recipe_name:
            recipe_name = recipe_name.split('：', 1)[1].strip()
        elif ':' in recipe_name:
            recipe_name = recipe_name.split(':', 1)[1].strip()

        # 如果已经有分类，直接保存
        if category:
            result = user_data_manager.add_recipe(user_openid, actual_content, category)
            if result['success']:
                category_display = consts.RecipeCategory.get_display_name(category)
                print(
                    f'用户 {user_openid} 快捷添加菜谱成功: {result["recipe_name"]} (分类: {category})'
                )
                return consts.RECIPE_ADD_SUCCESS_WITH_CATEGORY.format(
                    recipe_name=result['recipe_name'], category=category_display
                )
            else:
                return consts.RECIPE_ADD_FAILED

        # 没有分类，进入分类选择流程
        user_data_manager.set_user_session_state(
            user_openid,
            consts.SessionState.WAITING_RECIPE_CATEGORY,
            {'recipe_content': actual_content, 'recipe_name': recipe_name},
        )

        print(f'用户 {user_openid} 快捷输入菜谱: {recipe_name}，等待选择分类')
        return consts.RECIPE_CATEGORY_PROMPT.format(recipe_name=recipe_name)

    def _handle_view_recipe_list(self, user_openid):
        """
        处理查看菜谱列表（分荤素展示）

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        recipe_list = user_data_manager.get_recipe_list()

        if not recipe_list:
            return consts.RECIPE_LIST_EMPTY

        # 按分类分组
        meat_recipes = []
        veg_recipes = []

        for i, recipe in enumerate(recipe_list, 1):
            # 格式化日期，只显示月-日
            create_date = recipe.get('create_time_str', '')[:10]
            if create_date:
                parts = create_date.split('-')
                if len(parts) == 3:
                    create_date = f'{parts[1]}-{parts[2]}'

            # 构建菜谱行文本（带序号）
            recipe_line = f'{i}. {recipe["name"]} ({create_date})'

            # 按分类归组
            category = recipe.get('category')
            if category == 'meat':
                meat_recipes.append(recipe_line)
            elif category == 'veg':
                veg_recipes.append(recipe_line)
            else:
                # 未分类的默认放到素菜（或可以单独处理）
                veg_recipes.append(recipe_line)

        # 构建分类列表文本
        meat_list = '\n'.join(meat_recipes) if meat_recipes else consts.RECIPE_CATEGORY_LIST_EMPTY
        veg_list = '\n'.join(veg_recipes) if veg_recipes else consts.RECIPE_CATEGORY_LIST_EMPTY

        # 清除用户的菜谱通知（已查看）
        user_data_manager.clear_recipe_notifications(user_openid)

        return consts.RECIPE_LIST_TEMPLATE.format(
            meat_list=meat_list, veg_list=veg_list, total=len(recipe_list)
        )

    def _handle_view_recipe_detail(self, index):
        """
        处理查看菜谱详情

        Args:
            index: 菜谱序号（从1开始）

        Returns:
            str: 回复消息
        """
        recipe = user_data_manager.get_recipe_by_index(index)

        if not recipe:
            return consts.RECIPE_INDEX_INVALID

        # 处理菜谱内容显示
        content = recipe.get('content', '')
        # 如果内容和名称相同，不显示内容
        if content.strip() == recipe['name'].strip():
            content_display = ''
        else:
            content_display = content

        return consts.RECIPE_DETAIL_TEMPLATE.format(
            recipe_name=recipe['name'],
            recipe_content=content_display,
            create_time=recipe.get('create_time_str', '未知'),
            creator=recipe.get('creator_name', '未知'),
        )

    def _handle_random_recipe(self):
        """
        处理随机菜谱 - 返回一荤一素组合

        Returns:
            str: 回复消息
        """
        # 获取一荤一素的随机组合
        recipe_pair = user_data_manager.get_random_recipe_pair()

        # 如果都没有菜谱
        if not recipe_pair['has_any']:
            return consts.RANDOM_RECIPE_ALL_EMPTY

        # 构建荤菜部分
        meat_recipe = recipe_pair['meat']
        if meat_recipe:
            meat_content = meat_recipe.get('content', '')
            if meat_content.strip() == meat_recipe['name'].strip():
                meat_content = ''
            meat_section = consts.RANDOM_RECIPE_MEAT_SECTION.format(
                recipe_name=meat_recipe['name'], recipe_content=meat_content
            )
        else:
            meat_section = consts.RANDOM_RECIPE_CATEGORY_EMPTY.format(category='荤')

        # 构建素菜部分
        veg_recipe = recipe_pair['veg']
        if veg_recipe:
            veg_content = veg_recipe.get('content', '')
            if veg_content.strip() == veg_recipe['name'].strip():
                veg_content = ''
            veg_section = consts.RANDOM_RECIPE_VEG_SECTION.format(
                recipe_name=veg_recipe['name'], recipe_content=veg_content
            )
        else:
            veg_section = consts.RANDOM_RECIPE_CATEGORY_EMPTY.format(category='素')

        return consts.RANDOM_RECIPE_PAIR_TEMPLATE.format(
            meat_section=meat_section, veg_section=veg_section
        )

    def _append_recipe_notification(self, user_openid, reply_content):
        """
        检查并附加新菜谱通知

        Args:
            user_openid: 用户的OpenID
            reply_content: 原始回复内容

        Returns:
            str: 附加通知后的回复内容
        """
        # 只对VIP用户检查通知
        if not user_data_manager.is_vip_user(user_openid):
            return reply_content

        # 获取未读通知
        notifications = user_data_manager.get_new_recipe_notifications(user_openid)

        if notifications:
            # 附加通知
            return reply_content + consts.NEW_RECIPE_NOTIFICATION.format(count=len(notifications))

        return reply_content

    def _append_daily_weather_greeting(self, user_openid, reply_content, user_content):
        """
        检查VIP用户每日首次互动，附加天气提醒

        Args:
            user_openid: 用户的OpenID
            reply_content: 原始回复内容
            user_content: 用户发送的消息（用于判断是否为天气查询）

        Returns:
            str: 附加天气提醒后的回复内容
        """
        # 只对已订阅天气推送的VIP用户生效
        if not user_data_manager.is_weather_push_subscribed(user_openid):
            return reply_content

        # 如果用户正在查询天气，不重复附加
        if user_content in consts.Commands.WEATHER_KEYWORDS:
            # 记录今日互动（天气查询也算互动）
            user_data_manager.record_daily_interaction(user_openid)
            return reply_content

        # 检查是否为今日首次互动
        is_first = user_data_manager.check_and_record_first_interaction(user_openid)
        if not is_first:
            return reply_content

        # 获取用户设置的城市
        user_city = user_data_manager.get_user_weather_city(user_openid)
        if not user_city:
            return reply_content

        # 获取天气信息
        try:
            city_name = user_city['city_name']
            weather_info = smart_weather_service.get_weather(city_name)

            if not weather_info or not weather_info.get('success'):
                print(f'[DailyWeather] 获取天气失败: {city_name}')
                return reply_content

            # 获取穿衣建议
            temp = weather_info.get('temp', 0)
            weather_desc = weather_info.get('text', '')
            clothing_advice = get_clothing_advice(temp, weather_desc)

            # 附加天气提醒
            weather_greeting = consts.DAILY_WEATHER_GREETING.format(
                city=city_name,
                temp=temp,
                weather=weather_desc,
                clothing_advice=clothing_advice,
            )

            print(f'[DailyWeather] 为用户 {user_openid[:8]}... 附加每日天气提醒')
            return reply_content + weather_greeting

        except Exception as e:
            print(f'[DailyWeather] 获取天气异常: {e}')
            return reply_content

    # ==================== 天气功能处理方法 ==================== #

    def _handle_weather_city_session(self, user_openid, user_content):
        """
        处理天气城市设置会话中的用户输入

        Args:
            user_openid: 用户的OpenID
            user_content: 用户发送的消息内容

        Returns:
            str: 如果用户在天气城市设置会话中返回处理结果消息，否则返回None
        """
        # 检查用户会话状态
        session = user_data_manager.get_user_session_state(user_openid)
        if not session:
            return None

        state = session.get('state')

        # 处理等待设置天气城市的状态
        if state != consts.SessionState.WAITING_WEATHER_CITY:
            return None

        # 用户发送取消
        if user_content in consts.Commands.CANCEL_KEYWORDS:
            user_data_manager.clear_user_session_state(user_openid)
            print(f'用户 {user_openid} 取消了天气城市设置')
            return consts.WEATHER_CITY_CANCELLED

        # 用户发送城市名称，保存并查询天气
        city_name = user_content.strip()
        city_pinyin = self._get_city_pinyin(city_name)

        # 保存用户的天气城市偏好
        user_data_manager.set_user_weather_city(user_openid, city_name, city_pinyin)

        # 清除会话状态
        user_data_manager.clear_user_session_state(user_openid)

        print(f'用户 {user_openid} 设置天气城市: {city_name}')

        # 查询并返回天气（使用智能API切换），同时显示设置成功消息
        try:
            weather_reply = get_smart_weather_reply(city_name, city_pinyin)
            success_msg = consts.WEATHER_CITY_SET_SUCCESS.format(city=city_name)
            return f'{success_msg}\n\n{weather_reply}'
        except Exception as e:
            print(f'设置城市后查询天气失败: {str(e)}')
            return consts.WEATHER_CITY_SET_SUCCESS.format(city=city_name)

    def _handle_weather_keyword(self, user_openid):
        """
        处理天气关键词 - 智能判断是否需要设置城市

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 检查用户是否已设置天气城市
        user_city = user_data_manager.get_user_weather_city(user_openid)

        if user_city:
            # 已设置城市，直接查询天气（使用智能API切换）
            city_name = user_city['city_name']
            city_pinyin = user_city['city_pinyin']
            print(f'用户 {user_openid} 查询已保存城市天气: {city_name}')

            try:
                # 使用智能天气服务（自动切换API）
                weather_reply = get_smart_weather_reply(city_name, city_pinyin)
                # 在天气信息后附加城市提示
                return f'📍 {city_name}\n\n{weather_reply}\n\n💡 发送「更换城市」可修改'
            except Exception as e:
                print(f'查询天气失败: {str(e)}')
                return '😢 获取天气信息失败，请稍后再试~'
        else:
            # 未设置城市，进入城市设置流程
            user_data_manager.set_user_session_state(
                user_openid, consts.SessionState.WAITING_WEATHER_CITY
            )
            print(f'用户 {user_openid} 首次使用天气功能，进入城市设置')
            return consts.WEATHER_FIRST_USE_PROMPT

    def _handle_change_weather_city(self, user_openid):
        """
        处理更换天气城市命令

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 获取当前城市
        user_city = user_data_manager.get_user_weather_city(user_openid)
        current_city = user_city['city_name'] if user_city else '未设置'

        # 进入城市设置流程
        user_data_manager.set_user_session_state(
            user_openid, consts.SessionState.WAITING_WEATHER_CITY
        )

        print(f'用户 {user_openid} 请求更换天气城市，当前城市: {current_city}')
        return consts.WEATHER_CHANGE_CITY_PROMPT.format(current_city=current_city)

    def _handle_weather_query(self, city=None):
        """
        处理天气查询（使用智能API切换）

        Args:
            city: 城市名称，为None则使用默认城市

        Returns:
            str: 天气信息回复
        """
        print(f'处理天气查询: 城市={city or "默认"}')

        try:
            # 使用智能天气服务（自动切换API）
            if city:
                # 将中文城市名转换为拼音
                city_pinyin = self._get_city_pinyin(city)
                reply = get_smart_weather_reply(city, city_pinyin)
            else:
                # 默认查询北京天气
                reply = get_smart_weather_reply('北京', 'Beijing')

            return reply
        except Exception as e:
            print(f'天气查询失败: {str(e)}')
            return '😢 获取天气信息失败，请稍后再试~'

    def _get_city_pinyin(self, city_name):
        """
        将常见中文城市名转换为拼音

        Args:
            city_name: 中文城市名

        Returns:
            str: 城市拼音或原名称
        """
        # 常见城市映射表
        city_map = {
            '北京': 'Beijing',
            '上海': 'Shanghai',
            '广州': 'Guangzhou',
            '深圳': 'Shenzhen',
            '杭州': 'Hangzhou',
            '成都': 'Chengdu',
            '重庆': 'Chongqing',
            '武汉': 'Wuhan',
            '西安': 'Xian',
            '南京': 'Nanjing',
            '天津': 'Tianjin',
            '苏州': 'Suzhou',
            '长沙': 'Changsha',
            '郑州': 'Zhengzhou',
            '青岛': 'Qingdao',
            '大连': 'Dalian',
            '厦门': 'Xiamen',
            '福州': 'Fuzhou',
            '济南': 'Jinan',
            '合肥': 'Hefei',
            '昆明': 'Kunming',
            '贵阳': 'Guiyang',
            '南宁': 'Nanning',
            '海口': 'Haikou',
            '三亚': 'Sanya',
            '拉萨': 'Lasa',
            '乌鲁木齐': 'Urumqi',
            '哈尔滨': 'Harbin',
            '长春': 'Changchun',
            '沈阳': 'Shenyang',
            '石家庄': 'Shijiazhuang',
            '太原': 'Taiyuan',
            '呼和浩特': 'Hohhot',
            '银川': 'Yinchuan',
            '兰州': 'Lanzhou',
            '西宁': 'Xining',
        }

        return city_map.get(city_name, city_name)

    # ==================== 天气推送订阅处理方法 ==================== #

    def _handle_weather_push_subscribe(self, user_openid):
        """
        处理天气推送订阅

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 检查是否是VIP用户
        if not user_data_manager.is_vip_user(user_openid):
            return consts.WEATHER_PUSH_VIP_ONLY

        # 检查是否已经订阅
        if user_data_manager.is_weather_push_subscribed(user_openid):
            user_city = user_data_manager.get_user_weather_city(user_openid)
            city_name = user_city['city_name'] if user_city else '未设置'
            return consts.WEATHER_PUSH_ALREADY_SUBSCRIBED.format(city=city_name)

        # 检查是否已设置天气城市
        user_city = user_data_manager.get_user_weather_city(user_openid)
        if not user_city:
            return consts.WEATHER_PUSH_SUBSCRIBE_NO_CITY

        # 订阅天气推送
        success = user_data_manager.subscribe_weather_push(user_openid)
        if success:
            print(f'用户 {user_openid} 订阅了天气推送，城市: {user_city["city_name"]}')
            return consts.WEATHER_PUSH_SUBSCRIBE_SUCCESS.format(city=user_city['city_name'])
        else:
            return '😢 订阅失败，请稍后重试~'

    def _handle_weather_push_unsubscribe(self, user_openid):
        """
        处理取消天气推送订阅

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 检查是否已订阅
        if not user_data_manager.is_weather_push_subscribed(user_openid):
            return consts.WEATHER_PUSH_NOT_SUBSCRIBED

        # 取消订阅
        success = user_data_manager.unsubscribe_weather_push(user_openid)
        if success:
            print(f'用户 {user_openid} 取消了天气推送订阅')
            return consts.WEATHER_PUSH_UNSUBSCRIBE_SUCCESS
        else:
            return '😢 取消订阅失败，请稍后重试~'

    def _handle_weather_push_status(self, user_openid):
        """
        处理天气推送状态查询

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 检查是否是VIP用户
        if not user_data_manager.is_vip_user(user_openid):
            return consts.WEATHER_PUSH_VIP_ONLY

        # 获取订阅状态
        is_subscribed = user_data_manager.is_weather_push_subscribed(user_openid)
        user_city = user_data_manager.get_user_weather_city(user_openid)
        city_name = user_city['city_name'] if user_city else '未设置'

        status = '✅ 已订阅' if is_subscribed else '❌ 未订阅'
        action_hint = (
            '发送「取消订阅天气」关闭推送' if is_subscribed else '发送「订阅天气」开启推送'
        )

        return consts.WEATHER_PUSH_STATUS.format(
            status=status, city=city_name, action_hint=action_hint
        )

    # ==================== 签到积分功能处理方法 ==================== #

    def _handle_checkin(self, user_openid):
        """
        处理签到命令

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 执行签到
        result = user_data_manager.do_checkin(user_openid)

        # 今日已签到
        if result['is_already']:
            return consts.CHECKIN_ALREADY.format(
                consecutive_days=result['consecutive_days'],
                total_points=result['total_points'],
                total_checkins=result['total_checkins'],
            )

        # 签到成功，构建回复消息
        # 奖励文本
        bonus_text = ''
        if result['bonus_points'] > 0:
            bonus_text = f' (+{result["bonus_points"]}奖励)'

        # VIP双倍提示
        vip_bonus_text = consts.CHECKIN_VIP_BONUS_TEXT if result['is_vip_bonus'] else ''

        # 连续签到提示
        streak_tip = self._get_streak_tip(result['consecutive_days'], result['bonus_points'])

        return consts.CHECKIN_SUCCESS.format(
            consecutive_days=result['consecutive_days'],
            points_earned=result['points_earned'],
            bonus_text=bonus_text,
            total_points=result['total_points'],
            total_checkins=result['total_checkins'],
            vip_bonus_text=vip_bonus_text,
            streak_tip=streak_tip,
        )

    def _get_streak_tip(self, consecutive_days, bonus_points):
        """
        获取连续签到提示

        Args:
            consecutive_days: 连续签到天数
            bonus_points: 已获得的奖励积分

        Returns:
            str: 提示文本
        """
        # 如果刚好获得了奖励
        if consecutive_days % 7 == 0 and bonus_points > 0:
            return consts.CHECKIN_BONUS_GOT_7
        if consecutive_days % 3 == 0 and bonus_points > 0:
            return consts.CHECKIN_BONUS_GOT_3

        # 计算距离下一个奖励还有多少天
        days_to_3 = 3 - (consecutive_days % 3)
        days_to_7 = 7 - (consecutive_days % 7)

        # 优先提示7天奖励
        if days_to_7 <= 3:
            return consts.CHECKIN_BONUS_TIP_7.format(days=days_to_7)
        else:
            return consts.CHECKIN_BONUS_TIP_3.format(days=days_to_3)

    def _handle_my_points(self, user_openid):
        """
        处理查询积分命令

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 获取用户签到数据
        checkin_data = user_data_manager.get_user_checkin_data(user_openid)

        # 获取用户排名
        rank_info = user_data_manager.get_user_rank(user_openid)

        # VIP状态提示
        is_vip = user_data_manager.is_vip_user(user_openid)
        vip_status = consts.POINTS_IS_VIP if is_vip else consts.POINTS_NOT_VIP

        return consts.MY_POINTS_INFO.format(
            total_points=checkin_data.get('total_points', 0),
            consecutive_days=checkin_data.get('consecutive_days', 0),
            total_checkins=checkin_data.get('total_checkins', 0),
            rank=rank_info['rank'] if rank_info['rank'] > 0 else '-',
            total_users=rank_info['total_users'],
            vip_status=vip_status,
        )

    def _handle_points_ranking(self, user_openid):
        """
        处理积分排行榜命令

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 获取排行榜
        ranking = user_data_manager.get_points_ranking(10)

        if not ranking:
            return '🏆 积分排行榜\n\n暂无数据~\n\n💡 发送「签到」开始积累积分吧！'

        # 构建排行榜列表
        ranking_lines = []
        for i, item in enumerate(ranking, 1):
            if item['is_vip']:
                line = consts.RANKING_LINE_VIP.format(
                    rank=i,
                    name=item['display_name'],
                    points=item['total_points'],
                    checkins=item['total_checkins'],
                )
            else:
                line = consts.RANKING_LINE.format(
                    rank=i,
                    name=item['display_name'],
                    points=item['total_points'],
                    checkins=item['total_checkins'],
                )
            ranking_lines.append(line)

        ranking_list = '\n'.join(ranking_lines)

        # 获取当前用户信息
        user_checkin_data = user_data_manager.get_user_checkin_data(user_openid)
        user_rank = user_data_manager.get_user_rank(user_openid)

        return consts.POINTS_RANKING.format(
            ranking_list=ranking_list,
            my_rank=user_rank['rank'] if user_rank['rank'] > 0 else '-',
            my_points=user_checkin_data.get('total_points', 0),
        )

    # ==================== 昵称功能处理方法 ==================== #

    def _handle_nickname_session(self, user_openid, user_content):
        """
        处理昵称设置会话中的用户输入

        Args:
            user_openid: 用户的OpenID
            user_content: 用户发送的消息内容

        Returns:
            str: 如果用户在昵称设置会话中返回处理结果消息，否则返回None
        """
        # 检查用户会话状态
        session = user_data_manager.get_user_session_state(user_openid)
        if not session:
            return None

        state = session.get('state')

        # 处理等待设置昵称的状态
        if state != consts.SessionState.WAITING_NICKNAME:
            return None

        # 用户发送取消
        if user_content in consts.Commands.CANCEL_KEYWORDS:
            user_data_manager.clear_user_session_state(user_openid)
            print(f'用户 {user_openid} 取消了昵称设置')
            return consts.NICKNAME_SET_CANCELLED

        # 验证昵称格式
        nickname = user_content.strip()

        # 检查长度
        if len(nickname) < consts.NICKNAME_MIN_LENGTH or len(nickname) > consts.NICKNAME_MAX_LENGTH:
            return consts.NICKNAME_INVALID.format(
                min_len=consts.NICKNAME_MIN_LENGTH, max_len=consts.NICKNAME_MAX_LENGTH
            )

        # 检查是否包含特殊字符（只允许中文、英文、数字、下划线）
        import re

        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$', nickname):
            return consts.NICKNAME_INVALID.format(
                min_len=consts.NICKNAME_MIN_LENGTH, max_len=consts.NICKNAME_MAX_LENGTH
            )

        # 保存昵称
        success = user_data_manager.set_user_nickname(user_openid, nickname)

        # 清除会话状态
        user_data_manager.clear_user_session_state(user_openid)

        if success:
            print(f'用户 {user_openid} 设置昵称成功: {nickname}')
            return consts.NICKNAME_SET_SUCCESS.format(nickname=nickname)
        else:
            return '😢 昵称设置失败，请稍后重试~'

    def _handle_set_nickname(self, user_openid):
        """
        处理设置昵称命令

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 获取当前昵称
        current_nickname = user_data_manager.get_user_nickname(user_openid)

        # 设置用户会话状态为等待输入昵称
        user_data_manager.set_user_session_state(user_openid, consts.SessionState.WAITING_NICKNAME)

        print(f'用户 {user_openid} 进入昵称设置模式，当前昵称: {current_nickname}')
        return consts.NICKNAME_SET_PROMPT.format(
            current_nickname=current_nickname,
            min_len=consts.NICKNAME_MIN_LENGTH,
            max_len=consts.NICKNAME_MAX_LENGTH,
        )

    def _handle_my_nickname(self, user_openid):
        """
        处理查看昵称命令

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        # 获取当前昵称
        nickname = user_data_manager.get_user_nickname(user_openid)

        return consts.NICKNAME_INFO.format(nickname=nickname)

    def _handle_verify_keyword(self, user_openid):
        """
        处理验证关键词

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        import time

        # 检查用户是否已经是VIP
        if user_data_manager.is_vip_user(user_openid):
            vip_info = user_data_manager.get_vip_info(user_openid)
            return consts.ALREADY_VIP_MESSAGE.format(
                vip_id=vip_info['vip_id'], verify_time=vip_info['verify_time_str']
            )

        # 开始验证会话，设置会话状态和过期时间
        expire_time = time.time() + consts.SECRET_CODE_TIMEOUT
        user_data_manager.set_user_session_state(
            user_openid, consts.SessionState.WAITING_VERIFY, {'expire_time': expire_time}
        )

        print(f'用户 {user_openid} 通过关键词开始身份验证流程')
        return consts.SECRET_CODE_PROMPT

    def _handle_location_message(self, recMsg):
        """处理位置消息 - 自动返回该位置的天气信息，并可保存城市偏好"""
        toUser = recMsg.FromUserName
        fromUser = recMsg.ToUserName

        # 获取位置信息
        latitude = getattr(recMsg, 'Location_X', None)  # 纬度
        longitude = getattr(recMsg, 'Location_Y', None)  # 经度
        label = getattr(recMsg, 'Label', None)  # 地址描述

        print(f'处理位置消息: 用户({toUser})发送位置')
        print(f'  纬度: {latitude}, 经度: {longitude}')
        print(f'  地址: {label}')

        # 记录位置消息
        location_info = f'位置消息 - 纬度:{latitude}, 经度:{longitude}, 地址:{label}'
        user_data_manager.record_user_message(toUser, 'location', location_info)

        # 更新统计数据
        user_data_manager.update_statistics('location_message')

        # 检查用户是否处于天气城市设置模式
        session = user_data_manager.get_user_session_state(toUser)
        is_setting_city = (
            session and session.get('state') == consts.SessionState.WAITING_WEATHER_CITY
        )

        # 从地址标签中提取城市名称
        city_name = self._extract_city_from_label(label)

        # 如果用户在设置城市模式，保存城市偏好
        if is_setting_city and city_name:
            city_pinyin = self._get_city_pinyin(city_name)
            user_data_manager.set_user_weather_city(toUser, city_name, city_pinyin)
            user_data_manager.clear_user_session_state(toUser)
            print(f'用户 {toUser} 通过位置设置天气城市: {city_name}')

        # 获取该位置的天气信息
        try:
            weather_reply = get_weather_by_location(latitude, longitude, label)

            # 如果是设置城市模式，附加设置成功消息
            if is_setting_city and city_name:
                success_msg = consts.WEATHER_CITY_SET_SUCCESS.format(city=city_name)
                weather_reply = f'{success_msg}\n\n{weather_reply}'

            return self._create_text_response(toUser, fromUser, weather_reply)
        except Exception as e:
            print(f'根据位置获取天气失败: {str(e)}')
            # 即使天气查询失败，如果城市设置成功也要通知用户
            if is_setting_city and city_name:
                return self._create_text_response(
                    toUser, fromUser, consts.WEATHER_CITY_SET_SUCCESS.format(city=city_name)
                )
            return self._create_text_response(toUser, fromUser, '😢 获取天气信息失败，请稍后再试~')

    def _extract_city_from_label(self, label):
        """
        从地址标签中提取城市名称

        Args:
            label: 地址描述，如 "北京市朝阳区xxx"

        Returns:
            str: 城市名称，提取失败返回None
        """
        if not label:
            return None

        # 尝试提取城市名
        # 常见格式：省+市、直辖市、自治区等
        import re

        # 直辖市
        direct_cities = ['北京', '上海', '天津', '重庆']
        for city in direct_cities:
            if city in label:
                return city

        # 匹配 xx市
        city_match = re.search(r'([\u4e00-\u9fa5]{2,4})市', label)
        if city_match:
            return city_match.group(1)

        # 匹配 xx区（可能是直辖市的区）
        district_match = re.search(r'([\u4e00-\u9fa5]{2,4})区', label)
        if district_match:
            # 检查是否是直辖市的区
            for city in direct_cities:
                if city in label:
                    return city

        return None

    def _handle_image_message(self, recMsg):
        """处理图片消息"""
        toUser = recMsg.FromUserName
        fromUser = recMsg.ToUserName
        media_id = getattr(recMsg, 'MediaId', '')

        print(f'处理图片消息: 用户({toUser})发送了图片, MediaId: {media_id}')

        # 记录图片消息
        user_data_manager.record_user_message(toUser, 'image', f'图片消息 MediaId: {media_id}')

        # 更新统计数据
        user_data_manager.update_statistics('image_message')

        return self._create_text_response(toUser, fromUser, consts.IMAGE_REPLY)

    def _handle_subscribe_event(self, recMsg):
        """处理关注事件"""
        toUser = recMsg.FromUserName
        fromUser = recMsg.ToUserName
        welcome_content = consts.WELCOM_MESSAGE
        create_time = getattr(recMsg, 'CreateTime', '')

        print('=== 新用户关注事件 ===')
        print(f'新用户OpenID: {toUser}')
        print(f'欢迎消息: {welcome_content}')

        # 保存用户关注信息
        import time

        user_info = {
            'status': 'subscribed',
            'subscribe_time': create_time,
            'subscribe_time_str': time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(int(create_time))
            )
            if create_time
            else time.strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'wechat_official_account',
            'first_subscribe': True,
        }

        # 检查是否是老用户重新关注
        existing_user = user_data_manager.get_user_info(toUser)
        if existing_user:
            user_info['first_subscribe'] = False
            user_info['previous_unsubscribe_time'] = existing_user.get('unsubscribe_time', '')

        success = user_data_manager.save_user_info(toUser, user_info)
        if success:
            print(f'用户 {toUser} 关注信息已保存')

        # 更新统计数据
        user_data_manager.update_statistics('subscribe')

        print('=== 关注事件处理完成 ===')

        return self._create_text_response(toUser, fromUser, welcome_content)

    def _handle_unsubscribe_event(self, recMsg):
        """处理取消关注事件"""
        toUser = recMsg.FromUserName

        print(f'用户取消关注: {toUser}')

        # 保留用户数据，仅清除当前会话状态
        user_data_manager.clear_user_session_state(toUser)

        # 更新统计数据
        user_data_manager.update_statistics('unsubscribe')

        # 取消关注事件不需要回复消息
        return 'success'

    def _create_text_response(self, toUser, fromUser, content):
        """创建文本回复响应"""
        try:
            # 使用XML模板生成回复消息
            reply_str = WeChatXMLTemplate.text_reply(toUser, fromUser, content)

            # 设置正确的响应头
            web.header('Content-Type', 'application/xml; charset=utf-8')
            return reply_str
        except Exception as e:
            print(f'创建回复消息失败: {str(e)}')
            return 'success'

    def _validate_signature(self, signature, timestamp, nonce, token):
        """验证微信签名"""
        try:
            tmp_list = [token, timestamp, nonce]
            tmp_list.sort()
            tmp_str = ''.join(tmp_list)
            hashcode = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
            return hashcode == signature
        except Exception as e:
            print(f'签名验证异常: {str(e)}')
            return False
