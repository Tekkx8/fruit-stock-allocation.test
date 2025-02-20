import logging
from typing import Dict, List
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def allocate_fruits(stock: Dict[str, int], destinations: List[str], restrictions: Dict) -> Dict:
    """
    Allocate fruit stock across destinations while respecting restrictions.

    Args:
        stock (Dict[str, int]): Dictionary of fruit types and quantities (e.g., {"apples": 100, "bananas": 50}).
        destinations (List[str]): List of destination names (e.g., ["Store1", "Store2"]).
        restrictions (Dict): Restrictions from restrictions.py (e.g., max/min stock per destination).

    Returns:
        Dict[str, Dict[str, int]]: Allocation per destination (e.g., {"Store1": {"apples": 50}}).

    Raises:
        ValueError: If stock or destinations are invalid.
    """
    if not stock or not all(isinstance(v, (int, float)) and v >= 0 for v in stock.values()):
        raise ValueError("Stock must be a non-empty dict with non-negative values.")
    if not destinations or not all(isinstance(d, str) for d in destinations):
        raise ValueError("Destinations must be a non-empty list of strings.")

    allocation = {dest: {} for dest in destinations}
    total_destinations = len(destinations)

    for fruit, qty in stock.items():
        # Distribute evenly, respecting restrictions
        base_qty = qty // total_destinations
        remainder = qty % total_destinations

        for i, dest in enumerate(destinations):
            alloc_qty = base_qty + (1 if i < remainder else 0)
            # Apply restrictions (simplified—expand based on restrictions.py)
            max_limit = restrictions.get(dest, {}).get(fruit, {}).get("max", float('inf'))
            if alloc_qty > max_limit:
                alloc_qty = max_limit
                logger.warning(f"Reduced {fruit} for {dest} to {alloc_qty} due to max limit {max_limit}")
            allocation[dest][fruit] = allocation[dest].get(fruit, 0) + alloc_qty

    logger.info(f"Allocated stock: {json.dumps(allocation, indent=2)}")
    return allocation

if __name__ == "__main__":
    # Example usage
    sample_stock = {"apples": 100, "bananas": 50}
    sample_destinations = ["Store1", "Store2"]
    sample_restrictions = {
        "Store1": {"apples": {"max": 60}, "bananas": {"max": 30}},
        "Store2": {"apples": {"max": 40}, "bananas": {"max": 20}}
    }
    result = allocate_fruits(sample_stock, sample_destinations, sample_restrictions)
    print(result)
