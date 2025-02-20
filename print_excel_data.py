import pandas as pd
import os

EXCEL_DIR = r"C:\Users\adria\CascadeProjects\windsurf-project\backend\xlsx"

def print_excel_contents(filename):
    filepath = os.path.join(EXCEL_DIR, filename)
    print(f"\n=== Contents of {filename} ===")
    df = pd.read_excel(filepath, engine='openpyxl')
    print("\nColumns:")
    print(df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head().to_string())
    print("\nData Info:")
    print(df.info())
    print("\nValue counts for numeric columns:")
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        print(f"\n{col} - Unique values:")
        print(df[col].value_counts().head())

try:
    print_excel_contents("StockAllocation.xlsx")
    print("\n" + "="*50 + "\n")
    print_excel_contents("OrdersAllocation.xlsx")
except Exception as e:
    print(f"Error reading files: {str(e)}")
