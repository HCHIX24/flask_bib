from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from enum import Enum

# Flask setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Enum for loan durations
class BookType(Enum):
    SHORT = 1  #  1-2 days
    MEDIUM = 2  #  3-5 days
    LONG = 3    #  6-10 days

# User Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)  # Indicates if a user is active

# Relationship with Loan
    loans = db.relationship('Loan', back_populates='user', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "active": self.active
        }

# Book Model
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Boolean, default=True)  # Indicates if a book is available for borrowing
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "available": self.available
        }
# Relationship with Loan
    loans = db.relationship('Loan', back_populates='book', lazy=True)

    def __repr__(self):
        return f"<Book {self.title}>"

# Loan Model (Borrowing system)
class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    borrowed_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Enum(BookType), nullable=False)  # Borrow duration

    user = db.relationship('User', back_populates='loans')
    book = db.relationship('Book', back_populates='loans')

    def __init__(self, user, book, duration: BookType, borrowed_date=None):
# Ensure borrowed_date defaults to current time if not provided
        if borrowed_date is None:
            borrowed_date = datetime.utcnow()
        self.user = user
        self.book = book
        self.duration = duration
        self.borrowed_date = borrowed_date
        self.return_date = self.borrowed_date + timedelta(days=duration.value)  # Calculate return date based on duration
    def to_dict(self):
        return {
        "id": self.id,
        "user_id": self.user_id,
        "book_id": self.book_id,
        "borrowed_date": self.borrowed_date,
        "return_date": self.return_date,
        "duration": self.duration.name,  # You can use `.name` to get the enum name
    }
    def __repr__(self):
        return f"<Loan {self.user.username} borrowed {self.book.title}>"
# Initialize the database
with app.app_context():
    db.create_all()
