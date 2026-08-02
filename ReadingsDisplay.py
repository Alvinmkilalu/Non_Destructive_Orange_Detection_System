import serial
import time
import pandas as pd
from datetime import datetime
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


# ==========================
# SERIAL CONFIG
# ==========================
PORT = "COM15"      # change if needed
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    ser.reset_input_buffer()
    print("Connected to", PORT)

except serial.SerialException:
    print("Could not open serial port.")
    print("Close Arduino Serial Monitor and try again.")
    exit()


# ==========================
# CREATE LOG FILE
# ==========================
filename = "orange_log_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"

df = pd.DataFrame(columns=[
    "Timestamp",
    "610nm",
    "680nm",
    "730nm",
    "760nm",
    "810nm",
    "860nm"
])

print("Logging to:", filename)


# ==========================
# TKINTER GUI
# ==========================
root = tk.Tk()
root.title("Orange Spoilage Detector")
root.geometry("950x650")

label = tk.Label(
    root,
    text="Waiting for AS7263 data...",
    font=("Arial", 16),
    justify="left"
)
label.pack()


# ==========================
# GRAPH VARIABLES
# ==========================
x_data = []

y610 = []
y680 = []
y730 = []
y760 = []
y810 = []
y860 = []

fig = plt.figure(figsize=(8,4))
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

counter = 0


# ==========================
# UPDATE FUNCTION
# ==========================
def update():
    global counter
    global df

    if ser.in_waiting:

        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        print("RAW:", line)

        try:
            parts = line.split(',')

            values = {}

            for p in parts:
                k, v = p.split(':')
                values[k] = float(v)

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # update label
            label.config(
                text=
                f"Time: {timestamp}\n\n"
                f"610nm: {values['610']}\n"
                f"680nm: {values['680']}\n"
                f"730nm: {values['730']}\n"
                f"760nm: {values['760']}\n"
                f"810nm: {values['810']}\n"
                f"860nm: {values['860']}"
            )

            # save CSV
            df.loc[len(df)] = [
                timestamp,
                values['610'],
                values['680'],
                values['730'],
                values['760'],
                values['810'],
                values['860']
            ]

            df.to_csv(filename, index=False)

            # append graph data
            x_data.append(counter)

            y610.append(values['610'])
            y680.append(values['680'])
            y730.append(values['730'])
            y760.append(values['760'])
            y810.append(values['810'])
            y860.append(values['860'])

            counter += 1

            # redraw graph
            ax.clear()

            ax.plot(x_data, y610, label='610nm')
            ax.plot(x_data, y680, label='680nm')
            ax.plot(x_data, y730, label='730nm')
            ax.plot(x_data, y760, label='760nm')
            ax.plot(x_data, y810, label='810nm')
            ax.plot(x_data, y860, label='860nm')

            ax.set_title("Live AS7263 Spectral Readings")
            ax.set_xlabel("Samples")
            ax.set_ylabel("Intensity")
            ax.legend()

            canvas.draw()

        except:
            pass

    root.after(1000, update)


update()
root.mainloop()