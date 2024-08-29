import serial
import tkinter as tk
from tkinter import font, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np
import threading
import time
from datetime import datetime
import csv
import mplcursors

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
temperature_label.pack(pady=10)

humidity_label = tk.Label(root, text="Humidity: ", font=custom_font)
humidity_label.pack(pady=10)

# X축 단위 선택을 위한 드롭다운 메뉴
x_axis_unit = tk.StringVar(value="Minutes")
units = ["Minutes", "Hours", "Days", "Months"]

unit_menu = ttk.Combobox(root, textvariable=x_axis_unit, values=units)
unit_menu.pack(side=tk.LEFT, padx=10)

unit_label = tk.Label(root, text="", font=custom_font)
unit_label.pack(side=tk.LEFT, padx=10)

# 데이터 저장 간격 선택을 위한 드롭다운 메뉴
save_interval = tk.StringVar(value="10 minutes")
intervals = ["10 minutes", "1 hour", "1 day"]

interval_menu = ttk.Combobox(root, textvariable=save_interval, values=intervals)
interval_menu.pack(side=tk.LEFT, padx=10)

interval_label = tk.Label(root, text="", font=custom_font)
interval_label.pack(side=tk.LEFT, padx=10)

# 데이터 저장용 리스트
temperatures = []
humidities = []
timestamps = []

# 차트 설정
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle("Real-time Temperature and Humidity")

def read_serial_data():
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

                    # 현재 시간 기록
                    current_time = datetime.now()
                    timestamps.append(current_time)
                    temperatures.append(temperature)
                    humidities.append(humidity)

                    # Tkinter 라벨 업데이트 (메인 스레드에서 실행)
                    root.after(0, lambda: update_labels(temperature, humidity))

                    # 리스트 크기 조정 (옵션)
                    if len(timestamps) > 100:
                        timestamps.pop(0)
                        temperatures.pop(0)
                        humidities.pop(0)
                except ValueError:
                    pass

def update_plot():
    ax1.clear()
    ax2.clear()

    # X축 단위 설정
    unit = x_axis_unit.get()
    if unit == "Minutes":
        locator = mdates.MinuteLocator(interval=1)  # 1분 간격
        formatter = mdates.DateFormatter('%H:%M')
        xlabel = 'Time (Minutes)'
    elif unit == "Hours":
        locator = mdates.HourLocator(interval=1)  # 1시간 간격
        formatter = mdates.DateFormatter('%H-%M')
        xlabel = 'Time (Hours)'
    elif unit == "Days":
        locator = mdates.DayLocator(interval=1)  # 1일 간격
        formatter = mdates.DateFormatter('%m-%d')
        xlabel = 'Time (Days)'
    elif unit == "Months":
        locator = mdates.MonthLocator(interval=1)  # 1개월 간격
        formatter = mdates.DateFormatter('%Y-%m')
        xlabel = 'Time (Months)'

    # X축 형식 설정
    ax1.xaxis.set_major_locator(locator)
    ax1.xaxis.set_major_formatter(formatter)
    ax2.xaxis.set_major_locator(locator)
    ax2.xaxis.set_major_formatter(formatter)

    # 그래프 그리기
    ax1.plot(timestamps, temperatures, 'r-', label='Temperature (°C)')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_xlabel(xlabel)
    ax1.legend(loc='upper left')
    ax1.set_ylim(0, 70)  # Y축 범위 설정
    ax1.grid(True)

    ax2.plot(timestamps, humidities, 'b-', label='Humidity (%)')
    ax2.set_ylabel('Humidity (%)')
    ax2.set_xlabel(xlabel)
    ax2.legend(loc='upper left')
    ax2.set_ylim(0, 110)  # Y축 범위 설정
    ax2.grid(True)

    # X축 레이블 형식 조정
    fig.autofmt_xdate()  # 자동으로 X축 레이블을 회전

    # mplcursors를 사용하여 인터랙티브한 커서 추가
    cursor1 = mplcursors.cursor(ax1, hover=True)
    cursor2 = mplcursors.cursor(ax2, hover=True)
    
    def on_add(sel):
        idx = int(sel.index)  # 인덱스를 정수로 변환
        if sel.artist == ax1:
            text = (
                f'Time: {timestamps[idx].strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'Temperature: {temperatures[idx]:.1f} °C\n'
                f'Humidity: {humidities[idx]:.1f} %'
            )
        elif sel.artist == ax2:
            text = (
                f'Time: {timestamps[idx].strftime("%Y-%m-%d %H:%M:%S")}\n'
                f'Humidity: {humidities[idx]:.1f} %'
            )
        sel.annotation.set_text(text)
        sel.annotation.set_visible(True)
        canvas.draw()

        # 5초 후 자동으로 사라지게 하기 위해 타이머 설정
        def hide_annotation():
            sel.annotation.set_visible(False)
            canvas.draw()
        root.after(5000, hide_annotation)
    
    cursor1.connect("add", on_add)
    cursor2.connect("add", on_add)

    canvas.draw()

def save_data():
    while True:
        interval = save_interval.get()
        if interval == "10 minutes":
            delay = 10 * 60
        elif interval == "1 hour":
            delay = 60 * 60
        elif interval == "1 day":
            delay = 24 * 60 * 60
        else:
            delay = 10 * 60

        # 파일 이름을 고정
        filename = "Environment.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Temperature (°C)', 'Humidity (%)'])
            for i in range(len(timestamps)):
                writer.writerow([timestamps[i].strftime('%Y-%m-%d %H:%M:%S'), temperatures[i], humidities[i]])

        time.sleep(delay)  # 설정된 간격에 따라 데이터 저장

def update_labels(temperature=None, humidity=None):
    if temperature is not None and humidity is not None:
        unit_label.config(text=f"X-axis Unit: {x_axis_unit.get()}")
        interval_label.config(text=f"Save Interval: {save_interval.get()}")
        temperature_label.config(text=f"Temperature: {temperature:.1f} °C")
        humidity_label.config(text=f"Humidity: {humidity:.1f} %")

def animate():
    while True:
        update_plot()
        time.sleep(1)  # 1초마다 업데이트

# Tkinter Canvas와 Matplotlib Figure 통합
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# 시리얼 데이터 읽기, 데이터 저장, 차트 애니메이션, 라벨 업데이트를 위한 스레드 실행
threading.Thread(target=read_serial_data, daemon=True).start()
threading.Thread(target=save_data, daemon=True).start()
threading.Thread(target=animate, daemon=True).start()

# Tkinter 메인 루프 실행
root.mainloop()
