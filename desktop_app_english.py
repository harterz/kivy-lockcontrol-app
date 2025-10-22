#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Lock Controller - Desktop Version (English Interface)
A desktop application for controlling smart locks with full English interface
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
from kivy.config import Config

# Set window size
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', True)

# Simulate network request (for demonstration)
def simulate_network_request(url, data):
    """Simulate network request, return mock response"""
    time.sleep(1)  # Simulate network delay
    return {
        "status": "success",
        "message": "Operation successful",
        "data": {"response": "Mock response data"}
    }

class SmartLockControlApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lock_mac = "869701070802882"  # Default MAC address
        self.server_url = "https://svr.yefiot.com/yefiot/v1/mqttpost/"
        self.status_label = None
        self.log_text = ""
        self.is_connected = False
        
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='Smart Lock Controller (Desktop)',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            color=(0.2, 0.6, 1, 1),
            markup=True
        )
        main_layout.add_widget(title)
        
        # MAC address input area
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
        
        # Server address input area
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
        
        # Button area
        button_layout = GridLayout(cols=2, size_hint_y=None, height='150dp', spacing=10)
        
        # Unlock button
        unlock_btn = Button(
            text='UNLOCK DOOR',
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='18sp'
        )
        unlock_btn.bind(on_press=self.unlock_door)
        button_layout.add_widget(unlock_btn)
        
        # Query status button
        status_btn = Button(
            text='QUERY STATUS',
            background_color=(0.2, 0.2, 0.8, 1),
            font_size='18sp'
        )
        status_btn.bind(on_press=self.query_status)
        button_layout.add_widget(status_btn)
        
        # Test connection button
        test_btn = Button(
            text='TEST CONNECTION',
            background_color=(0.8, 0.6, 0.2, 1),
            font_size='18sp'
        )
        test_btn.bind(on_press=self.test_connection)
        button_layout.add_widget(test_btn)
        
        # Clear log button
        clear_btn = Button(
            text='CLEAR LOG',
            background_color=(0.8, 0.2, 0.2, 1),
            font_size='18sp'
        )
        clear_btn.bind(on_press=self.clear_log)
        button_layout.add_widget(clear_btn)
        
        main_layout.add_widget(button_layout)
        
        # Status label
        self.status_label = Label(
            text='Ready',
            size_hint_y=None,
            height='40dp',
            color=(0, 1, 0, 1),
            font_size='16sp'
        )
        main_layout.add_widget(self.status_label)
        
        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height='20dp'
        )
        main_layout.add_widget(self.progress_bar)
        
        # Log area
        log_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        log_title = Label(
            text='Operation Log:',
            size_hint_y=None,
            height='30dp',
            font_size='16sp'
        )
        log_layout.add_widget(log_title)
        
        # Scroll view containing log label
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
        
        # Initialize log
        self.add_log("Smart Lock Controller Started")
        self.add_log(f"Default Device MAC: {self.lock_mac}")
        
        return main_layout
    
    def update_status(self, message, color=(1, 1, 1, 1)):
        """Update status label"""
        if self.status_label:
            self.status_label.text = message
            self.status_label.color = color
    
    def add_log(self, message):
        """Add log information"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text += log_entry
        
        if hasattr(self, 'log_label'):
            self.log_label.text = self.log_text
            # Update text_size to fit content
            self.log_label.text_size = (700, None)
    
    def show_popup(self, title, message):
        """Show popup window"""
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
        """Update progress bar"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.value = value
    
    def simulate_progress(self, callback=None):
        """Simulate progress update"""
        def progress_thread():
            for i in range(0, 101, 10):
                Clock.schedule_once(lambda dt, val=i: self.update_progress(val), 0)
                time.sleep(0.1)
            if callback:
                Clock.schedule_once(lambda dt: callback(), 0)
        
        Thread(target=progress_thread, daemon=True).start()
    
    def send_lock_command(self, cmd_type, info_data):
        """Send lock command (simulated)"""
        def command_thread():
            try:
                self.update_status(f"Sending {cmd_type}...", (1, 1, 0, 1))
                self.add_log(f"Sending {cmd_type} command to device: {self.mac_input.text}")
                
                # Simulate network request
                self.simulate_progress(lambda: self.command_complete(cmd_type))
                
                # Simulate response
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
        """Command completion callback"""
        self.update_progress(100)
        self.add_log(f"{cmd_type} command sent successfully")
    
    def handle_response(self, cmd_type, response):
        """Handle response"""
        if response.get("status") == "success":
            self.update_status(f"{cmd_type} Success", (0, 1, 0, 1))
            self.add_log(f"{cmd_type} operation successful: {response.get('message', '')}")
            self.show_popup("Success", f"{cmd_type} operation completed successfully")
        else:
            self.update_status(f"{cmd_type} Failed", (1, 0, 0, 1))
            self.add_log(f"{cmd_type} operation failed: {response.get('message', 'Unknown error')}")
            self.show_popup("Failed", f"{cmd_type} operation failed")
        
        # Reset progress bar
        Clock.schedule_once(lambda dt: self.update_progress(0), 2)
    
    def handle_error(self, cmd_type, error_msg):
        """Handle error"""
        self.update_status(f"{cmd_type} Error", (1, 0, 0, 1))
        self.add_log(f"{cmd_type} error occurred: {error_msg}")
        self.show_popup("Error", f"Operation failed: {error_msg}")
        self.update_progress(0)
    
    def unlock_door(self, instance):
        """Unlock operation"""
        self.lock_mac = self.mac_input.text
        self.add_log(f"Attempting to unlock device: {self.lock_mac}")
        self.send_lock_command("UNLOCK", {"action": "unlock"})
    
    def query_status(self, instance):
        """Query lock status"""
        self.lock_mac = self.mac_input.text
        self.add_log(f"Querying device status: {self.lock_mac}")
        self.send_lock_command("STATUS QUERY", {"action": "status"})
    
    def test_connection(self, instance):
        """Test connection"""
        self.server_url = self.server_input.text
        self.add_log(f"Testing connection to server: {self.server_url}")
        
        def test_thread():
            try:
                self.update_status("Testing connection...", (1, 1, 0, 1))
                self.simulate_progress()
                
                # Simulate connection test
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
        """Connection test completion"""
        if response.get("status") == "success":
            self.is_connected = True
            self.update_status("Connection OK", (0, 1, 0, 1))
            self.add_log("Server connection test successful")
            self.show_popup("Connection Test", "Server connection is working properly")
        else:
            self.is_connected = False
            self.update_status("Connection Failed", (1, 0, 0, 1))
            self.add_log("Server connection test failed")
            self.show_popup("Connection Test", "Server connection failed")
        
        Clock.schedule_once(lambda dt: self.update_progress(0), 2)
    
    def clear_log(self, instance):
        """Clear log"""
        self.log_text = ""
        if hasattr(self, 'log_label'):
            self.log_label.text = "Log cleared\n"
        self.add_log("Log cleared")
        self.update_status("Log cleared", (0, 1, 1, 1))

if __name__ == '__main__':
    SmartLockControlApp().run()