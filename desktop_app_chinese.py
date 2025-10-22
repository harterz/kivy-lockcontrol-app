#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能门锁控制器 - 中文字体优化版本
专门解决macOS系统下的中文显示问题
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
from kivy.config import Config
import os
import platform

# 设置窗口大小
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', True)

# 注册中文字体
def register_chinese_font():
    """注册中文字体"""
    system = platform.system()
    
    # macOS 系统字体路径
    if system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial Unicode.ttf",
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc"
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/simhei.ttf"
        ]
    else:  # Linux
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]
    
    # 尝试注册找到的第一个字体
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name="Chinese", fn_regular=font_path)
                print(f"成功注册字体: {font_path}")
                return True
            except Exception as e:
                print(f"注册字体失败 {font_path}: {e}")
                continue
    
    print("未找到合适的中文字体，使用默认字体")
    return False

# 在应用启动前注册字体
register_chinese_font()

# 模拟网络请求（用于演示）
def simulate_network_request(url, data):
    """模拟网络请求，返回模拟响应"""
    time.sleep(1)  # 模拟网络延迟
    return {
        "status": "success",
        "message": "操作成功",
        "data": {"response": "模拟响应数据"}
    }

class ChineseLockControlApp(App):
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
        
        # 标题 - 使用英文避免字体问题
        title = Label(
            text='Smart Lock Controller (Desktop)',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            color=(0.2, 0.6, 1, 1),
            markup=True
        )
        main_layout.add_widget(title)
        
        # MAC地址输入区域
        mac_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        mac_label = Label(
            text='Device MAC:',
            size_hint_x=0.3,
            font_size='16sp'
        )
        self.mac_input = TextInput(
            text=self.lock_mac,
            multiline=False,
            size_hint_x=0.7,
            font_size='14sp'
        )
        mac_layout.add_widget(mac_label)
        mac_layout.add_widget(self.mac_input)
        main_layout.add_widget(mac_layout)
        
        # 服务器地址输入区域
        server_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        server_label = Label(
            text='Server URL:',
            size_hint_x=0.3,
            font_size='16sp'
        )
        self.server_input = TextInput(
            text=self.server_url,
            multiline=False,
            size_hint_x=0.7,
            font_size='12sp'
        )
        server_layout.add_widget(server_label)
        server_layout.add_widget(self.server_input)
        main_layout.add_widget(server_layout)
        
        # 按钮区域 - 使用英文标签
        button_layout = GridLayout(cols=2, size_hint_y=None, height='150dp', spacing=10)
        
        # 开锁按钮
        unlock_btn = Button(
            text='UNLOCK',
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='18sp'
        )
        unlock_btn.bind(on_press=self.unlock_door)
        button_layout.add_widget(unlock_btn)
        
        # 查询状态按钮
        status_btn = Button(
            text='STATUS',
            background_color=(0.2, 0.2, 0.8, 1),
            font_size='18sp'
        )
        status_btn.bind(on_press=self.query_status)
        button_layout.add_widget(status_btn)
        
        # 测试连接按钮
        test_btn = Button(
            text='TEST',
            background_color=(0.8, 0.6, 0.2, 1),
            font_size='18sp'
        )
        test_btn.bind(on_press=self.test_connection)
        button_layout.add_widget(test_btn)
        
        # 清除日志按钮
        clear_btn = Button(
            text='CLEAR',
            background_color=(0.8, 0.2, 0.2, 1),
            font_size='18sp'
        )
        clear_btn.bind(on_press=self.clear_log)
        button_layout.add_widget(clear_btn)
        
        main_layout.add_widget(button_layout)
        
        # 状态标签
        self.status_label = Label(
            text='Ready',
            size_hint_y=None,
            height='40dp',
            color=(0, 1, 0, 1),
            font_size='16sp'
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
        log_title = Label(
            text='Operation Log:',
            size_hint_y=None,
            height='30dp',
            font_size='16sp'
        )
        log_layout.add_widget(log_title)
        
        # 滚动视图包含日志标签
        scroll = ScrollView()
        self.log_label = Label(
            text='Application started\n',
            text_size=(None, None),
            valign='top',
            halign='left',
            font_size='14sp'
        )
        scroll.add_widget(self.log_label)
        log_layout.add_widget(scroll)
        
        main_layout.add_widget(log_layout)
        
        # 初始化日志
        self.add_log("Smart Lock Controller Started")
        self.add_log(f"Default Device MAC: {self.lock_mac}")
        
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
            self.log_label.text_size = (700, None)
    
    def show_popup(self, title, message):
        """显示弹出窗口"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        msg_label = Label(
            text=message, 
            text_size=(400, None), 
            halign='center',
            font_size='16sp'
        )
        content.add_widget(msg_label)
        
        close_btn = Button(
            text='Close', 
            size_hint_y=None, 
            height='40dp',
            font_size='16sp'
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
    
    def send_lock_command(self, cmd_type, info_data):
        """发送门锁命令（模拟）"""
        def command_thread():
            try:
                self.update_status(f"Sending {cmd_type}...", (1, 1, 0, 1))
                self.add_log(f"Sending {cmd_type} command to device: {self.mac_input.text}")
                
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
        self.add_log(f"{cmd_type} command sent successfully")
    
    def handle_response(self, cmd_type, response):
        """处理响应"""
        if response.get("status") == "success":
            self.update_status(f"{cmd_type} Success", (0, 1, 0, 1))
            self.add_log(f"{cmd_type} operation successful: {response.get('message', '')}")
            self.show_popup("Success", f"{cmd_type} operation completed successfully")
        else:
            self.update_status(f"{cmd_type} Failed", (1, 0, 0, 1))
            self.add_log(f"{cmd_type} operation failed: {response.get('message', 'Unknown error')}")
            self.show_popup("Failed", f"{cmd_type} operation failed")
        
        # 重置进度条
        Clock.schedule_once(lambda dt: self.update_progress(0), 2)
    
    def handle_error(self, cmd_type, error_msg):
        """处理错误"""
        self.update_status(f"{cmd_type} Error", (1, 0, 0, 1))
        self.add_log(f"{cmd_type} error occurred: {error_msg}")
        self.show_popup("Error", f"Operation failed: {error_msg}")
        self.update_progress(0)
    
    def unlock_door(self, instance):
        """开锁操作"""
        self.lock_mac = self.mac_input.text
        self.add_log(f"Attempting to unlock device: {self.lock_mac}")
        self.send_lock_command("UNLOCK", {"action": "unlock"})
    
    def query_status(self, instance):
        """查询门锁状态"""
        self.lock_mac = self.mac_input.text
        self.add_log(f"Querying device status: {self.lock_mac}")
        self.send_lock_command("STATUS", {"action": "status"})
    
    def test_connection(self, instance):
        """测试连接"""
        self.server_url = self.server_input.text
        self.add_log(f"Testing connection to server: {self.server_url}")
        
        def test_thread():
            try:
                self.update_status("Testing connection...", (1, 1, 0, 1))
                self.simulate_progress()
                
                # 模拟连接测试
                time.sleep(1)
                response = simulate_network_request(self.server_url, {"test": True})
                
                Clock.schedule_once(
                    lambda dt: self.connection_test_complete(response), 0
                )
                
            except Exception as e:
                Clock.schedule_once(
                    lambda dt: self.handle_error("Connection Test", str(e)), 0
                )
        
        Thread(target=test_thread, daemon=True).start()
    
    def connection_test_complete(self, response):
        """连接测试完成"""
        if response.get("status") == "success":
            self.is_connected = True
            self.update_status("Connection OK", (0, 1, 0, 1))
            self.add_log("Server connection test successful")
            self.show_popup("Connection Test", "Server connection is working")
        else:
            self.is_connected = False
            self.update_status("Connection Failed", (1, 0, 0, 1))
            self.add_log("Server connection test failed")
            self.show_popup("Connection Test", "Server connection failed")
        
        Clock.schedule_once(lambda dt: self.update_progress(0), 2)
    
    def clear_log(self, instance):
        """清除日志"""
        self.log_text = ""
        if hasattr(self, 'log_label'):
            self.log_label.text = "Log cleared\n"
        self.add_log("Log cleared")
        self.update_status("Log cleared", (0, 1, 1, 1))

if __name__ == '__main__':
    ChineseLockControlApp().run()