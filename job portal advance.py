import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

# =========================
# Configuration
# =========================
DB_HOST = "localhost"
DB_USER = "jobuser"
DB_PASSWORD = "jobpassword"
DB_NAME = "job_portal"     # database will be created if it doesn't exist


# =========================
# Domain Models
# =========================
class Job:
    def __init__(self, id_, title, description, salary, company):
        self.id = id_
        self.title = title
        self.description = description
        self.salary = salary
        self.company = company


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self._win = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Make inner frame adapt to width
        def _configure_inner(event):
            self.canvas.itemconfig(self._win, width=event.width)
        self.canvas.bind('<Configure>', _configure_inner)


# =========================
# Main Application
# =========================
class JobPortalApp:
    def __init__(self, master):
        self.master = master
        master.title("Job Portal")
        master.attributes('-fullscreen', True)

        self.conn = None
        self.cursor = None

        self._create_styles()
        self._create_layout()
        self.connect_db()
        self.ensure_schema()
        self.seed_sample_data_if_empty()
        self.load_jobs_from_db()

    # ---------- UI ----------
    def _create_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

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

    def _create_layout(self):
        # Top bar
        self.top_frame = ttk.Frame(self.master)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.login_button = ttk.Button(self.top_frame, text="Login", style="TopButton.TButton", command=self.open_login_page)
        self.login_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.signup_button = ttk.Button(self.top_frame, text="Sign Up", style="TopButton.TButton", command=self.open_signup_page)
        self.signup_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.profile_button = ttk.Button(self.top_frame, text="Your Profile", style="TopButton.TButton", command=self.view_profile)
        self.profile_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.add_job_button = ttk.Button(self.top_frame, text="Add Job", style="TopButton.TButton", command=self.open_add_job)
        self.add_job_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.label = ttk.Label(self.master, text="Welcome to the Job Portal!", style="Title.TLabel")
        self.label.pack(pady=10)

        # Search
        search_wrap = ttk.Frame(self.master)
        search_wrap.pack(pady=5)
        self.search_entry = ttk.Entry(search_wrap, width=60, font=('Helvetica', 12))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_button = ttk.Button(search_wrap, text="Search", style="SearchButton.TButton", command=self.search_jobs)
        self.search_button.pack(side=tk.LEFT)

        # Results list
        self.scrollable_frame = ScrollableFrame(self.master)
        self.scrollable_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Footer
        bottom_bar = ttk.Frame(self.master)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.show_jobs_button = ttk.Button(bottom_bar, text="Show Current Jobs", style="SearchButton.TButton", command=self.display_current_jobs)
        self.show_jobs_button.pack(side=tk.LEFT, padx=10, pady=8)
        self.quit_button = ttk.Button(bottom_bar, text="Quit", style="QuitButton.TButton", command=self.master.quit)
        self.quit_button.pack(side=tk.RIGHT, padx=10, pady=8)

    # ---------- DB ----------
    def connect_db(self):
        try:
            # Connect without database to create DB if missing
            tmp_conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
            tmp_cursor = tmp_conn.cursor()
            tmp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            tmp_cursor.close()
            tmp_conn.close()

            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("Database connected successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def ensure_schema(self):
        if not self.cursor:
            return
        stmts = [
            # employer
            """
            CREATE TABLE IF NOT EXISTS employer (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                COMPANY VARCHAR(100) NOT NULL UNIQUE,
                INDUSTRY VARCHAR(100) NOT NULL,
                LOCATION VARCHAR(100) NOT NULL,
                Website VARCHAR(255) UNIQUE,
                ContactPerson VARCHAR(100) NOT NULL,
                PhoneNo VARCHAR(20) NOT NULL UNIQUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            # jobseeker
            """
            CREATE TABLE IF NOT EXISTS jobseeker (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                Username VARCHAR(80) UNIQUE,
                PasswordHash VARCHAR(255),
                Name VARCHAR(100),
                Email VARCHAR(120) UNIQUE,
                Experience VARCHAR(50),
                Skills TEXT,
                PicturePath VARCHAR(255)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            # joblisting
            """
            CREATE TABLE IF NOT EXISTS joblisting (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                Title VARCHAR(120) NOT NULL,
                Description TEXT NOT NULL,
                Salary VARCHAR(50),
                CompanyID INT,
                FOREIGN KEY (CompanyID) REFERENCES employer(ID) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            # job_application
            """
            CREATE TABLE IF NOT EXISTS job_application (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                JobID INT NOT NULL,
                JobSeekerID INT NOT NULL,
                ApplicationDate DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                Status ENUM('Pending','Accepted','Rejected') NOT NULL DEFAULT 'Pending',
                CoverLetter TEXT,
                FOREIGN KEY (JobID) REFERENCES joblisting(ID) ON DELETE CASCADE,
                FOREIGN KEY (JobSeekerID) REFERENCES jobseeker(ID) ON DELETE CASCADE,
                UNIQUE(JobID, JobSeekerID)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
        ]
        for s in stmts:
            self.cursor.execute(s)
        self.conn.commit()

    def seed_sample_data_if_empty(self):
        # seed minimal employer + jobs if table empty
        self.cursor.execute("SELECT COUNT(*) AS c FROM employer")
        if self.cursor.fetchone()["c"] == 0:
            employers = [
                ("Tech Solutions", "Software", "Bengaluru", "https://techsolutions.example", "A. Kumar", "+91-9876543210"),
                ("Data Insights", "Analytics", "Pune", "https://datainsights.example", "S. Rao", "+91-9988776655"),
                ("Global Marketing", "Marketing", "Mumbai", "https://globalmkt.example", "R. Singh", "+91-9123456780"),
            ]
            self.cursor.executemany(
                """
                INSERT INTO employer (COMPANY, INDUSTRY, LOCATION, Website, ContactPerson, PhoneNo)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                employers,
            )
            self.conn.commit()

        self.cursor.execute("SELECT COUNT(*) AS c FROM joblisting")
        if self.cursor.fetchone()["c"] == 0:
            # map company names to ids
            self.cursor.execute("SELECT ID, COMPANY FROM employer")
            m = {row['COMPANY']: row['ID'] for row in self.cursor.fetchall()}
            jobs = [
                ("Software Engineer", "Develop web applications", "$100,000", m.get("Tech Solutions")),
                ("Data Scientist", "Analyze data and build predictive models", "$120,000", m.get("Data Insights")),
                ("Marketing Manager", "Lead marketing campaigns", "$90,000", m.get("Global Marketing")),
            ]
            self.cursor.executemany(
                """
                INSERT INTO joblisting (Title, Description, Salary, CompanyID)
                VALUES (%s, %s, %s, %s)
                """,
                jobs,
            )
            self.conn.commit()

    def load_jobs_from_db(self):
        try:
            sql = (
                "SELECT j.ID, j.Title, j.Description, j.Salary, e.COMPANY "
                "FROM joblisting j LEFT JOIN employer e ON j.CompanyID = e.ID "
                "ORDER BY j.ID DESC"
            )
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            self.jobs = [Job(r['ID'], r['Title'], r['Description'], r['Salary'] or "N/A", r['COMPANY'] or "Unknown") for r in rows]
            self.refresh_job_list(self.jobs)
        except mysql.connector.Error as err:
            messagebox.showerror("DB Error", f"Failed to load jobs: {err}")

    # ---------- CRUD helpers ----------
    def add_employer(self, company, industry, location, website, contact_person, phone):
        sql = (
            "INSERT INTO employer (COMPANY, INDUSTRY, LOCATION, Website, ContactPerson, PhoneNo) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        self.cursor.execute(sql, (company, industry, location, website, contact_person, phone))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_job(self, title, desc, salary, company_id):
        sql = "INSERT INTO joblisting (Title, Description, Salary, CompanyID) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(sql, (title, desc, salary, company_id))
        self.conn.commit()
        return self.cursor.lastrowid

    # ---------- UI Actions ----------
    def search_jobs(self):
        query = (self.search_entry.get() or "").strip().lower()
        if not query:
            self.refresh_job_list(self.jobs)
            return
        found = [j for j in self.jobs if query in j.title.lower() or query in j.description.lower() or query in j.company.lower()]
        if found:
            self.refresh_job_list(found)
        else:
            messagebox.showinfo("Job Search", "No matching jobs found!")

    def refresh_job_list(self, jobs):
        # clear
        for child in self.scrollable_frame.scrollable_frame.winfo_children():
            child.destroy()
        # repopulate
        for job in jobs:
            job_frame = ttk.Frame(self.scrollable_frame.scrollable_frame, style="JobFrame.TFrame", relief=tk.RIDGE, borderwidth=2)
            job_frame.pack(fill=tk.BOTH, padx=10, pady=6)

            title_label = ttk.Label(job_frame, text=f"{job.title}", font=('Helvetica', 13, 'bold'))
            title_label.pack(anchor=tk.W, padx=8, pady=(6,0))

            description_label = ttk.Label(job_frame, text=f"{job.description}", font=('Helvetica', 11))
            description_label.pack(anchor=tk.W, padx=8)

            meta = ttk.Label(job_frame, text=f"Company: {job.company}    •    Salary: {job.salary}", font=('Helvetica', 10))
            meta.pack(anchor=tk.W, padx=8, pady=(0,6))

            ttk.Button(job_frame, text="View Details", command=lambda j=job: self.view_job_details(j)).pack(padx=8, pady=(0,8))

    def display_current_jobs(self):
        self.load_jobs_from_db()

    # ---------- Auth & Profile ----------
    def open_login_page(self):
        win = tk.Toplevel(self.master)
        win.title("Login")
        win.geometry(self._centered_geometry(400, 220))

        ttk.Label(win, text="Enter Username", style="Subtitle.TLabel").pack(pady=10)
        username_entry = ttk.Entry(win)
        username_entry.pack(pady=4)
        ttk.Label(win, text="Password", style="Content.TLabel").pack()
        password_entry = ttk.Entry(win, show="*")
        password_entry.pack(pady=4)

        ttk.Button(win, text="Login", style="SearchButton.TButton",
                   command=lambda: self.login(username_entry.get(), password_entry.get(), win)).pack(pady=12)

    def open_signup_page(self):
        win = tk.Toplevel(self.master)
        win.title("Sign Up")
        win.geometry(self._centered_geometry(420, 360))

        ttk.Label(win, text="Sign Up", style="Subtitle.TLabel").pack(pady=10)

        entries = {}
        for label in ["Email", "Username", "Password", "Name"]:
            ttk.Label(win, text=f"{label}:", style="Content.TLabel").pack()
            e = ttk.Entry(win, show="*" if label == "Password" else None)
            e.pack(pady=2)
            entries[label] = e

        remember_var = tk.BooleanVar()
        ttk.Checkbutton(win, text="Remember Me", variable=remember_var).pack(pady=6)

        ttk.Button(
            win,
            text="Create Account",
            style="SearchButton.TButton",
            command=lambda: self.signup(
                email=entries["Email"].get(),
                username=entries["Username"].get(),
                password=entries["Password"].get(),
                name=entries["Name"].get(),
                remember_me=remember_var.get(),
                win=win,
            ),
        ).pack(pady=10)

    def view_profile(self):
        win = tk.Toplevel(self.master)
        win.title("Your Profile")
        win.geometry(self._centered_geometry(460, 440))

        ttk.Label(win, text="Add Your Details", style="Subtitle.TLabel").pack(pady=10)

        ttk.Label(win, text="Name:", style="Content.TLabel").pack()
        name_entry = ttk.Entry(win)
        name_entry.pack()

        ttk.Label(win, text="Email:", style="Content.TLabel").pack()
        email_entry = ttk.Entry(win)
        email_entry.pack()

        ttk.Label(win, text="Experience:", style="Content.TLabel").pack()
        experience_entry = ttk.Entry(win)
        experience_entry.pack()

        ttk.Label(win, text="Skills:", style="Content.TLabel").pack()
        skills_entry = ttk.Entry(win)
        skills_entry.pack()

        ttk.Label(win, text="Upload Picture:", style="Content.TLabel").pack()
        ttk.Button(win, text="Upload", style="SearchButton.TButton", command=lambda: self.upload_picture(win)).pack(pady=4)

        ttk.Button(
            win,
            text="Save",
            style="SearchButton.TButton",
            command=lambda: self.save_profile(name_entry.get(), email_entry.get(), experience_entry.get(), skills_entry.get()),
        ).pack(pady=16)

    def upload_picture(self, parent):
        filename = filedialog.askopenfilename(parent=parent, title="Select Profile Picture", filetypes=(("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*")))
        if filename:
            messagebox.showinfo("Selected", filename)
            # Optionally store the path somewhere or copy to app folder.
            return filename
        return None

    def login(self, username, password, win):
        if not username:
            messagebox.showwarning("Login", "Please enter username")
            return
        self.cursor.execute("SELECT ID, Username FROM jobseeker WHERE Username=%s", (username,))
        row = self.cursor.fetchone()
        if row:
            messagebox.showinfo("Login", f"Welcome back, {row['Username']} (ID {row['ID']})")
            win.destroy()
        else:
            messagebox.showwarning("Login", "User not found. Please sign up.")

    def signup(self, email, username, password, name, remember_me, win):
        if not username or not email:
            messagebox.showwarning("Sign Up", "Email and Username are required")
            return
        try:
            self.cursor.execute(
                "INSERT INTO jobseeker (Username, PasswordHash, Name, Email) VALUES (%s, %s, %s, %s)",
                (username, password, name, email),
            )
            self.conn.commit()
            messagebox.showinfo("Sign Up", f"Account created for {username}\nRemember Me: {remember_me}")
            win.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Sign Up Error", str(err))

    def save_profile(self, name, email, experience, skills):
        # For demo: upsert by email (if exists update, else insert minimal row)
        if not email:
            messagebox.showwarning("Profile", "Email is required to save profile")
            return
        try:
            self.cursor.execute("SELECT ID FROM jobseeker WHERE Email=%s", (email,))
            row = self.cursor.fetchone()
            if row:
                self.cursor.execute(
                    "UPDATE jobseeker SET Name=%s, Experience=%s, Skills=%s WHERE ID=%s",
                    (name, experience, skills, row['ID']),
                )
            else:
                self.cursor.execute(
                    "INSERT INTO jobseeker (Name, Email, Experience, Skills) VALUES (%s, %s, %s, %s)",
                    (name, email, experience, skills),
                )
            self.conn.commit()
            messagebox.showinfo("Profile Saved", "Your profile has been saved successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("DB Error", f"{err}")

    # ---------- Job details ----------
    def view_job_details(self, job):
        win = tk.Toplevel(self.master)
        win.title(job.title)
        win.geometry(self._centered_geometry(520, 360))

        ttk.Label(win, text=f"Title: {job.title}", font=('Helvetica', 14, 'bold')).pack(pady=6)
        ttk.Label(win, text=f"Company: {job.company}", font=('Helvetica', 12)).pack(anchor=tk.W, padx=10)
        ttk.Label(win, text=f"Salary: {job.salary}", font=('Helvetica', 12)).pack(anchor=tk.W, padx=10)
        ttk.Label(win, text=f"Description:\n{job.description}", font=('Helvetica', 12), wraplength=480, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=10)

        ttk.Button(win, text="Apply Now", style="SearchButton.TButton", command=lambda: self.open_apply_dialog(job)).pack(pady=10)

    def open_apply_dialog(self, job):
        win = tk.Toplevel(self.master)
        win.title(f"Apply: {job.title}")
        win.geometry(self._centered_geometry(520, 420))

        ttk.Label(win, text="Your Email (will create profile if new):", style="Content.TLabel").pack(pady=(10,0))
        email_entry = ttk.Entry(win, width=40)
        email_entry.pack(pady=4)

        ttk.Label(win, text="Cover Letter:", style="Content.TLabel").pack(pady=(10,0))
        cover = tk.Text(win, width=60, height=10)
        cover.pack(padx=8, pady=6)

        def submit():
            email = email_entry.get().strip()
            cover_text = cover.get("1.0", tk.END).strip()
            if not email:
                messagebox.showwarning("Apply", "Email required")
                return
            # ensure jobseeker exists
            self.cursor.execute("SELECT ID FROM jobseeker WHERE Email=%s", (email,))
            row = self.cursor.fetchone()
            if not row:
                self.cursor.execute("INSERT INTO jobseeker (Email) VALUES (%s)", (email,))
                self.conn.commit()
                jobseeker_id = self.cursor.lastrowid
            else:
                jobseeker_id = row['ID']
            # insert application
            try:
                self.cursor.execute(
                    "INSERT INTO job_application (JobID, JobSeekerID, ApplicationDate, Status, CoverLetter) VALUES (%s, %s, %s, %s, %s)",
                    (job.id, jobseeker_id, datetime.now(), 'Pending', cover_text or None),
                )
                self.conn.commit()
                messagebox.showinfo("Applied", "Application submitted!")
                win.destroy()
            except mysql.connector.Error as err:
                if err.errno == 1062:  # duplicate key (unique JobID, JobSeekerID)
                    messagebox.showwarning("Already Applied", "You have already applied for this job.")
                else:
                    messagebox.showerror("DB Error", str(err))

        ttk.Button(win, text="Submit Application", style="SearchButton.TButton", command=submit).pack(pady=10)

    # ---------- Add Job UI ----------
    def open_add_job(self):
        win = tk.Toplevel(self.master)
        win.title("Add Job Listing")
        win.geometry(self._centered_geometry(520, 520))

        # Employer dropdown populated from DB
        ttk.Label(win, text="Employer:", style="Content.TLabel").pack(pady=(10,0))
        employer_var = tk.StringVar()
        employer_combo = ttk.Combobox(win, textvariable=employer_var, state="readonly", width=46)
        self.cursor.execute("SELECT ID, COMPANY FROM employer ORDER BY COMPANY")
        employers = self.cursor.fetchall()
        employer_combo['values'] = [f"{e['ID']} - {e['COMPANY']}" for e in employers]
        employer_combo.pack(pady=4)

        def get_selected_employer_id():
            val = employer_var.get()
            return int(val.split(" - ")[0]) if val else None

        for label in ["Title", "Salary"]:
            ttk.Label(win, text=f"{label}:", style="Content.TLabel").pack(pady=(8,0))
            entry = ttk.Entry(win, width=48)
            entry.pack()
            if label == "Title":
                title_entry = entry
            else:
                salary_entry = entry

        ttk.Label(win, text="Description:", style="Content.TLabel").pack(pady=(8,0))
        desc_text = tk.Text(win, width=60, height=8)
        desc_text.pack(padx=8, pady=6)

        def save_job():
            cid = get_selected_employer_id()
            title = title_entry.get().strip()
            desc = desc_text.get("1.0", tk.END).strip()
            salary = salary_entry.get().strip()
            if not (cid and title and desc):
                messagebox.showwarning("Add Job", "Employer, Title and Description are required")
                return
            try:
                self.add_job(title, desc, salary, cid)
                messagebox.showinfo("Success", "Job added")
                win.destroy()
                self.load_jobs_from_db()
            except mysql.connector.Error as err:
                messagebox.showerror("DB Error", str(err))

        ttk.Button(win, text="Save Job", style="SearchButton.TButton", command=save_job).pack(pady=10)

    # ---------- Utils ----------
    def _centered_geometry(self, w, h):
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 2)
        return f"{w}x{h}+{x}+{y}"


def main():
    root = tk.Tk()
    app = JobPortalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
