import sqlite3
import datetime

# ANSI color codes
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RED = "\033[31m"
RESET = "\033[0m"

def initialize_db() -> None:
    """Initialize database and create table if not exists"""
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  author TEXT NOT NULL,
                  publication_year INTEGER NOT NULL,
                  genre TEXT NOT NULL,
                  read_status INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

def load_books() -> list[dict[str, object]]:
    """Load books from database into list of dictionaries"""
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('SELECT title, author, publication_year, genre, read_status FROM books')
    books: list[dict[str, object]] = []
    for row in c.fetchall():
        books.append({
            'title': row[0],
            'author': row[1],
            'publication_year': row[2],
            'genre': row[3],
            'read_status': bool(row[4])
        })
    conn.close()
    return books

def save_books(books: list[dict[str, object]]) -> None:
    """Save current library to database"""
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute('DELETE FROM books')  # Clear existing data
    
    for book in books:
        c.execute('''INSERT INTO books 
                     (title, author, publication_year, genre, read_status)
                     VALUES (?, ?, ?, ?, ?)''',
                  (book['title'], book['author'], book['publication_year'],
                   book['genre'], 1 if book['read_status'] else 0))
    conn.commit()
    conn.close()

def print_menu() -> None:
    """Display main menu with colorful formatting"""
    print(f"\n{YELLOW}Personal Library Manager{RESET}")
    print(f"{BLUE}1.{RESET} Add a book")
    print(f"{BLUE}2.{RESET} Remove a book")
    print(f"{BLUE}3.{RESET} Search for books")
    print(f"{BLUE}4.{RESET} Display all books")
    print(f"{BLUE}5.{RESET} Show statistics")
    print(f"{BLUE}6.{RESET} Exit")
    print("-------------------------")

def add_book(books: list[dict[str, object]]) -> None:
    """Add a new book with comprehensive validation"""
    print(f"\n{YELLOW}Add New Book{RESET}")
    title = input("Title: ").strip()
    while not title:
        print(f"{RED}Title cannot be empty!{RESET}")
        title = input("Title: ").strip()

    author = input("Author: ").strip()
    while not author:
        print(f"{RED}Author cannot be empty!{RESET}")
        author = input("Author: ").strip()

    current_year = datetime.datetime.now().year
    while True:
        year = input("Publication Year: ")
        try:
            year = int(year)
            if 1800 <= year <= current_year:
                break
            print(f"{RED}Year must be between 1800 and {current_year}{RESET}")
        except ValueError:
            print(f"{RED}Invalid year format!{RESET}")

    genre = input("Genre: ").strip()
    while not genre:
        print(f"{RED}Genre cannot be empty!{RESET}")
        genre = input("Genre: ").strip()

    read_status = input("Have you read this book? (yes/no): ").lower()
    while read_status not in ['yes', 'no', 'y', 'n']:
        print(f"{RED}Please enter yes/no{RESET}")
        read_status = input("Have you read this book? (yes/no): ").lower()
    
    books.append({
        'title': title,
        'author': author,
        'publication_year': year,
        'genre': genre,
        'read_status': read_status in ['yes', 'y']
    })
    print(f"{GREEN}Book added successfully!{RESET}")

def remove_book(books: list[dict[str, object]]) -> None:
    """Remove books with confirmation and multiple match handling"""
    print(f"\n{YELLOW}Remove Book{RESET}")
    search_term = input("Enter title to remove: ").strip().lower()
    matches = [b for b in books if search_term in b['title'].lower()]
    
    if not matches:
        print(f"{RED}No matching books found{RESET}")
        return

    print(f"\n{BLUE}Found {len(matches)} matches:{RESET}")
    for i, book in enumerate(matches, 1):
        status = "Read" if book['read_status'] else "Unread"
        print(f"{i}. {book['title']} by {book['author']} ({book['genre']}) - {status}")

    while True:
        choice = input("Enter number to remove (0 to cancel): ")
        if choice == '0':
            print(f"{YELLOW}Removal cancelled{RESET}")
            return
        try:
            index = int(choice) - 1
            if 0 <= index < len(matches):
                confirm = input(f"Remove '{matches[index]['title']}'? (yes/no): ").lower()
                if confirm in ['y', 'yes']:
                    books.remove(matches[index])
                    print(f"{GREEN}Book removed successfully!{RESET}")
                else:
                    print(f"{YELLOW}Removal cancelled{RESET}")
                return
        except ValueError:
            pass
        print(f"{RED}Invalid selection!{RESET}")

def search_books(books: list[dict[str, object]]) -> None:
    """Enhanced search with flexible matching"""
    print(f"\n{YELLOW}Search Options{RESET}")
    print(f"{BLUE}1.{RESET} Search by Title")
    print(f"{BLUE}2.{RESET} Search by Author")
    choice = input("Choose search type: ")
    
    if choice not in ['1', '2']:
        print(f"{RED}Invalid choice!{RESET}")
        return

    term = input("Enter search term: ").lower()
    results: list[dict[str, object]] = []
    if choice == '1':
        results = [b for b in books if term in b['title'].lower()]
    else:
        results = [b for b in books if term in b['author'].lower()]

    if not results:
        print(f"{RED}No matches found{RESET}")
        return

    print(f"\n{BLUE}Found {len(results)} matches:{RESET}")
    for i, book in enumerate(results, 1):
        status = "Read" if book['read_status'] else "Unread"
        print(f"{i}. {book['title']} by {book['author']} ({book['publication_year']})")
        print(f"   Genre: {book['genre']} | Status: {status}")

def display_all_books(books: list[dict[str, object]]) -> None:
    """Display with sorting options and rich formatting"""
    if not books:
        print(f"{YELLOW}Your library is empty{RESET}")
        return

    print(f"\n{YELLOW}Sort Options{RESET}")
    print(f"{BLUE}1.{RESET} Title (A-Z)")
    print(f"{BLUE}2.{RESET} Author (A-Z)")
    print(f"{BLUE}3.{RESET} Year (Newest)")
    print(f"{BLUE}4.{RESET} Genre (A-Z)")
    choice = input("Choose sort method: ").strip() or '1'

    sort_key = 'title'
    reverse = False
    if choice == '2':
        sort_key = 'author'
    elif choice == '3':
        sort_key = 'publication_year'
        reverse = True
    elif choice == '4':
        sort_key = 'genre'

    sorted_books = sorted(books, key=lambda x: x[sort_key], reverse=reverse)
    
    print(f"\n{BLUE}Your Library ({len(sorted_books)} books):{RESET}")
    for i, book in enumerate(sorted_books, 1):
        status = "Read" if book['read_status'] else "Unread"
        print(f"{i}. {YELLOW}{book['title']}{RESET} by {book['author']}")
        print(f"   Published: {book['publication_year']} | Genre: {book['genre']}")
        print(f"   Status: {GREEN if book['read_status'] else RED}{status}{RESET}\n")

def display_statistics(books: list[dict[str, object]]) -> None:
    """Enhanced statistics with genre/author analysis"""
    total = len(books)
    print(f"\n{YELLOW}Library Statistics{RESET}")
    print(f"{BLUE}Total Books:{RESET} {total}")

    if total == 0:
        return

    # Read percentage
    read_count = sum(1 for b in books if b['read_status'])
    print(f"{BLUE}Read Percentage:{RESET} {(read_count/total)*100:.1f}%")

    # Genre analysis
    genres: dict[str, int] = {}
    for b in books:
        genres[b['genre']] = genres.get(b['genre'], 0) + 1
    if genres:
        popular = max(genres.items(), key=lambda x: x[1])
        print(f"\n{BLUE}Most Popular Genre:{RESET} {popular[0]} ({popular[1]} books)")

    # Author analysis
    authors: dict[str, int] = {}
    for b in books:
        authors[b['author']] = authors.get(b['author'], 0) + 1
    if authors:
        prolific = max(authors.items(), key=lambda x: x[1])
        print(f"{BLUE}Most Prolific Author:{RESET} {prolific[0]} ({prolific[1]} books)")

def main() -> None:
    """Main program loop"""
    initialize_db()
    books = load_books()
    
    print(f"\n{YELLOW}Welcome to your Personal Library Manager!{RESET}")
    while True:
        print_menu()
        choice = input(f"{BLUE}Enter your choice (1-6): {RESET}").strip()
        
        if choice == '1':
            add_book(books)
        elif choice == '2':
            remove_book(books)
        elif choice == '3':
            search_books(books)
        elif choice == '4':
            display_all_books(books)
        elif choice == '5':
            display_statistics(books)
        elif choice == '6':
            save_books(books)
            print(f"{GREEN}Library saved successfully!{RESET}")
            print(f"{YELLOW}Goodbye!{RESET}")
            break
        else:
            print(f"{RED}Invalid choice! Please enter 1-6{RESET}")

if __name__ == "__main__":
    main()