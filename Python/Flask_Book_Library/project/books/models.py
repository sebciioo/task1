import re
from sqlalchemy.orm import validates
from project import db, app

# Dozwolone typy książki
ALLOWED_BOOK_TYPES = ('2days', '5days', '10days')

# Zabronione znaki
FORBIDDEN_CHARS = ('<', '>', '"', "'", ';', '{', '}')

class ValidationError(ValueError):
    """Zgłaszany, gdy dane wejściowe nie spełniają reguł."""
    pass

# Book model
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    author = db.Column(db.String(64))
    year_published = db.Column(db.Integer) 
    book_type = db.Column(db.String(20))
    status = db.Column(db.String(20), default='available')

    def __init__(self, name, author, year_published, book_type, status='available'):
        self.name = name
        self.author = author
        self.year_published = year_published
        self.book_type = book_type
        self.status = status

    # Walidacja
    def _validate_text(self, value, field_name, max_len=64):
        if not isinstance(value, str):
            raise ValidationError(f"Pole '{field_name}' musi być tekstem")
        cleaned = value.strip()
        if not (1 <= len(cleaned) <= max_len):
            raise ValidationError(
                f"Pole '{field_name}' musi mieć od 1 do {max_len} znaków")
        if re.search(r'[\x00-\x1f\x7f]', cleaned):
            raise ValidationError(
                f"Pole '{field_name}' zawiera niedozwolone znaki sterujące")
        for ch in FORBIDDEN_CHARS:
            if ch in cleaned:
                raise ValidationError(
                    f"Pole '{field_name}' zawiera niedozwolony znak: {ch}")
        return cleaned
    
    @validates('name')
    def _validate_name(self, key, value):
        return self._validate_text(value, 'name')

    @validates('author')
    def _validate_author(self, key, value):
        return self._validate_text(value, 'author')

    @validates('year_published')
    def _validate_year(self, key, value):
        try:
            year = int(value)
        except (TypeError, ValueError):
            raise ValidationError("Pole 'year_published' musi być liczbą")
        if not (1450 <= year <= 2100):
            raise ValidationError("Pole 'year_published' musi być z zakresu 1450-2100")
        return year

    @validates('book_type')
    def _validate_book_type(self, key, value):
        if value not in ALLOWED_BOOK_TYPES:
            raise ValidationError(
                f"Pole 'book_type' musi być jedną z: {', '.join(ALLOWED_BOOK_TYPES)}")
        return value


    def __repr__(self):
        return f"Book(ID: {self.id}, Name: {self.name}, Author: {self.author}, Year Published: {self.year_published}, Type: {self.book_type}, Status: {self.status})"


with app.app_context():
    db.create_all()