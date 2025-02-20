import json
from typing import Dict, Optional
from functools import lru_cache
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def load_restrictions(file_path: str = "customer_restrictions.json") -> Dict:
    """
    Load and cache restrictions from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing restrictions.

    Returns:
        Dict: Parsed restrictions (e.g., {"Store1": {"apples": {"max": 50}}})

    Raises:
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the JSON is invalid.
    """
    try:
        with open(file_path, 'r') as f:
            restrictions = json.load(f)
        logger.info(f"Loaded restrictions from {file_path}")
        return restrictions
    except FileNotFoundError:
        logger.error(f"Restrictions file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {str(e)}")
        return {}

class Restriction:
    def __init__(self, data: Dict):
        """
        Initialize restriction object with data from JSON.

        Args:
            data (Dict): Restriction data (e.g., {"max_stock": 100, "fruit_limits": {...}}).
        """
        self.max_stock = data.get("max_stock", float('inf'))
        self.min_stock = data.get("min_stock", 0)
        self.fruit_limits = data.get("fruit_limits", {})

    def validate_allocation(self, allocation: Dict[str, int]) -> bool:
        """
        Validate if an allocation meets the restrictions.

        Args:
            allocation (Dict[str, int]): Allocation data (e.g., {"apples": 50}).

        Returns:
            bool: True if valid, False otherwise.
        """
        total = sum(allocation.values())
        if not (self.min_stock <= total <= self.max_stock):
            return False

        for fruit, qty in allocation.items():
            max_limit = self.fruit_limits.get(fruit, float('inf'))
            if qty > max_limit:
                return False
        return True

if __name__ == "__main__":
    restrictions = load_restrictions()
    sample_alloc = {"apples": 50, "bananas": 20}
    restr = Restriction(restrictions.get("Store1", {}))
    print(f"Allocation valid? {restr.validate_allocation(sample_alloc)}")
