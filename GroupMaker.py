#LIBRARY YANG DIPAKAI
import random
import customtkinter as ctk
import tkinter.messagebox as messagebox
import csv
from tkinter import filedialog

#UNTUK PERHITUNGAN GROUP
class GroupStrategy:
    def create_groups(self, names, num_groups):
        raise NotImplementedError("Subclasses should implement this method.")

class RandomGroupStrategy(GroupStrategy):
    def create_groups(self, names, num_groups):
        random.shuffle(names)
        groups = [[] for _ in range(num_groups)]
        for i, name in enumerate(names):
            groups[i % num_groups].append(name)
        return groups

class AlphabeticalGroupStrategy(GroupStrategy):
    def create_groups(self, names, num_groups):
        names.sort()

        group_size = len(names) // num_groups
        remainder = len(names) % num_groups
    
        groups = []
        start = 0

        for i in range(num_groups):
            end = start + group_size + (1 if i < remainder else 0)
            groups.append(names[start:end])
            start = end

        return groups

class LengthBasedGroupStrategy(GroupStrategy):
    def create_groups(self, names, num_groups):
        names.sort(key=len)

        group_size = len(names) // num_groups
        remainder = len(names) % num_groups

        groups = []
        start = 0

        for i in range(num_groups):
            end = start + group_size + (1 if i < remainder else 0)
            groups.append(names[start:end])
            start = end

        return groups

class InputOrderGroupStrategy(GroupStrategy):
    def create_groups(self, names, num_groups):
        group_size = len(names) // num_groups
        remainder = len(names) % num_groups  

        groups = []
        start = 0

        for i in range(num_groups):
            end = start + group_size + (1 if i < remainder else 0)
            groups.append(names[start:end])
            start = end

        return groups


#UNTUK GUI UTAMA
class GroupMaker:
    def __init__(self, master):
        self.master = master
        master.title("GroupMaker")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        master.geometry("800x600")

        self.title_label = ctk.CTkLabel(master, text="GroupMaker", font=ctk.CTkFont(size=30, weight="bold"))
        self.title_label.pack(pady=15)

        self.label = ctk.CTkLabel(master, text="Masukkan nama (pisahkan dengan ' - ' )", font=ctk.CTkFont(size=20))
        self.label.pack()

        self.names_entry = ctk.CTkEntry(master, placeholder_text="Nama1-Nama2-Nama3", width=400, height=35)
        self.names_entry.pack(pady=5, fill="x", padx=20)

        self.import_button = ctk.CTkButton(master, text="Import dari CSV", command=self.import_from_csv)
        self.import_button.pack(pady=5)

        self.group_label = ctk.CTkLabel(master, text="Jumlah grup:", font=ctk.CTkFont(size=20))
        self.group_label.pack()

        self.group_entry = ctk.CTkEntry(master, placeholder_text="1, 2, 3", width=200, height=35)
        self.group_entry.pack(pady=5)

        self.strategy_label = ctk.CTkLabel(master, text="Pilih Metode Pengelompokan:", font=ctk.CTkFont(size=20))
        self.strategy_label.pack(pady=5)

        self.strategy_var = ctk.StringVar(value="Acak")
        self.strategy_optionmenu = ctk.CTkOptionMenu(master, values=["Acak", "Abjad", "Panjang Huruf", "Urutan Input"], variable=self.strategy_var)
        self.strategy_optionmenu.pack(pady=5)

        self.randomize_button = ctk.CTkButton(master, text="Generate", command=self.randomize_groups)
        self.randomize_button.pack(pady=10)

        self.export_button = ctk.CTkButton(master, text="Export ke CSV", command=self.export_to_csv)
        self.export_button.pack(pady=5)

        self.history_label = ctk.CTkLabel(master, text="Hasil                                                                                           Riwayat", font=ctk.CTkFont(size=20))
        self.history_label.pack(pady=5, fill="both", expand=True)
        
        # Frame untuk hasil dan riwayats
        self.result_frame = ctk.CTkFrame(master)
        self.result_frame.pack(pady=5, fill="both", expand=True)

        # Frame untuk hasil pengacakan
        self.groups_frame = ctk.CTkFrame(self.result_frame, fg_color="gray20")
        self.groups_frame.pack(side="left", padx=5, fill="both", expand=True)

        self.groups_scrollbar = ctk.CTkScrollbar(self.groups_frame)
        self.groups_scrollbar.pack(side="right", fill="y")

        self.groups_canvas = ctk.CTkCanvas(self.groups_frame, yscrollcommand=self.groups_scrollbar.set, bg="gray20", highlightthickness=0)
        self.groups_canvas.pack(side="left", fill="both", expand=True)

        self.groups_inner_frame = ctk.CTkFrame(self.groups_canvas, fg_color="gray20")
        self.groups_canvas.create_window((0, 0), width=650 ,window=self.groups_inner_frame, anchor="nw")

        self.groups_scrollbar.configure(command=self.groups_canvas.yview)

        # Frame untuk riwayat pengacakan
        self.history_frame = ctk.CTkFrame(self.result_frame, fg_color="gray20")
        self.history_frame.pack(side="right", padx=5, fill="both", expand=True)

        self.history_scrollbar = ctk.CTkScrollbar(self.history_frame)
        self.history_scrollbar.pack(side="right", fill="y")

        self.history_canvas = ctk.CTkCanvas(self.history_frame, yscrollcommand=self.history_scrollbar.set, bg="gray20", highlightthickness=0)
        self.history_canvas.pack(side="left", fill="both", expand=True)

        self.history_inner_frame = ctk.CTkFrame(self.history_canvas, fg_color="gray20")
        self.history_canvas.create_window((0, 0),width=650, window=self.history_inner_frame, anchor="nw")

        self.history_scrollbar.configure(command=self.history_canvas.yview)\
        
        self.import_button = ctk.CTkButton(master, text="Import dari CSV", command=self.import_from_csv)
        self.import_button.pack(pady=5)

        self.history = []
        self.result_widgets = []
        self.history_widgets = []

    #PROSES INPUT DAN PEMILIHAN
    def randomize_groups(self):
        for widget in self.result_widgets:
            widget.destroy()
        self.result_widgets.clear()

        names = self.names_entry.get().split('-')
        names = [name.strip() for name in names if name.strip()]

        num_groups = self.group_entry.get()

        if not num_groups.isdigit() or int(num_groups) <= 0:
            messagebox.showwarning("Warning", "Masukkan jumlah grup yang valid.")
            return

        num_groups = int(num_groups)

        if num_groups > len(names):
            messagebox.showwarning("Warning", "Jumlah grup tidak boleh lebih banyak dari jumlah nama.")
            return

        selected_strategy = self.strategy_var.get()
        if selected_strategy == "Acak":
            strategy = RandomGroupStrategy()
        elif selected_strategy == "Abjad":
            strategy = AlphabeticalGroupStrategy()
        elif selected_strategy == "Panjang Huruf":
            strategy = LengthBasedGroupStrategy()
        elif selected_strategy == "Urutan Input":
            strategy = InputOrderGroupStrategy()

        groups = strategy.create_groups(names, num_groups)
        self.save_history(groups)
        self.display_groups(groups)

    #UNTUK MENAMPILKAN HASIL 
    def display_groups(self, groups):
        for i, group in enumerate(groups):
            group_frame = ctk.CTkFrame(self.groups_inner_frame, corner_radius=10, width=400 , fg_color="gray30")
            group_frame.pack(pady=5, padx=5, fill="x")

            group_title = ctk.CTkLabel(group_frame, text=f"Grup {i + 1}", font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
            group_title.pack(anchor="w", padx=5, pady=5)

            for j, name in enumerate(group):
                name_label = ctk.CTkLabel(group_frame, text=f"{j + 1}. {name}", font=ctk.CTkFont(size=14), text_color="white")
                name_label.pack(anchor="w", padx=10, pady=2)

            self.result_widgets.append(group_frame)

        self.groups_canvas.update_idletasks()
        self.groups_canvas.configure(scrollregion=self.groups_canvas.bbox("all"))

    #UNTUK MENYIMPAN DAN MENAMPILKAN HISTORY HASIL SEBELUMNYA
    def save_history(self, groups):
        self.history.append(groups)
        history_frame = ctk.CTkFrame(self.history_inner_frame, corner_radius=10, fg_color="gray30")
        history_frame.pack(pady=5, padx=5, fill="x")

        history_title = ctk.CTkLabel(history_frame, text=f"Hasil {len(self.history)}", font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        history_title.pack(anchor="w", padx=5, pady=5)

        for i, group in enumerate(groups):
            group_label = ctk.CTkLabel(history_frame, text=f"Grup {i+1}: {', '.join(group)}", font=ctk.CTkFont(size=14), text_color="white", wraplength=self.history_frame.winfo_width() - 20)
            group_label.pack(anchor="w", padx=10, pady=2)

        self.history_widgets.append(history_frame)

        self.history_canvas.update_idletasks()
        self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all"))
    
    #UNTUK IMPORT FILE CSV
    def import_from_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        
        if file_path:
            try:
                with open(file_path, newline='') as file:
                    reader = csv.reader(file)
                    names = []

                    for row in reader:
                        if row:
                            names.extend(row)

                    self.names_entry.delete(0, ctk.END)
                    self.names_entry.insert(0, "-".join(names))

                messagebox.showinfo("Success", "Nama berhasil di-import dari CSV.")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal melakukan import CSV: {e}")

    #PROSES UNTUK MENGEXPORT MENJADI FILE CSV
    def export_to_csv(self):
        if not self.history:
            messagebox.showwarning("Warning", "Tidak ada hasil pengacakan untuk diexport.")
            return

        groups = self.history[-1]
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                with open(file_path, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    for i, group in enumerate(groups):
                        writer.writerow([f"Grup {i+1}"] + group)
                messagebox.showinfo("Info", "Hasil grup telah diexport ke " + file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal meng-export file: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = GroupMaker(root)
    root.mainloop()