import requests

def test_upload_stock():
    url = 'http://localhost:5000/upload_stock'
    files = {'file': open('xlsx/StockAllocation.xlsx', 'rb')}
    response = requests.post(url, files=files)
    print("Stock Upload Response:", response.json())

def test_upload_orders():
    url = 'http://localhost:5000/upload_orders'
    files = {'file': open('xlsx/OrdersAllocation.xlsx', 'rb')}
    response = requests.post(url, files=files)
    print("Orders Upload Response:", response.json())

if __name__ == "__main__":
    print("Testing Stock Upload...")
    test_upload_stock()
    print("\nTesting Orders Upload...")
    test_upload_orders()
