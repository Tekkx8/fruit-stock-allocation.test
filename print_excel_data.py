import pandas as pd
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_stock_excel(file_path: str) -> pd.DataFrame:
    """Read stock data from Excel file."""
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Read stock data: {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error reading stock Excel: {str(e)}")
        raise

def read_orders_excel(file_path: str) -> List[Dict]:
    """Read customer orders from Excel file."""
    try:
        df = pd.read_excel(file_path)
        orders = df.to_dict('records')
        logger.info(f"Read orders data: {len(orders)} orders")
        return [{
            "customer_id": row.get('CustomerID', 'default'),
            "fruit": row.get('Material ID', ''),
            "quantity": float(row.get('Quantity', 0))
        } for row in orders]
    except Exception as e:
        logger.error(f"Error reading orders Excel: {str(e)}")
        raise

if __name__ == "__main__":
    stock_df = read_stock_excel("stock.xlsx")
    orders = read_orders_excel("orders.xlsx")
    print(stock_df.head())
    print(orders)
