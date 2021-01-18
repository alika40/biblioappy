# PROJECT 1

## Web Programming with Python and JavaScript


## IMPLEMENTATION
This project was implemented using Flask Micro Framework. Flask and its dependencies(psycopg2, SQLAlchemy, jinja2, Werkzeug, etc.) were installed,
and some packages such as Flask-Login, Flask-WTF, Flask-Mail, PyJWT, and Requests were installed as well, but only the latter --Requests-- was implemented
in the project. PostgreSQL was used for database and the database lives online on Heroku. Adminer was used to manage the interface instead of installing
PostgreSQL and managing it locally.

The project has the following files:
1.) application.py. This file contains the application, its configurations and view functions.
2.) import.py. This file contains codes for converting CSV file to raedable format and importing it into a database that lives online.
3.) Templates Folder. This folder contains HTML files such as index.html, home.html, login.html, registration.html, dashboard.html, results.html, bookDetails.html, reviews.html, editReview.html.
4.) Static Folder. This folder contains a CSS file(styles.css) and an image folder containing some images.
5.) requirements.txt. This file contains all the packages required and installed for the project.

## ABOUT PROJECT
This project is a book review application where users can register and login to search for their favourity books, review and rate them, and can also view reviews written
by others on those books. Visit https://biblioappy.herokuapp.com to try it out. 

## FEATURES:
1.) Users can register, login, and logout.
2.) Users can search for a book by its author, title, isbn by typing in full or partial part of the word(or number) being searched for. And by clicking on the result(s),
users can view book details as well the reviews and ratings given by others plus the book details from #GOODREADS (www.goodreads.com) pulled using an API.
3.) Users can write a review on, and rate, a book. And Users are only allowed to do that once.
4.) Users can edit, ONLY, their own review and rating previuosly given on any given book. 
