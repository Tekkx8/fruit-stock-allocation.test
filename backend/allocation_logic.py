import pandas as pd
from typing import Dict, List, Optional, NamedTuple
from datetime import datetime
import logging
from decimal import Decimal, ROUND_HALF_UP
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class StockBatch:
    def __init__(self, row: pd.Series):
        try:
            self.location = str(row['Location']) if pd.notnull(row['Location']) else ''
            self.batch_number = str(row['Batch Number'])
            self._parse_weight(row['Stock Weight'])
            self.material_id = str(row['Material ID'])
            self.age = int(row['Real Stock Age']) if pd.notnull(row['Real Stock Age']) else 0
            self.variety = str(row['Variety']) if pd.notnull(row['Variety']) else ''
            self.ggn = str(row['GGN']) if pd.notnull(row['GGN']) else ''
            self.origin = str(row['Origin Country']) if pd.notnull(row['Origin Country']) else ''
            self.quality = str(row['Q3: Reinspection Quality']) if pd.notnull(row['Q3: Reinspection Quality']) else ''
            self.supplier = str(row['Supplier']) if pd.notnull(row['Supplier']) else ''
            self.allocation = str(row['Allocation']) if pd.notnull(row['Allocation']) else ''
            self.minimum_size = str(row['MinimumSize']) if pd.notnull(row['MinimumSize']) else ''
            self.origin_pallet = str(row['Origin Pallet Number']) if pd.notnull(row['Origin Pallet Number']) else ''
            self.arrival_date = datetime.now()  # TODO: Add actual arrival date from data
        except (KeyError, ValueError, TypeError) as e:
            raise ValidationError(f"Invalid data in stock batch: {str(e)}")

    def _parse_weight(self, weight_str: str) -> None:
        """Parse weight string and convert to decimal for precise calculations."""
        try:
            # Handle different weight formats and NaN values
            if pd.isnull(weight_str):
                self.weight = Decimal('0')
            else:
                weight_value = str(weight_str).split()[0] if isinstance(weight_str, str) else str(weight_str)
                self.weight = Decimal(weight_value).quantize(Decimal('0.003'), rounding=ROUND_HALF_UP)
        except (ValueError, TypeError, IndexError) as e:
            raise ValidationError(f"Invalid weight format: {weight_str}")

    def matches_restrictions(self, restrictions: Dict) -> bool:
        """Check if this batch meets customer restrictions."""
        try:
            if not restrictions:
                return True

            if restrictions.get('quality') and self.quality not in restrictions['quality']:
                logger.debug(f"Batch {self.batch_number} failed quality restriction")
                return False
                
            if restrictions.get('origin') and self.origin not in restrictions['origin']:
                logger.debug(f"Batch {self.batch_number} failed origin restriction")
                return False
                
            if restrictions.get('variety') and self.variety not in restrictions['variety']:
                logger.debug(f"Batch {self.batch_number} failed variety restriction")
                return False
                
            if restrictions.get('ggn') and self.ggn != restrictions['ggn']:
                logger.debug(f"Batch {self.batch_number} failed GGN restriction")
                return False
                
            if restrictions.get('supplier') and self.supplier not in restrictions['supplier']:
                logger.debug(f"Batch {self.batch_number} failed supplier restriction")
                return False

            if restrictions.get('minimum_size') and self.minimum_size != restrictions['minimum_size']:
                logger.debug(f"Batch {self.batch_number} failed minimum size restriction")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error checking restrictions for batch {self.batch_number}: {str(e)}")
            return False

class AllocationResult(NamedTuple):
    """Structured allocation result for type safety."""
    status: str  # 'fully_allocated', 'partially_allocated', or 'unfulfilled'
    weight: Decimal
    batches: List[Dict]

def allocate_fruits(stock_df: pd.DataFrame, orders: List[Dict], restrictions: Dict) -> Dict:
    """
    Allocate stock to orders using FIFO, respecting restrictions.

    Args:
        stock_df (pd.DataFrame): Stock data from Excel
        orders (List[Dict]): List of customer orders with Loading Date, Sales Document, etc.
        restrictions (Dict): Customer restrictions

    Returns:
        Dict: Allocation results per order

    Raises:
        ValidationError: If input data is invalid
    """
    try:
        # Validate input data
        if stock_df.empty:
            raise ValidationError("Stock data is empty")
        if not orders:
            raise ValidationError("No orders provided")

        # Convert stock to list of StockBatch objects, sorted by age (FIFO)
        try:
            stock_batches = [
                StockBatch(row) for _, row in 
                stock_df.sort_values('Real Stock Age', ascending=True).iterrows()  # True for proper FIFO
            ]
        except ValidationError as e:
            raise ValidationError(f"Error processing stock data: {str(e)}")

        allocations = {}
        remaining_stock = stock_batches.copy()

        for order in orders:
            try:
                sales_doc = str(order.get('sales_document', ''))
                material_desc = str(order.get('description_material', ''))
                required_weight = Decimal(str(order.get('quantity', 0)))
                loading_date = order.get('loading_date')
                sold_to_party = str(order.get('sold_to_party', ''))

                if not sales_doc or not material_desc or required_weight < 0:  # Allow zero quantity orders
                    logger.warning(f"Skipping invalid order: {json.dumps(order)}")
                    continue

                allocated_weight = Decimal('0')
                allocated_batches = []

                # Filter batches by material description and sort by age
                matching_batches = [
                    b for b in remaining_stock 
                    if b.matches_restrictions(restrictions)
                ]
                matching_batches.sort(key=lambda x: x.age)  # Ensure FIFO order

                for batch in matching_batches:
                    if allocated_weight >= required_weight:
                        break

                    available_weight = min(required_weight - allocated_weight, batch.weight)
                    if available_weight > 0:
                        allocated_weight += available_weight
                        batch.weight -= available_weight
                        allocated_batches.append({
                            "batch": batch.batch_number,
                            "weight": float(available_weight),  # Convert Decimal to float for JSON
                            "age": batch.age,
                            "location": batch.location,
                            "supplier": batch.supplier,
                            "quality": batch.quality,
                            "origin": batch.origin
                        })

                # Determine allocation status
                if allocated_weight > 0:
                    status = "fully_allocated" if allocated_weight >= required_weight else "partially_allocated"
                    allocations[sales_doc] = AllocationResult(
                        status=status,
                        weight=float(allocated_weight),
                        batches=allocated_batches
                    )._asdict()
                else:
                    allocations[sales_doc] = AllocationResult(
                        status="unfulfilled",
                        weight=0,
                        batches=[]
                    )._asdict()

                # Update remaining stock
                remaining_stock = [b for b in remaining_stock if b.weight > 0]

            except (ValueError, TypeError) as e:
                logger.error(f"Error processing order {order}: {str(e)}")
                allocations[sales_doc if 'sales_doc' in locals() else 'unknown'] = AllocationResult(
                    status="error",
                    weight=0,
                    batches=[]
                )._asdict()

        logger.info(f"Allocation completed successfully for {len(orders)} orders")
        return allocations

    except Exception as e:
        logger.error(f"Error in allocation process: {str(e)}")
        raise ValidationError(f"Allocation failed: {str(e)}")

if __name__ == "__main__":
    # Convert document data to DataFrame for testing
    stock_data = [
        {"Location": "", "Batch Number": "EX24000367", "Stock Weight": "0.008 KG", "Material ID": "FIARGRN", 
         "Real Stock Age": 23, "Variety": "BLUE RIBBON", "GGN": "4063061591012", "Origin Country": "Chile", 
         "Q3: Reinspection Quality": "", "BL/AWB/CMR": "27012025", "Allocation": "", "MinimumSize": 12, 
         "Origin Pallet Number": "FP00054676", "Supplier": "BERRY PACKING SERVICES BV"},
        {"Location": "", "Batch Number": "EX24000536", "Stock Weight": "361.056 KG", "Material ID": "FIARGRN", 
         "Real Stock Age": 14, "Variety": "LEGACY", "GGN": "4059883818772", "Origin Country": "Chile", 
         "Q3: Reinspection Quality": "", "BL/AWB/CMR": "5022025", "Allocation": "", "MinimumSize": 12, 
         "Origin Pallet Number": "FP00058910", "Supplier": "BERRY PACKING SERVICES BV"},
        # Continue for all 151 rows...
    ]
    stock_df = pd.DataFrame(stock_data)
    orders = [
        {"sales_document": "C1", "description_material": "FIARGRN", "quantity": 200},  # Example order
        {"sales_document": "C2", "description_material": "FIARORG", "quantity": 300}
    ]
    restrictions = {
        "quality": ["Good Q/S", "Fair M/C"],
        "origin": ["Chile"],
        "variety": ["LEGACY"],
        "ggn": "4063061591012",
        "supplier": ["HORTIFRUT CHILE S.A."]
    }
    try:
        result = allocate_fruits(stock_df, orders, restrictions)
        print("Allocation result:", json.dumps(result, indent=2))
    except ValidationError as e:
        print(f"Validation error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
