import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.metrics import edit_distance

# Download necessary NLTK resources
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))
sia = SentimentIntensityAnalyzer()

# In-memory data storage
books = {}
borrowers = {}

# Helper functions

# --- Book Entry & Management ---
def add_book():
    book_id = simpledialog.askstring("Book ID", "Enter Book ID:")
    if not book_id:
        return
    title = simpledialog.askstring("Title", "Enter Book Title:")
    author = simpledialog.askstring("Author", "Enter Author Name:")
    if book_id in books:
        messagebox.showerror("Error", "Book ID already exists!")
        return

    # NLP: Tokenize title & author, remove stopwords, create keywords
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
    update_book_list()
    messagebox.showinfo("Success", f"Book '{title}' added!")

# --- Search Functionality ---
def search_books():
    query = simpledialog.askstring("Search", "Enter book title or author:")
    if not query:
        return

    # NLP: Tokenize query and remove stopwords
    query_tokens = [w.lower() for w in word_tokenize(query) if w.lower() not in stop_words]

    results = []
    for book_id, info in books.items():
        # Check if any query token is close to book keywords using edit_distance
        if any(min([edit_distance(q, kw) for kw in info['keywords']]) <= 2 for q in query_tokens):
            results.append(f"{book_id}: {info['title']} by {info['author']} ({'Available' if info['available'] else 'Borrowed'})")
    if results:
        messagebox.showinfo("Search Results", "\n".join(results))
    else:
        messagebox.showinfo("Search Results", "No matching books found.")

# --- Sentiment Analysis for Reviews ---
def add_review():
    book_id = simpledialog.askstring("Book ID", "Enter Book ID to review:")
    if book_id not in books:
        messagebox.showerror("Error", "Book not found!")
        return
    review = simpledialog.askstring("Review", "Enter your review:")

    # NLP: Sentiment Analysis
    sentiment = sia.polarity_scores(review)['compound']
    sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
    books[book_id]['reviews'].append((review, sentiment_label))
    messagebox.showinfo("Review Added", f"Your review was added. Sentiment: {sentiment_label}")

# --- Borrowers Management ---
def add_borrower():
    borrower_id = simpledialog.askstring("Borrower ID", "Enter Borrower ID:")
    name = simpledialog.askstring("Name", "Enter Borrower Name:")
    if borrower_id in borrowers:
        messagebox.showerror("Error", "Borrower ID already exists!")
        return

    # NLP: Tokenize borrower name for later fuzzy search
    name_tokens = [w.lower() for w in word_tokenize(name) if w.lower() not in stop_words]

    borrowers[borrower_id] = {
        'name': name,
        'name_tokens': name_tokens,
        'borrowed_books': []
    }
    update_borrower_list()
    messagebox.showinfo("Success", f"Borrower '{name}' added!")

# --- Circulation: Borrowing & Returning ---
def borrow_book():
    borrower_input = simpledialog.askstring("Borrower", "Enter Borrower Name or ID:")
    if not borrower_input:
        messagebox.showerror("Error", "No borrower input provided!")
        return
    borrower_id = None
    # NLP: Try to match name using edit_distance
    borrower_input_lower = borrower_input.lower()
    for b_id, info in borrowers.items():
        if borrower_input_lower == b_id.lower() or min([edit_distance(t, borrower_input_lower) for t in info['name_tokens']]) <= 2:
            borrower_id = b_id
            break
    if not borrower_id:
        messagebox.showerror("Error", "Borrower not found!")
        return

    book_input = simpledialog.askstring("Book", "Enter Book Title or ID to borrow:")
    if not book_input:
        messagebox.showerror("Error", "No book input provided!")
        return
    book_id = None
    book_input_lower = book_input.lower()
    for b_id, info in books.items():
        if book_input_lower == b_id.lower() or min([edit_distance(t, book_input_lower) for t in info['keywords']]) <= 2:
            book_id = b_id
            break
    if not book_id:
        messagebox.showerror("Error", "Book not found!")
        return
    if not books[book_id]['available']:
        messagebox.showerror("Error", "Book is already borrowed!")
        return

    books[book_id]['available'] = False
    borrowers[borrower_id]['borrowed_books'].append(book_id)
    update_book_list()
    update_borrower_list()
    messagebox.showinfo("Success", f"Book '{books[book_id]['title']}' borrowed by '{borrowers[borrower_id]['name']}'")

def return_book():
    borrower_input = simpledialog.askstring("Borrower", "Enter Borrower Name or ID:")
    if not borrower_input:
        messagebox.showerror("Error", "No borrower input provided!")
        return
    borrower_id = None
    for b_id, info in borrowers.items():
        if borrower_input.lower() == b_id.lower() or min([edit_distance(t, borrower_input.lower()) for t in info['name_tokens']]) <= 2:
            borrower_id = b_id
            break
    if not borrower_id:
        messagebox.showerror("Error", "Borrower not found!")
        return

    book_input = simpledialog.askstring("Book", "Enter Book Title or ID to return:")
    if not book_input:
        messagebox.showerror("Error", "No book input provided!")
        return
    book_id = None
    for b_id, info in books.items():
        if book_input.lower() == b_id.lower() or min([edit_distance(t, book_input.lower()) for t in info['keywords']]) <= 2:
            book_id = b_id
            break
    if not book_id or book_id not in borrowers[borrower_id]['borrowed_books']:
        messagebox.showerror("Error", "This borrower did not borrow this book!")
        return

    borrowers[borrower_id]['borrowed_books'].remove(book_id)
    books[book_id]['available'] = True
    update_book_list()
    update_borrower_list()
    messagebox.showinfo("Success", f"Book '{books[book_id]['title']}' returned by '{borrowers[borrower_id]['name']}'")

# --- Update GUI lists ---
def update_book_list():
    for item in book_list.get_children():  
        book_list.delete(item)
    for book_id, info in books.items():
        book_list.insert("", "end", values=(book_id, info['title'], info['author'], 'Yes' if info['available'] else 'No'))

def update_borrower_list():
    borrower_list.delete(*borrower_list.get_children())
    for borrower_id, info in borrowers.items():
        borrowed_books = ", ".join(info['borrowed_books'])
        borrower_list.insert("", "end", values=(borrower_id, info['name'], borrowed_books))

# --- GUI ---
root = tk.Tk()
root.title("Library Management System with NLP")

# Frames
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

frame_books = tk.Frame(root)
frame_books.pack(pady=10)

frame_borrowers = tk.Frame(root)
frame_borrowers.pack(pady=10)

# Buttons
tk.Button(frame_buttons, text="Add Book", command=add_book).grid(row=0, column=0, padx=5)
tk.Button(frame_buttons, text="Search Books", command=search_books).grid(row=0, column=1, padx=5)
tk.Button(frame_buttons, text="Add Review", command=add_review).grid(row=0, column=2, padx=5)
tk.Button(frame_buttons, text="Add Borrower", command=add_borrower).grid(row=0, column=3, padx=5)
tk.Button(frame_buttons, text="Borrow Book", command=borrow_book).grid(row=0, column=4, padx=5)
tk.Button(frame_buttons, text="Return Book", command=return_book).grid(row=0, column=5, padx=5)

# Book List
tk.Label(frame_books, text="Books:").pack()
book_list = ttk.Treeview(frame_books, columns=("ID", "Title", "Author", "Available"), show="headings")
book_list.heading("ID", text="ID")
book_list.heading("Title", text="Title")
book_list.heading("Author", text="Author")
book_list.heading("Available", text="Available")
book_list.pack(fill="both", expand=True) 

# Borrower List
tk.Label(frame_borrowers, text="Borrowers:").pack()
borrower_list = ttk.Treeview(frame_borrowers, columns=("ID", "Name", "Borrowed Books"), show="headings")
borrower_list.heading("ID", text="ID")
borrower_list.heading("Name", text="Name")
borrower_list.heading("Borrowed Books", text="Borrowed Books")
borrower_list.pack()

root.mainloop()
