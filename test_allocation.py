import pandas as pd
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from allocation_logic import allocate_fruits
import json

def test_allocation():
    print("Loading stock file...")
    stock_df = pd.read_excel('xlsx/StockAllocation.xlsx')
    print(f"Loaded {len(stock_df)} stock records")
    
    print("\nLoading orders file...")
    orders_df = pd.read_excel('xlsx/OrdersAllocation.xlsx')
    print(f"Loaded {len(orders_df)} orders")
    
    # Convert orders DataFrame to list of dictionaries
    orders = []
    for _, row in orders_df.iterrows():
        order = {
            "loading_date": row['Loading Date'].strftime('%Y-%m-%d') if pd.notnull(row['Loading Date']) else None,
            "sales_document": str(row['Sales Document']),
            "sold_to_party": str(row['Sold-to Party']),
            "description_material": str(row['Description material']),
            "quantity": float(row['Quantity KG'])
        }
        orders.append(order)
    
    print("\nStarting allocation...")
    # For testing, we'll use empty restrictions
    restrictions = {}
    
    try:
        results = allocate_fruits(stock_df, orders, restrictions)
        
        print("\nAllocation Results Summary:")
        print(f"Total orders processed: {len(results)}")
        
        status_counts = {
            'fully_allocated': 0,
            'partially_allocated': 0,
            'unfulfilled': 0,
            'error': 0
        }
        
        total_allocated_weight = 0
        total_requested_weight = sum(order['quantity'] for order in orders)
        
        for sales_doc, allocation in results.items():
            status_counts[allocation['status']] += 1
            total_allocated_weight += allocation['weight']
            
            print(f"\nOrder {sales_doc}:")
            print(f"Status: {allocation['status']}")
            print(f"Allocated Weight: {allocation['weight']:.2f} KG")
            print(f"Number of batches used: {len(allocation['batches'])}")
            
            if allocation['batches']:
                print("First batch details:")
                first_batch = allocation['batches'][0]
                print(f"- Batch Number: {first_batch['batch']}")
                print(f"- Weight: {first_batch['weight']:.2f} KG")
                print(f"- Age: {first_batch['age']} days")
                print(f"- Location: {first_batch['location']}")
                print(f"- Supplier: {first_batch['supplier']}")
        
        print("\nFinal Statistics:")
        print(f"Total Requested Weight: {total_requested_weight:.2f} KG")
        print(f"Total Allocated Weight: {total_allocated_weight:.2f} KG")
        print(f"Allocation Rate: {(total_allocated_weight/total_requested_weight)*100:.1f}%")
        print("\nOrder Status Breakdown:")
        for status, count in status_counts.items():
            print(f"{status}: {count} orders")
            
    except Exception as e:
        print(f"Error during allocation: {str(e)}")

if __name__ == "__main__":
    test_allocation()
