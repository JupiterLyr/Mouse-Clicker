import keyboard
import pyautogui
import threading
import tkinter as tk
from tkinter import messagebox
import time
import webbrowser
from pathlib import Path


class MouseClickerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("鼠标连点器 v1.4")

        self.running = False
        self.click_interval = tk.DoubleVar(value=0.1)
        self.stop_after_minutes = tk.IntVar(value=0)
        self.stop_after_seconds = tk.DoubleVar(value=0)
        self.auto_stop_enabled = tk.BooleanVar(value=False)
        self.click_type = tk.StringVar(value="left")  # 默认选择左键

        self.create_widgets()
        self.setup_keyboard_shortcuts()

    def create_widgets(self):
        # 设置点击间隔
        interval_label = tk.Label(self.master, text="点击间隔（秒）:")
        interval_label.pack(pady=10)

        self.interval_entry = tk.Entry(self.master, textvariable=self.click_interval)
        self.interval_entry.pack()

        # 设置按压持续时间
        hold_label = tk.Label(self.master, text="按住时长（秒）:")
        hold_label.pack(pady=10)

        self.hold_duration = tk.DoubleVar(value=0)
        self.hold_entry = tk.Entry(self.master, textvariable=self.hold_duration)
        self.hold_entry.pack()

        # 复选框，启用按住功能
        self.hold_enabled = tk.BooleanVar(value=False)
        self.hold_checkbox = tk.Checkbutton(self.master, text="启用按住鼠标键功能", variable=self.hold_enabled, cursor="hand2")
        self.hold_checkbox.pack()

        # 设置多少秒后自动停止
        stop_after_label = tk.Label(self.master, text="自动停止（秒）:")
        stop_after_label.pack(pady=10)

        stop_after_frame = tk.Frame(self.master)
        stop_after_frame.pack()
        self.stop_after_minutes_entry = tk.Entry(stop_after_frame, width=5, textvariable=self.stop_after_minutes)
        self.stop_after_minutes_entry.grid(row=0, column=0, padx=5)
        tk.Label(stop_after_frame, text="分").grid(row=0, column=1)
        self.stop_after_seconds_entry = tk.Entry(stop_after_frame, width=5, textvariable=self.stop_after_seconds)
        self.stop_after_seconds_entry.grid(row=0, column=2, padx=5)
        tk.Label(stop_after_frame, text="秒").grid(row=0, column=3)

        # 复选框，启用自动停止功能
        self.auto_stop_checkbox = tk.Checkbutton(self.master, text="启用自动停止", variable=self.auto_stop_enabled, cursor="hand2")
        self.auto_stop_checkbox.pack()

        # 选择点击类型，左键或右键
        click_type_frame = tk.Frame(self.master)
        click_type_frame.pack(pady=5)

        left_button = tk.Radiobutton(click_type_frame, text="左键", variable=self.click_type, value="left", cursor="hand2")
        left_button.pack(side=tk.LEFT, padx=10)

        right_button = tk.Radiobutton(click_type_frame, text="右键", variable=self.click_type, value="right", cursor="hand2")
        right_button.pack(side=tk.LEFT, padx=10)

        # 启动/停止按钮
        self.start_stop_button = tk.Button(self.master, text="启动连点器\n请使用热键 Ctrl+F6", cursor='no',
                                           width=16, height=2, command=self.toggle_clicker)
        self.start_stop_button.pack(pady=20)

        # 强制退出的说明
        self.force2exit = tk.Label(self.master, text="建议使用热键启动/停止连点器，以免误触\n强制退出快捷键: Ctrl+Shift+Q\n", fg="red")
        self.force2exit.pack()

        # 版权信息与联系方式
        self.cprt = tk.Label(self.master, text="Made by JupiterLyr ©", font=("Times New Roman", 9))
        self.email = tk.Label(self.master, text="✉联系作者", font=("宋体", 9), fg="blue", cursor="hand2")
        self.cprt.pack()
        self.email.place(x=2, y=2)
        self.email.bind("<Button-1>", lambda event: send_email())

    def setup_keyboard_shortcuts(self):
        # 监听快捷键
        keyboard.add_hotkey('ctrl+f6', lambda: self.toggle_clicker())
        keyboard.add_hotkey('ctrl+shift+q', lambda: self.master.quit())  # 退出应用

    def toggle_clicker(self):
        if not self.running:
            interval = self.click_interval.get()
            if interval < 0.1:
                tk.messagebox.showerror("错误", "点击间隔不得小于0.1秒")
                return

            # 检查是否启用自动停止功能
            if self.auto_stop_enabled.get():
                # stop_after = self.stop_after.get()
                stop_minutes = self.stop_after_minutes.get()
                stop_seconds = self.stop_after_seconds.get()
                stop_after = stop_minutes * 60 + stop_seconds
                if stop_after > 1:
                    self.auto_stop_timer = threading.Timer(stop_after, self.stop_clicker)
                    self.auto_stop_timer.start()
                else:
                    tk.messagebox.showerror("错误", "自动停止时间不得小于1秒")
                    return

            self.running = True
            test_interval = interval - 0.13  # 时间间隔校准

            # 检查是否启用按住功能
            if self.hold_enabled.get():
                hold_duration = self.hold_duration.get()
                if hold_duration < 0.1:
                    tk.messagebox.showerror("错误", "按住时长不得小于0.1秒")
                    return
                if test_interval <= 0:
                    self.hold_thread = threading.Thread(target=self.hold_click_thread,
                                                        args=(hold_duration - 0.1, interval - 0.1,))
                else:
                    self.hold_thread = threading.Thread(target=self.hold_click_thread,
                                                        args=(hold_duration - 0.1, interval - 0.13,))
                self.hold_thread.start()
            else:
                if test_interval <= 0:
                    self.click_thread = threading.Thread(target=self.clicker_thread, args=(interval - 0.1,))
                else:
                    self.click_thread = threading.Thread(target=self.clicker_thread, args=(interval - 0.12,))
                self.click_thread.start()

            self.start_stop_button.config(text="停止连点器\n推荐用热键 Ctrl+F6", cursor='hand2')

        else:
            self.stop_clicker()

    def clicker_thread(self, interval):
        while self.running:
            if self.click_type.get() == "left":
                pyautogui.click(button='left')
            elif self.click_type.get() == "right":
                pyautogui.click(button='right')
            time.sleep(interval)

    def hold_click_thread(self, hold_duration, interval):
        while self.running and self.hold_enabled.get():
            if self.click_type.get() == "left":
                pyautogui.mouseDown(button='left')
                time.sleep(hold_duration)
                pyautogui.mouseUp(button='left')
            elif self.click_type.get() == "right":
                pyautogui.mouseDown(button='right')
                time.sleep(hold_duration)
                pyautogui.mouseUp(button='right')
            time.sleep(interval)

    def stop_clicker(self):
        self.running = False
        self.start_stop_button.config(text="启动连点器\n请使用热键 Ctrl+F6", cursor='no')

    def start(self):
        self.master.mainloop()


def send_email():
    if_send = tk.messagebox.askquestion(title="联系作者", message="即将给jupiterlyr@foxmail.com发送邮件，是否继续？\n点击“否”以获取更多联系方式")
    if if_send == 'yes':
        webbrowser.open("mailto:'jupiterlyr@foxmail.com'")
    else:
        tk.messagebox.showinfo(title="联系作者", message="您也可以添加微信并备注来意：JupiterLyr\n期待您的反馈！")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("360x540")
    root.resizable(False, False)
    root.iconbitmap(Path(__file__).parent / 'icon.ico')
    app = MouseClickerApp(root)
    app.start()
