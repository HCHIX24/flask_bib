frontend on http://127.0.0.1:5500/
backend on http://127.0.0.1:5000

unitest
--clr existing models/tables
--function to load data from json file
--function to update books table
--function to update the customers table 
--function to update the loans table
--main function to update all tables

rest api
--init db

ADD
--add books
--add customer
--add loan
 
READ/SHOW
--show all books
--show all customers
--show all loans

UPDATE
--update book by id
--fetch book by id-------
--get json data
--validate the update type field first----
--update other fields if provided
--commit changes to db

--update customer by id
--fetch customer by id
--update other fields if provided

--update loan dates by id
--retrieve data
--update loan date if provided

DELETE
--find book by id
--delete all loans associated with book
--delete the book
--"rollback" transaction if an error occurs
--find customer by id
--delete all loans associated with customer
--delete the customer
--rollback if error
--find loan by id
--rollback if error

HELPERS
--validation of customer/books by id /loandate >=returndate

