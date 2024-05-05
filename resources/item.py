from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_restful import Resource, reqparse
from flask_smorest import Blueprint

from models import ItemModel

blp = Blueprint("Items", "items", description="Operations on items")

BLANK_ERROR = "'{}' cannot be blank."
NAME_ALREADY_EXISTS = "An item with name '{}' already exists."
ERROR_INSERTING = "An error occurred while inserting the item."
ITEM_NOT_FOUND = "Item not found."
ITEM_DELETED = "Item deleted."

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help=BLANK_ERROR.format("price")
    )
    parser.add_argument(
        "store_id", type=int, required=True, help=BLANK_ERROR.format("store_id")
    )
    parser.add_argument(
        "description", type=str, required=False
    )
    @jwt_required()
    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {"message": "Item not found."}, 404

    @jwt_required(fresh=True)
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return (
                {"message": NAME_ALREADY_EXISTS.format(name)},
                400,
            )
        data = Item.parser.parse_args()
        item = ItemModel(name, **data)
        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500
        return item.json(), 201

    @jwt_required()
    def delete(self, name: str):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required."}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED}, 200
        return {"message": ITEM_NOT_FOUND}, 404

    def put(self, name: str):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if item:
            item.price = data["price"]
        else:
            item = ItemModel(name, **data)
        item.save_to_db()
        return item.json(), 200


class ItemList(Resource):
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = [i.json() for i in ItemModel.query.all()]
        if user_id:
            return {"items": items}, 200
        return (
            {
                "items": [item["name"] for item in items],
                "message": "More data available if you log in.",
            },
            200,
        )
