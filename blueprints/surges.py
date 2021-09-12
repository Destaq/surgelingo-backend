from flask import Blueprint, jsonify, request
from extensions import db
from models.user import User
from models.post import Post  # aka surge
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm.state import InstanceState


surges_bp = Blueprint("surges", __name__)


def convert_post_to_dict(post):
    post_dict = {}
    for attr in vars(post):
        attr_value = getattr(post, attr)
        if isinstance(attr_value, InstanceState):
            pass
        else:
            post_dict[attr] = attr_value
    return post_dict


@surges_bp.route("/create", methods=["POST"])
@jwt_required()
def create_surge_post():
    language_code = request.json.get("language_code")
    surge_text = request.json.get("content")
    surge_tags = request.json.get("tags")

    # and then author is taken from current_user
    author = current_user
    print("we have author", author)

    surge = Post(
        content=surge_text,
        language_code=language_code,
        author_id=author.id,
        tags=surge_tags.split(", "),
    )
    db.session.add(surge)
    db.session.commit()

    return jsonify(message="Success", route_link=surge.route_link), 201


@surges_bp.route("/get", methods=["GET"])
def get_surge():
    surge_id = request.args.get("id")

    surge = Post.query.filter_by(route_link=surge_id).first()
    return jsonify(surge=convert_post_to_dict(surge), author=User.query.filter_by(id=surge.author_id).first().username)


# TODO if time: use secondary table to only allow 1 upvote/downvote per user; if already upvoted/downvoted, remove vote
@surges_bp.route("/upvote", methods=["POST"])
def upvote():
    surge_id = request.args.get("id")
    surge = Post.query.filter_by(route_link=surge_id).first()
    surge.upvote()

    return jsonify(message="Success", upvotes=surge.upvotes)


@surges_bp.route("/downvote", methods=["POST"])
def downvote():
    surge_id = request.args.get("id")
    surge = Post.query.filter_by(route_link=surge_id).first()
    surge.downvote()

    return jsonify(message="Success", upvotes=surge.upvotes)
