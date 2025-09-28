# Mouse Clicker - 鼠标连点器
## Content - 目录
[Project Brief — 项目简介](#project-brief-br-项目简介) </br>
[Dependencies Installation — 安装依赖项](#dependencies-installation-br-安装依赖项) </br>
[Running Program — 运行程序](#运行程序-br-running-program) </br>
[Contact with Me — 联系作者](#联系作者-br-contact-with-me)

## Project Brief </br> 项目简介
This is a Python-based mouse continuous clicker software, including a classic clicker software and a mouse mapping software.
For the former, the software has realized the basic functions, and supports the settings such as clicking interval,
holding down the mouse time, automatic closing, left-clicking and right-clicking, etc.
For the latter, at present, only simple functions are supported: pressing a specific key is equivalent to clicking the left mouse button once.</br>
More functions are still under development.
</br>
这是一款基于 Python 的鼠标连点器软件，包含一个经典的连点器软件和一个鼠标映射软件。
前者已经实现基本功能，支持点击间隔时间、按住鼠标时间、自动关闭、左键右键等设置。
后者目前只支持简单功能：按下特定按键等效于点击一次鼠标左键。</br>
更多功能还在开发中。

The project is based on a single file, and the functions are not split because of the low code complexity.
</br>
该项目基于单文件，由于代码复杂度较低，没有将各功能拆分。
```text
Mouse_Clicker/
├── ClickerV1.2.py     # almost initial version
├── ClickerV1.3.py
├── ClickerV1.4.py
├── ClickerV2.0.py
├── ClickerV2.1.py     # updated version with a few bugs
├── ClickerV2.2.py     # updated version after fixing bugs
├── icon.ico
├── MouseMapperV1.0.py # exploration edition
├── README.md
└── requirements
```
Previous versions are no longer in use. Give priority to using the updated version.
</br>
旧版已不再使用，优先选择更新的版本。

## Dependencies Installation </br> 安装依赖项
Run the following command in the terminal in the project root directory to install the dependencies:
</br>
在项目根目录下的终端运行以下命令安装依赖项：
```bash
pip install -r requirements
```

## Running Program </br> 运行程序
Start the application by running the following command in the terminal in the project root directory:
</br>
在项目根目录下的终端运行以下命令启动应用程序：
```bash
python ClickerV2.2.py
```
When the program is running, use the shortcut key `Ctrl+Alt+F6` to start or stop.
Try not to click the button with the mouse to avoid touching it by mistake.
</br>
程序运行时，使用快捷键 `Ctrl+Alt+F6` 启动或停止，尽量不要使用鼠标点击按钮，以免误触。

The global monitoring hotkey `CTRL+SHIFT+Q` can force the thread to end and exit the software.
</br>
全局监听热键 `Ctrl+Shift+Q` 可以强制结束线程、退出软件。

## Contact with Me </br> 联系作者
If there are any questions, you can contact me at:</br>
如果有任何问题，您可以通过以下方式联系我：</br>
[Click Here to Email Me Now](mailto:jupiterlyr@foxmail.com)
