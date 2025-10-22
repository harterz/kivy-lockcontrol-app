from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class MinimalApp(App):
    def build(self):
        # 主布局
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        title = Label(
            text='Minimal Kivy App',
            font_size='24sp'
        )
        layout.add_widget(title)
        
        # 按钮
        button = Button(
            text='Click Me',
            size_hint_y=None,
            height='50dp'
        )
        button.bind(on_press=self.on_button_click)
        layout.add_widget(button)
        
        # 状态标签
        self.status_label = Label(
            text='Ready',
            font_size='16sp'
        )
        layout.add_widget(self.status_label)
        
        return layout
    
    def on_button_click(self, instance):
        self.status_label.text = 'Button clicked!'

if __name__ == '__main__':
    MinimalApp().run()