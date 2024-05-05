from hmac import compare_digest

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
    get_jwt
)
from flask_restful import Resource, reqparse
from flask_smorest import Blueprint

from blocklist import BLOCKLIST
from models import UserModel

blp = Blueprint("Users", "users", description="Operations on users")

_user_parser = reqparse.RequestParser()
_user_parser.add_argument("username", type=str, required=True, help="This field cannot be blank")
_user_parser.add_argument("password", type=str, required=True, help="This field cannot be blank")
_user_parser.add_argument("email", type=str, required=False)

BLANK_ERROR = "'{}' cannot be blank."
USER_ALREADY_EXISTS = "A user with that username already exists."
CREATED_SUCCESSFULLY = "User created successfully."
USER_NOT_FOUND = "User not found."
USER_DELETED = "User deleted."
INVALID_CREDENTIALS = "Invalid credentials!"
USER_LOGGED_OUT = "User <id={user_id}> successfully logged out."


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()
        if UserModel.find_by_username(data["username"]):
            return {"message": USER_ALREADY_EXISTS}, 400

        user = UserModel(**data)
        user.save_to_db()
        return {"message": CREATED_SUCCESSFULLY}, 201


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data["username"])
        if user and compare_digest(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        return {"message":INVALID_CREDENTIALS}, 401


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user.json(), 200

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        user_id = get_jwt_identity()
        BLOCKLIST.add(jti)
        return {"message": USER_LOGGED_OUT.format(user_id=user_id)}, 200


class RefreshToken(Resource):
    @jwt_required(fresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
