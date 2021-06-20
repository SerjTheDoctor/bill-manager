from . import db
from flaskr.config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, wanna_be_password):
        return check_password_hash(wanna_be_password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(Config.SECRET_KEY, expires_in=expiration)

        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(Config.SECRET_KEY)

        # try:
        #     data = s.loads(token)
        # except SignatureExpired:
        #     return None  # valid token, but expired
        # except BadSignature:
        #     return None  # invalid token

        user = User.query.get(1)#data['id'])

        return user
