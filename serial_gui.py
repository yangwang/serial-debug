import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import serial
import serial.tools.list_ports
import threading
import time


class SerialGUI:
    ser = serial.Serial()  # 串口对象
    ser_state = False  # 用于指示串口是否打开

    def __init__(self):
        # 创建界面
        self.win = tk.Tk()  # 窗口
        self.win.title("Python串口调试工具")  # 窗口标题
        self.win.resizable(0, 0)  # 窗口大小不可调
        self.win.protocol("WM_DELETE_WINDOW", self.func_delete)  # 关闭窗口时调用self.func_delete函数

        frame = tk.Frame(self.win)  # frame
        frame.grid(column=0, row=0, padx=10, pady=10, sticky=(tk.N, tk.W, tk.E, tk.S))

        txt_com = tk.Label(frame, text="串口号", font=("Times", 12))  # label，显示“串口号”
        txt_com.grid(column=1, row=1, sticky=tk.W)

        self.COM = tk.StringVar()  # 用于储存选中的串口号
        self.box = ttk.Combobox(frame, textvariable=self.COM, state="readonly", width=10, font=("Times", 12))
        # 当左键单击Combobox后，调用self.get_port_serial，获取所有可用的串口号，并显示在Combobox内
        self.box.bind("<Button-1>", self.get_port_serial)
        self.box.bind("<<ComboboxSelected>>", self.conn_button_on)  # 当用户选择串口后，调用conn_button_on函数，使按钮state = normal
        self.box.grid(column=2, row=1, sticky=tk.W)

        self.txt_com_state = tk.Label(frame, width=5)  # 用于显示当前的串口连接状态
        self.txt_com_state.grid(column=3, row=1, padx=20)

        labelBaudrate = tk.Label(frame, text="波特率 ", font=("Times", 12))  # label，显示“波特率”
        labelBaudrate.grid(column=1, row=2, pady=20, sticky=tk.W)
        self.Baudrate = tk.IntVar(value=9600)  # 储存波特率
        entryBaudrate = tk.Entry(frame, textvariable=self.Baudrate, font=("Times", 12), width=10)
        entryBaudrate.grid(column=2, row=2, pady=20, sticky=tk.W)

        self.button_conn = tk.Button(frame, text="连接", font=("Times", 12), width=10, command=self.func_conn)  # “连接”按钮
        self.button_conn["state"] = "disabled"  # 设置按钮不可用
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

        self.button_send = tk.Button(frame, text="发送", font=("Times", 12), width=10,
                                     command=self.send_mess)  # “发送”按钮，触发self.send_mess函数
        self.button_send["state"] = "disabled"  # 设置按钮不可用
        self.button_send.grid(column=4, row=6)

        self.win.mainloop()  # 进入mainloop

    # 获得所有可用的串口号
    def get_port_serial(self, event):
        port_serial = []
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) > 0:
            for i in range(0, len(port_list)):
                port_serial.append(port_list[i][0])

        self.box['values'] = port_serial

    # 当用户选择串口号后，让“连接”按钮可用
    def conn_button_on(self, event):
        self.button_conn["state"] = "normal"

    # 显示接收到的串口数据
    def ReceiveData(self):
        while self.ser.isOpen():
            time.sleep(0.2)  # 等0.2 s
            try:
                # 如果串口处有信息，才执行
                if self.ser.in_waiting:
                    rec = self.ser.read(self.ser.in_waiting).decode("gbk")  # 读取串口信息
                    self.OutputText.insert(tk.END, '接收到的消息：\n' + str(rec) + '\n')  # 将读到的信息显示在界面
                    self.OutputText.see(tk.END)  # 一直看着末尾

            except:
                pass

    # 点击“连接”按钮后执行
    def func_conn(self):
        # 当未连接时，连接串口
        if (self.ser_state == False):
            self.ser.baudrate = self.Baudrate.get()
            self.ser.port = self.COM.get()  # 串口号
            self.ser.bytesize = 8
            self.ser.parity = 'N'
            self.ser.stopbits = 1
            self.ser.timeout = 0.1  # timeout
            self.ser.open()  # 打开串口
            self.ser_state = True
            # 改变按钮等状态
            if self.ser.isOpen():
                self.txt_com_state["background"] = "green"
                self.txt_com_state["text"] = "连接"
                self.button_send["state"] = "normal"
                self.button_conn["text"] = "断开"
                # 开启线程
                self.t = threading.Thread(target=self.ReceiveData)  # 创建线程，线程将执行self.ReceiveData函数
                self.t.setDaemon(True)
                self.t.start()
            else:
                print("串口没有打开")
        # 关闭串口，并改变按钮等状态
        else:
            self.txt_com_state["background"] = "red"
            self.txt_com_state["text"] = "无连接"
            self.button_conn["text"] = "连接"
            self.button_send["state"] = "disabled"
            self.ser.close()
            self.ser_state = False

    # 发送指令，由“发送”按钮触发
    def send_mess(self):
        DataSend = self.send_str.get() + '\r\n'  # 指令+终止符（'\r\n'）
        self.OutputText.insert(tk.END, '发送指令为：' + str(DataSend) + '\n')  # 将发送的信息显示在界面上
        self.OutputText.see(tk.END)
        self.ser.write(DataSend.encode("gbk"))  # 向串口发送信息

    # 发送指令，Entry，由回车键<"Return">触发
    def send_mess_event(self, event):
        DataSend = self.send_str.get() + '\r\n'
        self.OutputText.insert(tk.END, '发送指令为：' + str(DataSend) + '\n')
        self.OutputText.see(tk.END)
        self.ser.write(DataSend.encode("gbk"))

    # 关闭串口对象和线程，当用户关闭窗口时触发
    def func_delete(self):
        if self.ser.isOpen():
            self.ser.close()  # 关闭串口对象

        time.sleep(0.5)
        self.win.destroy()  # 销毁窗口


if __name__ == "__main__":
    mySerial = SerialGUI()
