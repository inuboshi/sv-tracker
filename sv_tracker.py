import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime
from collections import defaultdict

# Classes sorted alphabetically, Bloodcraft replaced with Abysscraft
classes = sorted([
    "Forestcraft", "Swordcraft", "Runecraft", "Dragoncraft",
    "Shadowcraft", "Abysscraft", "Havencraft", "Portalcraft"
])

DATA_DIR = "results_by_day"
os.makedirs(DATA_DIR, exist_ok=True)

labels = {}
percent_labels = {}
data = {}
current_date = datetime.now().strftime("%Y-%m-%d")

def get_result_file(date_str):
    return os.path.join(DATA_DIR, f"{date_str}.txt")

def load_results(date_str):
    file_path = get_result_file(date_str)
    results = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                if ":" in line:
                    name, record = line.strip().split(":")
                    wins, losses = map(int, record.strip().replace("W", "").replace("L", "").split("-"))
                    results[name.strip()] = [wins, losses]
    for cls in classes:
        if cls not in results:
            results[cls] = [0, 0]
    return results

def save_results(date_str):
    file_path = get_result_file(date_str)
    with open(file_path, "w") as f:
        for cls in classes:
            wins, losses = data[cls]
            f.write(f"{cls}: {wins}W - {losses}L\n")

def update_record(cls, win_or_loss):
    if win_or_loss == "win":
        data[cls][0] += 1
    else:
        data[cls][1] += 1
    save_results(current_date)
    update_label(cls)

def change_day(event=None):
    global current_date, data
    selected = day_selector.get()
    current_date = selected
    if current_date == "Overall":
        data = compute_overall_stats()
    else:
        data = load_results(current_date)
    refresh_labels()

def get_all_dates():
    return [f[:-4] for f in os.listdir(DATA_DIR) if f.endswith(".txt")]

def compute_overall_stats():
    combined = defaultdict(lambda: [0, 0])
    for file in os.listdir(DATA_DIR):
        if file.endswith(".txt"):
            with open(os.path.join(DATA_DIR, file), "r") as f:
                for line in f:
                    if ":" in line:
                        name, record = line.strip().split(":")
                        wins, losses = map(int, record.strip().replace("W", "").replace("L", "").split("-"))
                        combined[name.strip()][0] += wins
                        combined[name.strip()][1] += losses
    for cls in classes:
        if cls not in combined:
            combined[cls] = [0, 0]
    return dict(combined)

def refresh_labels():
    for cls in classes:
        update_label(cls)
        state = "disabled" if current_date == "Overall" else "normal"
        win_buttons[cls].config(state=state)
        loss_buttons[cls].config(state=state)

def update_label(cls):
    wins, losses = data[cls]
    total = wins + losses
    percent = round((wins / total) * 100) if total > 0 else 0
    labels[cls].config(text=f"{wins}W - {losses}L")

    # Update % label color
    if percent > 50:
        color = "green"
    elif percent < 50:
        color = "red"
    else:
        color = "gray"
    percent_labels[cls].config(text=f"{percent}%", foreground=color)

# GUI setup
root = tk.Tk()
root.title("SV Tracker")

win_width = 350
win_height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (win_width / 2))
y = int((screen_height / 2) - (win_height / 2))
root.geometry(f"{win_width}x{win_height}+{x}+{y}")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

# Add window icon
root.iconbitmap("bampy.ico")

style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 12))
style.configure("TButton", font=("Segoe UI", 12), padding=3)

top_frame = ttk.Frame(root)
top_frame.pack(pady=6)

ttk.Label(top_frame, text="Select Day:").pack(side="left", padx=4)

all_days = get_all_dates()
if current_date not in all_days:
    all_days.append(current_date)
if "Overall" not in all_days:
    all_days.insert(0, "Overall")

day_selector = ttk.Combobox(top_frame, values=sorted(all_days), width=12, state="readonly")
day_selector.set(current_date)
day_selector.pack(side="left", padx=5)
day_selector.bind("<<ComboboxSelected>>", change_day)

main_frame = ttk.Frame(root)
main_frame.pack(pady=4, padx=8, fill="both", expand=True)

data = load_results(current_date)
labels = {}
percent_labels = {}
win_buttons = {}
loss_buttons = {}

for i, cls in enumerate(classes):
    row_frame = ttk.Frame(main_frame)
    row_frame.grid(row=i, column=0, pady=1, sticky="w")

    name_label = ttk.Label(row_frame, text=cls, width=11, anchor="w")
    name_label.pack(side="left", padx=(0, 4))

    win_button = tk.Button(row_frame, text="⬆", fg="white", bg="#4CAF50", font=("Segoe UI", 12, "bold"),
                           width=2, command=lambda c=cls: update_record(c, "win"))
    win_button.pack(side="left", padx=2)
    win_buttons[cls] = win_button

    loss_button = tk.Button(row_frame, text="⬇", fg="white", bg="#F44336", font=("Segoe UI", 12, "bold"),
                            width=2, command=lambda c=cls: update_record(c, "loss"))
    loss_button.pack(side="left", padx=2)
    loss_buttons[cls] = loss_button

    record_label = ttk.Label(row_frame, text=f"{data[cls][0]}W - {data[cls][1]}L", width=10, anchor="center")
    record_label.pack(side="left", padx=2)
    labels[cls] = record_label

    percent_label = ttk.Label(row_frame, text="0%", width=4, anchor="center")
    percent_label.pack(side="left", padx=(4, 0))
    percent_labels[cls] = percent_label

# Initial update of all % labels
refresh_labels()

root.mainloop()
