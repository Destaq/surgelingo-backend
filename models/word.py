from extensions import db


class Word(db.Model):
    """
    Word model
    """
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(32), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, word, author_id):
        self.word = word
        self.author_id = author_id
