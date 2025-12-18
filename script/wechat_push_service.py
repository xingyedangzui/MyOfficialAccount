# -*- coding: utf-8 -*-
"""
微信公众号消息推送服务
用于群发消息和素材管理
"""

import json
import time
import requests
from typing import Optional, Dict

import consts


class WeChatPushService:
    """微信消息推送服务"""

    def __init__(self):
        self.appid = consts.WECHAT_APPID
        self.appsecret = consts.WECHAT_APPSECRET
        self.access_token = None
        self.token_expires_at = 0

    def _get_access_token(self) -> Optional[str]:
        """
        获取微信接口访问凭证
        access_token有效期为2小时，需要缓存使用

        Returns:
            str: access_token，失败返回None
        """
        # 检查缓存的token是否有效
        if self.access_token and time.time() < self.token_expires_at - 300:
            return self.access_token

        try:
            url = f'https://api.weixin.qq.com/cgi-bin/token'
            params = {
                'grant_type': 'client_credential',
                'appid': self.appid,
                'secret': self.appsecret,
            }
            response = requests.get(url, params=params, timeout=10)
            result = response.json()

            if 'access_token' in result:
                self.access_token = result['access_token']
                self.token_expires_at = time.time() + result.get('expires_in', 7200)
                print(f'[WeChatPush] 获取access_token成功')
                return self.access_token
            else:
                print(f'[WeChatPush] 获取access_token失败: {result}')
                return None

        except Exception as e:
            print(f'[WeChatPush] 获取access_token异常: {e}')
            return None

    def add_draft(
        self,
        title: str,
        thumb_media_id: str,
        content: str,
        author: str = '',
        digest: str = '',
        content_source_url: str = '',
        show_cover_pic: int = 0,
        need_open_comment: int = 0,
        only_fans_can_comment: int = 0,
    ) -> Optional[str]:
        """
        新建草稿（新版接口，替代已废弃的add_news）

        Args:
            title: 标题
            thumb_media_id: 封面图片的media_id
            content: 图文消息的具体内容（支持HTML）
            author: 作者
            digest: 图文消息的摘要
            content_source_url: 原文链接
            show_cover_pic: 是否显示封面（0不显示，1显示）
            need_open_comment: 是否打开评论（0不打开，1打开）
            only_fans_can_comment: 是否粉丝才可评论（0否，1是）

        Returns:
            str: media_id，失败返回None
        """
        access_token = self._get_access_token()
        if not access_token:
            return None

        try:
            url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}'

            articles = [
                {
                    'title': title,
                    'thumb_media_id': thumb_media_id,
                    'author': author,
                    'digest': digest,
                    'content': content,
                    'content_source_url': content_source_url,
                    'show_cover_pic': show_cover_pic,
                    'need_open_comment': need_open_comment,
                    'only_fans_can_comment': only_fans_can_comment,
                }
            ]

            data = {'articles': articles}

            response = requests.post(
                url,
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'},
                timeout=15,
            )
            result = response.json()

            if 'media_id' in result:
                print(f'[WeChatPush] 新建草稿成功: {result["media_id"]}')
                return result['media_id']
            else:
                print(f'[WeChatPush] 新建草稿失败: {result}')
                return None

        except Exception as e:
            print(f'[WeChatPush] 新建草稿异常: {e}')
            return None

    # 保留旧方法名作为别名，保持向后兼容
    def add_news_material(self, *args, **kwargs) -> Optional[str]:
        """旧接口别名，已废弃，请使用add_draft"""
        print('[WeChatPush] 警告: add_news接口已废弃，自动切换到draft/add')
        return self.add_draft(*args, **kwargs)

    def upload_permanent_image(self, image_path: str) -> Optional[str]:
        """
        上传永久图片素材（用于图文封面等）

        Args:
            image_path: 本地图片路径

        Returns:
            str: media_id，失败返回None
        """
        access_token = self._get_access_token()
        if not access_token:
            return None

        try:
            url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image'

            with open(image_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, files=files, timeout=30)

            result = response.json()

            if 'media_id' in result:
                print(f'[WeChatPush] 上传图片素材成功: {result["media_id"]}')
                return result['media_id']
            else:
                print(f'[WeChatPush] 上传图片素材失败: {result}')
                return None

        except Exception as e:
            print(f'[WeChatPush] 上传图片素材异常: {e}')
            return None

    def send_mass_message_by_tag(
        self, media_id: str, tag_id: int = None, is_to_all: bool = True, msg_type: str = 'mpnews'
    ) -> Optional[str]:
        """
        根据标签进行群发（订阅号每天可群发1条）

        Args:
            media_id: 素材的media_id
            tag_id: 群发到的标签的tag_id（可选，若不填则群发给所有用户）
            is_to_all: 是否群发给所有用户
            msg_type: 消息类型，'mpnews'为图文消息

        Returns:
            str: 消息ID（msg_id），失败返回None
        """
        access_token = self._get_access_token()
        if not access_token:
            return None

        try:
            url = f'https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={access_token}'

            data = {
                'filter': {'is_to_all': is_to_all},
                msg_type: {'media_id': media_id},
                'msgtype': msg_type,
                'send_ignore_reprint': 0,  # 0表示可以被转载，1表示不能转载
            }

            if tag_id is not None and not is_to_all:
                data['filter']['tag_id'] = tag_id

            response = requests.post(
                url,
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'},
                timeout=15,
            )
            result = response.json()

            if result.get('errcode', 0) == 0:
                msg_id = result.get('msg_id', '')
                print(f'[WeChatPush] 群发消息成功: msg_id={msg_id}')
                return str(msg_id)
            else:
                errcode = result.get('errcode')
                errmsg = result.get('errmsg', '')
                print(f'[WeChatPush] 群发消息失败: errcode={errcode}, errmsg={errmsg}')
                return None

        except Exception as e:
            print(f'[WeChatPush] 群发消息异常: {e}')
            return None

    def get_material_list(
        self, material_type: str = 'news', offset: int = 0, count: int = 20
    ) -> Optional[Dict]:
        """
        获取素材列表

        Args:
            material_type: 素材类型（image/voice/video/news）
            offset: 偏移量
            count: 返回数量（1-20）

        Returns:
            dict: 素材列表，失败返回None
        """
        access_token = self._get_access_token()
        if not access_token:
            return None

        try:
            url = f'https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={access_token}'

            data = {'type': material_type, 'offset': offset, 'count': count}

            response = requests.post(
                url,
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'},
                timeout=15,
            )
            result = response.json()

            if 'item' in result:
                print(f'[WeChatPush] 获取素材列表成功: 共{result.get("total_count", 0)}个素材')
                return result
            else:
                print(f'[WeChatPush] 获取素材列表失败: {result}')
                return None

        except Exception as e:
            print(f'[WeChatPush] 获取素材列表异常: {e}')
            return None


# 全局实例
wechat_push_service = WeChatPushService()
