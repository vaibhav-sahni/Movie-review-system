import sys
import requests
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QListWidget, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
import webbrowser

TMDB_API_KEY = "INSERT TMDB API KEY HERE"

def search_movies(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url).json()
    return response.get('results', [])

def get_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    response = requests.get(url).json()
    for video in response.get('results', []):
        if video['type'] == 'Trailer':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return "Trailer not available."


def initialize_database():
    conn = sqlite3.connect('movie_recommendation.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Ratings (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        movie_id INTEGER,
                        rating REAL)''')
    conn.commit()
    conn.close()

def add_rating(user_id, movie_id, rating):
    conn = sqlite3.connect('movie_recommendation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Ratings (user_id, movie_id, rating) VALUES (?, ?, ?)", 
                   (user_id, movie_id, rating))
    conn.commit()
    conn.close()

def get_movie_rating(movie_id):
    conn = sqlite3.connect('movie_recommendation.db')
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(rating) FROM Ratings WHERE movie_id = ?", (movie_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] is not None else 0


class MovieApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie Recommendation System")
        self.setGeometry(200, 200, 800, 600)

        # Layouts
        main_layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        movie_list_layout = QVBoxLayout()
        action_buttons_layout = QVBoxLayout()
        rate_layout = QVBoxLayout()
        recommend_layout = QVBoxLayout()

        # Search Section
        self.search_label = QLabel("Search Movie:")
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_movies)
        self.movie_list = QListWidget()

        # Trailer Section
        self.watch_trailer_button = QPushButton("Watch Trailer")
        self.watch_trailer_button.clicked.connect(self.watch_trailer)

        # View Ratings Section
        self.view_rating_button = QPushButton("View Ratings")
        self.view_rating_button.clicked.connect(self.view_ratings)
        self.rating_label = QLabel("Average Rating: Not Available")

        # Rate Section
        self.user_id_label = QLabel("User ID:")
        self.user_id_input = QLineEdit()
        self.rating_label_2 = QLabel("Rating (0-5):")
        self.rating_input = QLineEdit()
        self.rate_button = QPushButton("Rate Movie")
        self.rate_button.clicked.connect(self.rate_movie)

        # Layout Organization
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        movie_list_layout.addWidget(self.movie_list)
        movie_list_layout.addWidget(self.watch_trailer_button)
        movie_list_layout.addWidget(self.view_rating_button)
        movie_list_layout.addWidget(self.rating_label)

        rate_layout.addWidget(self.user_id_label)
        rate_layout.addWidget(self.user_id_input)
        rate_layout.addWidget(self.rating_label_2)
        rate_layout.addWidget(self.rating_input)
        rate_layout.addWidget(self.rate_button)

        main_layout.addLayout(search_layout)
        main_layout.addLayout(movie_list_layout)
        main_layout.addLayout(rate_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # Functions
    def search_movies(self):
        query = self.search_input.text()
        results = search_movies(query)
        self.movie_list.clear()
        for movie in results:
            self.movie_list.addItem(f"{movie['id']} - {movie['title']}")

    def watch_trailer(self):
        selected = self.movie_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select a movie!")
            return
        movie_id = int(selected.text().split(" - ")[0])
        trailer_url = get_trailer(movie_id)
        if trailer_url != "Trailer not available.":
            webbrowser.open(trailer_url)
        else:
            QMessageBox.information(self, "Info", "Trailer not available.")

    def view_ratings(self):
        selected = self.movie_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select a movie!")
            return
        movie_id = int(selected.text().split(" - ")[0])
        avg_rating = get_movie_rating(movie_id)
        self.rating_label.setText(f"Average Rating: {avg_rating:.2f}")

    def rate_movie(self):
        try:
            user_id = int(self.user_id_input.text())
            rating = float(self.rating_input.text())
            selected = self.movie_list.currentItem()
            if not selected:
                QMessageBox.warning(self, "Error", "Please select a movie!")
                return
            movie_id = int(selected.text().split(" - ")[0])
            add_rating(user_id, movie_id, rating)
            QMessageBox.information(self, "Success", "Rating saved!")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input! Please check your entries.")




if __name__ == "__main__":
    initialize_database()
    app = QApplication(sys.argv)
    window = MovieApp()
    window.show()
    sys.exit(app.exec_())