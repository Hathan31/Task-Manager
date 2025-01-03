import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import db_connection, cursor
import matplotlib.pyplot as plt
from operator import attrgetter


class Task:
    def __init__(self, id, title, due_date, priority, comments, status):
        self.id = id
        self.title = title
        self.due_date = due_date
        self.priority = priority
        self.comments = comments
        self.status = status

class TaskManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.tasks_day = []
        self.tasks_week = []
        self.tasks_month = []

    def add_task(self, task):
        cursor.execute("SELECT id FROM tasks WHERE title = %s AND user_id = %s", (task.title, self.user_id))
        existing_task = cursor.fetchone()
        if existing_task:
            return

        today = datetime.today().date()
        due_date = task.due_date.date()

        if due_date <= today:
            self.tasks_day.append(task)
        if due_date <= (today + timedelta(days=7)):
            self.tasks_week.append(task)
        if due_date <= (today + timedelta(days=30)):
            self.tasks_month.append(task)

        cursor.execute("INSERT INTO tasks (user_id, title, due_date, priority, comments, status) VALUES (%s, %s, %s, %s, %s, %s)",
                    (self.user_id, task.title, task.due_date, task.priority, task.comments, task.status))
        db_connection.commit()
        
    def update_task(self, task):
        cursor.execute("UPDATE tasks SET title = %s, due_date = %s, priority = %s, comments = %s, status = %s WHERE id = %s",
                       (task.title, task.due_date, task.priority, task.comments, task.status, task.id))
        db_connection.commit()

    def remove_task(self, task):
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task.id,))
        db_connection.commit()

    def filter_tasks_by_title(self, keyword):
        cursor.execute("SELECT * FROM tasks WHERE (title LIKE %s OR comments LIKE %s) AND user_id = %s",
                       (f"%{keyword}%", f"%{keyword}%", self.user_id))
        return self._fetch_tasks(cursor.fetchall())

    def filter_tasks_by_due_date(self, keyword):
        try:
            due_date = datetime.strptime(keyword, "%Y-%m-%d").date()
            cursor.execute("SELECT * FROM tasks WHERE due_date = %s AND user_id = %s", (due_date, self.user_id))
            return self._fetch_tasks(cursor.fetchall())
        except ValueError:
            return []

    def filter_tasks_by_priority(self, keyword):
        cursor.execute("SELECT * FROM tasks WHERE priority = %s AND user_id = %s", (keyword, self.user_id))
        return self._fetch_tasks(cursor.fetchall())

    def filter_tasks_by_status(self, keyword):
        cursor.execute("SELECT * FROM tasks WHERE status = %s AND user_id = %s", (keyword, self.user_id))
        return self._fetch_tasks(cursor.fetchall())

    def get_completed_tasks_count(self):
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Completed' AND user_id = %s", (self.user_id,))
        return cursor.fetchone()[0]

    def get_inprogress_tasks_count(self):
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'In Progress' AND user_id = %s", (self.user_id,))
        return cursor.fetchone()[0]

    def get_pending_tasks_count(self):
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Pending' AND user_id = %s", (self.user_id,))
        return cursor.fetchone()[0]

class TaskManagerApp:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.task_manager = TaskManager(user_id)
        self.root = tk.Tk()
        self.root.title("Task Manager")
        self.root.geometry("1000x600")

        self.user_label = tk.Label(self.root, text=f"User: {self.username}", font=("Helvetica", 12))
        self.user_label.pack(ipady=2)

        self.tabControl = ttk.Notebook(self.root)
        self.tab_day = ttk.Frame(self.tabControl)
        self.tab_week = ttk.Frame(self.tabControl)
        self.tab_month = ttk.Frame(self.tabControl)

        self.tabControl.add(self.tab_day, text='Day')
        self.tabControl.add(self.tab_week, text='Week')
        self.tabControl.add(self.tab_month, text='Month')

        self.tabControl.pack(expand=1, fill="both")

        self.tables = {}
        self.create_task_table(self.tab_day, 'Day')
        self.create_task_table(self.tab_week, 'Week')
        self.create_task_table(self.tab_month, 'Month')

        self.add_buttons()
        self.load_tasks()

        self.create_search_bar()
        
    def create_task_table(self, tab, tab_text):
        tree = ttk.Treeview(tab, columns=("Task Name", "Due Date", "Priority", "Comments", "Status"), show="headings")
        tree.heading("Task Name", text="Task Name")
        tree.heading("Due Date", text="Due Date")
        tree.heading("Priority", text="Priority")
        tree.heading("Comments", text="Comments")
        tree.heading("Status", text="Status")
        tree.pack(fill="both", expand=True)

        tree.bind("<<TreeviewSelect>>", self.bind_select_event)

        self.tables[tab_text] = tree 

    def bind_select_event(self, event):
        selected_items = event.widget.selection()
        if not selected_items:
            return  

        selected_item = selected_items[0]  
        values = event.widget.item(selected_item, 'values')
        if not values:
            return  
        title, due_date_str, priority, comments, status = values
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        
        cursor.execute("SELECT id FROM tasks WHERE title = %s AND due_date = %s AND priority = %s AND comments = %s AND status = %s",
                    (title, due_date, priority, comments, status))
        task_id = cursor.fetchone()
        if task_id:
            self.selected_task = Task(task_id[0], title, due_date, priority, comments, status)
        else:
            self.selected_task = Task(None, title, due_date, priority, comments, status)

    def add_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(side="bottom", pady=10)

        add_button = tk.Button(button_frame, text="Add Task", command=self.open_add_window)
        add_button.grid(row=0, column=0, padx=5)

        edit_button = tk.Button(button_frame, text="Edit Task", command=self.edit_task)
        edit_button.grid(row=0, column=1, padx=5)

        remove_button = tk.Button(button_frame, text="Remove Task", command=self.remove_task)
        remove_button.grid(row=0, column=2, padx=5)

        pie_chart_button = tk.Button(button_frame, text="Task Completion", command=self.show_pie_chart)
        pie_chart_button.grid(row=0, column=3, padx=5)
        
        reset_button = tk.Button(button_frame, text="Reset", command=self.reset_tasks)
        reset_button.grid(row=0, column=4, padx=5)
        
        sort_button = tk.Button(button_frame, text="Sort", command=self.open_sort_window)
        sort_button.grid(row=0, column=5, padx=5)

    def create_search_bar(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(side="top", pady=10)

        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)

        filter_button = tk.Button(search_frame, text="Filter", command=self.filter_tasks)
        filter_button.pack(side="left", padx=5)

    def open_add_window(self):
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add Task")

        tk.Label(self.add_window, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        self.title_entry = tk.Entry(self.add_window)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.add_window, text="Due Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(self.add_window)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.add_window, text="Priority:").grid(row=2, column=0, padx=5, pady=5)
        self.priority_var = tk.StringVar(self.add_window)
        self.priority_var.set("Normal")
        priority_options = ["Normal", "Medium", "High"]
        priority_dropdown = tk.OptionMenu(self.add_window, self.priority_var, *priority_options)
        priority_dropdown.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.add_window, text="Comments:").grid(row=3, column=0, padx=5, pady=5)
        self.comments_entry = tk.Entry(self.add_window)
        self.comments_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.add_window, text="Status:").grid(row=4, column=0, padx=5, pady=5)
        self.status_var = tk.StringVar(self.add_window)
        self.status_var.set("Pending")
        status_options = ["Pending", "In Progress", "Completed"]
        status_dropdown = tk.OptionMenu(self.add_window, self.status_var, *status_options)
        status_dropdown.grid(row=4, column=1, padx=5, pady=5)

        add_button = tk.Button(self.add_window, text="Add", command=self.add_task)
        add_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

    def add_task(self):
        title = self.title_entry.get()
        due_date_str = self.date_entry.get()
        priority = self.priority_var.get()
        comments = self.comments_entry.get()
        status = self.status_var.get()

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        new_task = Task(None, title, due_date, priority, comments, status)
        self.task_manager.add_task(new_task)

        tab = self.get_tab_for_due_date(new_task.due_date.date())
        self.display_task(new_task, tab)

        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.priority_var.set("Normal")
        self.comments_entry.delete(0, tk.END)
        self.status_var.set("Pending")
        self.add_window.destroy()

    def get_tab_for_due_date(self, due_date):
        today = datetime.today().date()
        if due_date <= today:
            return 'Day'
        elif due_date <= (today + timedelta(days=7)):
            return 'Week'
        else:
            return 'Month'

    def display_task(self, task, tab):
        tree = self.tables[tab]
        tree.insert("", "end", values=(task.title, task.due_date.strftime('%Y-%m-%d'), task.priority, task.comments, task.status))

    def edit_task(self):
        if not hasattr(self, 'selected_task') or not self.selected_task:
            tk.messagebox.showwarning("Warning", "Please select a task to edit.")
            return

        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Task")

        selected_task = self.selected_task
        tk.Label(self.edit_window, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        self.edit_title_entry = tk.Entry(self.edit_window)
        self.edit_title_entry.insert(0, selected_task.title)
        self.edit_title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.edit_window, text="Due Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.edit_date_entry = tk.Entry(self.edit_window)
        self.edit_date_entry.insert(0, selected_task.due_date.strftime("%Y-%m-%d"))
        self.edit_date_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.edit_window, text="Priority:").grid(row=2, column=0, padx=5, pady=5)
        self.edit_priority_var = tk.StringVar(self.edit_window)
        self.edit_priority_var.set(selected_task.priority)
        priority_options = ["Normal", "Medium", "High"]
        priority_dropdown = tk.OptionMenu(self.edit_window, self.edit_priority_var, *priority_options)
        priority_dropdown.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.edit_window, text="Comments:").grid(row=3, column=0, padx=5, pady=5)
        self.edit_comments_entry = tk.Entry(self.edit_window)
        self.edit_comments_entry.insert(0, selected_task.comments)
        self.edit_comments_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.edit_window, text="Status:").grid(row=4, column=0, padx=5, pady=5)
        self.edit_status_var = tk.StringVar(self.edit_window)
        self.edit_status_var.set(selected_task.status)
        status_options = ["Pending", "In Progress", "Completed"]
        status_dropdown = tk.OptionMenu(self.edit_window, self.edit_status_var, *status_options)
        status_dropdown.grid(row=4, column=1, padx=5, pady=5)

        edit_button = tk.Button(self.edit_window, text="Save", command=self.update_task)
        edit_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

    def update_task(self):
        if not hasattr(self, 'selected_task') or not self.selected_task:
            tk.messagebox.showwarning("Warning", "Please select a task to edit.")
            return

        title = self.edit_title_entry.get()
        due_date_str = self.edit_date_entry.get()
        priority = self.edit_priority_var.get()
        comments = self.edit_comments_entry.get()
        status = self.edit_status_var.get()

        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        self.selected_task.title = title
        self.selected_task.due_date = due_date
        self.selected_task.priority = priority
        self.selected_task.comments = comments
        self.selected_task.status = status

        self.task_manager.update_task(self.selected_task)

        for tree in self.tables.values():
            tree.delete(*tree.get_children())

        self.load_tasks()

        self.edit_window.destroy()

    def remove_task(self):
        if not hasattr(self, 'selected_task') or not self.selected_task:
            tk.messagebox.showwarning("Warning", "Please select a task to remove.")
            return

        for tab_text, tree in self.tables.items():
            for item in tree.get_children():
                values = tree.item(item, 'values')
                if values and values[0] == self.selected_task.title:
                    tree.delete(item)

        self.task_manager.remove_task(self.selected_task)

        del self.selected_task

    def load_tasks(self):
        cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (self.user_id,))
        tasks = cursor.fetchall()
        for task in tasks:
            id, user_id, title, due_date, priority, comments, status = task
            due_date = datetime.combine(due_date, datetime.min.time())
            loaded_task = Task(id, title, due_date, priority, comments, status)
            self.task_manager.add_task(loaded_task)

            tab = self.get_tab_for_due_date(loaded_task.due_date.date())
            self.display_task(loaded_task, tab)

    def filter_tasks(self):
        keyword = self.search_entry.get()

        for tab_text, tree in self.tables.items():
            tree.delete(*tree.get_children())

            if keyword:
                cursor.execute("SELECT * FROM tasks WHERE (title LIKE %s OR due_date LIKE %s OR priority LIKE %s OR status LIKE %s) AND user_id = %s",
                               (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", self.user_id))
            else:
                cursor.execute("SELECT * FROM tasks WHERE user_id = %s", (self.user_id,))

            tasks = cursor.fetchall()
            for task in tasks:
                id, user_id, title, due_date, priority, comments, status = task
                due_date = datetime.combine(due_date, datetime.min.time())
                loaded_task = Task(id, title, due_date, priority, comments, status)

                if self.get_tab_for_due_date(loaded_task.due_date.date()) == tab_text:
                    self.display_task(loaded_task, tab_text)
                    
    def reset_tasks(self):
        for tab_text, tree in self.tables.items():
            tree.delete(*tree.get_children())

        self.load_tasks()

    def show_pie_chart(self):
        completed = self.task_manager.get_completed_tasks_count()
        in_progress = self.task_manager.get_inprogress_tasks_count()
        pending = self.task_manager.get_pending_tasks_count()

        labels = ['Completed', 'In Progress', 'Pending']
        sizes = [completed, in_progress, pending]
        colors = ['lightgreen', 'lightblue', 'lightcoral']
        explode = (0.1, 0, 0)

        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title('Task Completion Status')
        plt.show()
        
    def open_sort_window(self):
        sort_window = tk.Toplevel(self.root)
        sort_window.title("Sort Tasks")

        tk.Label(sort_window, text="Sort by:").grid(row=0, column=0, padx=5, pady=5)

        options = [("Due Date", "due_date"), ("Task Name", "title"), ("Status", "status"), ("Priority", "priority")]
        sort_criteria = tk.StringVar()
        for i, (text, value) in enumerate(options):
            tk.Radiobutton(sort_window, text=text, variable=sort_criteria, value=value).grid(row=i+1, column=0, padx=5, pady=2, sticky="w")

        tk.Button(sort_window, text="Sort", command=lambda: self.sort_tasks(sort_criteria.get())).grid(row=len(options)+1, column=0, padx=5, pady=10)

    def sort_tasks(self, criterion):
        if criterion:
            current_tab = self.tabControl.select()
            tree = self.tables[self.tabControl.tab(current_tab, "text")]

            tasks = []
            for item in tree.get_children():
                values = tree.item(item, 'values')
                if values:
                    title, due_date_str, priority, comments, status = values
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                    task = Task(None, title, due_date, priority, comments, status)
                    tasks.append(task)
                    
            if criterion == "title":
                tasks.sort(key=attrgetter('title'))
            elif criterion == "status":
                tasks.sort(key=lambda x: ('Pending', 'In Progress', 'Completed').index(x.status))
            elif criterion == "due_date":
                tasks.sort(key=attrgetter('due_date'))
            elif criterion == "priority":
                tasks.sort(key=lambda x: ('Normal', 'Medium', 'High').index(x.priority))

            tree.delete(*tree.get_children())

            for task in tasks:
                tree.insert("", "end", values=(task.title, task.due_date.strftime('%Y-%m-%d'), task.priority, task.comments, task.status))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    db_connection = db_connection()
    cursor = db_connection.cursor()
    user_id = 1
    username = "example_user"
    app = TaskManagerApp(user_id, username)
    app.run()
