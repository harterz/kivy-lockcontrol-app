#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能门锁控制器 - 桌面版本
这是一个可以在桌面环境下运行的Kivy应用程序
"""

import json
import time
import datetime
from threading import Thread
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
import os

# 注册中文字体
try:
    # 尝试注册系统中文字体
    if os.name == 'posix':  # macOS/Linux
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            '/System/Library/Fonts/Helvetica.ttc',  # macOS备选
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                LabelBase.register(name='Chinese', fn_regular=font_path)
                break
    elif os.name == 'nt':  # Windows
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
            'C:/Windows/Fonts/simhei.ttf',  # 黑体
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                LabelBase.register(name='Chinese', fn_regular=font_path)
                break
except Exception as e:
    print(f"字体注册失败: {e}")
    pass

# 模拟网络请求（用于演示）
def simulate_network_request(url, data):
    """模拟网络请求，返回模拟响应"""
    time.sleep(1)  # 模拟网络延迟
    return {
        "status": "success",
        "message": "操作成功",
        "data": {"response": "模拟响应数据"}
    }

class LockControlApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lock_mac = "869701070802882"  # 默认MAC地址
        self.server_url = "https://svr.yefiot.com/yefiot/v1/mqttpost/"
        self.status_label = None
        self.log_text = ""
        self.is_connected = False
        
    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        title = Label(
            text='智能门锁控制器 (桌面版)',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            color=(0.2, 0.6, 1, 1),
            font_name='Chinese'
        )
        main_layout.add_widget(title)
        
        # MAC地址输入区域
        mac_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        mac_label = Label(text='设备MAC:', size_hint_x=0.3, font_name='Chinese')
        self.mac_input = TextInput(
            text=self.lock_mac,
            multiline=False,
            size_hint_x=0.7
        )
        mac_layout.add_widget(mac_label)
        mac_layout.add_widget(self.mac_input)
        main_layout.add_widget(mac_layout)
        
        # 服务器地址输入区域
        server_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        server_label = Label(text='服务器:', size_hint_x=0.3, font_name='Chinese')
        self.server_input = TextInput(
            text=self.server_url,
            multiline=False,
            size_hint_x=0.7
        )
        server_layout.add_widget(server_label)
        server_layout.add_widget(self.server_input)
        main_layout.add_widget(server_layout)
        
        # 按钮区域
        button_layout = GridLayout(cols=2, size_hint_y=None, height='150dp', spacing=10)
        
        # 开锁按钮
        unlock_btn = Button(
            text='开锁',
            background_color=(0.2, 0.8, 0.2, 1),
            font_name='Chinese'
        )
        unlock_btn.bind(on_press=self.unlock_door)
        button_layout.add_widget(unlock_btn)
        
        # 查询状态按钮
        status_btn = Button(
            text='查询状态',
            background_color=(0.2, 0.2, 0.8, 1),
            font_name='Chinese'
        )
        status_btn.bind(on_press=self.query_status)
        button_layout.add_widget(status_btn)
        
        # 测试连接按钮
        test_btn = Button(
            text='测试连接',
            background_color=(0.8, 0.6, 0.2, 1),
            font_name='Chinese'
        )
        test_btn.bind(on_press=self.test_connection)
        button_layout.add_widget(test_btn)
        
        # 清除日志按钮
        clear_btn = Button(
            text='清除日志',
            background_color=(0.8, 0.2, 0.2, 1),
            font_name='Chinese'
        )
        clear_btn.bind(on_press=self.clear_log)
        button_layout.add_widget(clear_btn)
        
        main_layout.add_widget(button_layout)
        
        # 状态标签
        self.status_label = Label(
            text='准备就绪',
            size_hint_y=None,
            height='40dp',
            color=(0, 1, 0, 1),
            font_name='Chinese'
        )
        main_layout.add_widget(self.status_label)
        
        # 进度条
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height='20dp'
        )
        main_layout.add_widget(self.progress_bar)
        
        # 日志区域
        log_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        log_title = Label(text='操作日志:', size_hint_y=None, height='30dp', font_name='Chinese')
        log_layout.add_widget(log_title)
        
        # 滚动视图包含日志标签
        scroll = ScrollView()
        self.log_label = Label(
            text='应用启动\n',
            text_size=(None, None),
            valign='top',
            halign='left',
            font_name='Chinese'
        )
        scroll.add_widget(self.log_label)
        log_layout.add_widget(scroll)
        
        main_layout.add_widget(log_layout)
        
        # 初始化日志
        self.add_log("智能门锁控制器已启动")
        self.add_log(f"默认设备MAC: {self.lock_mac}")
        
        return main_layout
    
    def update_status(self, message, color=(1, 1, 1, 1)):
        """更新状态标签"""
        if self.status_label:
            self.status_label.text = message
            self.status_label.color = color
    
    def add_log(self, message):
        """添加日志信息"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text += log_entry
        
        if hasattr(self, 'log_label'):
            self.log_label.text = self.log_text
            # 更新text_size以适应内容
            self.log_label.text_size = (400, None)
    
    def show_popup(self, title, message):
        """显示弹出窗口"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        msg_label = Label(
            text=message, 
            text_size=(300, None), 
            halign='center',
            font_name='Chinese'
        )
        content.add_widget(msg_label)
        
        close_btn = Button(
            text='关闭', 
            size_hint_y=None, 
            height='40dp',
            font_name='Chinese'
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def update_progress(self, value):
        """更新进度条"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.value = value
    
    def simulate_progress(self, callback=None):
        """模拟进度更新"""
        def progress_thread():
            for i in range(0, 101, 10):
                Clock.schedule_once(lambda dt, val=i: self.update_progress(val), 0)
                time.sleep(0.1)
            if callback:
                Clock.schedule_once(lambda dt: callback(), 0)
        
        Thread(target=progress_thread, daemon=True).start()
    
    def parse_lock_command(self, hex_string):
        """解析门锁命令（模拟）"""
        commands = {
            "01": "开锁命令",
            "02": "状态查询",
            "03": "设置密码",
            "04": "删除密码"
        }
        return commands.get(hex_string[:2], "未知命令")
    
    def send_lock_command(self, cmd_type, info_data):
        """发送门锁命令（模拟）"""
        def command_thread():
            try:
                self.update_status("正在发送命令...", (1, 1, 0, 1))
                self.add_log(f"发送{cmd_type}命令到设备: {self.mac_input.text}")
                
                # 模拟网络请求
                self.simulate_progress(lambda: self.command_complete(cmd_type))
                
                # 模拟响应
                response = simulate_network_request(self.server_input.text, {
                    "mac": self.mac_input.text,
                    "command": cmd_type,
                    "data": info_data
                })
                
                Clock.schedule_once(
                    lambda dt: self.handle_response(cmd_type, response), 1.2
                )
                
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.handle_error(cmd_type, str(e)), 0
                )
        
        Thread(target=command_thread, daemon=True).start()
    
    def command_complete(self, cmd_type):
        """命令完成回调"""
        self.update_progress(100)
        self.add_log(f"{cmd_type}命令发送完成")
    
    def handle_response(self, cmd_type, response):
        """处理响应"""
        if response.get("status") == "success":
            self.update_status(f"{cmd_type}成功", (0, 1, 0, 1))
            self.add_log(f"{cmd_type}操作成功: {response.get('message', '')}")
            self.show_popup("操作成功", f"{cmd_type}操作已成功完成")
        else:
            self.update_status(f"{cmd_type}失败", (1, 0, 0, 1))
            self.add_log(f"{cmd_type}操作失败: {response.get('message', '未知错误')}")
            self.show_popup("操作失败", f"{cmd_type}操作失败")
        
        # 重置进度条
        Clock.schedule_once(lambda dt: self.update_progress(0), 2)
    
    def handle_error(self, cmd_type, error_msg):
        """处理错误"""
        self.update_status(f"{cmd_type}错误", (1, 0, 0, 1))
        self.add_log(f"{cmd_type}发生错误: {error_msg}")
        self.show_popup("错误", f"操作失败: {error_msg}")
        self.update_progress(0)
    
    def unlock_door(self, instance):
        """开锁操作"""
        self.lock_mac = self.mac_input.text
        self.add_log(f"尝试开锁设备: {self.lock_mac}")
        self.send_lock_command("开锁", {"action": "unlock"})
    
    def query_status(self, instance):
        """查询门锁状态"""
        self.lock_mac = self.mac_input.text
        self.add_log(f"查询设备状态: {self.lock_mac}")
        self.send_lock_command("状态查询", {"action": "status"})
    
    def test_connection(self, instance):
        """测试连接"""
        self.server_url = self.server_input.text
        self.add_log(f"测试连接到服务器: {self.server_url}")
        
        def test_thread():
            try:
                self.update_status("测试连接中...", (1, 1, 0, 1))
                self.simulate_progress()
                
                # 模拟连接测试
                time.sleep(1)
                response = simulate_network_request(self.server_url, {"test": True})
                
                Clock.schedule_once(
                    lambda dt: self.connection_test_complete(response), 0
                )
                
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.handle_error("连接测试", str(e)), 0
                )
        
        Thread(target=test_thread, daemon=True).start()
    
    def connection_test_complete(self, response):
        """连接测试完成"""
        if response.get("status") == "success":
            self.is_connected = True
            self.update_status("连接成功", (0, 1, 0, 1))
            self.add_log("服务器连接测试成功")
            self.show_popup("连接测试", "服务器连接正常")
        else:
            self.is_connected = False
            self.update_status("连接失败", (1, 0, 0, 1))
            self.add_log("服务器连接测试失败")
            self.show_popup("连接测试", "服务器连接失败")
        
        Clock.schedule_once(lambda dt: self.update_progress(0), 2)
    
    def clear_log(self, instance):
        """清除日志"""
        self.log_text = ""
        if hasattr(self, 'log_label'):
            self.log_label.text = "日志已清除\n"
        self.add_log("日志已清除")
        self.update_status("日志已清除", (0, 1, 1, 1))

if __name__ == '__main__':
    LockControlApp().run()