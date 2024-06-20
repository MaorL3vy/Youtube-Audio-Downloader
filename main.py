import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from pytube import YouTube
import threading
import os

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Audio Downloader")
        self.root.geometry("600x500")

        
        self.emojis = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "music": "🎵",
            "download": "⬇️"
        }

        self.create_widgets()

    def create_widgets(self):
        
        self.label = tk.Label(self.root, text=f"{self.emojis['music']} Welcome to YouTube Audio Downloader {self.emojis['music']}", font=("Helvetica", 20))
        self.label.pack(pady=20)

       
        self.url_label = tk.Label(self.root, text="Enter YouTube URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(self.root, width=60)
        self.url_entry.pack(pady=10)

        
        self.quality_label = tk.Label(self.root, text="Select Audio Quality:")
        self.quality_label.pack()
        self.quality_var = tk.StringVar()
        self.quality_var.set("highest")  
        qualities = ["highest", "lowest", "medium"]
        for quality in qualities:
            tk.Radiobutton(self.root, text=quality.capitalize(), variable=self.quality_var, value=quality).pack(anchor=tk.W)

     
        self.format_label = tk.Label(self.root, text="Select Audio Format:")
        self.format_label.pack()
        self.format_var = tk.StringVar()
        self.format_var.set("mp3")  
        formats = ["mp3", "m4a", "wav"]
        for fmt in formats:
            tk.Radiobutton(self.root, text=fmt.upper(), variable=self.format_var, value=fmt).pack(anchor=tk.W)

       
        self.download_button = tk.Button(self.root, text=f"{self.emojis['download']} Download Audio", command=self.download)
        self.download_button.pack(pady=20)

      
        self.progress_label = tk.Label(self.root, text="", fg="green")
        self.progress_label.pack(pady=5)
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

    def download(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Error", f"{self.emojis['error']} Please enter a valid YouTube URL.")
            return

        try:
            yt = YouTube(url)
        except Exception as e:
            messagebox.showerror("Error", f"{self.emojis['error']} Error accessing YouTube URL:\n{str(e)}")
            return

        self.download_audio(yt)

    def download_audio(self, yt):
        try:
            audio_streams = yt.streams.filter(only_audio=True)
            if not audio_streams:
                messagebox.showerror("Error", f"{self.emojis['error']} No audio streams available for this video.")
                return

            chosen_quality = self.quality_var.get()
            chosen_format = self.format_var.get()

            if chosen_quality == "highest":
                audio = audio_streams.first()
            elif chosen_quality == "lowest":
                audio = audio_streams.last()
            elif chosen_quality == "medium":
                audio = audio_streams.filter(abr="128kbps").first()  

            if not audio:
                messagebox.showerror("Error", f"{self.emojis['error']} Selected audio quality not available.")
                return

            destination = filedialog.askdirectory(initialdir=os.path.expanduser("~"), title="Select Destination Folder")
            if destination:
                download_thread = threading.Thread(target=self.download_audio_threaded, args=(audio, destination, yt.title, chosen_format))
                download_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"{self.emojis['error']} Error downloading audio:\n{str(e)}")

    def download_audio_threaded(self, audio, destination, title, chosen_format):
        try:
            self.update_progress(f"{self.emojis['download']} Downloading...")
            self.progress_bar["value"] = 0
            self.progress_bar["maximum"] = 100

            def progress_check(chunk, file_handle, bytes_remaining):
                progress = (float(bytes_remaining) / float(audio.filesize)) * 100.0
                self.progress_bar["value"] = 100 - progress

            out_file = audio.download(output_path=destination, filename=title, quiet=True, on_progress=progress_check)

          
            base, ext = os.path.splitext(out_file)
            if chosen_format == "mp3":
                new_file = os.path.join(destination, f"{title}.mp3")
                os.rename(out_file, new_file)
            elif chosen_format == "m4a":
                new_file = os.path.join(destination, f"{title}.m4a")
                os.rename(out_file, new_file)
            elif chosen_format == "wav":
                new_file = os.path.join(destination, f"{title}.wav")
                os.rename(out_file, new_file)

            self.update_progress(f"{self.emojis['success']} Conversion complete!")
            messagebox.showinfo("Success", f"Audio downloaded and converted to {chosen_format.upper()} successfully!")
        except Exception as e:
            self.update_progress(f"{self.emojis['error']} Error converting audio.")
            messagebox.showerror("Error", f"{self.emojis['error']} Error converting audio:\n{str(e)}")

    def update_progress(self, message):
        self.progress_label.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
