from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field cannot be left blank"
    )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every item needs a store id"
    )

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json() # returns a json dictionary instead of an item now
        return {'message': 'Item not found'}, 404
        # item = next(filter(lambda x: x['name'] == name, items), None)
        # return {'item': item}, 200 if item else 404
   
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400 # 400 is a bad request
        # checking for errors before parsing the data
        data = Item.parser.parse_args()

        item = ItemModel(name, **data) # also could do data['price'], data['store_id']
        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500 # internal server error

        return item.json(), 201
    
    #overwriting items list with new list without the define item
    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, data['price'], data['store_id'])
        else:
            item.price = data['price']
            item.store_id = data['store_id']

        item.save_to_db()
        return item.json()


class ItemList(Resource):
    def get(self):
        # could also use {'items': [item.json() for item in ItemModel.query.all()]}
        return {'items' : list(map(lambda x: x.json(), ItemModel.query.all()))}