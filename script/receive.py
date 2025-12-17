# -*- coding: utf-8 -*-
# webdata接受处理构造数据模块

import xml.etree.ElementTree as ET
import consts


class Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text


class TextMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Content = xmlData.find('Content').text


class ImageMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.PicUrl = xmlData.find('PicUrl').text
        self.MediaId = xmlData.find('MediaId').text


class LocationMsg(Msg):
    def __init__(self, xmlData):
        Msg.__init__(self, xmlData)
        self.Location_X = xmlData.find('Location_X').text
        self.Location_Y = xmlData.find('Location_Y').text


class EventMsg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.Event = xmlData.find('Event').text

        # 获取EventKey，如果存在的话
        eventkey_element = xmlData.find('EventKey')
        self.EventKey = eventkey_element.text if eventkey_element is not None else None

        print(f'事件类型: {self.Event}, EventKey: {self.EventKey}')


def parse_xml(web_data):
    if len(web_data) == 0:
        return None

    # 确保数据是字符串格式
    if isinstance(web_data, bytes):
        web_data = web_data.decode('utf-8')

    print('解析XML数据:', repr(web_data))

    xmlData = ET.fromstring(web_data)
    msg_type = xmlData.find('MsgType').text
    print('消息类型:', msg_type)

    if msg_type == consts.WeChatMsgType.TEXT:
        return TextMsg(xmlData)
    elif msg_type == consts.WeChatMsgType.IMAGE:
        return ImageMsg(xmlData)
    elif msg_type == consts.WeChatMsgType.LOCATION:
        return LocationMsg(xmlData)
    elif msg_type == consts.WeChatMsgType.EVENT:
        return EventMsg(xmlData)
