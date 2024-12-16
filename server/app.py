from models import db, Restaurant, RestaurantPizza, Pizza
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    restaurant_data = restaurant.to_dict()
    restaurant_data['restaurant_pizzas'] = [
        {
            "id": rp.id,
            "price": rp.price,
            "pizza": rp.pizza.to_dict()
        } for rp in restaurant.restaurant_pizzas
    ]
    return jsonify(restaurant_data)

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    db.session.delete(restaurant)
    db.session.commit()
    return make_response("", 204)

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    if not (1 <= data["price"] <= 30):
        return make_response(jsonify({"errors": ["validation errors"]}), 400)
    
    pizza = Pizza.query.get(data["pizza_id"])
    restaurant = Restaurant.query.get(data["restaurant_id"])

    if not pizza or not restaurant:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    try:
        restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify(restaurant_pizza.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)