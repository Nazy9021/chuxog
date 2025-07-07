import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'  # Use MySQL URI in production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Product model
class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)
    cost = db.Column(db.Float)
    supplier = db.Column(db.String(100))
    date_added = db.Column(db.Date)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "cost": self.cost,
            "supplier": self.supplier,
            "date_added": self.date_added.strftime("%Y-%m-%d") if self.date_added else None
        }

@app.route('/inventory', methods=['GET'])
def get_inventory():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/inventory/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(
        product_id=data['product_id'],
        name=data['name'],
        category=data['category'],
        quantity=data['quantity'],
        price=data['price'],
        cost=data['cost'],
        supplier=data['supplier'],
        date_added=datetime.strptime(data['date_added'], '%Y-%m-%d')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"}), 201

@app.route('/update_product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    product = Product.query.get_or_404(product_id)
    for key in data:
        setattr(product, key, data[key])
    db.session.commit()
    return jsonify({"message": "Product updated successfully"})

@app.route('/sale', methods=['POST'])
def make_sale():
    data = request.get_json()
    product = Product.query.get_or_404(data['product_id'])
    qty_sold = data['quantity']
    if product.quantity < qty_sold:
        return jsonify({"error": "Insufficient stock"}), 400
    product.quantity -= qty_sold
    db.session.commit()
    return jsonify({"message": "Sale recorded"})

@app.route('/low_stock', methods=['GET'])
def low_stock():
    threshold = int(request.args.get('threshold', 5))
    low_items = Product.query.filter(Product.quantity <= threshold).all()
    return jsonify([p.to_dict() for p in low_items])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)


