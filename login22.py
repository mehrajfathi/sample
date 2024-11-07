import sqlite3
import os

class Quiz:
    
    def __init__(self, username, is_admin):
        self.username = username  # Stores the user's name
        self.is_admin = is_admin  # Stores if the user is an admin
        self.categories = self.load_categories()  # Loads quiz categories

    def load_categories(self):
        # List all question files ending in '_questions.txt'
        files = [f for f in os.listdir() if f.endswith('_questions.txt')]
        return files

    def load_questions(self, questions_file):
        questions = []  # List to hold questions
        with open(questions_file, 'r') as file:
            while True:
                line = file.readline().strip()
                if not line:  # End of file
                    break

                question = line  # First line is the question
                options = [file.readline().strip() for _ in range(4)]  # Next 4 lines are options
                answer = file.readline().strip()  # Last line is the correct answer
                questions.append((question, options, answer))  # Add to questions list

        return questions

    def start_quiz(self):
        print("Welcome to the Quiz!")

        while True:
            # Display category options
            print("\nSelect a category to quiz:")
            for idx, category_file in enumerate(self.categories, start=1):
                print(f"{idx}. {category_file.replace('_questions.txt', '')}")

            try:
                # User selects a category
                category_choice = int(input("Select a category (number): ")) - 1
                if 0 <= category_choice < len(self.categories):
                    category_file = self.categories[category_choice]
                    questions = self.load_questions(category_file)

                    score = 0  # Initialize score
                    total_questions = len(questions)

                    # Quiz loop
                    for question, options, answer in questions:
                        print("\n" + question)
                        for i, option in enumerate(options):
                            print(f"{chr(65 + i)}) {option}")  # A, B, C, D

                        user_answer = input("Your answer (A, B, C, D): ").strip().upper()
                        if user_answer == answer:
                            print("Correct!")
                            score += 1
                        else:
                            print(f"Wrong! The correct answer was {answer}.")

                    # Show total score after quiz
                    print(f"\nYour total score in {category_file.replace('_questions.txt', '')} is {score}/{total_questions}.")
                    self.save_result(score, category_file.replace('_questions.txt', ''))  # Save result
                else:
                    print("Invalid category choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

            continue_quiz = input("Do you want to continue playing? (yes/no): ").strip().lower()
            if continue_quiz != 'yes':
                break

        print("Thank you for playing!")

    def save_result(self, score, category):
        # Save quiz result to database
        conn = sqlite3.connect('quiz_results.db')
        c = conn.cursor()
        c.execute("INSERT INTO results (name, category, score) VALUES (?, ?, ?)", (self.username, category, score))
        conn.commit()
        conn.close()

    def show_leaderboard(self):
        # Show leaderboard if user is admin
        if self.is_admin:
            conn = sqlite3.connect('quiz_results.db')
            c = conn.cursor()
            c.execute("SELECT * FROM results ORDER BY score DESC")
            results = c.fetchall()

            if results:
                print("\nLeaderboard:")
                for row in results:
                    print(f"ID: {row[0]}, Name: {row[1]}, Category: {row[2]}, Score: {row[3]}")
            else:
                print("\nNo results yet.")

            conn.close()
        else:
            print("Access denied. Only admins can view the leaderboard.")

    def show_registered_users(self):
        # Show registered users if user is admin
        if self.is_admin:
            conn = sqlite3.connect('quiz_results.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users")
            users = c.fetchall()

            if users:
                print("\nRegistered Users:")
                for user in users:
                    print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[3]}")
            else:
                print("\nNo registered users.")

            conn.close()
        else:
            print("Access denied. Only admins can view registered users.")

def reset_users():
    # Reset users and add default admin
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT)''')
    c.execute('''INSERT OR IGNORE INTO users (username, password, role) 
                 VALUES ('admin', 'adminpass', 'admin')''')
    conn.commit()
    conn.close()
    print("All users have been removed. Default admin restored.")

def create_database():
    # Create database tables for results and users
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    category TEXT,
                    score INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT)''')
    c.execute('''INSERT OR IGNORE INTO users (username, password, role) 
                 VALUES ('admin', 'adminpass', 'admin')''')
    conn.commit()
    conn.close()

def login():
    # Login process for users
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    print("Please log in:")
    username = input("Username: ")
    password = input("Password: ")
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    if user:
        print(f"Welcome, {username}!")
        conn.close()
        return user[1], user[3] == 'admin'
    else:
        print("Invalid login credentials. Please try again.")
        conn.close()
        return None, None

def register():
    # Register new users
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    print("Register a new user:")
    username = input("Choose a username: ")
    password = input("Choose a password: ")
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, 'user'))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists. Try a different one.")
    conn.close()

def admin_menu(quiz):
    while True:
        print("\nAdmin Menu:")
        print("1. Show Leaderboard")
        print("2. Show Registered Users")
        print("3. Reset All Users")
        print("4. Log Out")
        choice = input("Choose an option (1, 2, 3, or 4): ")
        if choice == '1':
            quiz.show_leaderboard()
        elif choice == '2':
            quiz.show_registered_users()
        elif choice == '3':
            confirm = input("Are you sure you want to reset all users? (yes/no): ").strip().lower()
            if confirm == 'yes':
                reset_users()
            else:
                print("Reset canceled.")
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please select again.")

def main():
    create_database()
    while True:
        print("\nMain Menu:")
        print("1. Log In")
        print("2. Register")
        print("3. Exit")
        choice = input("Choose an option (1, 2, or 3): ")
        if choice == '1':
            username, is_admin = login()
            if username:
                quiz = Quiz(username, is_admin)
                if is_admin:
                    admin_menu(quiz)
                else:
                    while True:
                        print("\nQuiz Menu:")
                        print("1. Play Quiz")
                        print("2. Log Out")
                        quiz_choice = input("Choose an option (1, 2): ")
                        if quiz_choice == '1':
                            quiz.start_quiz()
                        elif quiz_choice == '2':
                            print("Logging out...")
                            break
                        else:
                            print("Invalid choice. Please select again.")
        elif choice == '2':
            register()
        elif choice == '3':
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid choice. Please select again.")

if __name__ == "__main__":
    main()
