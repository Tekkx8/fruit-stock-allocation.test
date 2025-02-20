from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import logging
from allocation_logic import allocate_fruits
from restrictions import get_restrictions
import openpyxl
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restrictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')
logger = logging.getLogger(__name__)

# SQLite Model for Restrictions
class Restriction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False)
    quality = db.Column(db.String(100))
    origin = db.Column(db.String(50))
    variety = db.Column(db.String(50))
    ggn = db.Column(db.String(50))
    supplier = db.Column(db.String(100))

    def __repr__(self):
        return f"<Restriction {self.customer_id}>"

with app.app_context():
    db.create_all()

@app.route('/upload_stock', methods=['POST'])
def upload_stock():
    """Upload stock Excel file and process it."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.xlsx'):
        try:
            filename = f"temp_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file.save(filename)
            df = pd.read_excel(filename, engine='openpyxl')
            # Ensure column names match document
            df.columns = [col.strip() for col in df.columns]  # Clean column names
            logger.info(f"Stock uploaded: {len(df)} rows")
            os.remove(filename)  # Clean up temporary file
            return jsonify({"status": "success", "rows": len(df)}), 200
        except Exception as e:
            logger.error(f"Error uploading stock: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Invalid file format"}), 400

@app.route('/upload_orders', methods=['POST'])
def upload_orders():
    """Upload orders Excel file and process customer orders."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.xlsx'):
        try:
            filename = f"temp_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file.save(filename)
            df = pd.read_excel(filename, engine='openpyxl')
            orders = [{
                "customer_id": row.get('CustomerID', 'default'),
                "fruit": row.get('Material ID', ''),
                "quantity": float(row.get('Quantity', 0))
            } for _, row in df.iterrows()]
            logger.info(f"Orders uploaded: {len(orders)} orders")
            os.remove(filename)
            return jsonify({"status": "success", "orders": len(orders)}), 200
        except Exception as e:
            logger.error(f"Error uploading orders: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Invalid file format"}), 400

@app.route('/allocate_stock', methods=['POST'])
def allocate_stock():
    """Allocate stock based on orders and restrictions."""
    try:
        data = request.get_json()
        if not data or "stock_file" not in data or "orders" not in data:
            return jsonify({"error": "Missing stock or orders"}), 400

        # Assume stock_file is a path or DataFrame; for simplicity, use uploaded data
        stock_df = pd.read_excel(data["stock_file"]) if isinstance(data["stock_file"], str) else data["stock_file"]
        orders = data["orders"]
        customer_id = data.get("customer_id", "default")
        restrictions = get_restrictions(customer_id)

        # Ensure column names match stock data
        stock_df.columns = [col.strip() for col in stock_df.columns]
        stock_df['Stock Weight'] = stock_df['Stock Weight'].apply(lambda x: float(str(x).split()[0]) if isinstance(x, str) else float(x))
        stock_df['Real Stock Age'] = stock_df['Real Stock Age'].astype(int)

        allocation = allocate_fruits(stock_df, orders, restrictions)
        logger.info(f"Stock allocated: {json.dumps(allocation, indent=2)}")
        return jsonify({"allocation": allocation}), 200

    except Exception as e:
        logger.error(f"Allocation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_restrictions', methods=['GET'])
def get_restrictions_endpoint():
    """Retrieve customer restrictions from SQLite."""
    customer_id = request.args.get('customer_id', 'default')
    restrictions = get_restrictions(customer_id)
    return jsonify({"restrictions": restrictions}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
