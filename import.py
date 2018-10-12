import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, published_date in reader:
        db.execute("INSERT INTO books(isbn, title, author, published_date) VALUES(:isbn, :title, :author, :published_date)",
                    {"isbn": isbn, "title": title, "author": author, "published_date": published_date})
    db.commit()

if __name__ == "__main__":
    main()