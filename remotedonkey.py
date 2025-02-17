import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment

# Function to check and install FFmpeg
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

# Function to convert MP4 to MOV
def convert_mp4_to_mov(video_path):
    if video_path.lower().endswith(".mp4"):
        mov_path = video_path.replace(".mp4", ".MOV")
        os.system(f'ffmpeg -i "{video_path}" -c copy "{mov_path}"')
        return mov_path if os.path.exists(mov_path) else None
    return video_path

# Function to convert MOV to MP3
def convert_mov_to_mp3(video_path):
    mp3_path = video_path.replace(".MOV", ".mp3")
    os.system(f'ffmpeg -i "{video_path}" -vn -acodec libmp3lame -q:a 2 "{mp3_path}"')
    return mp3_path if os.path.exists(mp3_path) else None

# Function to split audio
def split_audio(mp3_path, interval, prefix):
    audio = AudioSegment.from_mp3(mp3_path)
    total_duration = len(audio)
    output_folder = os.path.dirname(mp3_path)
    interval_ms = interval * 1000
    start_time = 0
    clip_number = 1

    while start_time < total_duration:
        end_time = min(start_time + interval_ms, total_duration)
        output_filename = os.path.join(output_folder, f"{prefix}_{clip_number}.mp3")
        audio[start_time:end_time].export(output_filename, format="mp3")
        start_time = end_time
        clip_number += 1

    messagebox.showinfo("Success", f"✅ {clip_number - 1} clips saved!")
    open_folder(output_folder)

# Function to open output folder
def open_folder(folder_path):
    if os.name == "nt":
        os.startfile(folder_path)
    elif os.name == "posix":
        subprocess.run(["xdg-open", folder_path])

# Function to start processing
def start_conversion():
    video_path = file_path_var.get()
    if not video_path:
        messagebox.showerror("Error", "Please select a video file!")
        return

    interval = int(interval_var.get())
    prefix = prefix_entry.get().strip() or "clip"

    if not check_ffmpeg():
        messagebox.showerror("Error", "FFmpeg is not installed. Please install it and try again.")
        return

    video_path = convert_mp4_to_mov(video_path)
    mp3_path = convert_mov_to_mp3(video_path)
    if not mp3_path:
        messagebox.showerror("Error", "MP3 conversion failed!")
        return

    split_audio(mp3_path, interval, prefix)

# GUI Setup
root = tk.Tk()
root.title("RemoteDonkey - Video to Audio Cutter")
root.geometry("400x300")

# File Selection
file_path_var = tk.StringVar()
tk.Label(root, text="1️⃣ Select Video File").pack()
tk.Entry(root, textvariable=file_path_var, width=40).pack()
tk.Button(root, text="Browse", command=lambda: file_path_var.set(filedialog.askopenfilename(filetypes=[("MP4 & MOV Files", "*.mp4 *.MOV")]))).pack()

# Interval Selection
tk.Label(root, text="2️⃣ Select Cutting Interval (1-10 sec)").pack()
interval_var = tk.StringVar(value="3")
tk.OptionMenu(root, interval_var, *map(str, range(1, 11))).pack()

# Prefix Selection
tk.Label(root, text="3️⃣ Enter Clip Name Prefix").pack()
prefix_entry = tk.Entry(root)
prefix_entry.pack()

# Convert Button
tk.Button(root, text="Start Conversion", command=start_conversion).pack()

# Run GUI
root.mainloop()
