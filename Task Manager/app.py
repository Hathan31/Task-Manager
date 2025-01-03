"""
Program: app.py
Author: Jonathan Sampera
First Date Modifeid: 04/20/2024
Last Date Modified: 05/02/2024
The TaskManager is a Python application designed to help users organize their tasks efficiently. 
It allows users to add, edit, and remove tasks, categorizing them based on due dates into daily, 
weekly, and monthly tabs. Users can also filter tasks, view task completion statistics, and sort 
tasks based on various criteria such as due date, priority, status, and task name.
"""

import tkinter as tk
from database import cursor, db_connection
from taskManager import TaskManagerApp

class LoginScreen:
    def __init__(self, master):
        self.master = master
        master.title("User Login")

        self.welcome_label = tk.Label(master, text="Welcome to Task Manager!", font=("Helvetica", 18))
        self.welcome_label.pack(pady=(20, 10))

        self.username_label = tk.Label(master, text="Username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(master)
        self.username_entry.pack()

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)
    
        self.login_button = tk.Button(self.button_frame, text="Login", command=self.login)
        self.login_button.pack(side=tk.LEFT, padx=5)

        self.register_button = tk.Button(self.button_frame, text="Register", command=self.register)
        self.register_button.pack(side=tk.LEFT, padx=5)

    def login(self):
        username = self.username_entry.get()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone() 
        if user:
            print(f"Login successful! Welcome back, {username}!")
            self.open_task_manager(username)
        else:
            print("User not found. Please register or check your username.")
    
    def get_user_id(self, username):
        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        if user:
            return user[0]  
        else:
            print("User not found.")
            return None

    def open_task_manager(self, username):
        self.master.destroy()  
        user_id = self.get_user_id(username)  
        task_manager = TaskManagerApp(user_id, username)
        task_manager.run()

    def register(self):
        register_window = tk.Toplevel(self.master)
        register_window.title("Register")
        register_window.geometry("300x150")

        self.register_label = tk.Label(register_window, text="Register a New User", font=("Helvetica", 16))
        self.register_label.pack(pady=(10, 5))

        self.register_username_label = tk.Label(register_window, text="Username:")
        self.register_username_label.pack()

        self.register_username_entry = tk.Entry(register_window)
        self.register_username_entry.pack()

        self.create_user_button = tk.Button(register_window, text="Create User", command=lambda: self.create_user(register_window))
        self.create_user_button.pack(pady=10)

    def create_user(self, register_window):
        new_username = self.register_username_entry.get()
        cursor.execute("INSERT INTO users (username) VALUES (%s)", (new_username,))
        db_connection.commit()
        print(f"New user created! Welcome, {new_username}!")
        self.register_username_entry.delete(0, tk.END)
        register_window.destroy() 

def main():
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()