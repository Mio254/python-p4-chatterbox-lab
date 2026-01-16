# server/app.py

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_cors import CORS

from models import db, Message

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)


@app.get("/messages")
def get_messages():
    messages = (
        Message.query
        .order_by(Message.created_at.asc())
        .all()
    )
    return make_response(jsonify([m.to_dict() for m in messages]), 200)


@app.post("/messages")
def create_message():
    # Prefer JSON; fall back to form params if someone uses x-www-form-urlencoded
    data = request.get_json(silent=True) or request.form

    message = Message(
        body=data.get("body"),
        username=data.get("username"),
    )

    db.session.add(message)
    db.session.commit()

    return make_response(jsonify(message.to_dict()), 201)


@app.patch("/messages/<int:id>")
def update_message(id):
    message = db.session.get(Message, id)
    if message is None:
        return make_response(jsonify({"error": "Message not found"}), 404)

    data = request.get_json(silent=True) or request.form

    # Only updating body per requirements
    if "body" in data:
        message.body = data.get("body")

    db.session.commit()
    return make_response(jsonify(message.to_dict()), 200)


@app.delete("/messages/<int:id>")
def delete_message(id):
    message = db.session.get(Message, id)
    if message is None:
        return make_response(jsonify({"error": "Message not found"}), 404)

    db.session.delete(message)
    db.session.commit()

    return make_response("", 204)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
