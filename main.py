import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3

class DatabaseApp:
    def __init__(self, master, connection_params):
        self.master = master
        self.connection_params = connection_params
        self.master.title("Database App")

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')

        self.conn = sqlite3.connect(**connection_params)
        self.cursor = self.conn.cursor()
        self.table_names = self.get_table_names()

        for table_name in self.table_names:
            frame = tk.Frame(self.notebook)
            self.notebook.add(frame, text=table_name)
            self.create_table_view(frame, table_name)

    def get_table_names(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in self.cursor.fetchall()]

    def create_table_view(self, frame, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in self.cursor.fetchall()]

        tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
        tree.pack(expand=True, fill='both')

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(tree, table_name, c, False))
            tree.column(col, width=100, anchor='center')

        self.populate_treeview(tree, table_name)

        buttons = [
            ("Добавить", lambda: self.add_row(tree, table_name)),
            ("Удалить", lambda: self.delete_row(tree, table_name)),
            ("Изменить", lambda: self.edit_row(tree, table_name)),
            ("Обновить", lambda: self.populate_treeview(tree, table_name)),
            ("Поиск", lambda: self.search_treeview(tree)),
            ("Создать отчет", self.generate_report)
        ]

        for text, command in buttons:
            tk.Button(frame, text=text, command=command).pack(side=tk.LEFT, padx=10)

    def populate_treeview(self, tree, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name};")
        data = self.cursor.fetchall()
        tree.delete(*tree.get_children())
        for row in data:
            tree.insert('', 'end', values=row)

    def add_row(self, tree, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in self.cursor.fetchall()]

        add_dialog = tk.Toplevel(self.master)
        add_dialog.title("Добавить строку")

        entry_widgets = []
        for col in columns:
            label = tk.Label(add_dialog, text=col)
            label.grid(row=columns.index(col), column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(add_dialog)
            entry.grid(row=columns.index(col), column=1, padx=10, pady=5, sticky='w')
            entry_widgets.append(entry)

        def insert_row():
            values = [entry.get() for entry in entry_widgets]
            placeholders = ', '.join(['?' for _ in values])
            query = f"INSERT INTO {table_name} VALUES ({placeholders});"
            self.cursor.execute(query, values)
            self.conn.commit()
            self.populate_treeview(tree, table_name)
            add_dialog.destroy()

        tk.Button(add_dialog, text="Подтвердить", command=insert_row).grid(row=len(columns), columnspan=2, pady=10)

    def delete_row(self, tree, table_name):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите строку для удаления.")
            return

        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту строку?")
        if not confirm:
            return

        values = tree.item(selected_item)['values']
        where_clause = ' AND '.join([f"{column} = ?" for column in tree['columns']])
        query = f"DELETE FROM {table_name} WHERE {where_clause};"
        self.cursor.execute(query, values)
        self.conn.commit()
        self.populate_treeview(tree, table_name)

    def edit_row(self, tree, table_name):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите строку для изменения.")
            return

        values = tree.item(selected_item)['values']
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in self.cursor.fetchall()]

        edit_dialog = tk.Toplevel(self.master)
        edit_dialog.title("Изменить строку")

        entry_widgets = []
        for col, value in zip(columns, values):
            label = tk.Label(edit_dialog, text=col)
            label.grid(row=columns.index(col), column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(edit_dialog)
            entry.insert(0, value)
            entry.grid(row=columns.index(col), column=1, padx=10, pady=5, sticky='w')
            entry_widgets.append(entry)

        def update_row():
            new_values = [entry.get() for entry in entry_widgets]
            set_clause = ', '.join([f"{column} = ?" for column in columns])
            where_clause = ' AND '.join([f"{column} = ?" for column in columns])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"
            self.cursor.execute(query, new_values + values)
            self.conn.commit()
            self.populate_treeview(tree, table_name)
            edit_dialog.destroy()

        tk.Button(edit_dialog, text="Подтвердить", command=update_row).grid(row=len(columns), columnspan=2, pady=10)

    def sort_treeview(self, tree, table_name, column, reverse):
        query = f"SELECT * FROM {table_name} ORDER BY {column} {'DESC' if reverse else 'ASC'};"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        tree.delete(*tree.get_children())
        for row in data:
            tree.insert('', 'end', values=row)

    def search_treeview(self, tree):
        search_term = tk.simpledialog.askstring("Поиск", "Введите термин для поиска:")
        if search_term is not None:
            for item in tree.get_children():
                values = tree.item(item)['values']
                if any(str(search_term).lower() in str(value).lower() for value in values):
                    tree.selection_add(item)
                else:
                    tree.selection_remove(item)

    def generate_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

        if not file_path:
            return

        with open(file_path, 'w') as report_file:
            for table_name in self.table_names:
                report_file.write(f"Таблица: {table_name}\n")
                self.cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [row[1] for row in self.cursor.fetchall()]
                report_file.write("\tColumns: " + ", ".join(columns) + "\n")
                self.cursor.execute(f"SELECT * FROM {table_name};")
                data = self.cursor.fetchall()
                report_file.write("\tData:\n")
                for row in data:
                    report_file.write("\t\t" + ", ".join(str(value) for value in row) + "\n")
                report_file.write("\n")
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = self.cursor.fetchone()[0]
                report_file.write(f"Количество строк: {row_count}\n\n")

if __name__ == "__main__":
    connection_params = {"database": "mydb.sqlite3"}
    try:
        root = tk.Tk()
        app = DatabaseApp(root, connection_params)
        root.mainloop()
    except sqlite3.Error as err:
        print(f"Error: {err}")
