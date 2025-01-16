from flask import Flask, jsonify, request
import logging
from models import Book, BookType, Loan, User, db
from flask_cors import CORS
from flask_migrate import Migrate
# Initialize Flask app and configure it
app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"], methods=["GET", "POST", "PUT", "DELETE"])

# Set up logging
logger = logging.getLogger(__name__)

# Basic config for logging
logging.basicConfig(
    level=logging.DEBUG, # Logging level
    format='%(asctime)s - %(levelname)s - %(message)s', # Log format
    handlers= [
        logging.StreamHandler(), # Output logs to console
        logging.FileHandler('app.log') # Also save logs to a file
    ]
)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for performance

db.init_app(app)  # Properly initialize SQLAlchemy with the app
migrate = Migrate(app, db)
# -----------------------------TEST ROUTE--------------------------#
@app.route('/test')
def index():
    return "TESTING!"


# -----------------------------BOOK ROUTES--------------------------#

# Add a new book
@app.route('/books', methods=['POST'])
def add_book():
    """
    Adds a new book to the database.
    Expects 'title' and 'author' in JSON request body.
    """
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

# Get all books
@app.route('/books', methods=['GET'])
def get_books():
    """
    Retrieve all books from the database.
    """
    books = Book.query.all()
    logging.info("fetched books")
    if not books:
        return jsonify({"message": "No books found"}), 404
    return jsonify({"books": [book.to_dict() for book in books]}), 200

# Update book details
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """
    Update an existing book's details using its ID.
    """
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    # Parse data from request
    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.available = data.get('available', book.available)

    db.session.commit()
    return jsonify({
        "message": "Book updated successfully",
        "book": book.to_dict()
    }), 200

# Delete a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """
    Delete a book from the database.
    """
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": f"Book '{book.title}' has been deleted"}), 200


# -----------------------------USER ROUTES--------------------------#

# Add a new user
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

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    logging.info("fetched users")

    return jsonify([user.to_dict() for user in users]), 200

# -----------------------------BORROW BOOK ROUTES--------------------------#

@app.route('/borrow', methods=['POST'])
def borrow_book():
    """
    Borrow a book by providing user_id, book_id, and loan_type.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    book_id = data.get('book_id')
    loan_type = data.get('loan_type')

    if not user_id or not book_id or loan_type is None:
        return jsonify({"error": "User ID, Book ID, and loan type are required"}), 400

    user = db.session.get(User, user_id)
    book = db.session.get(Book, book_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    if not book:
        return jsonify({"error": "Book not found"}), 404
    if not book.available:
        return jsonify({"error": "Book is not available"}), 400

    try:
        loan_duration = BookType(int(loan_type))
    except ValueError:
        return jsonify({"error": "Invalid loan type"}), 400

    try:
        loan = Loan(user=user, book=book, duration=loan_duration)
        book.available = False

        db.session.add(loan)
        db.session.commit()

        return jsonify({
            "message": f"Book '{book.title}' borrowed by {user.username}",
            "return_date": loan.return_date.strftime("%Y-%m-%d"),
            "book_title": book.title,
            "user_name": user.username
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# -----------------------------RETURN BOOK ROUTES--------------------------#

@app.route('/return', methods=['POST', 'DELETE'])
def return_book():
    data = request.get_json()
    user_id = data.get('user_id')
    book_id = data.get('book_id')

    if not user_id or not book_id:
        return jsonify({'error': 'User ID and Book ID are required.'}), 400

    loan = Loan.query.filter_by(user_id=user_id, book_id=book_id, returned=False).first()

    if not loan:
        return jsonify({'error': 'No active loan found for this user and book.'}), 404

    # Mark the book as returned
    loan.returned = True
    book = Book.query.get(book_id)
    if book:
        book.available = True

    db.session.commit()

    return jsonify({'message': 'Book returned successfully!'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
