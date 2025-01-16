document.addEventListener("DOMContentLoaded", () => {
    // <-------- GLOBAL VARIABLES AND INITIALIZATION -------------------------->
    const userDropdown = document.getElementById("userDropdown");
    const bookDropdown = document.getElementById("bookDropdown");
    const loanTypeDropdown = document.getElementById("loanTypeDropdown");
    const submitBorrow = document.getElementById("submitBorrow");
    const returnBookButton = document.getElementById("returnBook");
    const statusMessage = document.getElementById("statusMessage");

    let usersFetched = false;
    let booksFetched = false;
    let actionInProgress = false;
    let borrowedBooks = {}; // Store borrowed books by the selected user


    // <-------- FORM EVENT HANDLING ------------------------------------------>
    document.querySelector("form").addEventListener("submit", (event) => event.preventDefault());

    // <-------- FETCH USERS -------------------------------------------------->
    function fetchUsers() {
        if (usersFetched || actionInProgress) return;
        actionInProgress = true;
        axios.get("http://127.0.0.1:5000/users")
            .then(response => {
                populateUserDropdown(response.data);
                usersFetched = true;
            })
            .catch(() => displayStatus("Failed to load users.", true))
            .finally(() => actionInProgress = false);
    }

    // <-------- POPULATE USER DROPDOWN ---------------------------------------> 
    function populateUserDropdown(users) {
        userDropdown.innerHTML = '<option value="">--Select a User--</option>';
        users.forEach(user => {
            const option = document.createElement("option");
            option.value = user.id;
            option.textContent = `${user.username} (${user.email})`;
            userDropdown.appendChild(option);
        });
        userDropdown.disabled = !users.length;
    }

    // <-------- FETCH BOOKS -------------------------------------------------->
    function fetchBooks() {
        if (booksFetched || actionInProgress) return;
        actionInProgress = true;
        axios.get("http://127.0.0.1:5000/books")
            .then(response => {
                populateBookDropdown(response.data.books);
                booksFetched = true;
            })
            .catch(error => {
                console.error("Error fetching books:", error);
                displayStatus("Failed to load books.", true);
            })
            .finally(() => actionInProgress = false);
    }

    // <-------- POPULATE BOOK DROPDOWN ------------------------------------->
    function populateBookDropdown(books) {
        bookDropdown.innerHTML = '<option value="">--Choose a Book--</option>';
        books.forEach(book => {
            const option = document.createElement("option");
            option.value = book.id;
            // Display borrowed status but keep the option clickable
            option.textContent = `${book.title} (${book.available ? "Available" : "Unavailable"})`;

            // Add "(Borrowed)" label for unavailable books but keep them selectable
            if (!book.available) {
                option.textContent += " (Borrowed)";
                option.style.fontStyle = "italic"; // Optional: Add italic style for borrowed books
            }

            bookDropdown.appendChild(option);
        });
        bookDropdown.disabled = false;
    }
    // <-------- DISPLAY STATUS MESSAGES -------------------------------------> 
    function displayStatus(message, isError = false) {
        statusMessage.textContent = message;
        statusMessage.style.color = isError ? "red" : "green";
        setTimeout(() => statusMessage.textContent = "", 50000);
    }

    // <-------- BORROW BOOK FUNCTION ----------------------------------------> 
    function borrowBook(userId, bookId, loanType) {
        axios.post("http://127.0.0.1:5000/borrow", { user_id: userId, book_id: bookId, loan_type: loanType })
            .then(response => {
                displayStatus("Book borrowed successfully!");
                console.log("Response from borrow:", response);  // Log the response for debugging
                // If needed, you can access specific data from the response
                const borrowedBookDetails = response.data; // Assuming response contains book details
                console.log("Borrowed book details:", borrowedBookDetails);
    
                // Save the borrowed book for the user
                borrowedBooks[userId] = borrowedBooks[userId] || []; // Ensure user has an entry
                borrowedBooks[userId].push(bookId);
            })
            .catch(error => {
                console.error("Error borrowing book:", error);
                displayStatus("Failed to borrow book.", true);
            });
    }
// <-------- RETURN BOOK FUNCTION ----------------------------------------> 
function handleReturnBook(userId, bookId) {
    axios.delete("http://127.0.0.1:5000/return", { data: { user_id: userId, book_id: bookId } })
        .then(() => {
            displayStatus("Book returned successfully!");
            // Remove the returned book from the borrowed list
            borrowedBooks[userId] = borrowedBooks[userId].filter(borrowedBookId => borrowedBookId !== bookId);
            // Optionally, re-enable the book for borrowing again
            fetchBooks(); // Refresh the books list after return
        })
        .catch(() => displayStatus("Failed to return book.", true));
}

    // <-------- CHECK SELECTIONS FUNCTION ----------------------------------------> 
    function checkSelections() {
        if (!userDropdown.value || !bookDropdown.value || !loanTypeDropdown.value) {
            submitBorrow.disabled = true;  // Disable submit button if any field is empty
        } else {
            submitBorrow.disabled = false; // Enable submit button if all fields are filled
        }

        // Enable the "Return" button only if the selected book is borrowed by the selected user
        const selectedBookId = bookDropdown.value;
        const selectedUserId = userDropdown.value;

        if (selectedBookId && selectedUserId && borrowedBooks[selectedUserId] && borrowedBooks[selectedUserId].includes(selectedBookId)) {
            returnBookButton.disabled = true; // Enable "Return" button if the conditions are met
        } else {
            returnBookButton.disabled = false; // Disable "Return" button if the conditions are not met
        }
    }
   // <-------- EVENT LISTENERS ---------------------------------------------> 
userDropdown.addEventListener("focus", fetchUsers);
userDropdown.addEventListener("change", () => { fetchBooks(); checkSelections(); });
bookDropdown.addEventListener("change", checkSelections);
loanTypeDropdown.addEventListener("change", checkSelections);

   // Prevent form reset and avoid page reload on submit
submitBorrow.addEventListener("click", (event) => {
          event.preventDefault(); // Prevent page refresh
borrowBook(userDropdown.value, bookDropdown.value, loanTypeDropdown.value);
});

returnBookButton.addEventListener("click", () => {
const userId = userDropdown.value;
const bookId = bookDropdown.value;

       // Ensure the return button only works when a valid user and borrowed book are selected
if (userId && bookId) {
handleReturnBook(userId, bookId);
}
});
});