import os

from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Project setup

#Set sqlite DB location
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "assets.db"))

# Create flask app and configure to use sqlite database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

# Create RESTful API, initialize SQLAlchem, initialze Marshmallow
api = Api(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Dictionaries containing allowed asset classes and types
allowed_asset_classes = {"satellite": ["dove", "rapideye"], "antenna": ["yagi", "dish"]}
allowed_asset_types = ["satellite", "antenna"]

# For use with unittest and flask-testing. Set to use a temporary DB.
def create_test_app():
    app = Flask(__name__)
    api = Api(app)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(os.path.join(project_dir, "test.db"))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Dynamically bind SQLAlchemy to application
    db.init_app(app)
    # app.app_context().push() # this does the binding
    api.add_resource(AssetsResource, '/asset/<asset_id>')
    api.add_resource(AssetsNameResource, '/asset/name/<name>')
    api.add_resource(AssetsListResource, '/assets')
    return app

# Database model for Asset table
class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    asset_class = db.Column(db.String(64), nullable=False)
    asset_type = db.Column(db.String(64), nullable=False)

    def __init__(self, name, asset_class, asset_type):
        if len(name) < 4 or len(name) > 64: raise Exception("Name must be between 4 and 64 characters")
        self.name = name
        self.asset_class = asset_class
        self.asset_type = asset_type

# Marshmallow schema for JSON serialization/deserialization
class AssetSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('name', 'asset_type', 'asset_class')

asset_schema = AssetSchema()
assets_schema = AssetSchema(many=True)

# All of the logic we run when receiving a POST request to ensure the asset is valid
def AssetValidator(name, asset_type, asset_class):
    # Check if name is too long or too short
    if len(name) < 4 or len(name) > 64: return {'message': 'Name must be between 4 and 64 characters'}, 400
    # Check if name is not unique
    if db.session.query(Asset).filter_by(name=name).scalar() != None:
        return {'message': 'Name not unique'}, 400
    # Check if name starts with a dash or underscore
    if name[0] == '_' or name[0] == '-':
        return {'message': 'Name cannot start with an underscore or dash'}, 400
    # Check if asset_type exists in our allowed_asset_types object.
    if asset_type not in allowed_asset_types:
        # we return bad request since asset_class is not listed in our list.
        return {'message': 'Invalid Asset Type'}, 400
    # Check if asset_class exists in our allowed_asset_classes object.
    if asset_class not in allowed_asset_classes[asset_type]:
        return {'message': 'Invalid Asset Class'}, 400
    # Check if asset name is ASCII encoded.
    try:
        name.decode('ascii')
    except UnicodeDecodeError:
        return {'message': 'Name must be ascii encoded'}, 400
    else:
        return 200

# Class for GET requests of a single resource
class AssetsResource(Resource):
    def get(self, asset_id):
        asset = db.session.query(Asset).filter_by(id=asset_id).first()
        if not asset:
            return {'message': 'Not Found'}, 404
        return asset_schema.jsonify(asset)

class AssetsListResource(Resource):

    # List all assets
    def get(self):
        return [{asset.id: {'name': asset.name, 'asset_class': asset.asset_class, 'asset_type': asset.asset_type}} for asset in db.session.query(Asset).all()]

    # Post new asset
    def post(self):
        # Validate data is JSON
        if not request.json:
            return {'message': "Data must be JSON"}, 400
        # Pull data out of JSON request
        name = request.json['name']
        asset_class = request.json['asset_class']
        asset_type = request.json['asset_type']

        # Validate data meets our requirements and return any errors if we don't get a success response from the function.
        if AssetValidator(name=name, asset_class=asset_class, asset_type=asset_type) != 200:
            return AssetValidator(name=name, asset_class=asset_class, asset_type=asset_type)
        new_asset = Asset(name=name, asset_class=asset_class, asset_type=asset_type)
        db.session.add(new_asset)
        db.session.commit()
        return {new_asset.id: {'name': new_asset.name, 'asset_class': new_asset.asset_class, 'asset_type': new_asset.asset_type}}, 201


class AssetsNameResource(Resource):
    # Get an Asset by name
    def get(self, name):
        asset_name = db.session.query(Asset).filter_by(name=name).first()
        if not asset_name:
            return {'message': 'Not Found'}, 404
        return asset_schema.jsonify(asset_name)

api.add_resource(AssetsResource, '/asset/<asset_id>')
api.add_resource(AssetsNameResource, '/asset/name/<name>')
api.add_resource(AssetsListResource, '/assets')

if __name__ == '__main__':
    # Run with 'host=0.0.0.0' to enable Dockerized operation
    app.run(host='0.0.0.0')
