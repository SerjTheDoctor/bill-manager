from flask import Blueprint, request, url_for, jsonify
from .schema import User
from . import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def new_user():
    email = request.json.get('email')
    password = request.json.get('password')

    if email is None or password is None:
        # missing arguments
        return {}, 400

    if User.query.filter_by(email=email).first() is not None:
        # user already exists
        return {}, 400

    user: User = User(email=email)
    user.hash_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'email': user.email}), 200, {'Location': url_for('get_user', id=user.id, _external=True)}
