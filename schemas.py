from marshmallow import Schema, fields


class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)


class StoreSchema(PlainStoreSchema):
    items = fields.Nested(PlainItemSchema(), many=True)


class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_from=True)
    stores = fields.Nested(PlainStoreSchema(), dump_only=True)


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
