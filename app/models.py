from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100))
    birth_year = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "country": self.country,
            "birth_year": self.birth_year,
        }


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    year = db.Column(db.Integer)
    copies = db.Column(db.Integer, nullable=False, default=1)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))

    author = db.relationship("Author", backref=db.backref("books", cascade="all, delete-orphan"))
    genre = db.relationship("Genre", backref="books")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "copies": self.copies,
            "author_id": self.author_id,
            "genre_id": self.genre_id,
        }


class Reader(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    phone = db.Column(db.String(50))

    def to_dict(self):
        return {"id": self.id, "full_name": self.full_name, "email": self.email, "phone": self.phone}


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    reader_id = db.Column(db.Integer, db.ForeignKey("reader.id"), nullable=False)
    issued_at = db.Column(db.Date, nullable=False, default=date.today)
    due_at = db.Column(db.Date)
    returned = db.Column(db.Boolean, nullable=False, default=False)

    book = db.relationship("Book", backref=db.backref("loans", cascade="all, delete-orphan"))
    reader = db.relationship("Reader", backref=db.backref("loans", cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "reader_id": self.reader_id,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "returned": self.returned,
        }
