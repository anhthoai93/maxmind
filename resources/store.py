from flask_restful import Resource
from flask_smorest import Blueprint

from models import StoreModel

blp = Blueprint("Stores", "stores", description="Operations on stores")


class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        return store

    def post(self, name):
        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": "An error occurred while creating the store."}, 500
        return store.json(), 201

    def delete(cls, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
        return {"message": "Store deleted"}


class StoreList(Resource):
    def get(self):
        return {
            "stores": [x.json() for x in StoreModel.find_all()]
        }

