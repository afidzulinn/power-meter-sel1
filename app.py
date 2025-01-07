import requests
import time
import math
from datetime import datetime
import threading
import os
import csv

# URL endpoint
url = "http://10.20.2.12:12081/power_meter_sel1?"

# ------------------------------- Global variable
total_amper = 0.00
total_voltage = 0.00
KWH = 0.00
PF = 0.00
biaya_rupiah = 0.00
formatted_biaya = 0.00

year = None
month = None
day = None
hour = None
minute = None
second = None

# Nama file CSV
filename = "results/power_data_meter_sel1-5s.csv"

# Membuat folder dan file jika belum ada
def setup_csv_file():
    # Buat folder jika belum ada
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Cek apakah file sudah ada
    if not os.path.isfile(filename):
        header = ["Timestamp", "Total Amper (RMS)", "Total Voltage (RMS)", "KWH", "PF", "Biaya (Rp)"]
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

def fetch_data():
    global total_amper, total_voltage, KWH, PF, biaya_rupiah
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            parameters = data.get("parameter", {})
            A_PH1 = float(parameters.get("A_PH1", 0))
            A_PH2 = float(parameters.get("A_PH2", 0))
            A_PH3 = float(parameters.get("A_PH3", 0))
            V_P12 = float(parameters.get("V_P12", 0))
            V_P13 = float(parameters.get("V_P13", 0))
            V_P23 = float(parameters.get("V_P23", 0))
            KWH = int(parameters.get("KWH", 0))
            PF = float(parameters.get("PF", 0))
            total_amper = math.sqrt(A_PH1**2 + A_PH2**2 + A_PH3**2)
            total_voltage = math.sqrt((V_P12**2 + V_P13**2 + V_P23**2) / 3)
            KWH = KWH / 100000
            biaya_rupiah = KWH * 11450
            return A_PH1, A_PH2, A_PH3, V_P12, V_P13, V_P23, KWH, PF, total_amper, total_voltage
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except requests.ConnectionError:
        print("Server is unreachable. Waiting for server to become active...")
    except requests.Timeout:
        print("Server request timed out. Retrying...")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

def get_power_data():
    global total_amper, total_voltage, KWH, PF, biaya_rupiah
    try:
        while True:
            fetch_data()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Program terminated by user.")

def waktu():
    global year, month, day, hour, minute, second
    while True:
        now = datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        time.sleep(5)

def save_to_csv():
    global year, month, day, hour, minute, second
    global total_amper, total_voltage, KWH, PF, biaya_rupiah
    global formatted_biaya

    # Data yang akan disimpan
    timestamp = f"{year}/{month}/{day} {hour}:{minute}:{second}"
    data = [timestamp, f"{total_amper:.2f}", f"{total_voltage:.2f}", f"{KWH}", f"{PF}", formatted_biaya]

    # Buka file CSV dalam mode append ('a')
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def print_information():
    global year, month, day, hour, minute, second
    global total_amper, total_voltage, KWH, PF, biaya_rupiah
    global formatted_biaya
    while True:
        formatted_biaya = f"Rp {biaya_rupiah:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        print(f"{year}/{month}/{day} {hour}:{minute}:{second}\t Total Ampere (RMS): {total_amper:.2f},\tTotal Voltage (RMS): {total_voltage:.2f},\tKWH: {KWH},\tPF: {PF}, \tBiaya Rp : {formatted_biaya}")
        
        save_to_csv()
        
        time.sleep(5)

if __name__ == "__main__":
    os.system('echo -ne "\033]0;Predictive Cost for Power Distribution\007"')
    setup_csv_file()  # Pastikan file CSV dibuat jika belum ada
    threading.Thread(target=get_power_data).start()
    threading.Thread(target=waktu).start()
    threading.Thread(target=print_information).start()
