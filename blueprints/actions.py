from flask import Blueprint, jsonify, request
from extensions import db
from models.user import User
from models.word import Word
from flask_jwt_extended import jwt_required, current_user


actions_bp = Blueprint("actions", __name__)


@actions_bp.route("/edit-wordbank", methods=["POST"])
@jwt_required()
def edit_user_wordbank():
    """
    Edit the user's wordbank.
    """
    wordbank = request.json["wordbank"]
    wordbank = wordbank.splitlines()
    for word in wordbank:
        gen_word = Word(word, current_user.id)

        # link word to user
        current_user.words.append(gen_word)
        db.session.add(gen_word)
        db.session.commit()

    return jsonify({"message": "Wordbank updated."})


@actions_bp.errorhandler(Exception)
def print_error(e):
    print(request.headers, "\n", e)
    return {"message": "Something went wrong"}, 500


# # needs to be run inside route
# import pandas as pd
# from models.post import Post


# # NOTE: currently limiting to 1k due to Heroku free database limit
# @actions_bp.route("/admin-content", methods=["GET"])
# def runner():
#     file = "data/tatoeba/spa_sentences.tsv"
#     admin_user = User.query.filter_by(username="SurgeOfficial").first()

#     datareader = pd.read_csv(file, delimiter="\t", nrows=1000)
#     count = 0
#     for index, row in datareader.iterrows():
#         count += 1
#         print(f"{count * 100 /1000}%", end="\r")
#         if len(row[2]) <= 200:
#             new_surge_post = Post(row[2], admin_user.id, [], "es")
#             db.session.add(new_surge_post)
#             db.session.commit()
#     return jsonify({"message": "Content imported."})


# # NOTE: sizes = 1MB/4k, so the number of posts that would fit in 10gb is 400 000 000
