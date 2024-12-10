from flask import Flask, jsonify, request
import logging
from models import Book, BookType, Loan, User, db
from flask_cors import CORS


#basic config for logging
logging.basicConfig(
    level=logging.DEBUG, #logging level
    format='%(asctime)s - %(levelname)s - %(message)s', #log format
    handlers= [
        logging.StreamHandler(), #output logs to console
        logging.FileHandler('app.log') #also save logs to a file
        ]
)
#usage
logging.debug('debug message')
logging.info('info message')
logging.warning('warning message')
logging.error('error message')
logging.critical('critical message')

# Initialize Flask app and configure it
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests


# Set up configuration for your app (e.g., database URI)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for performance

db.init_app(app)  # Properly initialize SQLAlchemy with the app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# -----------------------------test route--------------------------#

# Example route to test the setup
@app.route('/test')
def index():
    return "TESTING!"


# -----------------------------BOOK--------------------------#

# add book
@app.route('/books', methods=['POST'])
def add_book():
    #  """
    # Adds a new book to the database.
    # Expects 'title' and 'author' in JSON request body.
    # """

    data = request.get_json()
# Input validation
    title = data.get('title')
    author = data.get('author')

    if not title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    # Create and add book
    new_book = Book(title=title, author=author)
    try:
        db.session.add(new_book)
        db.session.commit()
        return jsonify({
            "message": "Book added successfully!",
            "book": new_book.to_dict()  # Assuming you have a to_dict method in your Book model
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
# Get all books route
@app.route('/books', methods=['GET'])
def get_books():
    """
    Get a list of all books in the database.
    """
    books = Book.query.all()
    logging.debug(f"Fetched books: {[book.to_dict() for book in books]}")
    # If no books found
    if not books:
        return jsonify({"message": "No books found"}), 404

    # Convert books to a list of dictionaries using the to_dict method
    books_list = [book.to_dict() for book in books]

    return jsonify({
        "books": books_list
    }), 200    
# Update book route
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    # """
    # Update an existing book's details using its ID.
    # """
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    # Parse data from request
    data = request.get_json()
    title = data.get('title', book.title)  # Default to current title if not provided
    author = data.get('author', book.author)  # Default to current author if not provided
    available = data.get('available', book.available)  # Default to current availability

    # Update book details
    book.title = title
    book.author = author
    book.available = available

    # Commit changes
    db.session.commit()

    return jsonify({
        "message": "Book updated successfully",
        "book": {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "available": book.available
        }
    }), 200


# Delete book route
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Delete a book from the database using its ID.
    """
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    # Delete book
    db.session.delete(book)
    db.session.commit()

    return jsonify({"message": f"Book '{book.title}' has been deleted"}), 200

# -----------------------------USERS--------------------------#

# CRUD Routes for Users
@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    logging.debug(f"Fetched users: {[user.to_dict() for user in users]}")
    return jsonify([user.to_dict() for user in users]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.active = data.get('active', user.active)

    db.session.commit()
    return jsonify(user.to_dict()), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

# -----------------------------BORROW--------------------------#

@app.route('/borrow', methods=['POST'])
def borrow_book():
    with app.app_context():
        data = request.get_json()
        user_id = data.get('user_id')
        book_id = data.get('book_id')
        loan_type = data.get('loan_type')

        # Validate inputs
        user = User.query.get(user_id)
        book = Book.query.get(book_id)
        
        if not user or not book:
            return jsonify({"error": "User or book not found"}), 404

        # Check book availability
        if not book.available:
            return jsonify({"error": "Book is not available"}), 400

        # Create loan and update book status
        loan = Loan(user=user, book=book, duration=BookType(int(loan_type)))
        book.available = False  # Mark book as unavailable

        db.session.add(loan)
        db.session.commit()

        return jsonify({
            "message": f"Book '{book.title}' borrowed by {user.username}",
            "return_date": loan.return_date.strftime("%Y-%m-%d")
        }), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)
