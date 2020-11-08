import serial
import threading
import time


class SerialThread:
    """
    串口通信线程，包含读线程和写线程
    """
    def __init__(self, port, baudrate=9600, bytesize=8, stopbits=1, timeout=1):
        self.my_serial = serial.Serial()
        self.my_serial.port = port              # 端口号
        self.my_serial.baudrate = baudrate      # 波特率
        self.my_serial.bytesize = bytesize      # 数据位
        self.my_serial.stopbits = stopbits      # 停止位
        self.my_serial.timeout = timeout

        self.alive = False                      # 当 alive 为 True，读写线程会进行
        self.thread_read = None                 # 读线程
        self.thread_write = None                # 写线程

    def start(self):
        self.my_serial.open()
        if self.my_serial.isOpen():
            self.alive = True

            # 设置一个线程为守护线程，就表示这个线程不重要，在进程退出时，不用等待这个线程退出
            self.thread_read = threading.Thread(target=self.read)
            self.thread_write = threading.Thread(target=self.write)

            self.thread_read.start()
            self.thread_write.start()

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
                n = self.my_serial.inWaiting()                       # 返回接收缓存中的字节数
                if n:
                    data = self.my_serial.read(n).decode("gbk")     # 解码成 gbk 码（处理中文字符问题）
                    if len(data) == 1 and ord(data[-1]) == 113:     # 当接收到“q”时，线程结束
                        break
                    print(data)
            except Exception as ex:
                print(ex)

    def write(self):
        while self.alive:
            try:
                receive = input()
                self.my_serial.write(receive.encode("gbk"))     # 解码成 gbk 码（处理中文字符问题）
            except Exception as ex:
                print(ex)


if __name__ == "__main__":
    my_serial = SerialThread("COM6")
    my_serial.start()

