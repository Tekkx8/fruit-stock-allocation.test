import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

def apply_restrictions(stock_df, restrictions):
    if not restrictions:
        return stock_df

    conditions = [
        stock_df[field].astype(str).isin([str(v) for v in values])
        for field, values in restrictions.items() if values
    ]
    
    if conditions:
        stock_df = stock_df[np.logical_and.reduce(conditions)]
    
    return stock_df

def allocate_stock(customers, stock_df):
    stock_df = stock_df.sort_values('real stock age', ascending=True)  # FIFO ordering

    allocations = []
    for customer in customers:
        customer_restrictions = customer.get("restrictions", {})
        filtered_stock = apply_restrictions(stock_df, customer_restrictions)
        
        if filtered_stock.empty:
            logging.warning(f"No stock found for Customer {customer['id']} with restrictions: {customer['restrictions']}")
            continue  # Skip this customer
        
        allocated_stock = filtered_stock.iloc[0].to_dict()
        allocations.append({"customer_id": customer["id"], "allocated_stock": allocated_stock})
        stock_df.drop(index=filtered_stock.index[0], inplace=True)  # Remove allocated stock
    
    return allocations
