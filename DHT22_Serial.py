import serial

# 아두이노가 연결된 포트 설정 (예: COM23 또는 /dev/ttyUSB0)
arduino_port = 'COM25'  # Windows에서는 'COM25', Linux/Mac에서는 '/dev/ttyUSB0' 등
baud_rate = 9600  # 아두이노에서 설정한 baud rate

# 시리얼 포트 열기
ser = serial.Serial(arduino_port, baud_rate)

try:
    while True:
        # 아두이노로부터 데이터 읽기
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
except KeyboardInterrupt:
    print("프로그램을 종료합니다.")
finally:
    ser.close()
