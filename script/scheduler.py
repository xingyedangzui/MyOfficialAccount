# -*- coding: utf-8 -*-
"""
定时任务调度器
用于执行每日天气草稿创建等周期性任务
"""

import os
import time
import threading
import schedule
import requests
from datetime import datetime
from typing import Optional

import consts
from data_manager import user_data_manager
from weather_service import weather_service, get_clothing_advice
from wechat_push_service import wechat_push_service


class NotificationService:
    """通知服务 - 用于发送提醒通知"""

    @staticmethod
    def send_server_chan(title: str, content: str) -> bool:
        """
        通过Server酱发送通知（https://sct.ftqq.com/）

        Args:
            title: 通知标题
            content: 通知内容（支持Markdown）

        Returns:
            bool: 是否发送成功
        """
        send_key = getattr(consts, 'SERVER_CHAN_SEND_KEY', '')
        if not send_key:
            print('[Notify] Server酱SendKey未配置，跳过通知')
            return False

        try:
            url = f'https://sctapi.ftqq.com/{send_key}.send'
            data = {
                'title': title,
                'desp': content,
            }
            response = requests.post(url, data=data, timeout=10)
            result = response.json()

            if result.get('code') == 0:
                print('[Notify] Server酱通知发送成功')
                return True
            else:
                print(f'[Notify] Server酱通知发送失败: {result}')
                return False
        except Exception as e:
            print(f'[Notify] Server酱通知异常: {e}')
            return False

    @staticmethod
    def send_email(subject: str, content: str) -> bool:
        """
        通过邮件发送通知

        Args:
            subject: 邮件主题
            content: 邮件内容

        Returns:
            bool: 是否发送成功
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.header import Header

        smtp_server = getattr(consts, 'SMTP_SERVER', '')
        smtp_port = getattr(consts, 'SMTP_PORT', 465)
        smtp_user = getattr(consts, 'SMTP_USER', '')
        smtp_password = getattr(consts, 'SMTP_PASSWORD', '')
        notify_email = getattr(consts, 'NOTIFY_EMAIL', '')

        if not all([smtp_server, smtp_user, smtp_password, notify_email]):
            print('[Notify] 邮件配置不完整，跳过邮件通知')
            return False

        try:
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['From'] = Header(smtp_user)
            msg['To'] = Header(notify_email)
            msg['Subject'] = Header(subject, 'utf-8')

            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, [notify_email], msg.as_string())

            print('[Notify] 邮件通知发送成功')
            return True
        except Exception as e:
            print(f'[Notify] 邮件通知异常: {e}')
            return False

    @staticmethod
    def send_notification(title: str, content: str) -> bool:
        """
        发送通知（尝试所有配置的通知渠道）

        Args:
            title: 通知标题
            content: 通知内容

        Returns:
            bool: 是否至少有一个渠道发送成功
        """
        success = False

        # 尝试Server酱
        if NotificationService.send_server_chan(title, content):
            success = True

        # 尝试邮件
        if NotificationService.send_email(title, content):
            success = True

        return success


class DraftScheduler:
    """草稿调度器 - 用于每日创建天气草稿并发送通知"""

    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None

    def _get_weather_html_content(self, city_name: str) -> Optional[dict]:
        """
        获取天气信息并生成HTML内容

        Args:
            city_name: 城市名称

        Returns:
            dict: 包含html_content和weather_summary的字典，失败返回None
        """
        try:
            # 使用底层weather_service获取天气数据字典
            weather_info = weather_service.get_weather(city_name)

            if not weather_info or not weather_info.get('success'):
                print(f'[Draft] 获取天气失败 -> {city_name}')
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
            clothing_advice = (
                f'{advice["emoji"]} {advice["level"]}：{advice["clothes"]}。{advice["tip"]}'
            )
            if advice.get('extra_tips'):
                clothing_advice += ' ' + ' '.join(advice['extra_tips'])

            today = datetime.now().strftime('%Y年%m月%d日')
            weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][
                datetime.now().weekday()
            ]

            # 生成HTML内容（微信图文消息支持的HTML格式）
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

            # 天气摘要（用于通知）
            weather_summary = f'{city_name} {weather_desc} {temp}°C'

            return {
                'html_content': html_content,
                'weather_summary': weather_summary,
                'temp': temp,
                'weather': weather_desc,
            }

        except Exception as e:
            print(f'[Draft] 生成天气内容异常: {e}')
            return None

    def create_daily_weather_draft(self) -> bool:
        """
        创建每日天气草稿并发送通知

        Returns:
            bool: 是否创建成功
        """
        print(
            f'\n[Draft] ===== 开始创建每日天气草稿 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ====='
        )

        try:
            # 获取配置的群发城市（使用广州作为默认）
            city_name = getattr(consts, 'MASS_SEND_WEATHER_CITY', '广州')

            # 检查是否配置了封面图片media_id
            thumb_media_id = getattr(consts, 'MASS_SEND_THUMB_MEDIA_ID', '')

            if not thumb_media_id:
                # 如果没有配置media_id，尝试上传本地图片
                image_path = getattr(consts, 'MASS_SEND_WEATHER_IMAGE_PATH', '')
                if image_path and os.path.exists(image_path):
                    print(f'[Draft] 正在上传封面图片: {image_path}')
                    thumb_media_id = wechat_push_service.upload_permanent_image(image_path)
                    if thumb_media_id:
                        print(f'[Draft] 封面图片上传成功，media_id: {thumb_media_id}')
                    else:
                        print('[Draft] 封面图片上传失败')
                        self._send_failure_notification('封面图片上传失败')
                        return False
                else:
                    print('[Draft] 未配置封面图片')
                    self._send_failure_notification('未配置封面图片')
                    return False

            # 生成天气HTML内容
            weather_data = self._get_weather_html_content(city_name)
            if not weather_data:
                print('[Draft] 获取天气内容失败')
                self._send_failure_notification('获取天气内容失败')
                return False

            # 生成标题
            today = datetime.now().strftime('%m月%d日')
            title = consts.MASS_SEND_WEATHER_TITLE.format(date=today, city=city_name)

            # 创建草稿
            print('[Draft] 正在创建草稿...')
            draft_media_id = wechat_push_service.add_draft(
                title=title,
                thumb_media_id=thumb_media_id,
                content=weather_data['html_content'],
                author=getattr(consts, 'MASS_SEND_AUTHOR', ''),
                digest=getattr(consts, 'MASS_SEND_DIGEST', f'{city_name}今日天气播报'),
                show_cover_pic=1,
            )

            if not draft_media_id:
                print('[Draft] 创建草稿失败')
                self._send_failure_notification('创建草稿失败')
                return False

            print(f'[Draft] 草稿创建成功: {draft_media_id}')

            # 发送成功通知
            self._send_success_notification(
                title=title,
                weather_summary=weather_data['weather_summary'],
                draft_media_id=draft_media_id,
            )

            # 记录统计
            user_data_manager.update_statistics('draft_create_success')
            print(f'[Draft] ===== 草稿创建完成 =====\n')
            return True

        except Exception as e:
            print(f'[Draft] 创建草稿异常: {e}')
            import traceback

            traceback.print_exc()
            self._send_failure_notification(f'创建草稿异常: {e}')
            return False

    def _send_success_notification(self, title: str, weather_summary: str, draft_media_id: str):
        """发送成功通知"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        notify_title = f'天气草稿已就绪 - {weather_summary}'
        notify_content = f"""## 📝 每日天气草稿已创建

**标题：** {title}

**天气：** {weather_summary}

**创建时间：** {now}

**草稿ID：** `{draft_media_id}`

---

### 📢 请前往公众号后台手动群发

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 进入「内容与互动」→「草稿箱」
3. 找到今日天气草稿，点击「群发」

---

*此消息由自动任务发送*
"""
        NotificationService.send_notification(notify_title, notify_content)

    def _send_failure_notification(self, error_msg: str):
        """发送失败通知"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        notify_title = f'⚠️ 天气草稿创建失败'
        notify_content = f"""## ❌ 每日天气草稿创建失败

**错误信息：** {error_msg}

**时间：** {now}

---

请检查服务日志排查问题。

*此消息由自动任务发送*
"""
        NotificationService.send_notification(notify_title, notify_content)

    def _run_scheduler(self):
        """运行调度器的后台线程"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(30)

    def start(self):
        """启动草稿调度器"""
        if self.is_running:
            print('[Draft] 调度器已在运行')
            return

        self.is_running = True

        # 设置定时任务：每天早上7点创建天气草稿
        push_time = getattr(consts, 'MASS_SEND_TIME', '07:00')
        schedule.every().day.at(push_time).do(self.create_daily_weather_draft)
        print(f'[Draft] 已设置每日天气草稿任务: 每天 {push_time}')

        # 启动后台线程
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print('[Draft] 草稿调度器已启动')

    def stop(self):
        """停止草稿调度器"""
        self.is_running = False
        schedule.clear()
        print('[Draft] 草稿调度器已停止')

    def run_now(self):
        """立即执行一次创建草稿（用于测试）"""
        print('[Draft] 手动触发创建天气草稿')
        return self.create_daily_weather_draft()


# 全局实例
draft_scheduler = DraftScheduler()

# 保持向后兼容的别名
mass_send_scheduler = draft_scheduler


# ==================== 便捷函数 ==================== #


def start_mass_send_scheduler():
    """启动草稿调度器"""
    draft_scheduler.start()


def stop_mass_send_scheduler():
    """停止草稿调度器"""
    draft_scheduler.stop()


def test_mass_send_now():
    """测试创建草稿（立即执行一次）"""
    return draft_scheduler.run_now()


# 兼容旧代码的别名
start_scheduler = start_mass_send_scheduler
stop_scheduler = stop_mass_send_scheduler
