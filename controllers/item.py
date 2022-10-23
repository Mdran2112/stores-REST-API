from typing import Dict, Any

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from controllers.utils import ItemNotFoundError, handle_error
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema
from db import items, db

blp = Blueprint("Items", "items", description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):

    @staticmethod
    def _get_item(item_id: str) -> Dict[str, Any]:
        item = items.get(item_id, None)
        if item is None:
            raise ItemNotFoundError
        return item

    @blp.response(200, ItemSchema)
    def get(self, item_id: int):
        item = ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id: int):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": f"Item {item_id} deleted"}

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data: Dict[str, Any], item_id: str):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    #@handle_error
    def post(self, item_data: Dict[str, Any]):
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A store with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error ocurred while inserting Item.")

        return item
