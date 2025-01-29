from customtkinter import CTk, CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCheckBox, CTkTabview
from pathlib import Path
import sys
from tkinter import messagebox
from threading import Thread
from calibration_page import calibration_page_func 
import os
from requests import get
from main_page import main_page_func_student

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir / "backend"))

from login_page_db import check_auth

parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(parent_dir / "Teacher-side/gui"))

from select_class_page import select_class_page_func

class StudentSideAppLoginPage(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('600x450')
        self.minsize(600, 450)
        self.title('Student Side Login Page')
        self.main_frame = CTkFrame(master=self, border_color='red', border_width=2)
        self.main_frame.pack(padx=20, pady=20, expand=True, fill='both')
        self.tabv = CTkTabview(self.main_frame)
        self.tabv.add('Students')
        self.tabv.add('Teachers')
        self.tabv.set('Students')
        self.tabv.pack(padx=20, pady=20,fill='both', expand=True)

        self.student_frame = self.tabv.tab('Students')
        self.teacher_frame = self.tabv.tab('Teachers')

        #################### students frame ####################
        self.element_frame = CTkFrame(master=self.student_frame, fg_color='transparent')
        self.element_frame.place(relx=0.5, rely=0.5, anchor='center')
       
        self.login_text = CTkLabel(master=self.element_frame, text="Login Page", font=('montserrat', 26, 'bold'), bg_color='transparent')
        self.username_lbl = CTkLabel(master=self.element_frame, text='USERNAME', font=('montserrat', 20))
        self.password_lbl = CTkLabel(master=self.element_frame, text='PASSWORD', font=('montserrat', 20))
        self.username_entry = CTkEntry(master=self.element_frame, placeholder_text='username', width=180, height=38, font=('montserrat', 15, 'bold'), corner_radius=10)
        self.password_entry = CTkEntry(master=self.element_frame, placeholder_text='password', show="*", width=180, height=38, font=('montserrat', 15, 'bold'), corner_radius=10)
        self.checkbox = CTkCheckBox(master=self.element_frame, text='I agree to Terms and Conditions', font=('montserrat', 15), corner_radius=20, checkbox_width=20, checkbox_height=20, border_width=2, onvalue="on", offvalue="off")
        self.login_btn = CTkButton(master=self.element_frame, text="Login", font=('montserrat', 20, 'bold'), corner_radius=10, command=lambda: self.start_login_thread('student'))

        self.login_text.grid(row=0, column=0, columnspan=2)
        self.username_lbl.grid(row=1, column=0, padx=(0,40), pady=(40,15))
        self.password_lbl.grid(row=2, column=0, padx=(0,40), pady=(0,15))
        self.username_entry.grid(row=1, column=1, padx=(40,0), pady=(40,15))
        self.password_entry.grid(row=2, column=1, padx=(40,0), pady=(0,15))
        self.checkbox.grid(row=3, column=0, pady=(0,15), columnspan=2)
        self.login_btn.grid(row=4, column=0, columnspan=2, sticky='ew')
        #################### students frame ####################
        #################### teachers frame ####################
        self.teachers_element_frame = CTkFrame(master=self.teacher_frame, fg_color='transparent')
        self.teachers_element_frame.place(relx=0.5, rely=0.5, anchor='center')
       
        self.teachers_login_text = CTkLabel(master=self.teachers_element_frame, text="Login Page", font=('montserrat', 26, 'bold'), bg_color='transparent')
        self.teachers_username_lbl = CTkLabel(master=self.teachers_element_frame, text='USERNAME', font=('montserrat', 20))
        self.teachers_password_lbl = CTkLabel(master=self.teachers_element_frame, text='PASSWORD', font=('montserrat', 20))
        self.teachers_username_entry = CTkEntry(master=self.teachers_element_frame, placeholder_text='username', width=180, height=38, font=('montserrat', 15, 'bold'), corner_radius=10)
        self.teachers_password_entry = CTkEntry(master=self.teachers_element_frame, placeholder_text='password', show="*", width=180, height=38, font=('montserrat', 15, 'bold'), corner_radius=10)
        self.teachers_checkbox = CTkCheckBox(master=self.teachers_element_frame, text='I agree to Terms and Conditions', font=('montserrat', 15), corner_radius=20, checkbox_width=20, checkbox_height=20, border_width=2, onvalue="on", offvalue="off")
        self.teachers_login_btn = CTkButton(master=self.teachers_element_frame, text="Login", font=('montserrat', 20, 'bold'), corner_radius=10, command=lambda: self.start_login_thread('teacher'))

        self.teachers_login_text.grid(row=0, column=0, columnspan=2)
        self.teachers_username_lbl.grid(row=1, column=0, padx=(0,40), pady=(40,15))
        self.teachers_password_lbl.grid(row=2, column=0, padx=(0,40), pady=(0,15))
        self.teachers_username_entry.grid(row=1, column=1, padx=(40,0), pady=(40,15))
        self.teachers_password_entry.grid(row=2, column=1, padx=(40,0), pady=(0,15))
        self.teachers_checkbox.grid(row=3, column=0, pady=(0,15), columnspan=2)
        self.teachers_login_btn.grid(row=4, column=0, columnspan=2, sticky='ew')
        #################### teachers frame ####################

    def block(self):
        self.login_btn.configure(state="disabled", text="Waiting...")
        self.teachers_login_btn.configure(state="disabled", text="Waiting...")

    def normal(self):
        self.login_btn.configure(state="normal", text="Login")
        self.teachers_login_btn.configure(state="normal", text="Login")

    def start_login_thread(self, person):
        """Starts the login function in a new thread to avoid blocking the main GUI thread."""
        # Disable the button and change its text
        self.block()

        try:
            # get('https://google.com')
            # Create and start the login thread
            login_thread = Thread(target=self.login, args=(person,))
            login_thread.start()
        except Exception:
            messagebox.showerror("Internet Connectoin", 'You dont have Internet Connection !')
            self.normal()

    def login(self, person):
        """Handles the login process in a separate thread."""
        if person == 'student' :
            username = self.username_entry.get()
            password = self.password_entry.get()
            rules_stat = self.checkbox.get()
        else:
            username = self.teachers_username_entry.get()
            password = self.teachers_password_entry.get()
            rules_stat = self.teachers_checkbox.get()        
        print(f'self.username = {username}\nself.password = {password}')
        if username != '' and password != '' :
            if rules_stat == 'on' :
                # Perform authentication check
                login_success = check_auth(username, password, person)
                print(login_success)
                # After the login attempt, update the UI on the main thread
                self.after(0, self.finish_login, login_success, person)
            else:
                messagebox.showerror("Error", 'You have not Agreed to our terms and condition')
                self.normal()     

        else:
            messagebox.showerror("Error", 'Username or passwrod cant be empty !')
            self.normal()

    def finish_login(self, login_success, person):
        """Handles the final actions after the login process is done."""
        if login_success[0]:
            self.normal()    # Re-enable the login button and reset the text in the main thread
            self.success_login(login_success[1], person) # Close the login window on successful login
        else:
            messagebox.showerror('Login Failed', 'Your username or password is incorrect!')
            self.normal()

    def success_login(self, user_data, person):
        self.destroy()
        if person == 'student' :
            parnet_path = 'C:\\sap-project'
            if not os.path.exists(parnet_path) :          # Check data folder exists
                try:
                    os.mkdir(rf'{parnet_path}')           # Make data folder
                except FileExistsError :
                    print(f'Directory {parnet_path}')
                except PermissionError :
                    print('Premision Denied !')
                calibration_page_func(user_data)
            else:                                                           # If data folder and calibration data exists it run main page 
                if os.path.exists(parnet_path+'\\calibration-data.txt'):    
                    main_page_func_student(user_data)
                else:
                    calibration_page_func(user_data)                     # If calibration_data not exists, will create it 
            print(user_data)
            sys.exit()
        else:
            select_class_page_func(user_data)
            sys.exit()

    def run(self):
        self.mainloop()


def main():
    app = StudentSideAppLoginPage()
    app.run()


if __name__ == '__main__':
    main()
