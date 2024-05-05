from flask_restful import Resource
from flask_smorest import Blueprint

from models import StoreModel

blp = Blueprint("Stores", "stores", description="Operations on stores")

NAME_ALREADY_EXISTS = "A store with name '{}' already exists."
ERROR_INSERTING = "An error occurred while inserting the store."
STORE_NOT_FOUND = "Store not found."
STORE_DELETED = "Store deleted."

class Store(Resource):
    def get(self, name: str):
        store = StoreModel.find_by_name(name)
        return store

    def post(self, name: str):
        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500
        return store.json(), 201

    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
        return {"message": STORE_DELETED}


class StoreList(Resource):
    def get(self):
        return {
            "stores": [x.json() for x in StoreModel.find_all()]
        }

