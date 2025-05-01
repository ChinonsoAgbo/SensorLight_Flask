import serial
ser = serial.Serial('COM4', 230400)
while True:
    try:
        data =  ser.readline().decode('utf-8').strip()
        print(f"{data}")
    except Exception as e:
        print("Error:", e)