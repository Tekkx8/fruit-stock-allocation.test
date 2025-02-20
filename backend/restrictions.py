from flask_sqlalchemy import SQLAlchemy
from typing import Dict, Optional
import logging

db = SQLAlchemy()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Restriction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False)
    quality = db.Column(db.String(100))
    origin = db.Column(db.String(50))
    variety = db.Column(db.String(50))
    ggn = db.Column(db.String(50))
    supplier = db.Column(db.String(100))

    def to_dict(self) -> Dict:
        return {
            "quality": self.quality.split(',') if self.quality else [],
            "origin": self.origin.split(',') if self.origin else [],
            "variety": self.variety.split(',') if self.variety else [],
            "ggn": self.ggn,
            "supplier": self.supplier.split(',') if self.supplier else []
        }

def get_restrictions(customer_id: str = "default") -> Dict:
    """
    Retrieve restrictions for a customer from SQLite.

    Args:
        customer_id (str): Customer identifier.

    Returns:
        Dict: Restrictions (quality, origin, variety, GGN, supplier).
    """
    restriction = Restriction.query.filter_by(customer_id=customer_id).first()
    if not restriction:
        logger.warning(f"No restrictions found for customer {customer_id}")
        return {
            "quality": ["Good Q/S", "Fair M/C"],
            "origin": ["Chile"],
            "variety": ["LEGACY"],
            "ggn": "4063061591012",
            "supplier": ["HORTIFRUT CHILE S.A."]
        }
    return restriction.to_dict()

def set_restrictions(customer_id: str, restrictions: Dict):
    """
    Store or update restrictions for a customer in SQLite.
    """
    restriction = Restriction.query.filter_by(customer_id=customer_id).first()
    if not restriction:
        restriction = Restriction(customer_id=customer_id)
    
    restriction.quality = ','.join(restrictions.get('quality', []))
    restriction.origin = ','.join(restrictions.get('origin', []))
    restriction.variety 
