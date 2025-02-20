from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Database configuration (SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restrictions.db"
db = SQLAlchemy(app)

# Configure CORS (Only allow frontend)
CORS(app, origins=["http://localhost:3001"])

# Logging setup
logging.basicConfig(filename="app.log", level=logging.INFO)

# Allowed file types
ALLOWED_EXTENSIONS = {"xlsx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Column mapping for handling variations in uploaded files
COLUMN_MAPPING_ORDERS = {
    "Sales Document": "Order",
    "Sold-to Party": "Customer ID",
    "Quantity KG": "Quantity"
}

COLUMN_MAPPING_STOCK = {
    "Origin Country": "Origin",
    "Q3: Reinspection Quality": "Quality"
}

def rename_columns(df, mapping):
    return df.rename(columns=lambda col: mapping.get(col, col))

@app.route('/upload_orders', methods=['POST'])
def upload_orders():
    if 'orders_file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400

    file = request.files['orders_file']
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Invalid file format. Only .xlsx allowed"}), 400

    try:
        df = pd.read_excel(file)
        df = rename_columns(df, COLUMN_MAPPING_ORDERS)

        # Prioritize "Order" column, fallback to "Sales Document"
        if "Order" not in df.columns and "Sales Document" in df.columns:
            df = df.rename(columns={"Sales Document": "Order"})

        return jsonify({"success": True, "orders": df.to_dict(orient="records")})
    except Exception as e:
        logging.error(f"Error processing orders file: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/upload_stock', methods=['POST'])
def upload_stock():
    if 'stock_file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400

    file = request.files['stock_file']
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Invalid file format. Only .xlsx allowed"}), 400

    try:
        stock_df = pd.read_excel(file)
        stock_df = rename_columns(stock_df, COLUMN_MAPPING_STOCK)

        # Remove stock entries with weight < 0.01 KG
        stock_df = stock_df[stock_df["Stock Weight"] >= 0.01]

        return jsonify({"success": True, "stock": stock_df.to_dict(orient="records")})
    except Exception as e:
        logging.error(f"Error processing stock file: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
