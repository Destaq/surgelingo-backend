from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


upvoted_content_helper_table = db.Table(
    "upvoted_content_helper_table",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id")),
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    upvoted_posts = db.relationship(
        "Post",
        secondary="upvoted_content_helper_table",
        backref="upvoters",
        lazy="dynamic",
    )
    words = db.relationship("Word", backref="author", lazy="dynamic")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
