"""
Module Name: main.py

This module represents  CLI application that creates a customized library based on classes Book and Library, and functions
that implement the user interface. The module also has a couple of auxiliary functions to make code more readable.

The application provides:
- creating a new library or you can continue to work with the existing one;
- adding new books to the library;
- deleting book by ID;
- getting all library books (you can see key information about each book: title, author, publication year, ID, status;
- searching books by author, by title, or by year;
- changing book status.

All books data is to be saved in JSON file.
"""


import json
import os
import datetime
from time import sleep


class Book:
    """
    Class 'Book' initiates book instance and displays it for a user in a readable way.
    """

    def __init__(self, title: str, author: str, year: str, id: int, status="Available") -> None:
        self.id = id
        self.title = title
        self.author = author
        self.year = year
        self.status = status

    def __str__(self):
        return f"Title: {self.title}\nAuthor: {self.author}\nPublication date: {self.year}\nStatus: {self.status}\nID: {self.id}"


class Library:
    """
    Class 'Library' initiates creating new json file for storing books data or opens the existing one if user wants to
    work with the data saved before.
    """

    def __init__(self, lib_name: str) -> None:
        self.lib_name = f"{lib_name}.json"
        with open(self.lib_name, "a+") as my_lib:
            # creating new file for the library
            if os.path.getsize(self.lib_name) == 0:
                start_data = {"current_id": 0, "books": {}, "years": {}, "authors": {}}
                json.dump(start_data, my_lib)
            # downloading data from library data file
            my_lib.seek(0)
            self.lib_data = json.load(my_lib)

    def save_data(self) -> None:
        """
        Rewrites library data to the json file on disk.

        :return: None
        """
        with open(self.lib_name, "w+", encoding="utf-8", errors="ignore") as file:
            json.dump(self.lib_data, file, ensure_ascii=False, indent=4)

    def add_book(self, title: str, author: str, year: str) -> Book:
        """
        Creates a Book instance using provided data and calculated id, saves it to the library.

        :param title:str
        :param author:str
        :param year:str
        :return:Book
        """
        current_id = self.lib_data["current_id"]
        new_book_id = current_id + 1
        new_book = Book(title, author, year, new_book_id)

        # add new book data to the general book list
        self.lib_data["books"][str(new_book.id)] = {"title": new_book.title, "author": new_book.author,
                                                    "year": new_book.year, "status": new_book.status}
        self.lib_data["current_id"] = new_book.id

        # add new book id to the publication year index in order to make future search by year faster
        if new_book.year in self.lib_data["years"]:
            self.lib_data["years"][new_book.year].append(new_book.id)
        else:
            self.lib_data["years"][new_book.year] = [new_book.id]

        # add new book id to the author index in order to make future search by year faster
        if new_book.author in self.lib_data["authors"]:
            self.lib_data["authors"][new_book.author].append(new_book.id)
        else:
            self.lib_data["authors"][new_book.author] = [new_book.id]

        self.save_data()
        return new_book

    def delete_book(self, book: Book) -> None:
        """
        Deletes the book from the library. Change is also saved to disk.

        :param book: Book
        :return: None
        """
        # deleting book data from the general book list
        del (self.lib_data["books"][str(book.id)])

        # deleting book id from publication year index
        self.lib_data["years"][book.year].remove(book.id)
        if not self.lib_data["years"][book.year]:
            del self.lib_data["years"][book.year]

        # deleting book id from author index
        self.lib_data["authors"][book.author].remove(book.id)
        if not self.lib_data["authors"][book.author]:
            del self.lib_data["authors"][book.author]
        self.save_data()
        return

    def get_all_books(self) -> dict:
        """
        Extracts all books from the library.

        :return: dict
        """
        return self.lib_data.get("books")

    def search_by_author_or_year(self, value: str, criteria: str) -> dict:
        """
        Extracts books by author or year from all available in the library

        :param value: str
        :param criteria: str
        :return: dict
        """
        found_books = []
        if criteria == "author":
            found_books = self.lib_data["authors"].get(value, [])
        if criteria == "year":
            found_books = self.lib_data["years"].get(value, [])

        rez_books = {}
        for book in found_books:
            rez_books[book] = self.lib_data["books"][str(book)]
        return rez_books

    def search_by_title(self, title: str) -> dict:
        """
        Extracts books from library json data file by title.

        :param title: str
        :return: dict
        """
        res_books = {}
        for book in self.lib_data["books"]:
            if self.lib_data["books"][book]["title"].lower() == title.lower():
                res_books[book] = self.lib_data["books"][book]
        return res_books

    def search_by_id(self, id: str) -> dict:
        """
        Extracts a book by ID from all available in the library

        :param id: str
        :return: dict
        """
        return self.lib_data["books"].get(id, None)

    def change_book_status(self, book: Book, new_status: str) -> None:
        """
        Changes the book status. Change is also saved to disk.

        :param book: Book
        :param new_status: str
        :return: None
        """
        self.lib_data["books"][str(book.id)]["status"] = new_status
        self.save_data()
        return


def check_input(start_value: int) -> int:
    """
    Checks whether user entered exactly number as requested

    :param start_value: int
    :return: int
    """
    value = start_value
    try:
        value = int(input("Enter required option: "))
    except ValueError:
        print("You can enter only digits corresponding to the options above")
    finally:
        return value


def add(lib: Library) -> None:
    """
    Asks user for data about the new book and adds it to the library.

    :param lib: Library
    :return:
    """
    title = input("Enter book title: ").strip()
    if not title:
        print("Title can not be empty")
        print("")
        return

    author = input("Enter author name: ").strip()
    if not author:
        print("Title can not be empty")
        print("")
        return

    year = input("Enter publication year: ").strip()

    # check whether user entered digits
    try:
        int_year = int(year)
    except ValueError:
        print("Incorrect year value. Use only digits.")
        print("")
        return

    # check whether user entered real year value.
    # the oldest extant printed book is a work of the Diamond Sutra and dates back to 868 CE (Google)
    if int_year < 868 or int_year > datetime.datetime.now().year:
        print(f"Incorrect year value. It must be in range from 868 until {datetime.datetime.now().year}")
        print("")
        return

    new_book = lib.add_book(title, author, year)
    print("The following book was added to the library:")
    print(f"{new_book}")
    print("")
    return


def delete(lib: Library) -> None:
    """
    Finds the book by ID, gets confirmation from the user for deletion and deletes the book from the library

    :param lib: Library
    :return: None
    """

    try:
        id = int(input("Enter book ID to delete: ").strip())
    except ValueError:
        print("Incorrect ID input.ID must be a number.")
        print("")
        return

    found = lib.search_by_id(str(id))
    if found is None:
        print(f"Book with id: {id} was not found")
        print("")
        return

    book = Book(found["title"], found["author"], found["year"], id, found["status"])
    print("Are you sure you want to delete book:")
    print(book)

    print("Choose Operation Reference Number from the listed below:")
    print(f"1 - 'Delete'\n2 - 'Cancel deletion'")
    decision = check_input(0)
    if decision == 0:
        return
    if decision == 1:
        lib.delete_book(book)
        print(f"The book with id: {id} was deleted from the library")
        print("")
    elif decision == 2:
        print(f"The deletion of book with id: {id} was canceled")
        print("")
    else:
        print("")


def books_list(lib: Library) -> None:
    """
    Lists all books to the user
    :param lib: Library
    :return: None
    """
    books = lib.get_all_books()
    if not books:
        print("There are no books in the library")
        print("")
        return
    print(f"'{lib.lib_name[:-5]}' Library Books:")
    counter = 0
    for book in books:
        counter += 1
        current = Book(books[book]["title"],
                       books[book]["author"],
                       books[book]["year"],
                       book,
                       books[book]["status"])
        print(f"---------------({counter})---------------")
        print(current)
    print(f"---------- Total: {counter} books ----------")
    print("")
    return


def ask_for_repeat_search(criteria: str, current_choice: int) -> int:
    """
    Asks user whether he wants to repeat search by criteria.

    :param criteria: str
    :param current_choice: int
    :return: int
    """
    print(f"Do you want to repeat the search by {criteria}?")
    print("")
    print("Choose Operation Reference Number from the listed below:")
    print(f"1 - 'Yes, repeat the search by {criteria}'\n2 - 'No, finish the search'")
    decision = check_input(4)
    if decision == 1:
        return current_choice
    return 4


def search(lib: Library) -> None:
    """
    Manages search options (by author, by title or by year), uses appropriate search method depending on search
    criteria and prints book(s) found in library according to the value provided.
    :param lib: Library
    :return: None
    """
    print("Specify the search criteria")
    print("Choose Operation Reference Number from the listed below:")
    print("1 - 'Search by author'")
    print("2 - 'Search by title'")
    print("3 - 'Search by publication year'")
    print("4 - 'Cancel the search'")
    decision = check_input(4)
    books = {}
    criteria = None
    while decision in (1, 2, 3):
        if decision == 1 or decision == 3:
            if decision == 1:
                author = input("Enter author name for search:  ").strip()
                criteria = "author"
                books = lib.search_by_author_or_year(author, criteria)
            if decision == 3:
                year = input("Enter publication year for search:  ").strip()
                criteria = "year"
                books = lib.search_by_author_or_year(year, criteria)
        if decision == 2:
            title = input("Enter title for search:  ").strip()
            criteria = "title"
            books = lib.search_by_title(title)

        if not books:
            print("Search result: 0 books")
            decision = ask_for_repeat_search(criteria, decision)
        else:
            counter = 0
            for book in books:
                counter += 1
                current = Book(books[book]["title"], books[book]["author"],
                               books[book]["year"], book,
                               books[book]["status"])
                print(f"---------------({counter})---------------")
                print(current)
            print(f"---------- Total: {counter} books ----------")
            print("")
            decision = ask_for_repeat_search(criteria, decision)

    if decision == 4:
        print("Canceling the search...")
        sleep(1)
    else:
        print("Incorrect input")
        print("")


def change_status(lib: Library) -> None:
    """
    Communicates with user who wants to change status of one book. Firstly it calls for method 'search_by_id' to get
    required object and if so, change its status to the one which provided by app.
    :param lib: Library
    :return: None
    """
    try:
        id = int(input("Enter book ID: "))
    except ValueError:
        print("Incorrect ID input.ID must be a number.")
        print("")
        return

    found = lib.search_by_id(str(id))
    if found is None:
        print(f"Book with id: {id} was not found")
        print("")
        return
    book = Book(found["title"], found["author"], found["year"], int(id), found["status"])
    print("You want to change status for the following book:")
    print(book)
    print("Enter new status for the book from the listed below:")
    print("1 - 'Available'")
    print("2 - 'Сhecked out")
    choice = int(input("Enter required option: "))
    if choice == 1:
        new_status = "Available"
        lib.change_book_status(book, new_status)
        print(f"The status for book id: {id} was changed to '{new_status}'")
        print("")
    if choice == 2:
        new_status = "Сhecked out"
        lib.change_book_status(book, new_status)
        print(f"The status for book id: {id} was changed to '{new_status}'")
        print("")
    if choice != 1 and choice != 2:
        print("Incorrect input")
        print("")


def get_libraries() -> list:
    """
    Returns list of available libraries.
    :return: list
    """
    my_libraries = []
    for lib in os.listdir(path="."):
        if lib.endswith('.json'):
            my_libraries.append(lib[:-5])
    return my_libraries


def check_availability(my_libraries: list, lib_name: str) -> bool:
    """
    Returns whether requested library data file is available or not.
    :param my_libraries: list
    :param lib_name: str
    :return:
    """
    available = False
    for lib in my_libraries:
        if lib == lib_name:
            available = True
    return available


def main():
    app_name = "My Library"
    lib_name = ""
    print("***************************")
    print(f"Welcome to {app_name} App")
    print("***************************")
    print("Do you want to work with one of the current libraries?")
    print("Answer options:")
    print("1 - 'Yes'")
    print("2 - 'No. I want to create new library'")
    print(f"3 - 'Leave {app_name} App'")

    lib_decision = 0
    try:
        lib_decision = int(input("Enter your answer: "))
    except ValueError:
        print("You can enter only digits corresponding to the options above")

    if lib_decision == 1:
        my_libraries = get_libraries()
        if not my_libraries:
            print("There are no available libraries at the moment")
            print("Create new?")
            print("Choose Operation Reference Number from the listed below:")
            print(f"1 - 'No, leave {app_name} App'")
            print("2 - 'Yes'")
            new_lib = check_input(1)
            if new_lib == 1:
                print(f"'{app_name} App was closed'")
                return
            lib_decision = 2
        else:
            print("Available Libraries")
            lib_counter = 1
            for lib in my_libraries:
                print(f"{lib_counter}. {lib}")
                lib_counter += 1
            lib_name = input("Enter the library name from the listed above: ").strip()
            available = check_availability(my_libraries, lib_name)
            if not available:
                print(f"There is no '{lib_name}' library in available libraries list")
                lib_decision = 3

    if lib_decision == 2:
        while True:
            lib_name = input("Enter new library_name: ").strip()
            if lib_name:
                break
            print("Entered value can not be empty")

    if lib_decision == 3:
        print(f"'{app_name} App was closed'")
        return

    if lib_decision != 1 and lib_decision != 2:
        print("Incorrect input")
        print(f"'{app_name} App was closed'")
        return

    lib = Library(lib_name)
    print(f"Start working with library '{lib_name}'")

    current_choice = 0
    while current_choice in range(0, 6):
        print("**** Library manager ****")
        print("Choose Operation Reference Number from the listed below:")
        print("1 - 'Add book'")
        print("2 - 'Delete book'")
        print("3 - 'Get all books'")
        print("4 - 'Search book'")
        print("5 - 'Change status'")
        print("6 - 'Leave My Library App'")

        current_choice = check_input(0)

        if current_choice == 1:
            add(lib)
        elif current_choice == 2:
            delete(lib)
        elif current_choice == 3:
            books_list(lib)
        elif current_choice == 4:
            search(lib)
        elif current_choice == 5:
            change_status(lib)
    if current_choice == 6:
        print(f"'{app_name} App was closed'")
        return
    else:
        print("Incorrect input. It must be digit from 1 to 6.")
        print(f"'{app_name} App was closed'")
        return


if __name__ == "__main__":
    main()
