from customtkinter import CTk, CTkTextbox, CTkLabel, CTkButton, CTkFrame, CTkOptionMenu, CTkEntry
import cv2
from PIL import Image, ImageTk
import os
from threading import Thread

class MainPage(CTk):
    def __init__(self):
        super().__init__()

        self.title('Main-Page')
        self.geometry('900x700')
        self.resizable(False, False)
        # getting avaiable cameras
        self.get_available_cameras()
        # main red frame
        self.main_frame = CTkFrame(master=self, border_color='red', border_width=2)
        self.main_frame.pack(padx=20, pady=20, expand=True, fill='both')
        # center frame for holding everything in center
        self.elements_frame = CTkFrame(self.main_frame, fg_color='transparent')
        self.elements_frame.place(relx=0.5, rely=0.5, anchor='center')
        # elements
        self.camera_label = CTkLabel(master=self.elements_frame, text='')
        self.user_detail_textbox = CTkTextbox(master=self.elements_frame, border_color='white', border_width=2)
        self.camera_selectbox_lbl = CTkLabel(self.elements_frame, text='Camera :' , font=('montserrat', 30, 'bold'))
        self.camera_selectbox = CTkOptionMenu(self.elements_frame, values=list(self.available_camera.keys()), font=('montserrat', 25, 'bold'), height=40, command=self.change_camera)
        self.rechech_availale_camera = CTkButton(self.elements_frame, text='Recheck', font=('montserrat', 20, 'bold'), height=40, border_color='white', border_width=2, command=self.recheck_button)
        self.current_connection_status_lbl = CTkLabel(self.elements_frame, text='Current Status Of Connection :' , font=('montserrat', 30))
        self.current_connection_status_entry = CTkEntry(self.elements_frame , font=('montserrat', 20, 'bold'), border_color='white', border_width=2)
        self.current_ping_status_lbl = CTkLabel(self.elements_frame, text='PING :' , font=('montserrat', 30))
        self.current_ping_status_entry = CTkEntry(self.elements_frame , font=('montserrat', 20, 'bold'), border_color='white', border_width=2)
        self.start_button = CTkButton(self.elements_frame, height=50, text='START', font=('montserrat', 20, 'bold'))

        
        # placing elements
        self.camera_label.grid(        row=0, column=0, rowspan=4)
        self.user_detail_textbox.grid( row=0, column=1, padx=(20,0),   sticky='nswe')
        self.camera_selectbox_lbl.grid(row=1, column=1, padx=(20,0),   sticky='w', pady=(5,0))
        self.camera_selectbox.grid(    row=2, column=1, padx=(20,0),   sticky='we', pady=(0,5))     
        self.rechech_availale_camera.grid(row=3, column=1, padx=(20, 0), sticky='we', pady=5)
        self.current_connection_status_lbl.grid(  row=4, column=0,                sticky='w', pady=(15, 0))
        self.current_connection_status_entry.grid(row=4, column=1, padx=(20,0),   sticky='we',pady=(15, 0))
        self.current_ping_status_lbl.grid(  row=5, column=0,                sticky='w', pady=(15, 0))
        self.current_ping_status_entry.grid(row=5, column=1, padx=(20,0),   sticky='we',pady=(15, 0))
        self.start_button.grid(        row=6, column=0, columnspan=2,  sticky='ew', pady=(15, 0))


        Thread(target=self.start_video_stream).start()

    # starting camera with default camera index 
    def start_video_stream(self):
        default_camera_index = 0
        self.cap = cv2.VideoCapture(default_camera_index)
        self.update_video()
    # getting connected camera to system by testing their index in VideoCapture
    def get_available_cameras(self):
        cameras = {}
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                name = f"CAM-{i}"
                cameras[name] = i
                cap.release()
        self.available_camera = cameras if cameras else {'No Camera found' : -1}
        print(self.available_camera)
    # changing camera by releasing and reopening with VideoCapture
    def change_camera(self, camera_name):
        camera_index = self.available_camera.get(camera_name, -1)
        if self.cap.isOpened():
            self.cap.release()
        self.cap = cv2.VideoCapture(camera_index)
    # update video each 10ms
    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (600, 450))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        
        self.after(10, self.update_video)
    
    def recheck_button(self):
        Thread(target=self.get_available_cameras).start()
        self.camera_selectbox.configure(values=list(self.available_camera.keys()))
        print(self.available_camera)

    def run(self):
        self.mainloop()

def main_page_func():
    app = MainPage()
    app.run()


if __name__ == "__main__":
    main_page_func()


