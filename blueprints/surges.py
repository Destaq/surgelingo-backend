from flask import Blueprint, jsonify, request
from extensions import db
from models.user import User
from models.post import Post  # aka surge
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm.state import InstanceState
import collections
from operator import itemgetter

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
    return jsonify(
        surge=convert_post_to_dict(surge),
        author=User.query.filter_by(id=surge.author_id).first().username,
    )


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


#######################


def calculator(user_stems, content_stems):
    """
    Returns the number of words a user knows in a stemmed content B.
    """
    c_a=collections.Counter(user_stems)
    c_b=collections.Counter(content_stems)
    duplicates=[]
    for c in c_a:
        duplicates+=[c]*min(c_a[c],c_b[c])
    
    number_overlapping_words = len(duplicates)
    content_stem_length = len(content_stems)

    return number_overlapping_words / content_stem_length


@surges_bp.route("/return-personalized", methods=["GET"])
@jwt_required()
def return_personalized_surges():
    # returns top n surges based on % content known by user
    user_known_stems = [word.word for word in list(set(current_user.words))]
    desired_language_code = request.args.get("language_code")
    returned_surges = Post.query.filter_by(language_code=desired_language_code).all()


    # TODO BUG NOTE - far from the best way to do this, especially with larger db sizes
    # NOTE: sorted does not work
    show_dict = {}
    for elem in returned_surges:
        show_dict[elem] = calculator(user_known_stems, elem.stemmed_content.split(" "))
    
    res = sorted(show_dict.items(), key=itemgetter(1), reverse=True)

    return jsonify(surges=[convert_post_to_dict(el[0]) for el in res[:20]])
