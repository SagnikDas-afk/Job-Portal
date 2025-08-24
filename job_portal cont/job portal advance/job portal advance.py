import tkinter as tk
from tkinter import ttk, messagebox, filedialog

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
        self.create_widgets()

    def create_widgets(self):
        # Create a style for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Choose a ttk theme

        # Colorful style configurations
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
        
        # Create a top frame for login, sign up, and profile buttons
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

        self.jobs = [
            Job("Software Engineer", "Develop web applications", "$100,000", "Tech Solutions"),
            Job("Data Scientist", "Analyze data and build predictive models", "$120,000", "Data Insights"),
            Job("Marketing Manager", "Lead marketing campaigns", "$90,000", "Global Marketing"),
            Job("Product Manager", "Manage product development lifecycle", "$110,000", "Product Innovations"),
            Job("Graphic Designer", "Design marketing materials and brand assets", "$80,000", "Creative Studios"),
            Job("Accountant", "Maintain financial records", "$70,000", "Finance Corp"),
            Job("HR Manager", "Oversee human resources activities", "$85,000", "HR Solutions"),
            Job("Sales Executive", "Generate sales leads", "$95,000", "Sales Pro"),
            Job("Customer Service Representative", "Assist customers with inquiries", "$75,000", "Service Solutions"),
            Job("Project Manager", "Coordinate project activities", "$105,000", "Project Management Inc"),
            Job("UX/UI Designer", "Create intuitive user interfaces", "$85,000", "Design Innovations"),
            Job("Network Engineer", "Manage network infrastructure", "$100,000", "Network Systems"),
            Job("Quality Assurance Analyst", "Test software products", "$90,000", "QA Solutions")
        ]

        self.show_jobs_button = ttk.Button(self.master, text="Show Current Jobs", style="SearchButton.TButton", command=self.display_current_jobs)
        self.show_jobs_button.pack()

    def open_login_page(self):
        login_window = tk.Toplevel(self.master)
        login_window.title("Login")

        # Get the screen width and height
        screen_width = login_window.winfo_screenwidth()
        screen_height = login_window.winfo_screenheight()

        # Calculate x and y coordinates for the login window to be centered
        x = (screen_width - 400) / 2
        y = (screen_height - 200) / 2

        # Set the login window to be centered
        login_window.geometry("400x200+%d+%d" % (x, y))

        ttk.Label(login_window, text="Enter Your Login ID", font=('Helvetica', 16), style="Subtitle.TLabel").pack(pady=10)

        login_entry = ttk.Entry(login_window)
        login_entry.pack(pady=10)

        ttk.Button(login_window, text="Login", style="SearchButton.TButton", command=lambda: self.login(login_entry.get())).pack(pady=20)

    def open_signup_page(self):
        signup_window = tk.Toplevel(self.master)
        signup_window.title("Sign Up")

        # Get the screen width and height
        screen_width = signup_window.winfo_screenwidth()
        screen_height = signup_window.winfo_screenheight()

        # Calculate x and y coordinates for the signup window to be centered
        x = (screen_width - 400) / 2
        y = (screen_height - 300) / 2

        # Set the signup window to be centered
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

        # Get the screen width and height
        screen_width = profile_window.winfo_screenwidth()
        screen_height = profile_window.winfo_screenheight()

        # Calculate x and y coordinates for the profile window to be centered
        x = (screen_width - 400) / 2
        y = (screen_height - 300) / 2

        # Set the profile window to be centered
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
            # Do something with the selected file, like displaying it in the UI or saving its path
            print("Selected file:", filename)

    def save_profile(self, name, email, experience, skills):
        messagebox.showinfo("Profile Saved", "Your profile has been saved successfully!")

    def login(self, login_id):
        messagebox.showinfo("Login", f"Login ID: {login_id}")

    def signup(self, email, username, password, remember_me):
        messagebox.showinfo("Sign Up", f"Email: {email}\nUsername: {username}\nPassword: {password}\nRemember Me: {remember_me}")

    def search_jobs(self):
        query = self.search_entry.get().lower()
        found_jobs = [job for job in self.jobs if query in job.title.lower() or query in job.description.lower() or query in job.company.lower()]
        if found_jobs:
            self.display_jobs(found_jobs)
        else:
            messagebox.showinfo("Job Search", "No matching jobs found!")

    def display_jobs(self, jobs=None):
        if jobs is None:
            jobs = self.jobs
        for job in jobs:
            job_frame = ttk.Frame(self.scrollable_frame.scrollable_frame, relief=tk.RIDGE, borderwidth=2)
            job_frame.pack(fill=tk.BOTH, padx=10, pady=5)

            title_label = ttk.Label(job_frame, text=f"Title: {job.title}", font=('Helvetica', 12))
            title_label.pack(anchor=tk.W)

            description_label = ttk.Label(job_frame, text=f"Description: {job.description}", font=('Helvetica', 12))
            description_label.pack(anchor=tk.W)

            salary_label = ttk.Label(job_frame, text=f"Salary: {job.salary}", font=('Helvetica', 12))
            salary_label.pack(anchor=tk.W)

            company_label = ttk.Label(job_frame, text=f"Company: {job.company}", font=('Helvetica', 12))
            company_label.pack(anchor=tk.W)

            view_details_button = ttk.Button(job_frame, text="View Details", command=lambda j=job: self.view_job_details(j))
            view_details_button.pack()

    def view_job_details(self, job):
        details_window = tk.Toplevel(self.master)
        details_window.title(job.title)

        ttk.Label(details_window, text=f"Title: {job.title}", font=('Helvetica', 14, 'bold')).pack(pady=5)
        ttk.Label(details_window, text=f"Description: {job.description}", font=('Helvetica', 12)).pack(anchor=tk.W, padx=10)
        ttk.Label(details_window, text=f"Salary: {job.salary}", font=('Helvetica', 12)).pack(anchor=tk.W, padx=10)
        ttk.Label(details_window, text=f"Company: {job.company}", font=('Helvetica', 12)).pack(anchor=tk.W, padx=10)

    def display_current_jobs(self):
        self.display_jobs()

def main():
    root = tk.Tk()
    app = JobPortalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
