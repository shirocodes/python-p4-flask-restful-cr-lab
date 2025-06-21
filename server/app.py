#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = True

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Plants(Resource):
    def get(self):
        plants = Plant.query.all()
        
        response_dict_list = [n.to_dict() for n in plants]
        
        return make_response(response_dict_list, 200)
    
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        name = data.get("name")
        image = data.get("image")
        price = data.get("price")
        
        if not all([name, image, price]):
            return jsonify({"error": "Missing required fields"}), 400
        
        try:
            new_record = Plant(
            name=name,
            image=image,
            price=float(price)
            )
            db.session.add(new_record)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400
        
        return new_record.to_dict(), 201
    
api.add_resource(Plants, '/plants')
        
class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.filter_by(id=id).first()
        
        if not plant:
            return {"error": "not found"}, 400
        
        response_dict = plant.to_dict()
        return make_response(response_dict, 200)
        
api.add_resource(PlantByID, '/plants/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
