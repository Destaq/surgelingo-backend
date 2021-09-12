from flask import Blueprint, jsonify, request
from extensions import db
from models.user import User
from models.post import Post  # aka surge
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm.state import InstanceState
import collections
from operator import itemgetter
from random import shuffle


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
    c_a = collections.Counter(user_stems)
    c_b = collections.Counter(content_stems)
    duplicates = []
    for c in c_a:
        duplicates += [c] * min(c_a[c], c_b[c])

    number_overlapping_words = len(duplicates)
    content_stem_length = len(content_stems)

    return number_overlapping_words / content_stem_length


@surges_bp.route("/detailed-search", methods=["GET"])
def search_surges():
    author_username = request.args.get("username")
    language_code = request.args.get("language_code")
    tag = request.args.get("tag")
    contents = request.args.get("contents")
    query_config = []
    query_config.append(language_code == language_code)

    if request.args.get("alreadyShown"):
        exclude_links = request.args.get("alreadyShown").split(",")
    else:
        exclude_links = []

    if author_username != "null":
        query_config.append(User.query.filter_by(username=author_username).first())
    if tag != "null":
        query_config.append(Post.tags.contains([tag]))
    if contents != "null":
        query_config.append(Post.content.contains(contents))


    results = Post.query.filter(Post.route_link.notin_(exclude_links)).filter(*query_config).limit(10).all()
    results = [convert_post_to_dict(result) for result in results]

    for item in results:
        item["author"] = User.query.filter_by(id=item["author_id"]).first().username

    return jsonify(surges=results)


@surges_bp.route("/return-personalized", methods=["GET"])
@jwt_required()
def return_personalized_surges():
    # returns top n surges based on % content known by user
    user_known_stems = [word.word for word in list(set(current_user.words))]
    desired_language_code = request.args.get("language_code")
    if request.args.get("alreadyShown"):
        exclude_links = request.args.get("alreadyShown").split(",")
    else:
        exclude_links = []

    if request.args.get("difficulty"):
        difficulty_limit = float(request.args.get("difficulty"))
    else:
        difficulty_limit = 0.8  # default of medium
    returned_surges = (
        Post.query.filter_by(language_code=desired_language_code)
        .filter(Post.route_link.notin_(exclude_links))
        .all()
    )

    # TODO BUG NOTE - far from the best way to do this, especially with larger db sizes
    # NOTE: sorted does not work without this roundabout method
    # need to learn some more SQL to do it properly
    show_dict = {}
    for elem in returned_surges:
        if difficulty_limit != 0:
            value = calculator(user_known_stems, elem.stemmed_content.split(" "))
            if value >= difficulty_limit:
                show_dict[elem] = value
        else:
            # just show randomly
            show_dict[elem] = 0

    res = sorted(show_dict.items(), key=itemgetter(1), reverse=True)

    # not random by default, retains input order, so shuffle if difficulty limit is zero
    if difficulty_limit == 0:
        shuffle(res)

    readable_res = [convert_post_to_dict(el[0]) for el in res[:20]]
    for item in readable_res:
        item["author"] = User.query.filter_by(id=item["author_id"]).first().username

    # TODO: create a highlighted value for the word
    for element in readable_res:
        known_or_not = []
        stemmed_content = element["stemmed_content"].split(" ")
        for word in stemmed_content:
            if word in user_known_stems:
                # green highlight as known
                known_or_not.append(True)
            else:
                # red highlight as unknown
                known_or_not.append(False)
        element["knownLemmas"] = known_or_not

    return jsonify(surges=readable_res)


@surges_bp.errorhandler(Exception)
def print_error(e):
    print(request.headers, "\n", e)
    return {"message": "Something went wrong"}, 500
