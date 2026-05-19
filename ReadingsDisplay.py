import serial
import pandas as pd
from datetime import datetime
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ---------------- SERIAL ----------------
PORT = 'COM15'   # change to your Arduino port
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)

# ---------------- LOG FILE ----------------
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

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Orange Spoilage Detection Monitor")
root.geometry("900x600")

label = tk.Label(root, text="Waiting for data...", font=("Arial", 16))
label.pack()

# graph data
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


def update():
    global counter

    if ser.in_waiting:
        line = ser.readline().decode().strip()

        try:
            # expected:
            # 610:120,680:130,...
            parts = line.split(',')

            values = {}
            for p in parts:
                k, v = p.split(':')
                values[k] = float(v)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # update text
            label.config(
                text=f"""
Time: {timestamp}

610nm: {values['610']}
680nm: {values['680']}
730nm: {values['730']}
760nm: {values['760']}
810nm: {values['810']}
860nm: {values['860']}
"""
            )

            # save log
            global df
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

            # update graph
            x_data.append(counter)
            y610.append(values['610'])
            y680.append(values['680'])
            y730.append(values['730'])
            y760.append(values['760'])
            y810.append(values['810'])
            y860.append(values['860'])

            counter += 1

            ax.clear()
            ax.plot(x_data, y610, label='610nm')
            ax.plot(x_data, y680, label='680nm')
            ax.plot(x_data, y730, label='730nm')
            ax.plot(x_data, y760, label='760nm')
            ax.plot(x_data, y810, label='810nm')
            ax.plot(x_data, y860, label='860nm')

            ax.set_title("Live Spectral Data")
            ax.set_xlabel("Sample")
            ax.set_ylabel("Intensity")
            ax.legend()

            canvas.draw()

        except:
            pass

    root.after(500, update)


update()
root.mainloop()