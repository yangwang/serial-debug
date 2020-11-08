import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import serial
import threading
import time


class SerialThread:
    def __init__(self, port, baudrate=9600, bytesize=8, stopbits=1, timeout=1):
        self.my_serial = serial.Serial()
        self.my_serial.port = port  # 端口号
        self.my_serial.baudrate = baudrate  # 波特率
        self.my_serial.bytesize = bytesize  # 数据位
        self.my_serial.stopbits = stopbits  # 停止位
        self.my_serial.timeout = timeout

        self.alive = False  # 当 alive 为 True，读写线程会进行
        self.thread_read = None  # 读线程
        self.thread_write = None  # 写线程

        self.win = tk.Tk()  # 窗口
        self.win.title("Python串口调试工具")  # 窗口标题
        self.win.resizable(0, 0)  # 窗口大小不可调
        self.win.protocol("WM_DELETE_WINDOW", self.func_delete)  # 关闭窗口时调用self.func_delete函数

        frame = tk.Frame(self.win)  # frame
        frame.grid(column=0, row=0, padx=10, pady=10, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.button_conn = tk.Button(frame, text="连接", font=("Times", 12), width=10, command=self.start())  # “连接”按钮
        self.button_conn.grid(column=4, row=1)

        tk.Label(frame, text="接收到的信息：", font=("Times", 12)).grid(column=1, row=3, columnspan=2, sticky=(tk.W, tk.S))
        self.OutputText = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=11,
                                                    font=("Times", 12))  # ScrolledText，显示接收到的串口信息
        self.OutputText.grid(column=1, row=4, sticky=tk.W, pady=20, columnspan=4)

        tk.Label(frame, text="发送消息：", font=("Times", 12)).grid(column=1, row=5, columnspan=2, sticky=(tk.W, tk.S))
        self.send_str = tk.StringVar()  # 储存用户输入的指令
        entry_send = tk.Entry(frame, textvariable=self.send_str, width=30, font=("Times", 12))  # 用户输入指令到Entry
        entry_send.bind("<Return>", self.send_mess_event)  # 当用户按下回车键后，自动将指令发送给串口
        entry_send.grid(column=1, row=6, columnspan=3, sticky=tk.W)

        self.win.mainloop()  # 进入mainloop

    def start(self):
        self.my_serial.open()
        if self.my_serial.isOpen():
            self.alive = True

            # 设置一个线程为守护线程，就表示这个线程不重要，在进程退出时，不用等待这个线程退出
            self.thread_read = threading.Thread(target=self.read)
            self.thread_read.setDaemon(True)  # 当主线程结束，读线程和主线程一并退出
            self.thread_read.start()

            return True
        else:
            return False

    def stop(self):
        self.alive = False
        if self.my_serial.isOpen():
            self.my_serial.close()

    def read(self):
        while self.alive:
            try:
                time.sleep(0.01)
                n = self.my_serial.inWaiting()  # 返回接收缓存中的字节数
                if n:
                    data = self.my_serial.read(n).decode("gbk")  # 解码成 gbk 码（处理中文字符问题）
                    self.OutputText.insert(tk.END, str(data))  # 将读到的信息显示在界面
                    self.OutputText.see(tk.END)  # 一直看着末尾
            except Exception as ex:
                print(ex)

    # 发送指令，Entry，由回车键<"Return">触发
    def send_mess_event(self, event):
        receive = self.send_str.get()
        self.my_serial.write(receive.encode("gbk"))  # 解码成 gbk 码（处理中文字符问题）

    def write(self):
        while self.alive:
            try:
                receive = input()
                self.my_serial.write(receive.encode("gbk"))  # 解码成 gbk 码（处理中文字符问题）
            except Exception as ex:
                print(ex)

    # 关闭串口对象和线程，当用户关闭窗口时触发
    def func_delete(self):
        if self.my_serial.isOpen():
            self.my_serial.close()  # 关闭串口对象
        time.sleep(0.5)
        self.win.destroy()  # 销毁窗口


if __name__ == "__main__":
    my_serial = SerialThread("COM6")
