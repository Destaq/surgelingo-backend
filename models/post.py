from extensions import db
from sqlalchemy.dialects.postgresql import ARRAY
import shortuuid
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
import string
from flask_sqlalchemy import BaseQuery


all_punc = string.punctuation
all_punc += "€¿¡"  # more languages


def stem_sentence(sentence, stemmer):
    words = word_tokenize(sentence)
    stemmed_words = [stemmer.stem(word) for word in words if word not in all_punc]
    return " ".join(stemmed_words)


# language stemmers - more languages on the way
english_stemmer = SnowballStemmer("english")
french_stemmer = SnowballStemmer("french")
german_stemmer = SnowballStemmer("german")
spanish_stemmer = SnowballStemmer("spanish")


stemmer_map = {
    "en": english_stemmer,
    "fr": french_stemmer,
    "de": german_stemmer,
    "es": spanish_stemmer,
}


class Post(db.Model):
    """
    A class that stores the short posts, but without a title - the only important aspect is the content used for analysis.
    """

    __tablename__ = "posts"
    # query_class = CustomOrderQuery

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    stemmed_content = db.Column(db.String(250))
    tags = db.Column(ARRAY(db.String(20)))
    language_code = db.Column(db.String(20))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    upvotes = db.Column(db.Integer)
    time_created = db.Column(db.DateTime, server_default=db.func.now())
    route_link = db.Column(db.String(12), unique=True)

    def __init__(self, content, author_id, tags, language_code):
        self.content = content
        self.author_id = author_id
        self.upvotes = 0
        self.tags = tags
        self.language_code = language_code
        self.route_link = shortuuid.uuid()[:12]
        self.stemmed_content = stem_sentence(
            self.content, stemmer_map[self.language_code]
        )

    def upvote(self):
        self.upvotes += 1
        db.session.commit()

    def downvote(self):
        self.upvotes -= 1

        # if reached critical mass of -5 downvotes, delete post
        if self.upvotes <= -5:
            db.session.delete(self)

        db.session.commit()

    def add_comment(self, comment):
        self.comments.append(comment)
