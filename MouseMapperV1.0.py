import keyboard
import pyautogui
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import time
from pathlib import Path

WIN_WIDTH = 630
WIN_HEIGHT = 520
VERSION = 1.0


class MouseClickerApp:
    def __init__(self, master):
        self.master = master
        self.master.title(f"鼠标映射器 - v{VERSION}")

        # 状态变量
        self.is_enabled = False  # 记录是否启动
        self.running = True  # 用于守护线程
        self.left_key = None
        self.right_key = None
        self.left_pressed = False
        self.right_pressed = False
        self.click_mode = tk.StringVar(value="click")
        self.modifier_var = tk.StringVar(value="ctrl")  # 默认 Ctrl+<Key>
        self.hotkeys_registered = {}

        # 可用的键盘按键列表
        self.available_keys = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
            'Space', 'Enter', 'Up', 'Down', 'Left', 'Right'
        ]
        self.create_widgets()
        self.dummy_thread()  # 保持主线程不退出
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)  # 重写关闭操作

    def create_widgets(self):
        """GUI布局"""
        main = tk.Frame(self.master, padx=20, pady=15)
        main.pack(fill=tk.BOTH, expand=True)
        tk.Label(main, text="鼠标按键映射器", font=("黑体", 16)).pack(pady=(0, 12))

        # 1. 下拉框选择映射键
        combo_line = tk.Frame(main)
        combo_line.pack(fill=tk.X, pady=6)
        tk.Label(combo_line, text="鼠标左键映射:", font=("黑体", 11)).pack(side=tk.LEFT, padx=(0, 6))
        self.left_combo = ttk.Combobox(combo_line, values=self.available_keys, width=10,
                                       state="readonly", font=("黑体", 11))
        self.left_combo.pack(side=tk.LEFT)
        self.left_combo.bind("<<ComboboxSelected>>", self.on_left_key_selected)

        self.right_combo = ttk.Combobox(combo_line, values=self.available_keys, width=10,
                                        state="readonly", font=("黑体", 11))
        self.right_combo.pack(side=tk.RIGHT)
        tk.Label(combo_line, text="鼠标右键映射:", font=("黑体", 11)).pack(side=tk.RIGHT, padx=(20, 6))
        self.right_combo.bind("<<ComboboxSelected>>", self.on_right_key_selected)

        # 2. 快捷键组合
        mod_frame = tk.LabelFrame(main, text="快捷键组合", font=("黑体", 11), padx=10, pady=8)
        mod_frame.pack(fill=tk.X, pady=8)

        tk.Radiobutton(mod_frame, text="直接采用设定按键", variable=self.modifier_var,
                       value="none", command=self.on_modifier_changed, font=("黑体", 11)).pack(anchor=tk.W)
        row2 = tk.Frame(mod_frame)
        row2.pack(fill=tk.X, pady=4)
        for txt, val in [("Ctrl+", "ctrl"), ("Ctrl+Shift+", "ctrl+shift"), ("Ctrl+Alt+", "ctrl+alt")]:
            tk.Radiobutton(row2, text=txt + "<Key>", variable=self.modifier_var,
                           value=val, command=self.on_modifier_changed,
                           font=("黑体", 11)).pack(side=tk.LEFT, padx=(0, 25), anchor=tk.W)
        row3 = tk.Frame(mod_frame)
        row3.pack(fill=tk.X, pady=4)
        for txt, val in [("Alt+", "alt"), ("Shift+", "shift"), ("Alt+Shift+", "alt+shift")]:
            tk.Radiobutton(row3, text=txt + "<Key>", variable=self.modifier_var,
                           value=val, command=self.on_modifier_changed,
                           font=("黑体", 11)).pack(side=tk.LEFT, padx=(0, 25), anchor=tk.W)

        # 3. 动作模式
        mode_frame = tk.LabelFrame(main, text="鼠标动作模式", font=("黑体", 11), padx=10, pady=6)
        mode_frame.pack(fill=tk.X, pady=8)
        tk.Radiobutton(mode_frame, text="点击模式（每按下一次快捷键，进行一次完整点击）", variable=self.click_mode,
                       value="click", font=("黑体", 11)).pack(anchor=tk.W)
        tk.Radiobutton(mode_frame, text="切换模式（按下快捷键后，切换“按住”“释放”状态）", variable=self.click_mode,
                       value="toggle", font=("黑体", 11)).pack(anchor=tk.W)

        # 4. 显示快捷键
        status_line = tk.Frame(main)
        status_line.pack(fill=tk.X, pady=6)
        self.left_status = tk.Label(status_line, text="左键: 未设置", fg="red", font=("黑体", 11))
        self.left_status.pack(side=tk.LEFT, padx=(0, 25))
        self.right_status = tk.Label(status_line, text="右键: 未设置", fg="red", font=("黑体", 11))
        self.right_status.pack(side=tk.LEFT)

        # ---------- 5. 按钮行 ----------
        btn_line = tk.Frame(main)
        btn_line.pack(pady=10)
        self.enable_btn = tk.Button(btn_line, text="启  用", width=12, font=("黑体", 11),
                                    fg="green", cursor="hand2", command=self.toggle_enable)
        self.enable_btn.pack(side=tk.LEFT, padx=(0, 15))
        tk.Button(btn_line, text="清除设置", width=10, font=("黑体", 11), cursor="hand2",
                  command=self.clear_settings).pack(side=tk.LEFT)

        # ---------- 6. 版权 ----------
        tk.Label(main, text=f"JupiterLyr © Version {VERSION}", font=("Times New Roman", 9)).pack(pady=(15, 0))

    def toggle_enable(self):
        """切换启停状态"""
        if self.is_enabled:
            self.do_stop()
        else:
            self.do_start()
        self.update_enable_button()

    def do_start(self):
        """真正启用"""
        if not self.left_key and not self.right_key:
            messagebox.showwarning("提示", "请先设置左键或右键映射！")
            return
        self.register_current_keys()
        self.is_enabled = True

    def do_stop(self):
        """真正停止"""
        self.unregister_all()
        self.is_enabled = False
        self.release_mouse()

    def update_enable_button(self):
        self.enable_btn.config(text="停  止" if self.is_enabled else "启  用", fg="red" if self.is_enabled else "green")

    def register_current_keys(self):
        """按当前设置注册热键"""
        self.unregister_all()
        mod = self.modifier_var.get()
        if self.left_key:
            hotkey = self._build_hotkey(mod, self.left_key)
            keyboard.add_hotkey(hotkey, self.handle_left_click, suppress=True)
            self.hotkeys_registered['left'] = hotkey
        if self.right_key:
            hotkey = self._build_hotkey(mod, self.right_key)
            keyboard.add_hotkey(hotkey, self.handle_right_click, suppress=True)
            self.hotkeys_registered['right'] = hotkey
        self.update_status()

    def unregister_all(self):
        """注销所有已注册热键"""
        for hk in self.hotkeys_registered.values():
            keyboard.remove_hotkey(hk)
        self.hotkeys_registered.clear()

    @staticmethod
    def _build_hotkey(mod, key):
        """若使用原始设定按键，返回按键本身；否则与组合键联合返回"""
        return key if mod == "none" else f"{mod}+{key}"

    def on_modifier_changed(self):
        if self.is_enabled:
            self.register_current_keys()

    def on_left_key_selected(self, _):
        k = self.left_combo.get()
        if k == self.right_key:
            messagebox.showwarning("警告", "该主键已被右键使用！")
            self.left_combo.set("")
            return
        self.left_key = k
        if self.is_enabled:
            self.register_current_keys()

    def on_right_key_selected(self, _):
        k = self.right_combo.get()
        if k == self.left_key:
            messagebox.showwarning("警告", "该主键已被左键使用！")
            self.right_combo.set("")
            return
        self.right_key = k
        if self.is_enabled:
            self.register_current_keys()

    def update_status(self):
        mod = self.modifier_var.get().replace('+', '+').title()
        if self.left_key:
            self.left_status.config(text=f"左键: {self._build_hotkey(mod, self.left_key)}", foreground="green")
        else:
            self.left_status.config(text="左键: 未设置", foreground="red")
        if self.right_key:
            self.right_status.config(text=f"右键: {self._build_hotkey(mod, self.right_key)}", foreground="green")
        else:
            self.right_status.config(text="右键: 未设置", foreground="red")

    def handle_left_click(self):
        if self.click_mode.get() == "toggle":
            if not self.left_pressed:
                pyautogui.mouseDown(button='left')
                self.left_pressed = True
            else:
                pyautogui.mouseUp(button='left')
                self.left_pressed = False
        else:
            pyautogui.click(button='left')

    def handle_right_click(self):
        if self.click_mode.get() == "toggle":
            if not self.right_pressed:
                pyautogui.mouseDown(button='right')
                self.right_pressed = True
            else:
                pyautogui.mouseUp(button='right')
                self.right_pressed = False
        else:
            pyautogui.click(button='right')

    def clear_settings(self):
        self.left_combo.set("")
        self.right_combo.set("")
        self.left_key = None
        self.right_key = None
        if self.is_enabled:
            self.register_current_keys()
        else:
            self.update_status()
        self.release_mouse()

    def release_mouse(self):
        """释放鼠标"""
        if self.left_pressed:
            pyautogui.mouseUp(button='left')
            self.left_pressed = False
        if self.right_pressed:
            pyautogui.mouseUp(button='right')
            self.right_pressed = False

    def dummy_thread(self):
        """线程监听"""
        def _run():
            while self.is_enabled:
                time.sleep(0.2)
        threading.Thread(target=_run, daemon=True).start()

    def on_close(self):
        """窗口关闭时清理"""
        self.do_stop()
        self.is_enabled = False
        self.master.quit()

    def start(self):
        self.master.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(str(WIN_WIDTH) + "x" + str(WIN_HEIGHT))
    root.resizable(False, False)
    try:
        root.iconbitmap(Path(__file__).parent / 'icon2.ico')
    except Exception as e:
        messagebox.showwarning("Warning", f"The icon file not found!\n{e}")
    app = MouseClickerApp(root)
    app.start()
