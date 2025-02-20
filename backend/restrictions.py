from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CustomerRestriction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String, unique=True, nullable=False)
    restrictions = db.Column(db.JSON, nullable=False)

def get_customer_restrictions(customer_id):
    entry = CustomerRestriction.query.filter_by(customer_id=customer_id).first()
    return entry.restrictions if entry else {}

def set_customer_restrictions(customer_id, restrictions):
    entry = CustomerRestriction.query.filter_by(customer_id=customer_id).first()
    if entry:
        entry.restrictions = restrictions
    else:
        entry = CustomerRestriction(customer_id=customer_id, restrictions=restrictions)
        db.session.add(entry)
    
    db.session.commit()
