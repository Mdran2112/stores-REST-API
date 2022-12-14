from typing import Dict, Any

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from controllers.utils import handle_error
from db import db
from models import StoreModel
from schemas import PlainStoreSchema


blp = Blueprint("Stores", "stores", description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):

    @blp.response(200, PlainStoreSchema)
    def get(self, store_id: int):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required()
    def delete(self, store_id: str):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": f"store {store_id} deleted."}


@blp.route("/store")
class StoreList(MethodView):

    @blp.response(200, PlainStoreSchema(many=True))
    @handle_error
    def get(self):
        return StoreModel.query.all()

    @jwt_required()
    @blp.arguments(PlainStoreSchema)
    @blp.response(201, PlainStoreSchema)
    def post(self, store_data: Dict[str, Any]):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message=f"A store with that name already exists: {store.name}.")
        except SQLAlchemyError:
            abort(500, message=f"An error ocurred while inserting Store: {store_data}.")

        return store
