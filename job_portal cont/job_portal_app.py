import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3

class Job:
    def __init__(self, title, description, salary, company):
        self.title = title
        self.description = description
        self.salary = salary
        self.company = company

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class JobPortalApp:
    def __init__(self, master):
        self.master = master
        master.title("Job Portal")
        master.attributes('-fullscreen', True)  # Set fullscreen mode

        # Connect to the database
        self.conn = sqlite3.connect('job_portal.db')
        self.cursor = self.conn.cursor()

        self.create_widgets()

    def create_widgets(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TopButton.TButton", foreground="white", background="#007bff", font=('Helvetica', 10))
        self.style.map("TopButton.TButton", background=[("active", "#0056b3")])

        self.style.configure("Title.TLabel", foreground="#007bff", font=('Helvetica', 24, 'bold'))
        self.style.configure("Subtitle.TLabel", font=('Helvetica', 14))

        self.style.configure("Content.TLabel", font=('Helvetica', 12), background="#f8f9fa")
        self.style.configure("SearchButton.TButton", font=('Helvetica', 12), foreground="white", background="#28a745")
        self.style.map("SearchButton.TButton", background=[("active", "#218838")])

        self.style.configure("JobFrame.TFrame", background="#f8f9fa", borderwidth=2)
        self.style.configure("QuitButton.TButton", font=('Helvetica', 12), foreground="white", background="#dc3545")
        self.style.map("QuitButton.TButton", background=[("active", "#c82333")])

        self.top_frame = ttk.Frame(self.master, style="My.TFrame")
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.login_button = ttk.Button(self.top_frame, text="Login", style="TopButton.TButton", command=self.open_login_page)
        self.login_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.signup_button = ttk.Button(self.top_frame, text="Sign Up", style="TopButton.TButton", command=self.open_signup_page)
        self.signup_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.profile_button = ttk.Button(self.top_frame, text="Your Profile", style="TopButton.TButton", command=self.view_profile)
        self.profile_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.label = ttk.Label(self.master, text="Welcome to the Job Portal!", font=('Helvetica', 24), style="Title.TLabel")
        self.label.pack(pady=20)

        self.search_label = ttk.Label(self.master, text="Search Job:", font=('Helvetica', 14), style="Subtitle.TLabel")
        self.search_label.pack()

        self.search_entry = ttk.Entry(self.master, width=50, font=('Helvetica', 12))
        self.search_entry.pack(pady=10)

        self.search_button = ttk.Button(self.master, text="Search", style="SearchButton.TButton", command=self.search_jobs)
        self.search_button.pack()

        self.scrollable_frame = ScrollableFrame(self.master)
        self.scrollable_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.quit_button = ttk.Button(self.master, text="Quit", style="QuitButton.TButton", command=self.master.quit)
        self.quit_button.pack(side=tk.BOTTOM, pady=20)

        self.show_jobs_button = ttk.Button(self.master, text="Show Current Jobs", style="SearchButton.TButton", command=self.display_current_jobs)
        self.show_jobs_button.pack()

    def open_login_page(self):
        login_window = tk.Toplevel(self.master)
        login_window.title("Login")

        screen_width = login_window.winfo_screenwidth()
        screen_height = login_window.winfo_screenheight()
        x = (screen_width - 400) / 2
        y = (screen_height - 200) / 2
        login_window.geometry("400x200+%d+%d" % (x, y))

        ttk.Label(login_window, text="Enter Your Login ID", font=('Helvetica', 16), style="Subtitle.TLabel").pack(pady=10)

        login_entry = ttk.Entry(login_window)
        login_entry.pack(pady=10)

        ttk.Button(login_window, text="Login", style="SearchButton.TButton", command=lambda: self.login(login_entry.get())).pack(pady=20)

    def open_signup_page(self):
        signup_window = tk.Toplevel(self.master)
        signup_window.title("Sign Up")

        screen_width = signup_window.winfo_screenwidth()
        screen_height = signup_window.winfo_screenheight()
        x = (screen_width - 400) / 2
        y = (screen_height - 300) / 2
        signup_window.geometry("400x300+%d+%d" % (x, y))

        ttk.Label(signup_window, text="Sign Up", font=('Helvetica', 16), style="Subtitle.TLabel").pack(pady=10)

        ttk.Label(signup_window, text="Email:", font=('Helvetica', 12), style="Content.TLabel").pack()
        email_entry = ttk.Entry(signup_window)
        email_entry.pack()

        ttk.Label(signup_window, text="Username:", font=('Helvetica', 12), style="Content.TLabel").pack()
        username_entry = ttk.Entry(signup_window)
        username_entry.pack()

        ttk.Label(signup_window, text="Password:", font=('Helvetica', 12), style="Content.TLabel").pack()
        password_entry = ttk.Entry(signup_window, show="*")
        password_entry.pack()

        remember_me_var = tk.BooleanVar()
        remember_me_checkbutton = ttk.Checkbutton(signup_window, text="Remember Me", variable=remember_me_var)
        remember_me_checkbutton.pack()

        ttk.Button(signup_window, text="Sign Up", style="SearchButton.TButton", command=lambda: self.signup(email_entry.get(), username_entry.get(), password_entry.get(), remember_me_var.get())).pack(pady=20)

    def view_profile(self):
        profile_window = tk.Toplevel(self.master)
        profile_window.title("Your Profile")

        screen_width = profile_window.winfo_screenwidth()
        screen_height = profile_window.winfo_screenheight()
        x = (screen_width - 400) / 2
        y = (screen_height - 300) / 2
        profile_window.geometry("400x300+%d+%d" % (x, y))

        ttk.Label(profile_window, text="Add Your Details", font=('Helvetica', 16), style="Subtitle.TLabel").pack(pady=10)

        ttk.Label(profile_window, text="Name:", font=('Helvetica', 12), style="Content.TLabel").pack()
        name_entry = ttk.Entry(profile_window)
        name_entry.pack()

        ttk.Label(profile_window, text="Email:", font=('Helvetica', 12), style="Content.TLabel").pack()
        email_entry = ttk.Entry(profile_window)
        email_entry.pack()

        ttk.Label(profile_window, text="Experience:", font=('Helvetica', 12), style="Content.TLabel").pack()
        experience_entry = ttk.Entry(profile_window)
        experience_entry.pack()

        ttk.Label(profile_window, text="Skills:", font=('Helvetica', 12), style="Content.TLabel").pack()
        skills_entry = ttk.Entry(profile_window)
        skills_entry.pack()

        ttk.Label(profile_window, text="Upload Picture:", font=('Helvetica', 12), style="Content.TLabel").pack()
        upload_button = ttk.Button(profile_window, text="Upload", style="SearchButton.TButton", command=self.upload_picture)
        upload_button.pack()

        ttk.Button(profile_window, text="Save", style="SearchButton.TButton", command=lambda: self.save_profile(name_entry.get(), email_entry.get(), experience_entry.get(), skills_entry.get())).pack(pady=20)

    def upload_picture(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select Profile Picture", filetypes=(("Image files", "*.jpg; *.jpeg; *.png"), ("All files", "*.*")))
        if filename:
            messagebox.showinfo("Success", "Profile picture uploaded successfully.")

    def save_profile(self, name, email, experience, skills):
        self.cursor.execute("INSERT INTO profiles (name, email, experience, skills) VALUES (?, ?, ?, ?)", (name, email, experience, skills))
        self.conn.commit()
        messagebox.showinfo("Success", "Profile details saved successfully.")

    def login(self, login_id):
        self.cursor.execute("SELECT * FROM profiles WHERE id = ?", (login_id,))
        user = self.cursor.fetchone()
        if user:
            messagebox.showinfo("Success", "Login successful!")
        else:
            messagebox.showerror("Error", "Login ID not found.")

    def signup(self, email, username, password, remember_me):
        self.cursor.execute("INSERT INTO users (email, username, password, remember_me) VALUES (?, ?, ?, ?)", (email, username, password, remember_me))
        self.conn.commit()
        messagebox.showinfo("Success", "Sign up successful!")

    def search_jobs(self):
        search_term = self.search_entry.get()
        self.cursor.execute("SELECT title, description, salary, company FROM jobs WHERE title LIKE ?", ('%' + search_term + '%',))
        jobs = self.cursor.fetchall()

        for widget in self.scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

        if jobs:
            for job in jobs:
                job_frame = ttk.Frame(self.scrollable_frame.scrollable_frame, style="JobFrame.TFrame")
                job_frame.pack(pady=10, padx=10, fill="x")

                ttk.Label(job_frame, text=job[0], font=('Helvetica', 14, 'bold'), style="Subtitle.TLabel").pack(anchor="w")
                ttk.Label(job_frame, text=f"Company: {job[3]}", font=('Helvetica', 12), style="Content.TLabel").pack(anchor="w")
                ttk.Label(job_frame, text=f"Salary: {job[2]}", font=('Helvetica', 12), style="Content.TLabel").pack(anchor="w")
                ttk.Label(job_frame, text=f"Description: {job[1]}", font=('Helvetica', 12), style="Content.TLabel").pack(anchor="w")
        else:
            ttk.Label(self.scrollable_frame.scrollable_frame, text="No jobs found.", font=('Helvetica', 12), style="Content.TLabel").pack(anchor="w")

    def display_current_jobs(self):
        self.cursor.execute("SELECT title, description, salary, company FROM jobs")
        jobs = self.cursor.fetchall()

        for widget in self.scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

        if jobs:
            for job in jobs:
                job_frame = ttk.Frame(self.scrollable_frame.scrollable_frame, style="JobFrame.TFrame")
                job_frame.pack(pady=10, padx=10, fill="x")

                ttk.Label(job_frame, text=job[0], font=('Helvetica', 14, 'bold'), style="Subtitle.TLabel").pack(anchor="w")
                ttk.Label(job_frame, text=f"Company: {job[3]}", font=('Helvetica', 12), style="Content.TLabel").pack(anchor="w")
                ttk.Label(job_frame, text=f"Salary: {job[2]}", font=('Helvetica', 12), style="Content.TLabel").pack(anchor="w")
                ttk.Label(job_frame, text=f"Description: {job[1]}", font=('Helvetica', 12), style="Content.TLabel").pack(anchor="w")
        else:
            ttk.Label(self.scrollable_frame.scrollable_frame, text="No jobs available.", font=('Helvetica', 12), style="Content.TLabel").pack(anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    app = JobPortalApp(root)
    root.mainloop()
