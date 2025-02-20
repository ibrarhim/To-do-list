import tkinter as tk
from tkinter import messagebox, ttk
import winsound
import datetime


# Data Structures
class TaskNode:
    def __init__(self, description, priority, completed=False, due_date=None):
        self.description = description
        self.priority = priority
        self.completed = completed
        self.due_date = due_date
        self.next = None


class TaskLinkedList:
    def __init__(self):
        self.head = None

    def add_task(self, node):
        if not self.head:
            self.head = node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = node

    def delete_task(self, description):
        current = self.head
        prev = None
        while current:
            if current.description == description:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                return True
            prev = current
            current = current.next
        return False


class TaskHashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return sum(ord(char) for char in key) % self.size

    def insert(self, node):
        index = self._hash(node.description)
        self.table[index].append(node)

    def search(self, description):
        index = self._hash(description)
        for task in self.table[index]:
            if task.description == description:
                return task
        return None

    def delete(self, description):
        index = self._hash(description)
        for i, task in enumerate(self.table[index]):
            if task.description == description:
                del self.table[index][i]
                return True
        return False


class TaskBSTNode:
    def __init__(self, task_node):
        self.task = task_node
        self.left = None
        self.right = None


class TaskBST:
    def __init__(self):
        self.root = None

    def insert(self, node):
        if not self.root:
            self.root = TaskBSTNode(node)
        else:
            self._insert_recursive(self.root, node)

    def _insert_recursive(self, current, node):
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        new_prio = priority_order[node.priority]
        current_prio = priority_order[current.task.priority]

        if new_prio < current_prio:
            if current.left is None:
                current.left = TaskBSTNode(node)
            else:
                self._insert_recursive(current.left, node)
        else:
            if current.right is None:
                current.right = TaskBSTNode(node)
            else:
                self._insert_recursive(current.right, node)

    def in_order_traversal(self):
        tasks = []
        self._traverse(self.root, tasks)
        return tasks

    def _traverse(self, node, tasks):
        if node:
            self._traverse(node.left, tasks)
            tasks.append(node.task)
            self._traverse(node.right, tasks)


class AdvancedTaskManager:
    def __init__(self):
        self.linked_list = TaskLinkedList()
        self.hash_table = TaskHashTable()
        self.priority_bst = TaskBST()

    def _rebuild_bst(self):
        self.priority_bst = TaskBST()
        current = self.linked_list.head
        while current:
            self.priority_bst.insert(current)
            current = current.next

    def add_task(self, description, priority, due_date=None):
        if self.hash_table.search(description):
            messagebox.showwarning("Duplicate", "Task already exists!")
            return False

        new_task = TaskNode(description, priority, due_date=due_date)
        self.linked_list.add_task(new_task)
        self.hash_table.insert(new_task)
        self.priority_bst.insert(new_task)
        return True

    def delete_task(self, description):
        task = self.hash_table.search(description)
        if task:
            self.linked_list.delete_task(description)
            self.hash_table.delete(description)
            self._rebuild_bst()
            return True
        return False

    def toggle_completion(self, description):
        task = self.hash_table.search(description)
        if task:
            task.completed = not task.completed
            return True
        return False

    def get_sorted_tasks(self):
        return self.priority_bst.in_order_traversal()


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Task Manager")
        self.root.geometry("800x700")
        self.root.configure(bg="#2C3E50")

        self.manager = AdvancedTaskManager()

        style = ttk.Style()
        style.configure("TButton", padding=10, font=("Arial", 12), background="#3498DB")
        style.configure("TLabel", foreground="white", background="#2C3E50", font=("Arial", 12))

        # Input Section
        input_frame = ttk.Frame(root)
        input_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(input_frame, text="Task Description:").grid(row=0, column=0, sticky="w")
        self.task_entry = ttk.Entry(input_frame, width=40)
        self.task_entry.grid(row=1, column=0, padx=5, sticky="ew")

        ttk.Label(input_frame, text="Priority:").grid(row=0, column=1, sticky="w")
        self.priority_var = tk.StringVar(value="Medium")
        self.priority_menu = ttk.Combobox(input_frame, textvariable=self.priority_var,
                                          values=["High", "Medium", "Low"], width=10)
        self.priority_menu.grid(row=1, column=1, padx=5)

        ttk.Label(input_frame, text="Due Date:").grid(row=0, column=2, sticky="w")
        self.due_date_var = tk.StringVar()
        self.due_date_picker = ttk.Combobox(input_frame, textvariable=self.due_date_var,
                                            values=self.generate_due_dates(), width=12)
        self.due_date_picker.grid(row=1, column=2, padx=5)

        self.add_btn = ttk.Button(input_frame, text="Add Task", command=self.add_task)
        self.add_btn.grid(row=1, column=3, padx=5)

        # Search/Display Section
        search_frame = ttk.Frame(root)
        search_frame.pack(pady=5, padx=20, fill="x")

        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)

        ttk.Button(search_frame, text="Search",
                   command=self.search_task).pack(side="left", padx=5)

        # New Display All Tasks Button
        ttk.Button(search_frame, text="Display All Tasks",
                   command=self.display_tasks).pack(side="left", padx=5)

        # Task List
        list_frame = ttk.Frame(root)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.task_listbox = tk.Listbox(list_frame, width=80, height=20,
                                       font=("Arial", 12), selectbackground="#3498DB")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_listbox.yview)
        self.task_listbox.configure(yscrollcommand=scrollbar.set)

        self.task_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.task_listbox.bind("<Double-Button-1>", self.toggle_completion)
        self.task_listbox.bind("<Delete>", self.delete_task)

        self.display_tasks()

    def generate_due_dates(self):
        today = datetime.datetime.today()
        return [(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, 31)]

    def add_task(self):
        description = self.task_entry.get().strip()
        priority = self.priority_var.get()
        due_date = self.due_date_var.get() or "No due date"

        if description:
            if self.manager.add_task(description, priority, due_date):
                self.clear_inputs()
                messagebox.showinfo("Success", "Task added successfully!")
                winsound.Beep(1000, 200)
                self.display_tasks()
        else:
            messagebox.showwarning("Error", "Please enter a task description!")

    def clear_inputs(self):
        self.task_entry.delete(0, tk.END)
        self.priority_var.set("Medium")
        self.due_date_var.set("")

    def search_task(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.display_tasks()
            return

        found_tasks = []
        for task in self.manager.get_sorted_tasks():
            if query in task.description.lower():
                found_tasks.append(task)

        self.update_listbox(found_tasks)
        messagebox.showinfo("Search Results", f"Found {len(found_tasks)} matching tasks")

    def display_tasks(self):
        self.update_listbox(self.manager.get_sorted_tasks())

    def update_listbox(self, tasks):
        self.task_listbox.delete(0, tk.END)
        for task in tasks:
            status = "✔" if task.completed else "✘"
            priority_icon = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(task.priority, "⚪")
            due_date = task.due_date if task.due_date else "No due date"
            self.task_listbox.insert(tk.END,
                                     f"{status} | {task.description} | {priority_icon} {task.priority} | 📅 {due_date}")

    def toggle_completion(self, event):
        selection = self.task_listbox.curselection()
        if selection:
            task_text = self.task_listbox.get(selection[0])
            description = task_text.split("|")[1].strip()
            if self.manager.toggle_completion(description):
                self.display_tasks()

    def delete_task(self, event):
        selection = self.task_listbox.curselection()
        if selection:
            task_text = self.task_listbox.get(selection[0])
            description = task_text.split("|")[1].strip()
            if messagebox.askyesno("Confirm Delete", "Delete this task?"):
                if self.manager.delete_task(description):
                    self.display_tasks()
                    messagebox.showinfo("Success", "Task deleted successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()