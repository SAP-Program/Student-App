from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkProgressBar
from threading import Thread
from tkinter import messagebox
import sys
from pathlib import Path
import requests
import time
import os
from add_face_page import add_face_page_func

# System paths
OPENCV_FACE_DETECTOR_PATH = r"c:\sap-project\opencv\haarcascade_frontalface_default.xml"
OPENCV_FACE_RECOGNIZER_PATH = r"c:\sap-project\opencv\face_recognition_sface_2021dec.onnx"

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "backend"))

MODELS = [
    {
        "url": "https://github.com/SAP-Program/Head-Position-Estimation/raw/main/models/face_recognition_sface_2021dec.onnx",
        "path": OPENCV_FACE_RECOGNIZER_PATH,
        "name": "Face Recognition Model"
    },
    {
        "url": "https://github.com/SAP-Program/Head-Position-Estimation/raw/main/models/haarcascade_frontalface_default.xml",
        "path": OPENCV_FACE_DETECTOR_PATH,
        "name": "Face Detector Model"
    }
]

class DownloadModelPage(CTk):
    def __init__(self, udata):
        super().__init__()
        self.udata = udata
        self.download_queue = []
        self.current_download = None
        self.running = False
        self.init_ui()
        self.setup_window()
        self.check_existing_files()

    def init_ui(self):
        """Initialize all UI components"""
        # Main frame with red border
        self.main_frame = CTkFrame(master=self, border_color='red', border_width=2)

        # Title
        self.title_label = CTkLabel(
            master=self.main_frame, 
            text="Model Download Page", 
            font=('montserrat', 26, 'bold'))

        # Progress bar section
        self.progress_frame = CTkFrame(self.main_frame, fg_color='transparent')
        self.progress_bar = CTkProgressBar(self.progress_frame, height=15, width=300)
        self.progress_bar.set(0)

        # Status labels
        self.status_label = CTkLabel(
            self.progress_frame, 
            text="Ready to download", 
            text_color="gray70"
        )

        self.details_label = CTkLabel(
            self.progress_frame, 
            text="", 
            text_color="gray70"
        )

        # Buttons frame
        self.button_frame = CTkFrame(self.main_frame, fg_color='transparent')

        # Download button
        self.download_btn = CTkButton(
            self.button_frame,
            text="Download Missing Files",
            font=('montserrat', 20, 'bold'),
            width=300,
            height=40,
            corner_radius=10,
            command=self.start_download_thread
        )

        # Next page button
        self.next_btn = CTkButton(
            self.button_frame,
            text="Continue to Next Page",
            font=('montserrat', 20, 'bold'),
            width=300,
            height=40,
            corner_radius=10,
            state="disabled",
            command=self.go_to_next_page
        )

        # Placing elements
        self.title_label.pack(pady=(50, 30))
        self.main_frame.pack(padx=20, pady=20, expand=True, fill='both')
        self.progress_frame.pack(fill='x', padx=20, pady=10)
        self.progress_bar.pack()  
        self.status_label.pack(pady=(5, 0))
        self.details_label.pack(pady=(2, 0))
        self.button_frame.pack(pady=(0, 30))
        self.download_btn.pack(pady=5)
        self.next_btn.pack(pady=5)
    
    def setup_window(self):
        """Configure main window settings"""
        self.geometry('600x400')
        self.minsize(600, 400)
        self.title('Model Download Page')

    def check_existing_files(self):
        """Check which files need to be downloaded"""
        self.download_queue = []
        for model in MODELS:
            if not Path(model['path']).exists():
                self.download_queue.append(model)
        
        self.update_ui_state()

    def update_ui_state(self):
        """Update UI elements state"""
        if self.download_queue:
            self.download_btn.configure(state="normal", text="Download Missing Files")
            self.update_status(f"{len(self.download_queue)} files need download")
        else:
            self.download_btn.configure(state="disabled", text="All files downloaded")
            self.update_status("All files are already downloaded", "green")
            self.next_btn.configure(state="normal")

    def all_files_downloaded(self):
        """Check if all files are downloaded"""
        return all(Path(model['path']).exists() for model in MODELS)

    def start_download_thread(self):
        """Start download process in a thread"""
        if not self.check_internet():
            return
            
        self.download_btn.configure(state="disabled")
        self.running = True
        Thread(target=self.download_process, daemon=True).start()

    def download_process(self):
        """Main download process"""
        try:
            for model in self.download_queue:
                if not self.running:
                    break
                
                self.current_download = model
                self.update_status(f"Downloading {model['name']}...")
                
                # Create directory if not exists
                os.makedirs(os.path.dirname(model['path']), exist_ok=True)
                
                # Start download
                response = requests.get(model['url'], stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                
                with open(model['path'], 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if not self.running:
                            break
                            
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            self.update_progress(downloaded, total_size, start_time)

            if self.running:
                self.after(0, self.show_success)
        except Exception as e: 
            self.after(0, lambda e=e: self.show_error("Download Error", str(e))) 
        finally:
            self.running = False
            self.after(0, self.check_existing_files)

    def update_progress(self, downloaded, total, start_time):
        """Update progress bar and details"""
        progress = downloaded / total if total > 0 else 0
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total / (1024 * 1024)
        
        elapsed = time.time() - start_time
        speed = (downloaded / 1024) / elapsed if elapsed > 0 else 0
        
        details = (
            f"{mb_downloaded:.1f}MB of {mb_total:.1f}MB | "
            f"{speed:.1f} KB/s | "
            f"{progress:.1%}"
        )
        
        self.after(0, lambda: [
            self.progress_bar.set(progress),
            self.details_label.configure(text=details)
        ])

    def update_status(self, text, color="gray70"):
        self.status_label.configure(text=text, text_color=color)

    def check_internet(self):
        """Check internet connection"""
        try:
            requests.get('https://google.com', timeout=5)
            return True
        except requests.ConnectionError:
            self.show_error("Connection Error", "No internet connection!")
            return False

    def show_error(self, title, message):
        """Show error message dialog"""
        messagebox.showerror(title, message)
        self.reset_ui()

    def show_success(self):
        messagebox.showinfo("Success", "All files downloaded successfully!")
        self.reset_ui()

    def reset_ui(self):
        self.progress_bar.set(0)
        self.details_label.configure(text="")
        self.check_existing_files()

    def go_to_next_page(self):
        """Callback for next page button"""
        self.destroy()
        add_face_page_func(udata=self.udata)

    def run(self):
        self.mainloop()

def start():
    app = DownloadModelPage('x')
    app.run()   

if __name__ == '__main__':
    start()