from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Warehouse(db.Model):
    __tablename__ = 'warehouses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    location = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)

    items = db.relationship(
        'Item', backref='warehouse', lazy=True, cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'items': [item.to_dict() for item in self.items]
        }


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    warehouse_id = db.Column(
        db.Integer, db.ForeignKey('warehouses.id'), nullable=False
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'warehouse_id': self.warehouse_id
        }
