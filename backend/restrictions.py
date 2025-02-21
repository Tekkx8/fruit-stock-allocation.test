from flask_sqlalchemy import SQLAlchemy
from typing import Dict, Optional, List
import logging
from datetime import datetime
import json
from database import db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class Restriction(db.Model):
    """Model for customer restrictions with validation."""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    quality = db.Column(db.String(500))  # Increased length for multiple values
    origin = db.Column(db.String(500))
    variety = db.Column(db.String(500))
    ggn = db.Column(db.String(50))
    supplier = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, customer_id: str, **kwargs):
        super().__init__(**kwargs)
        self.customer_id = customer_id
        self.validate_customer_id()

    def validate_customer_id(self):
        """Validate customer ID format."""
        if not self.customer_id or not isinstance(self.customer_id, str):
            raise ValidationError("Customer ID must be a non-empty string")
        if len(self.customer_id) > 50:
            raise ValidationError("Customer ID must be 50 characters or less")

    def to_dict(self) -> Dict:
        """Convert restriction to dictionary with proper type handling."""
        try:
            return {
                "id": self.id,
                "customer_id": self.customer_id,
                "quality": self._split_field(self.quality),
                "origin": self._split_field(self.origin),
                "variety": self._split_field(self.variety),
                "ggn": self.ggn,
                "supplier": self._split_field(self.supplier),
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error converting restriction to dict: {str(e)}")
            raise

    def _split_field(self, field: Optional[str]) -> List[str]:
        """Safely split comma-separated field values."""
        if not field:
            return []
        return [item.strip() for item in field.split(',') if item.strip()]

    @staticmethod
    def from_dict(data: Dict) -> 'Restriction':
        """Create Restriction instance from dictionary with validation."""
        try:
            customer_id = data.get('customer_id')
            if not customer_id:
                raise ValidationError("Customer ID is required")

            restriction = Restriction(customer_id=customer_id)
            
            # Validate and set list fields
            for field in ['quality', 'origin', 'variety', 'supplier']:
                values = data.get(field, [])
                if not isinstance(values, list):
                    raise ValidationError(f"{field} must be a list")
                setattr(restriction, field, ','.join(str(v).strip() for v in values if v))

            # Validate and set GGN
            ggn = data.get('ggn')
            if ggn is not None:
                if not isinstance(ggn, str):
                    raise ValidationError("GGN must be a string")
                restriction.ggn = ggn.strip()

            return restriction
        except Exception as e:
            logger.error(f"Error creating restriction from dict: {str(e)}")
            raise

def get_restrictions(customer_id: str = "default") -> Dict:
    """
    Retrieve restrictions for a customer from SQLite with proper error handling.

    Args:
        customer_id (str): Customer identifier.

    Returns:
        Dict: Restrictions (quality, origin, variety, GGN, supplier).

    Raises:
        ValidationError: If customer_id is invalid
    """
    try:
        if not customer_id or not isinstance(customer_id, str):
            raise ValidationError("Invalid customer ID")

        restriction = Restriction.query.filter_by(customer_id=customer_id).first()
        
        if not restriction:
            logger.warning(f"No restrictions found for customer {customer_id}, using defaults")
            return {
                "quality": ["Good Q/S", "Fair M/C"],
                "origin": ["Chile"],
                "variety": ["LEGACY"],
                "ggn": None,
                "supplier": []
            }

        return restriction.to_dict()

    except Exception as e:
        logger.error(f"Error retrieving restrictions for customer {customer_id}: {str(e)}")
        raise

def set_restrictions(customer_id: str, restrictions: Dict) -> Dict:
    """
    Store or update restrictions for a customer in SQLite with validation.

    Args:
        customer_id (str): Customer identifier
        restrictions (Dict): Restriction values

    Returns:
        Dict: Updated restrictions

    Raises:
        ValidationError: If input data is invalid
    """
    try:
        if not customer_id or not isinstance(customer_id, str):
            raise ValidationError("Invalid customer ID")

        if not isinstance(restrictions, dict):
            raise ValidationError("Restrictions must be a dictionary")

        # Start database transaction
        try:
            restriction = Restriction.query.filter_by(customer_id=customer_id).first()
            
            if restriction:
                # Update existing restriction
                for field in ['quality', 'origin', 'variety', 'supplier']:
                    values = restrictions.get(field, [])
                    if not isinstance(values, list):
                        raise ValidationError(f"{field} must be a list")
                    setattr(restriction, field, ','.join(str(v).strip() for v in values if v))

                ggn = restrictions.get('ggn')
                if ggn is not None:
                    if not isinstance(ggn, str):
                        raise ValidationError("GGN must be a string")
                    restriction.ggn = ggn.strip()

                restriction.updated_at = datetime.utcnow()
            else:
                # Create new restriction
                restriction = Restriction.from_dict({
                    "customer_id": customer_id,
                    **restrictions
                })

            db.session.add(restriction)
            db.session.commit()

            logger.info(f"Successfully updated restrictions for customer {customer_id}")
            return restriction.to_dict()

        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error while setting restrictions: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Error setting restrictions for customer {customer_id}: {str(e)}")
        raise

def delete_restrictions(customer_id: str) -> bool:
    """
    Delete restrictions for a customer.

    Args:
        customer_id (str): Customer identifier

    Returns:
        bool: True if restrictions were deleted, False if not found

    Raises:
        ValidationError: If customer_id is invalid
    """
    try:
        if not customer_id or not isinstance(customer_id, str):
            raise ValidationError("Invalid customer ID")

        restriction = Restriction.query.filter_by(customer_id=customer_id).first()
        if restriction:
            db.session.delete(restriction)
            db.session.commit()
            logger.info(f"Successfully deleted restrictions for customer {customer_id}")
            return True
        
        logger.warning(f"No restrictions found to delete for customer {customer_id}")
        return False

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting restrictions for customer {customer_id}: {str(e)}")
        raise
