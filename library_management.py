import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1200x700")
        self.configure(bg="#f5f5f5")

        # Main container
        self.container = tk.Frame(self, bg="#f5f5f5")
        self.container.pack(fill="both", expand=True)

        # Layout: Sidebar + Main Content
        self.sidebar = tk.Frame(self.container, bg="#333", width=200)
        self.sidebar.pack(side="left", fill="y")

        self.main_content = tk.Frame(self.container, bg="white")
        self.main_content.pack(side="right", fill="both", expand=True)

        # Store books for Book Entry page
        self.books = []

        self.create_sidebar()
        self.create_header()
        self.show_home_page()

    def create_sidebar(self):
        """Sidebar with navigation buttons"""
        logo = tk.Label(self.sidebar, text="LorimIpsum", fg="white", bg="#333", font=("Arial", 16, "bold"))
        logo.pack(pady=20)

        # Navigation Buttons
        nav_buttons = [
            ("Home", self.show_home_page),
            ("My Library", self.show_library_page),
            ("Borrower Management", self.show_borrower_page),
            ("Book Entry", self.show_book_entry_page),
            ("Logout", self.quit)
        ]

        for name, command in nav_buttons:
            btn = tk.Button(self.sidebar, text=name, command=command,
                            bg="#444", fg="white", font=("Arial", 12),
                            relief="flat", pady=10)
            btn.pack(fill="x", pady=5)

    def create_header(self):
        """Search bar on top of main content"""
        self.header = tk.Frame(self.main_content, bg="white", height=60)
        self.header.pack(fill="x")

        search_entry = ttk.Entry(self.header, width=50)
        search_entry.pack(padx=20, pady=10, side="left")

        search_btn = tk.Button(self.header, text="Search", bg="#555", fg="white")
        search_btn.pack(side="left", padx=5)

    def clear_main_area(self):
        """Clears content below header"""
        for widget in self.main_content.winfo_children():
            if widget != self.header:
                widget.destroy()

    def show_home_page(self):
        """Recommended Books page"""
        self.clear_main_area()

        content = tk.Frame(self.main_content, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        lbl = tk.Label(content, text="Recommended", font=("Arial", 16, "bold"), bg="white")
        lbl.pack(anchor="w")

        # Example book covers + ratings
        book_data = [
            ("images/book1.jpg", "4.5/5"),
            ("images/book2.png", "4.0/5"),
            ("images/book3.jpg", "5.0/5"),
            ("images/book4.jpg", "3.5/5"),
        ]

        books_frame = tk.Frame(content, bg="white")
        books_frame.pack(fill="x", pady=10)

        for path, rating in book_data:
            try:
                img = Image.open(path)
                img = img.resize((120, 160))
                photo = ImageTk.PhotoImage(img)

                # Container for image + rating
                card = tk.Frame(books_frame, bg="white")
                card.pack(side="left", padx=10)

                # Book image
                label = tk.Label(card, image=photo, bg="white")
                label.image = photo  # keep reference
                label.pack(side="top")

                # Rating below image
                tk.Label(card, text=rating, bg="white").pack(side="top", pady=5)

            except Exception as e:
                print(f"Error loading {path}: {e}")

    def show_library_page(self):
        """User's Library"""
        self.clear_main_area()

        content = tk.Frame(self.main_content, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        lbl = tk.Label(content, text="My Books", font=("Arial", 16, "bold"), bg="white")
        lbl.pack(anchor="w")

        books_frame = tk.Frame(content, bg="white")
        books_frame.pack(fill="x", pady=10)

        for i in range(5):
            book = tk.Frame(books_frame, bg="#ddd", width=150, height=200)
            book.pack(side="left", padx=10)

    def show_book_detail(self, title="Learning Python"):
        """Book detail view"""
        self.clear_main_area()

        content = tk.Frame(self.main_content, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Book Cover + Info
        book_frame = tk.Frame(content, bg="white")
        book_frame.pack(fill="x")

        cover = tk.Frame(book_frame, bg="#ddd", width=120, height=180)
        cover.pack(side="left", padx=10)

        info_frame = tk.Frame(book_frame, bg="white")
        info_frame.pack(side="left", padx=10)

        tk.Label(info_frame, text=title, font=("Arial", 16, "bold"), bg="white").pack(anchor="w")
        tk.Label(info_frame, text="Author: Pablo Escobar", bg="white").pack(anchor="w")
        tk.Label(info_frame, text="Rating: 4.5/5", bg="white").pack(anchor="w")
        tk.Label(info_frame, text="Description: Lorem ipsum dolor sit amet...", wraplength=600, bg="white").pack(anchor="w", pady=5)

        # Metadata
        details = {
            "Publisher": "Python Co.",
            "First Publish": "December 2019",
            "Language": "Filipino",
            "Pages": "50"
        }
        for k, v in details.items():
            tk.Label(info_frame, text=f"{k}: {v}", bg="white").pack(anchor="w")

        borrow_btn = tk.Button(content, text="Borrow", bg="#007BFF", fg="white", font=("Arial", 12))
        borrow_btn.pack(pady=10)

    def show_borrower_page(self):
        """Borrower Management page"""
        self.clear_main_area()

        content = tk.Frame(self.main_content, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        lbl = tk.Label(content, text="Borrower Management", font=("Arial", 16, "bold"), bg="white")
        lbl.pack(anchor="w")

        # Table for borrower list
        cols = ("Borrower", "Book", "Status", "Due Date")
        table = ttk.Treeview(content, columns=cols, show="headings", height=10)
        for col in cols:
            table.heading(col, text=col)
            table.column(col, width=150)

        table.pack(fill="both", expand=True, pady=10)

        # Example Data
        table.insert("", "end", values=("John Doe", "Learning Python", "Borrowed", "2025-09-20"))

    # ----------- Integrated Book Entry Page -----------
    def show_book_entry_page(self):
        """Book Entry page: add/delete books"""
        self.clear_main_area()

        content = tk.Frame(self.main_content, bg="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(content, text="Add / Delete Books", font=("Arial", 16, "bold"), bg="white").pack(anchor="w")

        form_frame = tk.Frame(content, bg="white")
        form_frame.pack(anchor="w", pady=10)

        tk.Label(form_frame, text="Title:", bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.entry_title = tk.Entry(form_frame, width=30)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Author:", bg="white").grid(row=1, column=0, padx=5, pady=5)
        self.entry_author = tk.Entry(form_frame, width=30)
        self.entry_author.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Year:", bg="white").grid(row=2, column=0, padx=5, pady=5)
        self.entry_year = tk.Entry(form_frame, width=30)
        self.entry_year.grid(row=2, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Book", command=self.add_book).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Book", command=self.delete_book).grid(row=0, column=1, padx=5)

        self.listbox = tk.Listbox(content, width=50, height=10)
        self.listbox.pack(pady=10)

        self.update_listbox()

    def add_book(self):
        title = self.entry_title.get()
        author = self.entry_author.get()
        year = self.entry_year.get()

        if title and author and year:
            self.books.append((title, author, year))
            self.update_listbox()
            self.entry_title.delete(0, tk.END)
            self.entry_author.delete(0, tk.END)
            self.entry_year.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    def delete_book(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.books.pop(index)
            self.update_listbox()
        else:
            messagebox.showwarning("Selection Error", "Please select a book to delete.")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for idx, (title, author, year) in enumerate(self.books, start=1):
            self.listbox.insert(tk.END, f"{idx}. {title} by {author} ({year})")


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
