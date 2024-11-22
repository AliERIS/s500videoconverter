import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import os
import threading

class VideoConverter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Video Converter")

        self.input_label = tk.Label(self, text="Input Video Path:")
        self.input_label.pack()

        self.input_path = tk.Entry(self, width=50)
        self.input_path.pack()

        self.browse_button = tk.Button(self, text="Browse", command=self.browse_file)
        self.browse_button.pack()

        self.output_label = tk.Label(self, text="Output Video Path:")
        self.output_label.pack()

        self.output_path = tk.Entry(self, width=50)
        self.output_path.insert(0, "output.mp4")
        self.output_path.pack()

        self.output_browse_button = tk.Button(self, text="Select Output Location", command=self.browse_output_file)
        self.output_browse_button.pack()

        self.codec_label = tk.Label(self, text="Codec:")
        self.codec_label.pack()

        self.codec = tk.StringVar(self)
        self.codec.set("mpeg4")
        self.codec_menu = tk.OptionMenu(self, self.codec, "mpeg4", "h263", command=self.update_resolution)
        self.codec_menu.pack()

        self.resolution_label = tk.Label(self, text="Resolution (width,height):")
        self.resolution_label.pack()

        self.resolution = tk.Entry(self, width=20)
        self.resolution.pack()

        self.convert_button = tk.Button(self, text="Convert", command=self.start_conversion)
        self.convert_button.pack()

        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack()

        self.update_resolution("mpeg4")

        # Butonları bir listeye ekle
        self.buttons = [
            self.browse_button,
            self.output_browse_button,
            self.codec_menu,
            self.convert_button
        ]

    def get_unique_output_path(self, base_path):
        # Dosya adı ve uzantıyı ayır
        directory = os.path.dirname(base_path)
        filename = os.path.basename(base_path)
        name, ext = os.path.splitext(filename)
        
        # Eğer dosya adı "output" ile başlıyorsa ve sayı içeriyorsa
        if name.startswith("output"):
            base_name = "output"
        else:
            base_name = name

        counter = 1
        new_path = base_path
        
        # Benzersiz dosya adı bulana kadar sayıyı arttır
        while os.path.exists(new_path):
            new_path = os.path.join(directory, f"{base_name}{counter}{ext}")
            counter += 1
        
        return new_path

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("All Files", "*.*"), ("MP4 Files", "*.mp4")])
        if file:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, file)
            # Çıktı dosya adını otomatik oluştur
            default_output = self.get_unique_output_path("output.mp4")
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, default_output)

    def browse_output_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")])
        if file:
            # Seçilen dosya adını benzersiz yap
            unique_file = self.get_unique_output_path(file)
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, unique_file)

    def update_resolution(self, codec):
        if codec == "mpeg4":
            self.resolution.delete(0, tk.END)
            self.resolution.insert(0, "320,240")
        elif codec == "h263":
            self.resolution.delete(0, tk.END)
            self.resolution.insert(0, "176,144")

    def start_conversion(self):
        threading.Thread(target=self.convert_video).start()

    def disable_buttons(self):
        for button in self.buttons:
            button.config(state='disabled')

    def enable_buttons(self):
        for button in self.buttons:
            button.config(state='normal')

    def convert_video(self):
        self.disable_buttons()
        try:
            input_path = self.input_path.get()
            output_path = self.get_unique_output_path(self.output_path.get())
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, output_path)
            resolution = self.resolution.get().split(',')
            width, height = resolution[0], resolution[1]
            codec = self.codec.get()
            bitrate = '200k'
            audio_codec = 'mp3'

            ffmpeg_path = 'ffmpeg.exe'

            # H.263 için özel parametreler
            if codec == "h263":
                output_path = os.path.splitext(output_path)[0] + '.3gp'  # H.263 için 3GP container
                command = [
                    ffmpeg_path,
                    '-i', input_path,
                    '-vf', f'scale={width}:{height}',
                    '-c:v', 'h263',
                    '-b:v', bitrate,
                    '-ar', '8000',  # H.263 için tipik örnekleme hızı
                    '-ac', '1',     # Mono ses
                    '-acodec', 'mp3',  # AAC ses codec'i
                    '-strict', 'experimental',
                    output_path
                ]
            else:
                # MPEG4 için normal parametreler
                command = [
                    ffmpeg_path,
                    '-i', input_path,
                    '-vf', f'scale={width}:{height}',
                    '-vcodec', codec,
                    '-b:v', bitrate,
                    '-acodec', audio_codec,
                    output_path
                ]

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            duration = self.get_video_duration(input_path)
            
            for line in process.stdout:
                if "out_time_ms=" in line:
                    try:
                        time_ms = int(line.split('=')[1])
                        seconds = time_ms / 1000000.0
                        if duration > 0:
                            progress = min((seconds / duration) * 100, 100)
                            self.progress['value'] = progress
                            self.update_idletasks()
                    except (ValueError, IndexError):
                        continue

            process.wait()
            self.progress['value'] = 100
            messagebox.showinfo("Conversion Complete", "The video conversion is complete!")
            self.progress['value'] = 0
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.enable_buttons()

    def get_video_duration(self, path):
        try:
            ffmpeg_path = 'ffmpeg.exe'
            result = subprocess.run([ffmpeg_path, '-i', path], 
                                  stderr=subprocess.PIPE, 
                                  stdout=subprocess.PIPE, 
                                  universal_newlines=True)
            
            for line in result.stderr.split('\n'):
                if "Duration" in line:
                    try:
                        duration_str = line.split(' ')[3].strip(',')
                        if duration_str != 'N/A':
                            time_parts = duration_str.split(':')
                            return int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
                    except (ValueError, IndexError):
                        continue
            return 0
        except Exception:
            return 0

if __name__ == "__main__":
    app = VideoConverter()
    app.mainloop()
