import keyboard
import pyautogui
import threading
import tkinter as tk
from tkinter import messagebox
import time
import webbrowser
from pathlib import Path

win_width = 360
win_height = 580
version = 2.2


class MouseClickerApp:
    def __init__(self, master):
        self.master = master
        self.master.title(f"鼠标连点器 v{version}")

        self.running = False
        self.click_interval = tk.DoubleVar(value=0.1)
        self.hold_duration = tk.DoubleVar(value=0)
        self.stop_after_minutes = tk.IntVar(value=0)
        self.stop_after_seconds = tk.DoubleVar(value=0)
        self.hold_enabled = tk.BooleanVar(value=False)
        self.auto_stop_enabled = tk.BooleanVar(value=False)
        self.click_type = tk.StringVar(value="left")  # 默认选择左键

        self.interval_entry = None
        self.hold_entry = None
        self.hold_checkbox = None
        self.stop_after_minutes_entry = None
        self.stop_after_seconds_entry = None
        self.auto_stop_checkbox = None
        self.start_stop_button = None
        self.left_button = None
        self.right_button = None

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

        self.hold_entry = tk.Entry(self.master, textvariable=self.hold_duration, state="disabled")
        self.hold_entry.pack()

        # 复选框，启用按住功能
        self.hold_checkbox = tk.Checkbutton(self.master, text="启用按住鼠标键功能", variable=self.hold_enabled, cursor="hand2",
                                            command=lambda: self.hold_entry.config(state="normal") if self.hold_enabled.get() else self.hold_entry.config(state="disabled"))
        self.hold_checkbox.pack()

        # 设置多少秒后自动停止
        stop_after_label = tk.Label(self.master, text="设定自动停止时长:")
        stop_after_label.pack(pady=10)

        stop_after_frame = tk.Frame(self.master)
        stop_after_frame.pack()
        self.stop_after_minutes_entry = tk.Entry(stop_after_frame, width=5, textvariable=self.stop_after_minutes, state="disabled")
        self.stop_after_minutes_entry.grid(row=0, column=0, padx=5)
        tk.Label(stop_after_frame, text="分").grid(row=0, column=1)
        self.stop_after_seconds_entry = tk.Entry(stop_after_frame, width=5, textvariable=self.stop_after_seconds, state="disabled")
        self.stop_after_seconds_entry.grid(row=0, column=2, padx=5)
        tk.Label(stop_after_frame, text="秒").grid(row=0, column=3)

        # 复选框，启用自动停止功能
        self.auto_stop_checkbox = tk.Checkbutton(self.master, text="启用自动停止", variable=self.auto_stop_enabled, cursor="hand2",
                                                 command=lambda: (
                                                     self.stop_after_minutes_entry.config(state="normal"),
                                                     self.stop_after_seconds_entry.config(state="normal")) if self.auto_stop_enabled.get() else (
                                                     self.stop_after_minutes_entry.config(state="disabled"),
                                                     self.stop_after_seconds_entry.config(state="disabled")))
        self.auto_stop_checkbox.pack()

        # 选择点击类型，左键或右键
        click_type_frame = tk.Frame(self.master)
        click_type_frame.pack(pady=5)

        self.left_button = tk.Radiobutton(click_type_frame, text="左键", variable=self.click_type,
                                          value="left", cursor="hand2")
        self.left_button.pack(side=tk.LEFT, padx=10)

        self.right_button = tk.Radiobutton(click_type_frame, text="右键", variable=self.click_type,
                                           value="right", cursor="hand2")
        self.right_button.pack(side=tk.LEFT, padx=10)

        # 启动/停止按钮
        self.start_stop_button = tk.Button(self.master, text="启动连点器\n热键 Ctrl+Alt+F6", cursor='no',
                                           width=16, height=2, command=self.toggle_clicker)
        self.start_stop_button.pack(pady=20)

        # 强制退出的说明
        force2exit = tk.Label(self.master, text="强烈建议使用热键启动/停止连点器\n尽量避免点击按钮，防止误触\n\n强制退出快捷键: Ctrl+Shift+Q", fg="red")
        force2exit.pack()

        # 版权信息与联系方式
        cprt = tk.Label(self.master, text=f"JupiterLyr © Version {version}", font=("Times New Roman", 9))
        email = tk.Label(self.master, text="✉联系作者", font=("宋体", 9), fg="blue", cursor="hand2")
        cprt.pack(pady=25)
        email.place(x=win_width-85, y=win_height-25)
        email.bind("<Button-1>", lambda event: send_email())

    def setup_keyboard_shortcuts(self):
        # 监听快捷键
        keyboard.add_hotkey('ctrl+alt+f6', lambda: self.toggle_clicker())
        keyboard.add_hotkey('ctrl+shift+q', lambda: self.master.quit())  # 退出应用

    def toggle_clicker(self):
        if not self.running:
            try:
                interval = self.click_interval.get()
            except tk.TclError as e:
                tk.messagebox.showerror("错误", "点击间隔填写内容不合法，请重新修改！\n" + str(e))
                return
            if interval < 0.1:
                tk.messagebox.showerror("错误", "点击间隔不得小于0.1秒")
                return

            # 检查是否启用自动停止功能
            if self.auto_stop_enabled.get():
                try:
                    stop_minutes = self.stop_after_minutes.get()
                    stop_seconds = self.stop_after_seconds.get()
                    if stop_seconds >= 60:
                        con = tk.messagebox.askokcancel("注意", "秒钟数会与设定的分钟数叠加，您设定的秒数已不低于60秒，确定要继续吗？\nTips: 仅设定秒数依旧可以正常运行哦")
                        if not con:
                            return
                except Exception as e:
                    tk.messagebox.showerror("错误", "设定的自动停止时间不合法，请重新修改！\n" + str(e))
                    return
                else:
                    stop_after = stop_minutes * 60 + stop_seconds
                    if stop_after > 1:
                        self.auto_stop_timer = threading.Timer(stop_after, self.stop_clicker)
                        self.auto_stop_timer.start()
                    else:
                        tk.messagebox.showerror("错误", "自动停止时间不得小于1秒")
                        return

            self.interval_entry.config(state="disabled")
            self.hold_entry.config(state="disabled")
            self.hold_checkbox.config(state="disabled")
            self.stop_after_minutes_entry.config(state="disabled")
            self.stop_after_seconds_entry.config(state="disabled")
            self.auto_stop_checkbox.config(state="disabled")
            self.left_button.config(state="disabled")
            self.right_button.config(state="disabled")
            self.running = True
            test_interval = interval - 0.13  # 时间间隔校准

            # 检查是否启用按住功能
            if self.hold_enabled.get():
                try:
                    hold_duration = self.hold_duration.get()
                except Exception as e:
                    tk.messagebox.showerror("错误", "设定的按住时间不合法，请重新修改！\n" + str(e))
                    return
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

            self.start_stop_button.config(text="按下 Ctrl+Alt+F6\n以停止连点器")

        else:
            self.stop_clicker()

    def clicker_thread(self, interval):
        time.sleep(0.1)
        while self.running:
            if self.click_type.get() == "left":
                pyautogui.click(button='left')
            elif self.click_type.get() == "right":
                pyautogui.click(button='right')
            time.sleep(interval)

    def hold_click_thread(self, hold_duration, interval):
        time.sleep(0.1)
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
        self.start_stop_button.config(text="正在关闭线程", state="disabled", cursor="arrow")

        if hasattr(self, 'auto_stop_timer') and self.auto_stop_timer.is_alive():
            self.auto_stop_timer.cancel()  # 停止自动停止计时器
        if hasattr(self, 'hold_thread') and self.hold_thread.is_alive():
            self.hold_thread.join(2)  # 停止按住线程，超过2秒自动判定超时，主进程不再等待子线程
        if hasattr(self, 'click_thread') and self.click_thread.is_alive():
            self.click_thread.join(3)  # 停止连点线程，超过3秒自动判定超时，主进程不再等待子线程

        self.interval_entry.config(state="normal")
        self.hold_checkbox.config(state="normal")
        self.auto_stop_checkbox.config(state="normal")
        self.left_button.config(state="normal")
        self.right_button.config(state="normal")
        if self.hold_enabled.get():
            self.hold_entry.config(state="normal")
        if self.auto_stop_enabled.get():
            self.stop_after_minutes_entry.config(state="normal")
            self.stop_after_seconds_entry.config(state="normal")
        self.start_stop_button.config(text="启动连点器请用\n热键 Ctrl+Alt+F6", state="normal", cursor="no")

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
    root.geometry(str(win_width) + "x" + str(win_height))
    root.resizable(False, False)
    root.iconbitmap(Path(__file__).parent / 'icon.ico')
    app = MouseClickerApp(root)
    app.start()
