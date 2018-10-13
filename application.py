import os
import requests

from flask import Flask, session, flash, render_template, request, redirect, jsonify, abort, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse
#from datetime import datetime
#from flask_mail import Mail




app = Flask(__name__)
#mail = Mail(app)



# Check for environment variable             
SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

DATABASE_URL = os.environ.get("DATABASE_URL", default=None)
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))




@app.route('/')
@app.route('/home')
def index():
    """Lists all Books."""
    return render_template("index.html")



@app.route('/home/registration', methods=['GET', 'POST'])
def registration():
    username = request.form.get('username')
    email = request.form.get('email')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    error = None
    #Form Validation
    if request.method =='POST':
        #Check that passwords 1 & 2 match each other
        if password1 != password2:
            flash(u'The Passwords Do Not Match. Please Re-enter Password.', 'error')
            return render_template('registration.html', title='BIBLIAOPPY')
        #Check that a username has not been taken already. Note: column CONSTRAINT is set to UNIQUE for stricter validation
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone() is not None:
            flash(u'This Username "{}" Has Been Taken.' .format(username), 'error')
            return render_template('registration.html', title='BIBLIAOPPY')
        #Check that a Email has not been taken already. Note: column CONSTRAINT is set to UNIQUE for stricter validation
        if db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchone() is not None:
            flash(u'This email "{}" Is Not Available For Use.' .format(email), 'error')
            return render_template('registration.html', title='BIBLIAOPPY')
        #If the validates then, hash password and store it in the DB after thwarting/escaping to avoid SQL injection
        if error is None:
            hashed_password = generate_password_hash(password1)
            db.execute("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)", {"username": username, "password": hashed_password, "email": email})
            db.commit()
            flash(u'Congratulations {}! You are now a registered user.\nPlease Login.' .format(username), 'message')
            return redirect(url_for('login'))
    return render_template('registration.html', title='REGISTRATION')



@app.route('/home/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db_username = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        error = None      
        if db_username is None:
            flash(u'Invalid username', 'error')
            return render_template('login.html', title='LOG IN')
        if not check_password_hash(db_username['password'], password):
            flash(u'Invalid password', 'error')
            return render_template('login.html', title='LOG IN')        
        if error is None:
            session.clear()
            session['user'] = db_username['id']
            return redirect(url_for('dashboard'))
    return render_template('login.html', title='LOG IN')




@app.route('/logout')
def logout():
    session.clear()
    # return redirect(url_for('index'))
    return render_template('login.html', title='LOG IN')
    


@app.route('/dashboard/', methods=['GET', 'POST'])
def dashboard():
    """ LIST OUT BOOKS """
    if not session.get('user'):
        abort(401)
    user_id = session.get('user')
    if request.method=="POST":
        result = request.form.get('result')
        if result == "":
            flash(u'You haven\'t entered anything. Nothing to search for.', 'message')
            return render_template('dashboard.html', title='USER HOME PAGE')
        result += '%' #Concatenating wildcat(%) that goes with LIKE operator with the value from input before passing it.
        books = db.execute("SELECT * FROM books WHERE author ILIKE :results OR title ILIKE :results OR isbn ILIKE :results ORDER BY author ASC LIMIT 25",
                           {"results": result}).fetchall()
        if books is None:
            flash(u'No match for "{}".' .format(result), 'message')
            return render_template('dashboard.html', title='USER HOME PAGE')
        else:
            return render_template('results.html', title='RESULT PAGE', books=books)
    return render_template('dashboard.html', title='USER HOME PAGE')



 
@app.route("/dashboard/result/<int:book_id>")
def bookDetails(book_id):
    if not session.get('user'):
        abort(401)
    reviewer_id = session.get('user')
    db.execute("UPDATE reviews SET review_count = (SELECT SUM(counter) FROM reviews WHERE book_id = :bookID), average_rating = (SELECT AVG(rating) FROM reviews WHERE book_id = :bookID) WHERE book_id = :bookID", {"bookID": book_id})
    db.commit()
    oneBook = db.execute("SELECT books.id, isbn, title, author, books.published_date, review_count, average_rating FROM books JOIN reviews ON reviews.book_id = books.id WHERE books.id = :id", {"id": book_id}).fetchone()
    if oneBook is None:
        aBook = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        #Code For API Request From GOODREADS
        resq = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "4zYzvmninNJqkEWnsTsQ", "isbns": aBook['isbn']})
        data1 = resq.json()
        details1 = data1['books'][0]
        return render_template('bookDetails.html', apiReviews=details1,  book=aBook)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "4zYzvmninNJqkEWnsTsQ", "isbns": oneBook['isbn']})#ISBN ERROR
    data = res.json()
    details = data['books'][0]
    editableReview = db.execute("SELECT review_content, review_count, rating, average_rating, published_date, username FROM reviews JOIN users ON users.id = reviews.user_id WHERE reviews.book_id = :book_id AND users.id = :userID", {"book_id": book_id, "userID": reviewer_id}).fetchone()
    reviews = db.execute("SELECT review_content, review_count, rating, average_rating, published_date, user_id, username FROM reviews JOIN users ON users.id = reviews.user_id WHERE reviews.book_id = :book_id AND NOT users.id = :userID ORDER BY published_date DESC", {"book_id": book_id, "userID": reviewer_id}).fetchall()
    return render_template('bookDetails.html', book=oneBook, apiReviews=details, editReview=editableReview, reviews=reviews)




@app.route("/dashboard/<int:book_id>/review", methods=['GET', 'POST'])
def reviews(book_id):
    if not session.get('user'):
        abort(401)
    reviewer_id = session.get('user')
    review = request.form.get('review')
    rating = request.form.get('rating')
    aveRating = ""
    if review == "":
        flash(u'You cannot submit empty review', 'info')
        return render_template('reviews.html', title='REVIEW PAGE')
    getBook = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if request.method == 'POST':        
        #Check whether a user has previously given a review for the same book, if yes, deny access.
        getReviewer = db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :userID", {"book_id": book_id, "userID": reviewer_id}).fetchone()
        if getReviewer is None:
            db.execute("INSERT INTO reviews (review_content, average_rating, rating, book_id, user_id) VALUES (:review_content, :average_rating, :rating, :book_id, :user_id)",
                    {"review_content": review, "average_rating": rating, "rating": rating, "book_id":book_id, "user_id": reviewer_id})
            db.commit()
            return redirect(url_for('bookDetails', book_id=getBook.id))
    return render_template('reviews.html', book=getBook, title="REVIEW PAGE")



@app.route('/dashboard/reviews/<int:book_id>/editreview', methods=['GET', 'POST'])
def editreview(book_id):
    if not session.get('user'):
        abort(401)
    reviewer_id = session.get('user')
    editedReview = request.form.get('review')
    rating = request.form.get('rating')
    if editedReview == "":
        flash(u'You cannot submit empty review', 'info')
        return render_template('reviews.html', title='REVIEW PAGE')
    getReviewer = db.execute("SELECT books.id, title, author, review_content, rating FROM books JOIN reviews ON reviews.book_id = books.id WHERE books.id = :id AND user_id = :userID", {"id": book_id, "userID": reviewer_id}).fetchone()
    if request.method =='POST':
        db.execute("UPDATE reviews SET review_content = :review, rating = :rating WHERE book_id = :book_id AND user_id = :userID",
                   {"review": editedReview, "rating": rating, "book_id": book_id, "userID": reviewer_id})
        db.commit()
        return redirect(url_for('bookDetails', book_id=getReviewer.id))
    return render_template('editReview.html', editreview=getReviewer, title="EDIT REVIEW")



@app.route('/api/<isbn>/JSON', methods=['GET'])
def api_request(isbn):
    if request.method =='GET':
        get_book = db.execute("SELECT books.id, isbn, title, author, books.published_date, review_count, average_rating FROM books JOIN reviews ON reviews.book_id = books.id WHERE books.isbn = :isbn", {"isbn": isbn}).fetchone()
        if get_book is None:
            getBook = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
            if getBook is not None:
                return jsonify({
                   "title": getBook.title,
                   "author": getBook.author,
                   "year": getBook.published_date,
                   "isbn": getBook.isbn,
                   "review_count": 0,
                   "average_score": 0
                })
            if getBook is None:
                return jsonify({"ERROR": f"The book with isbn:{isbn} does not exist."}), 422
        serializedDecimal = float(get_book.average_rating)
        return jsonify({
            "title": get_book.title,
            "author": get_book.author,
            "year": get_book.published_date,
            "isbn": get_book.isbn,
            "review_count": get_book.review_count,
            "average_score": serializedDecimal
        })
    


##################################################################
"""    
@app.route('/<int:book_id>/review/delete')
def deleteReview(book_id):
    if not session.get('user'):
        abort(401)
    reviewer_id = session.get('user')
    db_username = db.execute("SELECT * FROM users WHERE users.id = :reviewer_id", {"reviewer_id": reviewer_id}).fetchone()
    if db_username is not None:
        db.execute("DELETE FROM  reviews USING books WHERE reviews.book_id = books.id AND reviews.user_id = :userID", {"userID": reviewer_id})
        db.commit
        getBook = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        return redirect(url_for('bookDetails', book_id=getBook.id))
   
    
    
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if session.get('user'):
        #abort(401)
        return render_template('login.html', title='LOG IN')
    
    email = request.form.get('email')
    if request.method =='POST':
        #user = User.query.filter_by(email=form.email.data).first()
        user = db.execute("SELECT email FROM users WHERE email = :userEmail", {"userEmail": email}).fetchone()
        if user is None:
            flash(u'This email does not exist.', 'info')
            return render_template('login.html', title='LOG IN')
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('resetPassword.html', title='Reset Password')
"""