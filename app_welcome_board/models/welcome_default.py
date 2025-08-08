import mongoengine as me
from bson import ObjectId

from base_models.basemodel import BaseClass


class WelcomeBoardDefault(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    path = me.StringField(null=True, required=False, default=None)
    note = me.StringField(null=True, required=False, default=None)
    isActive = me.BooleanField()

    meta = {
        'collection': 'welComeBoardDefault'
    }