import serial
import tkinter as tk
from tkinter import font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import time

# 시리얼 포트 설정
arduino_port = 'COM3'  # 실제 아두이노가 연결된 포트로 변경
baud_rate = 9600  # 아두이노의 baud rate
ser = serial.Serial(arduino_port, baud_rate, timeout=1)  # timeout 추가

# Tkinter 설정
root = tk.Tk()
root.title("DHT22 Sensor Data")

# 폰트 설정
custom_font = font.Font(size=16)

# 라벨 설정
temperature_label = tk.Label(root, text="Temperature: ", font=custom_font)
temperature_label.pack(pady=20)

humidity_label = tk.Label(root, text="Humidity: ", font=custom_font)
humidity_label.pack(pady=20)

# 데이터 저장용 리스트
temperatures = []
humidities = []
times = []

# 차트 설정
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
fig.suptitle("Real-time Temperature and Humidity")

def read_serial_data():
    start_time = time.time()
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            if "Humidity:" in line and "Temperature:" in line:
                parts = line.split('\t')
                humidity_str = parts[0].split(": ")[1].replace(" %", "")
                temperature_str = parts[1].split(": ")[1].replace(" *C", "")

                try:
                    humidity = float(humidity_str)
                    temperature = float(temperature_str)

                    # 현재 시간 계산
                    current_time = time.time() - start_time
                    times.append(current_time)
                    temperatures.append(temperature)
                    humidities.append(humidity)

                    # Tkinter 라벨 업데이트
                    temperature_label.config(text=f"Temperature: {temperature:.1f} °C")
                    humidity_label.config(text=f"Humidity: {humidity:.1f} %")

                    # 리스트 크기 조정 (옵션)
                    if len(times) > 100:
                        times.pop(0)
                        temperatures.pop(0)
                        humidities.pop(0)
                except ValueError:
                    pass

def update_plot():
    ax1.clear()
    ax2.clear()

    ax1.plot(times, temperatures, 'r-', label='Temperature (°C)')
    ax1.set_ylabel('Temperature (°C)')
    ax1.legend(loc='upper left')
    ax1.grid(True)

    ax2.plot(times, humidities, 'b-', label='Humidity (%)')
    ax2.set_ylabel('Humidity (%)')
    ax2.set_xlabel('Time (s)')
    ax2.legend(loc='upper left')
    ax2.grid(True)

    canvas.draw()

def animate():
    while True:
        update_plot()
        time.sleep(1)  # 1초마다 업데이트

# Tkinter Canvas와 Matplotlib Figure 통합
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# 시리얼 데이터 읽기를 백그라운드에서 실행
threading.Thread(target=read_serial_data, daemon=True).start()

# 차트 애니메이션을 위한 스레드 실행
threading.Thread(target=animate, daemon=True).start()

# Tkinter 메인 루프 실행
root.mainloop()
