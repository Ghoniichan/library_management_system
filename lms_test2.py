import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.metrics import edit_distance

# ---------------------------
# NLTK setup (same as original)
# ---------------------------
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))
sia = SentimentIntensityAnalyzer()

# ===========================
# In-memory data (same structure)
# ===========================
books = {}      # { book_id: {title, author, available, reviews: [(text, label)], keywords:set(...) } }
borrowers = {}  # { borrower_id: {name, name_tokens:[...], borrowed_books:[book_ids]} }

# ===========================
# Core functions (logic preserved)
# ===========================

def add_book_logic(book_id, title, author):
    if not book_id or not title or not author:
        messagebox.showerror("Error", "Please complete all fields.")
        return False

    if book_id in books:
        messagebox.showerror("Error", "Book ID already exists!")
        return False

    title_tokens = [w.lower() for w in word_tokenize(title) if w.lower() not in stop_words]
    author_tokens = [w.lower() for w in word_tokenize(author) if w.lower() not in stop_words]
    keywords = set(title_tokens + author_tokens)

    books[book_id] = {
        'title': title,
        'author': author,
        'available': True,
        'reviews': [],
        'keywords': keywords
    }
    return True

def search_books_logic(query):
    if not query:
        return []

    query_tokens = [w.lower() for w in word_tokenize(query) if w.lower() not in stop_words]
    results = []
    for book_id, info in books.items():
        if not info['keywords']:
            continue
        # if any query token is within edit distance <=2 of any keyword
        if any(min(edit_distance(q, kw) for kw in info['keywords']) <= 2 for q in query_tokens):
            results.append((book_id, info))
    return results

def add_review_logic(book_id, review_text):
    if book_id not in books:
        messagebox.showerror("Error", "Book not found!")
        return None
    if not review_text:
        messagebox.showerror("Error", "Review cannot be empty.")
        return None
    sentiment = sia.polarity_scores(review_text)['compound']
    label = "Positive" if sentiment > 0 else ("Negative" if sentiment < 0 else "Neutral")
    books[book_id]['reviews'].append((review_text, label))
    return label

def add_borrower_logic(borrower_id, name):
    if not borrower_id or not name:
        messagebox.showerror("Error", "Please complete all fields.")
        return False
    if borrower_id in borrowers:
        messagebox.showerror("Error", "Borrower ID already exists!")
        return False
    name_tokens = [w.lower() for w in word_tokenize(name) if w.lower() not in stop_words]
    borrowers[borrower_id] = {
        'name': name,
        'name_tokens': name_tokens,
        'borrowed_books': []
    }
    return True

def _resolve_borrower_id(user_input):
    """Fuzzy match name or exact/ci ID; edit distance <=2 against name tokens."""
    if not user_input:
        return None
    s = user_input.lower()
    for b_id, info in borrowers.items():
        if s == b_id.lower():
            return b_id
        if info['name_tokens']:
            if min(edit_distance(t, s) for t in info['name_tokens']) <= 2:
                return b_id
    return None

def _resolve_book_id(user_input):
    """Fuzzy match title tokens/keywords or exact/ci ID; edit distance <=2."""
    if not user_input:
        return None
    s = user_input.lower()
    for b_id, info in books.items():
        if s == b_id.lower():
            return b_id
        if info['keywords']:
            if min(edit_distance(t, s) for t in info['keywords']) <= 2:
                return b_id
    return None

def borrow_book_logic():
    borrower_input = simpledialog.askstring("Borrower", "Enter Borrower Name or ID:")
    borrower_id = _resolve_borrower_id(borrower_input)
    if not borrower_id:
        messagebox.showerror("Error", "Borrower not found!")
        return None, None

    book_input = simpledialog.askstring("Book", "Enter Book Title or ID to borrow:")
    book_id = _resolve_book_id(book_input)
    if not book_id:
        messagebox.showerror("Error", "Book not found!")
        return None, None

    if not books[book_id]['available']:
        messagebox.showerror("Error", "Book is already borrowed!")
        return None, None

    books[book_id]['available'] = False
    borrowers[borrower_id]['borrowed_books'].append(book_id)
    messagebox.showinfo("Success", f"Book '{books[book_id]['title']}' borrowed by '{borrowers[borrower_id]['name']}'")
    return borrower_id, book_id

def return_book_logic():
    borrower_input = simpledialog.askstring("Borrower", "Enter Borrower Name or ID:")
    borrower_id = _resolve_borrower_id(borrower_input)
    if not borrower_id:
        messagebox.showerror("Error", "Borrower not found!")
        return None, None

    book_input = simpledialog.askstring("Book", "Enter Book Title or ID to return:")
    book_id = _resolve_book_id(book_input)
    if not book_id:
        messagebox.showerror("Error", "Book not found!")
        return None, None

    if book_id not in borrowers[borrower_id]['borrowed_books']:
        messagebox.showerror("Error", "This borrower did not borrow this book!")
        return None, None

    borrowers[borrower_id]['borrowed_books'].remove(book_id)
    books[book_id]['available'] = True
    messagebox.showinfo("Success", f"Book '{books[book_id]['title']}' returned by '{borrowers[borrower_id]['name']}'")
    return borrower_id, book_id

# ===========================
# Modern UI App
# ===========================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Library Management System")
        self.root.geometry("1200x720")
        self.root.configure(bg="#f5f6fa")

        # ttk style
        self._setup_style()

        # ---- Topbar ----
        self._build_topbar()

        # ---- Sidebar ----
        self._build_sidebar()

        # ---- Main content (switchable) ----
        self.main = tk.Frame(self.root, bg="#f5f6fa")
        self.main.pack(side="right", fill="both", expand=True)

        # Instance refs for manage view treeviews
        self.book_tree = None
        self.borrower_tree = None

        # Default view
        self.show_home()

    # ---------------- Style ----------------
    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Primary.TButton",
                        font=("Segoe UI", 11, "bold"),
                        padding=8,
                        relief="flat",
                        background="#ff7a00",
                        foreground="white")
        style.map("Primary.TButton",
                    background=[("active", "#e86e00"),   # Hover/pressed
                    ("disabled", "#a0a0a0")],
                    foreground=[("disabled", "#ffffff")])
        style.configure("Ghost.TButton",
                        font=("Segoe UI", 11),
                        padding=8,
                        relief="flat",
                        background="gray90",
                        foreground="black")
        style.map("Ghost.TButton",
                  background=[("active", "#dfe3e7")])

        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

        style.configure("TEntry", padding=6, font=("Segoe UI", 11))

    # ---------------- Topbar ----------------
    def _build_topbar(self):
        top = tk.Frame(self.root, bg="white", height=64, bd=0, highlightthickness=1, highlightbackground="#e5e7eb")
        top.pack(side="top", fill="x")

        tk.Label(top, text="📖 Library Management", font=("Segoe UI", 16, "bold"), bg="white", fg="#1f2937").pack(side="left", padx=16)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top, textvariable=self.search_var, width=50)
        self.search_entry.pack(side="left", padx=10, pady=12, ipady=4)

        ttk.Button(top, text="🔎 Search", style="Primary.TButton", command=self.search_view).pack(side="left", padx=6)

    # ---------------- Sidebar ----------------
    def _build_sidebar(self):
        side = tk.Frame(self.root, bg="#111827", width=220)
        side.pack(side="left", fill="y")

        def side_btn(text, cmd):
            b = tk.Button(side, text=text, font=("Segoe UI", 12), fg="white", bg="#111827",
                          activebackground="#1f2937", activeforeground="white",
                          relief="flat", bd=0, anchor="w", command=cmd)
            b.pack(fill="x", padx=14, pady=4, ipady=6)
            return b

        side_btn("🏠  Home", self.show_home)
        side_btn("📚  My Library", self.show_my_library)
        side_btn("🛠️  Manage", self.show_manage)
        side_btn("➕  Issue Book", self.show_issue_book)
        side_btn("👤  Add Borrower", self.show_add_borrower)
        side_btn("🚪  Logout", self.root.quit)

    # ---------------- Helpers ----------------
    def _clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def _section_title(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 16, "bold"), bg="#f5f6fa", fg="#111827").pack(anchor="w", padx=20, pady=16)

    def _card(self, parent):
        f = tk.Frame(parent, bg="white", bd=1, relief="solid", highlightthickness=0)
        f.pack(fill="x", padx=20, pady=10)
        return f

    def _pill(self, parent, text, fg="#065f46", bg="#d1fae5"):
        lab = tk.Label(parent, text=text, bg=bg, fg=fg, font=("Segoe UI", 9, "bold"))
        lab.pack(side="left", padx=4, pady=2, ipadx=6, ipady=2)

    # ---------------- Views ----------------
    def show_home(self):
        self._clear_main()
        self._section_title(self.main, "📌 Recommended / All Books")

        container = tk.Frame(self.main, bg="#f5f6fa")
        container.pack(fill="both", expand=True)

        if not books:
            tk.Label(container, text="No books yet. Add some from ➕ Issue Book.",
                     font=("Segoe UI", 11), bg="#f5f6fa", fg="#6b7280").pack(pady=20)
            return

        for book_id, info in books.items():
            card = self._card(container)

            header = tk.Frame(card, bg="white")
            header.pack(fill="x", padx=12, pady=10)

            # Title + author
            title = tk.Label(header, text=info['title'], font=("Segoe UI", 13, "bold"), bg="white", fg="#111827")
            title.pack(anchor="w")
            tk.Label(header, text=f"by {info['author']}", font=("Segoe UI", 10), bg="white", fg="#6b7280").pack(anchor="w")

            # Availability pill
            pill_wrap = tk.Frame(header, bg="white")
            pill_wrap.pack(anchor="e")
            if info['available']:
                self._pill(pill_wrap, "Available", fg="#065f46", bg="#d1fae5")
            else:
                self._pill(pill_wrap, "Borrowed", fg="#92400e", bg="#ffedd5")

            # Actions
            actions = tk.Frame(card, bg="#f9fafb")
            actions.pack(fill="x", padx=12, pady=10)

            ttk.Button(actions, text="View Details", style="Ghost.TButton",
                       command=lambda b=book_id: self.open_book_details(b)).pack(side="left", padx=4)
            ttk.Button(actions, text="Borrow", style="Primary.TButton",
                       state=("normal" if info['available'] else "disabled"),
                       command=lambda b=book_id: self._borrow_and_refresh(b)).pack(side="left", padx=4)

    def show_my_library(self):
        self._clear_main()
        self._section_title(self.main, "📖 My Library (Borrowed Books)")

        container = tk.Frame(self.main, bg="#f5f6fa")
        container.pack(fill="both", expand=True)

        # Collect borrowed items across borrowers (for display)
        borrowed_pairs = []
        for borrower_id, info in borrowers.items():
            for b_id in info['borrowed_books']:
                borrowed_pairs.append((borrower_id, b_id))

        if not borrowed_pairs:
            tk.Label(container, text="No borrowed books.",
                     font=("Segoe UI", 11), bg="#f5f6fa", fg="#6b7280").pack(pady=20)
            return

        for borrower_id, b_id in borrowed_pairs:
            info = books[b_id]
            card = self._card(container)

            tk.Label(card, text=info['title'], font=("Segoe UI", 13, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=12, pady=6)
            tk.Label(card, text=f"by {info['author']} — Borrowed by {borrowers[borrower_id]['name']}",
                     font=("Segoe UI", 10), bg="white", fg="#6b7280").pack(anchor="w", padx=12, pady=2)

            act = tk.Frame(card, bg="#f9fafb")
            act.pack(fill="x", padx=12, pady=10)
            ttk.Button(act, text="View Details", style="Ghost.TButton",
                       command=lambda b=b_id: self.open_book_details(b)).pack(side="left", padx=4)
            ttk.Button(act, text="Return", style="Primary.TButton",
                       command=lambda: self._return_and_refresh()).pack(side="left", padx=4)

    def show_manage(self):
        self._clear_main()
        self._section_title(self.main, "🛠️ Manage (Books & Borrowers)")

        wrap = tk.Frame(self.main, bg="#f5f6fa")
        wrap.pack(fill="both", expand=True, padx=16, pady=4)

        # Books table
        books_frame = tk.LabelFrame(wrap, text="Books", font=("Segoe UI", 11, "bold"), bg="#f5f6fa", fg="#111827")
        books_frame.pack(fill="both", expand=True, side="left", padx=8, pady=8)

        self.book_tree = ttk.Treeview(books_frame, columns=("ID", "Title", "Author", "Available"), show="headings")
        for col in ("ID", "Title", "Author", "Available"):
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=120 if col in ("ID", "Available") else 220, anchor="w")
        self.book_tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Borrowers table
        borrowers_frame = tk.LabelFrame(wrap, text="Borrowers", font=("Segoe UI", 11, "bold"), bg="#f5f6fa", fg="#111827")
        borrowers_frame.pack(fill="both", expand=True, side="right", padx=8, pady=8)

        self.borrower_tree = ttk.Treeview(borrowers_frame, columns=("ID", "Name", "Borrowed Books"), show="headings")
        for col in ("ID", "Name", "Borrowed Books"):
            self.borrower_tree.heading(col, text=col)
            self.borrower_tree.column(col, width=160 if col != "Borrowed Books" else 260, anchor="w")
        self.borrower_tree.pack(fill="both", expand=True, padx=8, pady=8)

        self.update_book_list()
        self.update_borrower_list()

        # Quick circulation buttons (uses the NLP dialogs)
        btns = tk.Frame(self.main, bg="#f5f6fa")
        btns.pack(fill="x", padx=20, pady=8)
        ttk.Button(btns, text="Borrow Book", style="Primary.TButton",
                   command=self._borrow_and_refresh).pack(side="left", padx=4)
        ttk.Button(btns, text="Return Book", style="Ghost.TButton",
                   command=self._return_and_refresh).pack(side="left", padx=4)

    def show_issue_book(self):
        self._clear_main()
        self._section_title(self.main, "➕ Issue Book")

        form = tk.Frame(self.main, bg="white", bd=1, relief="solid")
        form.pack(padx=20, pady=10, anchor="n")

        labels = ["Book ID", "Title", "Author"]
        self.issue_entries = {}

        for i, label in enumerate(labels):
            tk.Label(form, text=label, font=("Segoe UI", 11), bg="white").grid(row=i, column=0, sticky="e", padx=12, pady=8)
            ent = ttk.Entry(form, width=40)
            ent.grid(row=i, column=1, padx=12, pady=8, ipady=3)
            self.issue_entries[label] = ent

        def submit():
            ok = add_book_logic(
                self.issue_entries["Book ID"].get(),
                self.issue_entries["Title"].get(),
                self.issue_entries["Author"].get()
            )
            if ok:
                messagebox.showinfo("Success", "Book added!")
                self.show_manage()

        btns = tk.Frame(form, bg="white")
        btns.grid(row=len(labels), column=0, columnspan=2, pady=12)
        ttk.Button(btns, text="Add to Library", style="Primary.TButton", command=submit).pack(side="left", padx=6)
        ttk.Button(btns, text="Cancel", style="Ghost.TButton", command=self.show_home).pack(side="left", padx=6)

    def show_add_borrower(self):
        self._clear_main()
        self._section_title(self.main, "👤 Add Borrower")

        form = tk.Frame(self.main, bg="white", bd=1, relief="solid")
        form.pack(padx=20, pady=10, anchor="n")

        labels = ["Borrower ID", "Name"]
        self.borrower_entries = {}

        for i, label in enumerate(labels):
            tk.Label(form, text=label, font=("Segoe UI", 11), bg="white").grid(row=i, column=0, sticky="e", padx=12, pady=8)
            ent = ttk.Entry(form, width=40)
            ent.grid(row=i, column=1, padx=12, pady=8, ipady=3)
            self.borrower_entries[label] = ent

        def submit_borrower():
            ok = add_borrower_logic(
                self.borrower_entries["Borrower ID"].get(),
                self.borrower_entries["Name"].get()
            )
            if ok:
                messagebox.showinfo("Success", "Borrower added!")
                self.show_manage()

        btns = tk.Frame(form, bg="white")
        btns.grid(row=len(labels), column=0, columnspan=2, pady=12)
        ttk.Button(btns, text="Save Borrower", style="Primary.TButton", command=submit_borrower).pack(side="left", padx=6)
        ttk.Button(btns, text="Cancel", style="Ghost.TButton", command=self.show_home).pack(side="left", padx=6)

    def search_view(self):
        self._clear_main()
        q = self.search_var.get()
        self._section_title(self.main, f"🔎 Search Results for “{q}”")

        container = tk.Frame(self.main, bg="#f5f6fa")
        container.pack(fill="both", expand=True)

        results = search_books_logic(q)
        if not results:
            tk.Label(container, text="No matching books found.",
                     font=("Segoe UI", 11), bg="#f5f6fa", fg="#6b7280").pack(pady=20)
            return

        for book_id, info in results:
            card = self._card(container)
            header = tk.Frame(card, bg="white")
            header.pack(fill="x", padx=12, pady=10)
            tk.Label(header, text=info['title'], font=("Segoe UI", 13, "bold"), bg="white", fg="#111827").pack(anchor="w")
            tk.Label(header, text=f"by {info['author']}", font=("Segoe UI", 10), bg="white", fg="#6b7280").pack(anchor="w")

            actions = tk.Frame(card, bg="#f9fafb")
            actions.pack(fill="x", padx=12, pady=10)

            ttk.Button(actions, text="View Details", style="Ghost.TButton",
                       command=lambda b=book_id: self.open_book_details(b)).pack(side="left", padx=4)
            ttk.Button(actions, text="Borrow", style="Primary.TButton",
                       state=("normal" if info['available'] else "disabled"),
                       command=lambda b=book_id: self._borrow_and_refresh(b)).pack(side="left", padx=4)

    # ---------- Book Details + Reviews (live update after save) ----------
    def open_book_details(self, book_id):
        if book_id not in books:
            messagebox.showerror("Error", "Book not found!")
            return

        info = books[book_id]

        win = tk.Toplevel(self.root)
        win.title(info['title'])
        win.geometry("520x520")
        win.configure(bg="white")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text=info['title'], font=("Segoe UI", 15, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=16, pady=10)
        tk.Label(win, text=f"by {info['author']}", font=("Segoe UI", 11), bg="white", fg="#6b7280").pack(anchor="w", padx=16)

        status = "Available" if info['available'] else "Borrowed"
        st_fg, st_bg = ("#065f46", "#d1fae5") if info['available'] else ("#92400e", "#ffedd5")
        tag = tk.Label(win, text=status, bg=st_bg, fg=st_fg, font=("Segoe UI", 9, "bold"))
        tag.pack(anchor="w", padx=16, pady=8, ipadx=6, ipady=2)

        sep = ttk.Separator(win, orient="horizontal")
        sep.pack(fill="x", padx=12, pady=8)

        # Reviews list
        tk.Label(win, text="Reviews", font=("Segoe UI", 12, "bold"), bg="white", fg="#111827").pack(anchor="w", padx=16, pady=6)

        review_box = tk.Frame(win, bg="#f9fafb")
        review_box.pack(fill="both", expand=True, padx=16, pady=6)

        review_list = tk.Listbox(review_box, font=("Segoe UI", 10), bd=0, highlightthickness=0)
        review_list.pack(fill="both", expand=True, padx=8, pady=8)

        def refresh_reviews():
            review_list.delete(0, tk.END)
            if not books[book_id]['reviews']:
                review_list.insert(tk.END, "No reviews yet.")
            else:
                for text, label in books[book_id]['reviews']:
                    review_list.insert(tk.END, f"[{label}] {text}")

        refresh_reviews()

        # Add review area
        add_wrap = tk.Frame(win, bg="white")
        add_wrap.pack(fill="x", padx=16, pady=6)
        tk.Label(add_wrap, text="Write a review:", font=("Segoe UI", 10), bg="white").pack(anchor="w")

        review_var = tk.StringVar()
        review_entry = ttk.Entry(add_wrap, textvariable=review_var, width=52)
        review_entry.pack(fill="x", pady=6, ipady=4)

        def save_review():
            text = review_var.get().strip()
            label = add_review_logic(book_id, text)
            if label:
                review_var.set("")
                refresh_reviews()  # ✅ live update after save

        btns = tk.Frame(win, bg="white")
        btns.pack(fill="x", padx=16, pady=8)
        ttk.Button(btns, text="Save Review", style="Primary.TButton", command=save_review).pack(side="left", padx=4)
        ttk.Button(btns, text="Close", style="Ghost.TButton", command=win.destroy).pack(side="left", padx=4)

    # ---------------- List updaters (Manage view) ----------------
    def update_book_list(self):
        if not self.book_tree:
            return
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
        for book_id, info in books.items():
            self.book_tree.insert("", "end", values=(book_id, info['title'], info['author'], 'Yes' if info['available'] else 'No'))

    def update_borrower_list(self):
        if not self.borrower_tree:
            return
        self.borrower_tree.delete(*self.borrower_tree.get_children())
        for borrower_id, info in borrowers.items():
            borrowed_books_str = ", ".join(info['borrowed_books'])
            self.borrower_tree.insert("", "end", values=(borrower_id, info['name'], borrowed_books_str))

    # ---------------- Circulation triggers (keep NLP dialogs) ----------------
    def _borrow_and_refresh(self, _book_id=None):
        brr_id, b_id = borrow_book_logic()
        # refresh visible views
        if b_id:
            self.update_book_list()
            self.update_borrower_list()
            self.show_home()

    def _return_and_refresh(self):
        brr_id, b_id = return_book_logic()
        if b_id:
            self.update_book_list()
            self.update_borrower_list()
            self.show_my_library()

# ===========================
# Run
# ===========================
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
