from flask import Flask
from extensions import db, jwt
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_cors import CORS
import os
from models.user import *

# import blueprints
from blueprints.auth import auth_bp

# other imports for flask-migrate
from models.post import Post


load_dotenv()

migrate = Migrate(compare_type=True)
cors = CORS()


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ.get("APP_SETTINGS"))
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/*": {"origins": r"http://localhost:3000/*"}},
        supports_credentials=True,
    )  # TODO: not localhost but custom domain host

    # auto-loads JWT from user_object (to create access tokens from user itself, not from username)
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    # auto-loads user object from JWT
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()
        

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    return app
