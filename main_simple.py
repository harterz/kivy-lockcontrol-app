from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

class SimpleApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_label = None
        self.log_text = ""
        
    def build(self):
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        title = Label(
            text='Simple Kivy App',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            color=(0.2, 0.6, 1, 1)
        )
        main_layout.add_widget(title)
        
        # 输入区域
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        input_label = Label(text='输入:', size_hint_x=0.3)
        self.text_input = TextInput(
            text='Hello World',
            multiline=False,
            size_hint_x=0.7
        )
        input_layout.add_widget(input_label)
        input_layout.add_widget(self.text_input)
        main_layout.add_widget(input_layout)
        
        # 按钮区域
        button_layout = GridLayout(cols=2, size_hint_y=None, height='100dp', spacing=10)
        
        # 显示按钮
        show_btn = Button(
            text='显示文本',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        show_btn.bind(on_press=self.show_text)
        button_layout.add_widget(show_btn)
        
        # 清除按钮
        clear_btn = Button(
            text='清除',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_text)
        button_layout.add_widget(clear_btn)
        
        main_layout.add_widget(button_layout)
        
        # 状态标签
        self.status_label = Label(
            text='准备就绪',
            size_hint_y=None,
            height='40dp',
            color=(0, 1, 0, 1)
        )
        main_layout.add_widget(self.status_label)
        
        # 日志区域
        log_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        log_title = Label(text='日志:', size_hint_y=None, height='30dp')
        log_layout.add_widget(log_title)
        
        # 滚动视图包含日志标签
        scroll = ScrollView()
        self.log_label = Label(
            text='应用启动\n',
            text_size=(None, None),
            valign='top',
            halign='left'
        )
        scroll.add_widget(self.log_label)
        log_layout.add_widget(scroll)
        
        main_layout.add_widget(log_layout)
        
        return main_layout
    
    def update_status(self, message, color=(1, 1, 1, 1)):
        """更新状态标签"""
        if self.status_label:
            self.status_label.text = message
            self.status_label.color = color
    
    def add_log(self, message):
        """添加日志信息"""
        import datetime
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
        
        msg_label = Label(text=message, text_size=(300, None), halign='center')
        content.add_widget(msg_label)
        
        close_btn = Button(text='关闭', size_hint_y=None, height='40dp')
        content.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_text(self, instance):
        """显示输入的文本"""
        text = self.text_input.text
        self.update_status(f"显示: {text}", (0, 1, 0, 1))
        self.add_log(f"显示文本: {text}")
        self.show_popup("文本显示", f"您输入的文本是:\n{text}")
    
    def clear_text(self, instance):
        """清除输入文本"""
        self.text_input.text = ""
        self.update_status("文本已清除", (1, 1, 0, 1))
        self.add_log("清除了输入文本")

if __name__ == '__main__':
    SimpleApp().run()