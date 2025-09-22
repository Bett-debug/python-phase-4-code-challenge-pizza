
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)



@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    response = [restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in restaurants]
    return make_response(response, 200)


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)   
    if restaurant:
        return make_response(restaurant.to_dict(), 200)
    return make_response({"error": "Restaurant not found"}, 404)




@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    
    db.session.delete(restaurant)
    db.session.commit()
    return make_response({}, 204)



@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return make_response(
        [p.to_dict(rules=("-restaurant_pizzas",)) for p in pizzas],
        200
    )



@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"],
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response = {
            "id": new_restaurant_pizza.id,
            "price": new_restaurant_pizza.price,
            "pizza_id": new_restaurant_pizza.pizza_id,
            "restaurant_id": new_restaurant_pizza.restaurant_id,
            "pizza": new_restaurant_pizza.pizza.to_dict(),
            "restaurant": new_restaurant_pizza.restaurant.to_dict(),
        }
        return jsonify(response), 201

    except Exception:
        # ✅ match test expectation
        return jsonify({"errors": ["validation errors"]}), 400





if __name__ == "__main__":
    app.run(port=5555, debug=True)

