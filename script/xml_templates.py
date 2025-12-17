# -*- coding: utf-8 -*-
# filename: xml_templates.py

import time


class WeChatXMLTemplate:
    """微信XML消息模板类"""

    @staticmethod
    def text_reply(to_user, from_user, content, create_time=None):
        """
        生成文本回复消息的XML

        Args:
            to_user (str): 接收方用户openid
            from_user (str): 发送方用户名（公众号原始ID）
            content (str): 回复的文本内容
            create_time (int, optional): 消息创建时间. 默认为当前时间

        Returns:
            str: 格式化的XML字符串
        """
        if create_time is None:
            create_time = int(time.time())

        return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{create_time}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""

    @staticmethod
    def image_reply(to_user, from_user, media_id, create_time=None):
        """
        生成图片回复消息的XML

        Args:
            to_user (str): 接收方用户openid
            from_user (str): 发送方用户名（公众号原始ID）
            media_id (str): 媒体文件ID
            create_time (int, optional): 消息创建时间. 默认为当前时间

        Returns:
            str: 格式化的XML字符串
        """
        if create_time is None:
            create_time = int(time.time())

        return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{create_time}</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<Image>
<MediaId><![CDATA[{media_id}]]></MediaId>
</Image>
</xml>"""

    @staticmethod
    def news_reply(to_user, from_user, articles, create_time=None):
        """
        生成图文回复消息的XML

        Args:
            to_user (str): 接收方用户openid
            from_user (str): 发送方用户名（公众号原始ID）
            articles (list): 图文消息列表，每个元素包含title, description, pic_url, url
            create_time (int, optional): 消息创建时间. 默认为当前时间

        Returns:
            str: 格式化的XML字符串
        """
        if create_time is None:
            create_time = int(time.time())

        article_count = len(articles)
        articles_xml = ''

        for article in articles:
            articles_xml += f"""
<item>
<Title><![CDATA[{article.get('title', '')}]]></Title>
<Description><![CDATA[{article.get('description', '')}]]></Description>
<PicUrl><![CDATA[{article.get('pic_url', '')}]]></PicUrl>
<Url><![CDATA[{article.get('url', '')}]]></Url>
</item>"""

        return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{create_time}</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>{article_count}</ArticleCount>
<Articles>{articles_xml}
</Articles>
</xml>"""

    @staticmethod
    def music_reply(
        to_user,
        from_user,
        title,
        description,
        music_url,
        hq_music_url,
        thumb_media_id,
        create_time=None,
    ):
        """
        生成音乐回复消息的XML

        Args:
            to_user (str): 接收方用户openid
            from_user (str): 发送方用户名（公众号原始ID）
            title (str): 音乐标题
            description (str): 音乐描述
            music_url (str): 音乐链接
            hq_music_url (str): 高质量音乐链接
            thumb_media_id (str): 缩略图媒体ID
            create_time (int, optional): 消息创建时间. 默认为当前时间

        Returns:
            str: 格式化的XML字符串
        """
        if create_time is None:
            create_time = int(time.time())

        return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{create_time}</CreateTime>
<MsgType><![CDATA[music]]></MsgType>
<Music>
<Title><![CDATA[{title}]]></Title>
<Description><![CDATA[{description}]]></Description>
<MusicUrl><![CDATA[{music_url}]]></MusicUrl>
<HQMusicUrl><![CDATA[{hq_music_url}]]></HQMusicUrl>
<ThumbMediaId><![CDATA[{thumb_media_id}]]></ThumbMediaId>
</Music>
</xml>"""

    @staticmethod
    def voice_reply(to_user, from_user, media_id, create_time=None):
        """
        生成语音回复消息的XML

        Args:
            to_user (str): 接收方用户openid
            from_user (str): 发送方用户名（公众号原始ID）
            media_id (str): 媒体文件ID
            create_time (int, optional): 消息创建时间. 默认为当前时间

        Returns:
            str: 格式化的XML字符串
        """
        if create_time is None:
            create_time = int(time.time())

        return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{create_time}</CreateTime>
<MsgType><![CDATA[voice]]></MsgType>
<Voice>
<MediaId><![CDATA[{media_id}]]></MediaId>
</Voice>
</xml>"""

    @staticmethod
    def video_reply(to_user, from_user, media_id, title, description, create_time=None):
        """
        生成视频回复消息的XML

        Args:
            to_user (str): 接收方用户openid
            from_user (str): 发送方用户名（公众号原始ID）
            media_id (str): 媒体文件ID
            title (str): 视频标题
            description (str): 视频描述
            create_time (int, optional): 消息创建时间. 默认为当前时间

        Returns:
            str: 格式化的XML字符串
        """
        if create_time is None:
            create_time = int(time.time())

        return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{create_time}</CreateTime>
<MsgType><![CDATA[video]]></MsgType>
<Video>
<MediaId><![CDATA[{media_id}]]></MediaId>
<Title><![CDATA[{title}]]></Title>
<Description><![CDATA[{description}]]></Description>
</Video>
</xml>"""


# 为了向后兼容，保留一个简单的函数接口
def create_text_reply(to_user, from_user, content):
    """
    创建文本回复消息（向后兼容函数）

    Args:
        to_user (str): 接收方用户openid
        from_user (str): 发送方用户名（公众号原始ID）
        content (str): 回复的文本内容

    Returns:
        str: 格式化的XML字符串
    """
    return WeChatXMLTemplate.text_reply(to_user, from_user, content)
