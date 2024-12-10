document.addEventListener("DOMContentLoaded", () => {
    const userDropdown = document.getElementById("userDropdown");
    const bookDropdown = document.getElementById("bookDropdown");

    // Function to fetch and populate users
    function fetchUsers() {
        axios.get("http://127.0.0.1:5000/users")
            .then(response => {
                const users = response.data;
                console.log("Fetched users:", users);  // Debugging log

                if (users.length === 0) {
                    console.log("No users found");
                    return;
                }

                // Populate the dropdown with users
                users.forEach(user => {
                    const option = document.createElement("option");
                    option.value = user.id;
                    option.textContent = `${user.username} (${user.email})`;
                    userDropdown.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Error fetching users:", error);
            });
    }

    // Function to fetch and populate books
    function fetchBooks() {
        axios.get("http://127.0.0.1:5000/books")
            .then(response => {
                console.log("Fetched books response:", response); // Log fetched books
                console.log("Fetched books data:", response.data); // Log only the data part

                // Check if response.data is an array before attempting to use forEach
                if (!Array.isArray(response.data.books)) {
                    console.error("Expected an array, but got:", response.data);
                    return; // Exit if the data is not an array
                }
                // Clear existing options
                bookDropdown.innerHTML = '<option value="">--Choose a Book--</option>';

                if (response.data.books.length === 0) {
                    console.log("No books found");
                    return;
                }

                // Populate the dropdown with books
                response.data.books.forEach(book => {
                    const option = document.createElement("option");
                    option.value = book.id;
                    option.textContent = book.title;

                    // Debugging to ensure book.available is correct
                    console.log(`Book: ${book.title}, Available: ${book.available}`);

                    // Add class based on availability
                    if (book.available) {
                        option.classList.add("available");
                    } else {
                        option.classList.add("unavailable");
                    }
                    bookDropdown.appendChild(option);
                });
            })
            .catch(error => console.error("Error fetching books:", error));
    }


    // Event listener for user selection
    userDropdown.addEventListener("change", (event) => {
        event.preventDefault(); // Prevent form submission or page reload

        const selectedUser = userDropdown.value;
        console.log("User selected:", selectedUser);  // Debugging log

        if (selectedUser) {
            // Enable the book dropdown and fetch books
            bookDropdown.disabled = false;
            fetchBooks();
        } else {
            // Disable book dropdown if no user is selected
            bookDropdown.disabled = true;
            bookDropdown.innerHTML = '<option value="">--Choose a Book--</option>';
        }
    });

    // Initial calls
    fetchUsers(); // Populate users on page load
});
