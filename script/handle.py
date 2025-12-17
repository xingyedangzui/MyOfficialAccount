# -*- coding: utf-8 -*-
# 微信消息处理模块

import hashlib
import web
import receive
from xml_templates import WeChatXMLTemplate
import consts
from data_manager import user_data_manager, data_manager


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

        # 根据用户输入生成回复内容
        reply_content = self._generate_text_reply(toUser, user_content)

        # 检查是否有新菜谱通知需要附加
        reply_content = self._append_recipe_notification(toUser, reply_content)

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
        生成默认回复

        Args:
            user_openid: 用户的OpenID
            user_content: 用户发送的消息内容
            content_lower: 小写形式的消息内容

        Returns:
            str: 默认回复内容
        """
        is_vip = user_data_manager.is_vip_user(user_openid)
        vip_prefix = consts.VIP_PREFIX if is_vip else ''

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
        recipe_name = session.get('recipe_name', '')

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
        快捷记录菜谱（VIP专属）- 进入分类选择流程

        Args:
            user_openid: 用户的OpenID
            recipe_content: 菜谱内容

        Returns:
            str: 回复消息
        """
        # 检查是否是VIP用户
        if not user_data_manager.is_vip_user(user_openid):
            return consts.RECIPE_VIP_ONLY

        # 解析菜名（用于提示）
        lines = recipe_content.strip().split('\n')
        recipe_name = lines[0].strip()
        if '：' in recipe_name:
            recipe_name = recipe_name.split('：', 1)[1].strip()
        elif ':' in recipe_name:
            recipe_name = recipe_name.split(':', 1)[1].strip()

        # 保存菜谱内容到会话，等待用户选择分类
        user_data_manager.set_user_session_state(
            user_openid,
            consts.SessionState.WAITING_RECIPE_CATEGORY,
            {'recipe_content': recipe_content, 'recipe_name': recipe_name},
        )

        print(f'用户 {user_openid} 快捷输入菜谱: {recipe_name}，等待选择分类')
        return consts.RECIPE_CATEGORY_PROMPT.format(recipe_name=recipe_name)

    def _handle_view_recipe_list(self, user_openid):
        """
        处理查看菜谱列表

        Args:
            user_openid: 用户的OpenID

        Returns:
            str: 回复消息
        """
        recipe_list = user_data_manager.get_recipe_list()

        if not recipe_list:
            return consts.RECIPE_LIST_EMPTY

        # 构建菜谱列表文本
        recipe_lines = []
        for i, recipe in enumerate(recipe_list, 1):
            # 格式化日期，只显示月-日
            create_date = recipe.get('create_time_str', '')[:10]
            if create_date:
                # 转换为 MM-DD 格式
                parts = create_date.split('-')
                if len(parts) == 3:
                    create_date = f'{parts[1]}-{parts[2]}'

            # 获取分类标识
            category = recipe.get('category')
            if category == 'meat':
                category_icon = '🥩'
            elif category == 'veg':
                category_icon = '🥬'
            else:
                category_icon = '📝'

            recipe_lines.append(f'{i}. {category_icon} {recipe["name"]} ({create_date})')

        recipe_list_text = '\n'.join(recipe_lines)

        # 清除用户的菜谱通知（已查看）
        user_data_manager.clear_recipe_notifications(user_openid)

        return consts.RECIPE_LIST_TEMPLATE.format(
            recipe_list=recipe_list_text, total=len(recipe_list)
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
