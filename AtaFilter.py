import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

df_global = None  # داده CSV یا Excel پس از بارگذاری

def browse_csv():
    global df_global
    file_path = filedialog.askopenfilename(filetypes=[("CSV or Excel Files", "*.csv *.xlsx")])
    if file_path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                df = pd.read_excel(file_path)

            df.columns = df.columns.str.strip()
            df_global = df

            columns = df.columns.tolist()
            column_dropdown['values'] = columns
            if columns:
                column_dropdown.current(0)

        except Exception as e:
            messagebox.showerror("خطا", f"❌ خطا در خواندن فایل:\n{e}")

def browse_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, folder_path)

def process_csv():
    global df_global
    file_path = csv_entry.get()
    output_base = output_entry.get()
    group_column = column_dropdown.get().strip()
    delimiter = delimiter_entry.get()

    if df_global is None:
        messagebox.showerror("خطا", "لطفاً فایل ورودی را انتخاب کنید.")
        return

    if not output_base or not group_column:
        messagebox.showerror("خطا", "لطفاً پوشه خروجی و ستون را مشخص کنید.")
        return

    if not delimiter:
        messagebox.showerror("خطا", "لطفاً کاراکتر جداکننده را وارد کنید.")
        return

    try:
        df = df_global
        if group_column not in df.columns:
            messagebox.showerror("خطا", f'ستون "{group_column}" در فایل وجود ندارد.')
            return

        unique_groups = df[group_column].dropna().unique()

        for group in unique_groups:
            group_df = df[df[group_column] == group]
            row_count = len(group_df)

            safe_group_name = str(group).strip().replace('/', '_').replace('\\', '_') \
                                 .replace(':', '_').replace('*', '_').replace('?', '_') \
                                 .replace('"', '_').replace('<', '_').replace('>', '_') \
                                 .replace('|', '_').replace('\n', '').replace('\r', '').replace(' ', '_')

            group_folder = os.path.join(output_base, safe_group_name)
            os.makedirs(group_folder, exist_ok=True)

            output_file = os.path.join(group_folder, f'{safe_group_name} ({row_count}).csv')

            # ذخیره با جداکننده مشخص‌شده
            group_df.to_csv(output_file, index=False, encoding='utf-8-sig', sep=delimiter)

            # اضافه کردن خط مخفی
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write('\n# تولید شده توسط  برنامه AtaFilter | نسخه: 1.0.0\n')

        messagebox.showinfo("موفق", "✅ همه فایل‌ها با موفقیت ذخیره شدند.")
    except Exception as e:
        messagebox.showerror("خطا", f"❌ خطا در پردازش:\n{e}")

# ساخت پنجره اصلی
root = tk.Tk()
root.title("AtaFilter برنامه ")
root.geometry("700x360")
root.resizable(False, False)

tk.Label(root, text="📄 مسیر فایل CSV یا Excel:").grid(row=0, column=0, sticky="e", padx=5, pady=10)
csv_entry = tk.Entry(root, width=50)
csv_entry.grid(row=0, column=1, padx=5)
tk.Button(root, text="Browse", command=browse_csv).grid(row=0, column=2, padx=5)

tk.Label(root, text="📁 مسیر ذخیره خروجی:").grid(row=1, column=0, sticky="e", padx=5, pady=10)
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=5)
tk.Button(root, text="Browse", command=browse_output_folder).grid(row=1, column=2, padx=5)

tk.Label(root, text="🔑 انتخاب ستون گروه‌بندی:").grid(row=2, column=0, sticky="e", padx=5, pady=10)
column_dropdown = ttk.Combobox(root, state="readonly", width=47)
column_dropdown.grid(row=2, column=1, padx=5)

tk.Label(root, text="🔣 کاراکتر جداکننده خروجی:").grid(row=3, column=0, sticky="e", padx=5, pady=10)
delimiter_entry = tk.Entry(root, width=10)
delimiter_entry.grid(row=3, column=1, sticky="w", padx=5)
delimiter_entry.insert(0, ",")  # مقدار پیش‌فرض

tk.Button(root, text="🚀 اجرا", command=process_csv, bg="green", fg="white", font=("tahoma", 12)).grid(row=4, column=1, pady=30)

root.mainloop()
