from extensions import db
from sqlalchemy.dialects.postgresql import ARRAY
import shortuuid


class Post(db.Model):
    """
    A class that stores the short posts, but without a title - the only important aspect is the content used for analysis.
    """

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
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

    def update_content(self, content):
        self.content = content

    def update_tags(self, tags):
        self.tags = tags

    def update_language(self, language):
        self.language = language

    def add_upvote(self):
        self.upvotes += 1

    def downvote(self):
        self.upvotes -= 1

    def add_comment(self, comment):
        self.comments.append(comment)
