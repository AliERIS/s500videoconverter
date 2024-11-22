import os
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import shutil
import webbrowser

class VideoConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Digiphone S500 Video Dönüştürücü 0.01")
        self.root.geometry("600x450")
        self.root.configure(bg="black")  # Set background color to black
        
        # Video preview değişkenleri
        self.is_previewing = False
        self.preview_thread = None
        
        # Input File
        tk.Label(root, text="Dönüştürülecek Video:", bg="black", fg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.input_entry = tk.Entry(root, width=50, bg="black", fg="white", insertbackground="white")
        self.input_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(root, text="Gözat", command=self.browse_file, bg="black", fg="white").grid(row=0, column=2, padx=10, pady=5)
        
        # Preview Frame
        self.preview_frame = tk.Label(root, bg="black")
        self.preview_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        # Preview Controls
        self.preview_button = tk.Button(root, text="Önizleme", command=self.toggle_preview, bg="black", fg="white")
        self.preview_button.grid(row=2, column=1, pady=5)
        
        # Output File
        tk.Label(root, text="Dosya Kayıt Yeri:", bg="black", fg="white").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.output_entry = tk.Entry(root, width=50, bg="black", fg="white", insertbackground="white")
        self.output_entry.grid(row=3, column=1, padx=10, pady=5)
        tk.Button(root, text="Seç", command=self.save_file, bg="black", fg="white").grid(row=3, column=2, padx=10, pady=5)
        
        # Codec Dropdown
        tk.Label(root, text="Kodek:", bg="black", fg="white").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.codec_var = tk.StringVar(root)
        self.codec_var.set("mpeg4")
        self.codec_menu = tk.OptionMenu(root, self.codec_var, "mpeg4", "h263")
        self.codec_menu.config(bg="black", fg="white")
        self.codec_menu["menu"].config(bg="black", fg="white")
        self.codec_menu.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        
        # Bitrate Dropdown
        tk.Label(root, text="Bitrate:", bg="black", fg="white").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.bitrate_var = tk.StringVar(root)
        self.bitrate_var.set("200k")  # Default value
        self.bitrate_menu = tk.OptionMenu(root, self.bitrate_var, "200k", "500k", "800k", "1200k")
        self.bitrate_menu.config(bg="black", fg="white")
        self.bitrate_menu["menu"].config(bg="black", fg="white")
        self.bitrate_menu.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        
        # Subtitle File
        tk.Label(root, text="Altyazi Dosyasi:", bg="black", fg="white").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.subtitle_entry = tk.Entry(root, width=50, bg="black", fg="white", insertbackground="white")
        self.subtitle_entry.grid(row=6, column=1, padx=10, pady=5)
        tk.Button(root, text="Subtitle Seç", command=self.browse_subtitle, bg="black", fg="white").grid(row=6, column=2, padx=10, pady=5)
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.grid(row=7, column=1, pady=10)
        
        # Convert Button
        tk.Button(root, text="Dönüştür", command=self.start_conversion, bg="black", fg="white").grid(row=8, column=1, pady=10)
        
        # Blog and YouTube Labels
        #tk.Label(root, text="Blog:", bg="black", fg="white").grid(row=9, column=0, padx=10, pady=5, sticky="w")
        self.blog_label = tk.Label(root, text="Visit Blog", fg="blue", cursor="hand2", bg="black")
        self.blog_label.grid(row=9, column=1, padx=10, pady=5, sticky="w")
        self.blog_label.bind("<Button-1>", lambda e: self.open_url("https://digiphone-s500.blogspot.com"))
        
       # tk.Label(root, text="YouTube:", bg="black", fg="white").grid(row=10, column=0, padx=10, pady=5, sticky="w")
        self.youtube_label = tk.Label(root, text=" YouTube", fg="blue", cursor="hand2", bg="black")
        self.youtube_label.grid(row=10, column=1, padx=10, pady=5, sticky="w")
        self.youtube_label.bind("<Button-1>", lambda e: self.open_url("https://www.youtube.com/@DigiphoneS500-f8u"))

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv")])
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)

    def browse_subtitle(self):
        filename = filedialog.askopenfilename(filetypes=[("Subtitle files", "*.srt")])
        if filename:
            self.subtitle_entry.delete(0, tk.END)
            self.subtitle_entry.insert(0, filename)

    def toggle_preview(self):
        if self.is_previewing:
            self.stop_preview()
        else:
            self.start_preview()

    def start_preview(self):
        input_file = self.input_entry.get()
        if not input_file:
            return
        
        self.is_previewing = True
        self.preview_button.config(text="Stop Preview")
        self.preview_thread = threading.Thread(target=self.preview_video)
        self.preview_thread.start()

    def stop_preview(self):
        self.is_previewing = False
        self.preview_button.config(text="Preview")
        if self.preview_thread:
            self.preview_thread.join()

    def preview_video(self):
        cap = cv2.VideoCapture(self.input_entry.get())
        
        while self.is_previewing:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
                
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (320, 240))
            photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            
            self.preview_frame.config(image=photo)
            self.preview_frame.image = photo
            
            self.root.update()
            cv2.waitKey(30)
        
        cap.release()
        self.preview_frame.config(image='')

    def save_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".mp4")
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, filename)

    def start_conversion(self):
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        subtitle_file = self.subtitle_entry.get() if hasattr(self, 'subtitle_entry') else None

        if not output_file:
            tk.messagebox.showerror("Error", "Lütfen bir dosya kayıt yeri seçin.")
            return

        # Copy files to temp
        temp_video = "temp.mp4"
        temp_subtitle = "temp.srt"
        shutil.copy(input_file, temp_video)
        if subtitle_file:
            shutil.copy(subtitle_file, temp_subtitle)
            subtitle_file = temp_subtitle

        self.convert_video(temp_video, output_file, subtitle_file)

    def convert_video(self, input_file, output_file, subtitle_file=None):
        ffmpeg_path = "ffmpeg.exe"
        bitrate = self.bitrate_var.get()
        if subtitle_file:
            subtitle_file_utf8 = self.convert_to_utf8(subtitle_file)
            subtitle_filter = f"subtitles='{subtitle_file_utf8}':force_style='FontSize=16,Alignment=2'"
            command = [
                ffmpeg_path, 
                '-i', input_file,
                '-vf', subtitle_filter,
                '-vcodec', self.codec_var.get(),
                '-s', '320x240',
                '-b:v', bitrate,
                '-acodec', 'mp3',
                output_file
            ]
        else:
            command = [
                ffmpeg_path, 
                '-i', input_file,
                '-vcodec', self.codec_var.get(),
                '-s', '320x240',
                '-b:v', bitrate,
                '-acodec', 'mp3',
                output_file
            ]

        print(f"Executing command: {' '.join(command)}")
        
        self.progress_bar['value'] = 0
        
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            self.update_progress(process)
        except Exception as e:
            tk.messagebox.showerror("Error", f"FFmpeg Error: {str(e)}")

    def convert_to_utf8(self, subtitle_file):
        with open(subtitle_file, 'r', encoding='latin1') as file:
            content = file.read()
        utf8_file = subtitle_file + ".utf8.srt"
        with open(utf8_file, 'w', encoding='utf-8') as file:
            file.write(content)
        return utf8_file

    def update_progress(self, process):
        duration = None
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                if "Duration" in output:
                    duration = self.parse_duration(output)
                if "time=" in output and duration:
                    elapsed_time = self.parse_time(output)
                    progress = (elapsed_time / duration) * 100
                    self.progress_bar['value'] = progress
                    self.root.update_idletasks()
        process.wait()
        tk.messagebox.showinfo("Conversion Complete", "The video conversion is complete!")
        self.progress_bar['value'] = 0

    def parse_duration(self, output):
        time_str = output.split("Duration: ")[1].split(',')[0]
        time_parts = time_str.split(':')
        return float(time_parts[0])*3600 + float(time_parts[1])*60 + float(time_parts[2])

    def parse_time(self, output):
        time_str = output.split("time=")[1].split(' ')[0]
        time_parts = time_str.split(':')
        return float(time_parts[0])*3600 + float(time_parts[1])*60 + float(time_parts[2])

    def get_unique_output_path(self, base_path):
        directory = os.path.dirname(base_path)
        filename = os.path.basename(base_path)
        name, ext = os.path.splitext(filename)
        
        if name.startswith("output"):
            # Add logic to handle unique output path
            pass

    def open_url(self, url):
        webbrowser.open_new(url)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverter(root)
    tk.messagebox.showinfo("Patch Notes: 0.01", "Dönüştüre bastıktan sonra yanıt vermiyor yazarsa bekleyin o arkaplanda dönüştürmeye devam ediyor.")
    root.mainloop()