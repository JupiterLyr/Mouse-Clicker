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
        self.master.title("鼠标连点器 v1.2")

        self.running = False
        self.click_interval = tk.DoubleVar(value=0.1)
        self.stop_after = tk.DoubleVar(value=0)
        self.auto_stop_enabled = tk.BooleanVar(value=False)

        self.create_widgets()
        self.setup_keyboard_shortcuts()

    def create_widgets(self):
        # 设置点击间隔
        interval_label = tk.Label(self.master, text="点击间隔（秒）:")
        interval_label.pack(pady=10)

        self.interval_entry = tk.Entry(self.master, textvariable=self.click_interval)
        self.interval_entry.pack()

        # 设置多少秒后自动停止
        stop_after_label = tk.Label(self.master, text="自动停止（秒）:")
        stop_after_label.pack(pady=10)

        self.stop_after_entry = tk.Entry(self.master, textvariable=self.stop_after)
        self.stop_after_entry.pack()

        # 复选框，启用自动停止功能
        self.auto_stop_checkbox = tk.Checkbutton(self.master, text="启用自动停止", variable=self.auto_stop_enabled)
        self.auto_stop_checkbox.pack()

        # 启动/停止按钮
        self.start_stop_button = tk.Button(self.master, text="启动连点器 (Ctrl+F6)", command=self.toggle_clicker)
        self.start_stop_button.pack(pady=20)

        # 强制退出的说明
        self.force2exit = tk.Label(self.master, text="建议使用快捷键启动/停止连点器，以免误触\n强制退出快捷键: Ctrl+Shift+Q\n", fg="red")
        self.force2exit.pack()

        # 版权信息与联系方式
        self.cprt = tk.Label(self.master, text="制作人：JupiterLyr ©", font=("宋体", 9))
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
            if interval <= 0:
                tk.messagebox.showerror("错误", "点击间隔必须大于0秒")
                return

            # 检查是否启用自动停止功能
            if self.auto_stop_enabled.get():
                stop_after = self.stop_after.get()
                if stop_after > 1:
                    self.auto_stop_timer = threading.Timer(stop_after, self.stop_clicker)
                    self.auto_stop_timer.start()
                else:
                    tk.messagebox.showerror("错误", "自动停止时间必须大于1秒")
                    return

            self.running = True
            self.start_stop_button.config(text="停止连点器 (Ctrl+F6)")
            self.click_thread = threading.Thread(target=self.clicker_thread, args=(interval,))
            self.click_thread.start()

        else:
            self.stop_clicker()

    def clicker_thread(self, interval):
        while self.running:
            pyautogui.click()
            time.sleep(interval)

    def stop_clicker(self):
        self.running = False
        self.start_stop_button.config(text="启动连点器 (Ctrl+F6)")

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
    root.geometry("360x360")
    root.resizable(False, False)
    root.iconbitmap(Path(__file__).parent / 'icon.ico')
    app = MouseClickerApp(root)
    app.start()
