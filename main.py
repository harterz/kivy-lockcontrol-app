import requests
import json
import time
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

class LockControlApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lock_mac = "869701070802882"  # 默认MAC地址
        self.server_url = "https://svr.yefiot.com/yefiot/v1/mqttpost/"
        self.status_label = None
        self.log_text = ""
        
    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        title = Label(
            text='智能门锁控制器',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            color=(0.2, 0.6, 1, 1)
        )
        main_layout.add_widget(title)
        
        # MAC地址输入区域
        mac_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        mac_label = Label(text='设备MAC:', size_hint_x=0.3)
        self.mac_input = TextInput(
            text=self.lock_mac,
            multiline=False,
            size_hint_x=0.7
        )
        mac_layout.add_widget(mac_label)
        mac_layout.add_widget(self.mac_input)
        main_layout.add_widget(mac_layout)
        
        # 控制按钮区域
        button_layout = GridLayout(cols=2, size_hint_y=None, height='120dp', spacing=10)
        
        # 开锁按钮
        unlock_btn = Button(
            text='🔓 开锁',
            font_size='18sp',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        unlock_btn.bind(on_press=self.unlock_door)
        
        # 查询状态按钮
        status_btn = Button(
            text='📊 查询状态',
            font_size='18sp',
            background_color=(0.2, 0.6, 1, 1)
        )
        status_btn.bind(on_press=self.query_status)
        
        # 测试连接按钮
        test_btn = Button(
            text='🔗 测试连接',
            font_size='18sp',
            background_color=(1, 0.6, 0.2, 1)
        )
        test_btn.bind(on_press=self.test_connection)
        
        # 清除日志按钮
        clear_btn = Button(
            text='🗑️ 清除日志',
            font_size='18sp',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_log)
        
        button_layout.add_widget(unlock_btn)
        button_layout.add_widget(status_btn)
        button_layout.add_widget(test_btn)
        button_layout.add_widget(clear_btn)
        main_layout.add_widget(button_layout)
        
        # 状态显示
        self.status_label = Label(
            text='状态: 就绪',
            size_hint_y=None,
            height='40dp',
            color=(0.2, 0.8, 0.2, 1)
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
        
        # 日志显示区域
        log_label = Label(
            text='操作日志:',
            size_hint_y=None,
            height='30dp',
            text_size=(None, None)
        )
        main_layout.add_widget(log_label)
        
        # 滚动日志
        scroll = ScrollView()
        self.log_display = Label(
            text='应用启动完成\n',
            text_size=(None, None),
            valign='top',
            markup=True
        )
        scroll.add_widget(self.log_display)
        main_layout.add_widget(scroll)
        
        return main_layout
    
    def update_status(self, message, color=(1, 1, 1, 1)):
        """更新状态显示"""
        if self.status_label:
            self.status_label.text = f"状态: {message}"
            self.status_label.color = color
    
    def add_log(self, message):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text += log_entry
        
        # 限制日志长度
        lines = self.log_text.split('\n')
        if len(lines) > 50:
            self.log_text = '\n'.join(lines[-50:])
        
        if self.log_display:
            self.log_display.text = self.log_text
            self.log_display.text_size = (self.log_display.parent.width, None)
    
    def show_popup(self, title, message):
        """显示弹窗"""
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, text_size=(300, None), halign='center')
        popup_button = Button(text='确定', size_hint_y=None, height='40dp')
        
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)
        
        popup = Popup(
            title=title,
            content=popup_layout,
            size_hint=(0.8, 0.6)
        )
        popup_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def parse_lock_command(self, hex_string):
        """解析门锁指令"""
        if not hex_string.startswith('HD'):
            return None
        
        return {
            'header': hex_string[:2],
            'command': hex_string[2:4],
            'data': hex_string[4:-1],
            'checksum': hex_string[-1]
        }
    
    def send_lock_command(self, cmd_type, info_data):
        """发送门锁命令"""
        try:
            self.update_status("发送命令中...", (1, 1, 0, 1))
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 30), 0)
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36'
            }
            
            payload = {
                "type": "yfn03",
                "mac": self.mac_input.text.strip(),
                "cmd": cmd_type,
                "sn": int(time.time()),
                "info": info_data
            }
            
            self.add_log(f"发送命令: {cmd_type}, MAC: {payload['mac']}")
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 60), 0)
            
            response = requests.post(
                self.server_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 90), 0)
            
            if response.status_code == 200:
                response_data = response.json()
                self.add_log(f"响应成功: {response_data}")
                
                if 'data' in response_data and response_data['data']:
                    msg_info = response_data['data'][0].get('msg_info', '')
                    parsed = self.parse_lock_command(msg_info)
                    
                    if parsed:
                        self.add_log(f"指令解析: 命令码={parsed['command']}, 数据={parsed['data']}")
                        
                        # 根据响应判断操作结果
                        if parsed['command'] == '2B':
                            self.update_status("操作成功", (0.2, 0.8, 0.2, 1))
                            Clock.schedule_once(lambda dt: self.show_popup("成功", "门锁操作执行成功！"), 0.1)
                        else:
                            self.update_status("操作完成", (0.2, 0.6, 1, 1))
                    else:
                        self.update_status("响应格式异常", (1, 0.6, 0.2, 1))
                else:
                    self.update_status("无响应数据", (1, 0.6, 0.2, 1))
            else:
                self.add_log(f"请求失败: HTTP {response.status_code}")
                self.update_status("请求失败", (0.8, 0.2, 0.2, 1))
                Clock.schedule_once(lambda dt: self.show_popup("错误", f"请求失败: {response.status_code}"), 0.1)
                
        except requests.exceptions.Timeout:
            self.add_log("请求超时")
            self.update_status("连接超时", (0.8, 0.2, 0.2, 1))
            Clock.schedule_once(lambda dt: self.show_popup("错误", "连接超时，请检查网络"), 0.1)
        except Exception as e:
            self.add_log(f"错误: {str(e)}")
            self.update_status("操作失败", (0.8, 0.2, 0.2, 1))
            Clock.schedule_once(lambda dt: self.show_popup("错误", f"操作失败: {str(e)}"), 0.1)
        finally:
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 0), 1)
    
    def unlock_door(self, instance):
        """开锁操作"""
        if not self.mac_input.text.strip():
            self.show_popup("错误", "请输入设备MAC地址")
            return
        
        # 在后台线程执行网络请求
        thread = Thread(target=self.send_lock_command, args=("0", "HD2F0454049024910010000000000000000000006EDA1000000007EW"))
        thread.daemon = True
        thread.start()
    
    def query_status(self, instance):
        """查询状态"""
        if not self.mac_input.text.strip():
            self.show_popup("错误", "请输入设备MAC地址")
            return
        
        # 使用不同的命令码查询状态
        thread = Thread(target=self.send_lock_command, args=("1", "HD1F0000000000000000000000000000000000000000000000000000W"))
        thread.daemon = True
        thread.start()
    
    def test_connection(self, instance):
        """测试连接"""
        if not self.mac_input.text.strip():
            self.show_popup("错误", "请输入设备MAC地址")
            return
        
        self.add_log("测试连接...")
        thread = Thread(target=self.send_lock_command, args=("0", "HD2F0454049024910010000000000000000000006EDA1000000007EW"))
        thread.daemon = True
        thread.start()
    
    def clear_log(self, instance):
        """清除日志"""
        self.log_text = "日志已清除\n"
        if self.log_display:
            self.log_display.text = self.log_text
        self.update_status("就绪", (0.2, 0.8, 0.2, 1))

if __name__ == '__main__':
    LockControlApp().run()