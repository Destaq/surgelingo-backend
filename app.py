from flask import Flask
from extensions import db, jwt
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_cors import CORS
import os
from models.user import *
from datetime import timedelta, datetime, timezone
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    set_access_cookies,
    get_jwt
)

# import blueprints
from blueprints.auth import auth_bp
from blueprints.surges import surges_bp
from blueprints.actions import actions_bp

# other imports for flask-migrate
from models.post import Post
from models.word import Word


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
        resources={r"/*": {"origins": r"*"}},
        supports_credentials=True,
    )  # TODO: not localhost but custom domain host

    # to use current_user
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if type(user) is not int:
            return user.id
        else:
            return User.query.filter_by(id=user).one_or_none().id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()



    # cookie scheme auto-refresh, note that conflicts with nuxt-auth for the moment
    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original respone
            return response
        

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(surges_bp, url_prefix="/api/surges")
    app.register_blueprint(actions_bp, url_prefix="/api/actions")
    return app
