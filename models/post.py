from extensions import db


class Post(db.Model):
    """
    A class that stores the short posts, but without a title - the only important aspect is the content used for analysis.
    """

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    upvotes = db.Column(db.Integer)
    time_created = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, content, author_id):
        self.content = content
        self.author_id = author_id
        self.upvotes = 0

    def update_content(self, content):
        self.content = content

    def add_upvote(self):
        self.upvotes += 1

    def downvote(self):
        self.upvotes -= 1

    def add_comment(self, comment):
        self.comments.append(comment)
