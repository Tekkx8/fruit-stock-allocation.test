from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import logging
from logging.handlers import RotatingFileHandler
from allocation_logic import allocate_fruits
from restrictions import get_restrictions, Restriction
import openpyxl
from datetime import datetime
import tempfile
from werkzeug.utils import secure_filename
import hashlib
from pathlib import Path
from database import db

# Environment configuration
IS_DEVELOPMENT = os.getenv('FLASK_ENV', 'development') == 'development'
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3001')
PORT = int(os.getenv('PORT', 5001))

app = Flask(__name__)

# CORS configuration - allow localhost in development, use env var in production
if IS_DEVELOPMENT:
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
else:
    CORS(app, resources={
        r"/*": {
            "origins": [FRONTEND_URL],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fruit_allocation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Upload folder configuration
if os.getenv('RENDER'):
    app.config['UPLOAD_FOLDER'] = '/tmp'  # Use Render's temp directory
else:
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Debug mode in development
app.config['DEBUG'] = IS_DEVELOPMENT

ALLOWED_EXTENSIONS = {'xlsx'}

# Initialize SQLAlchemy with the app
db.init_app(app)

# Initialize the database
with app.app_context():
    db.create_all()

# Configure logging
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add file handler
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=1024*1024,
    backupCount=5
)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
app.logger.addHandler(file_handler)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_excel_columns(df, required_columns, file_type):
    """Validate that all required columns are present in the Excel file."""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in {file_type} file: {', '.join(missing_columns)}")

def secure_temp_file():
    """Create a secure temporary file with a random name."""
    random_suffix = hashlib.md5(os.urandom(32)).hexdigest()
    return Path(tempfile.gettempdir()) / f"temp_{random_suffix}.xlsx"

@app.route('/upload_stock', methods=['POST'])
def upload_stock():
    """Upload and validate stock Excel file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file format. Only .xlsx files are allowed"}), 400

        # Save with consistent name
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'stock.xlsx')
        try:
            file.save(temp_path)
            df = pd.read_excel(temp_path, engine='openpyxl')
            
            # Validate required columns
            required_columns = [
                'Location', 'Batch Number', 'Stock Weight', 'Material ID',
                'Real Stock Age', 'Variety', 'GGN', 'Origin Country',
                'Q3: Reinspection Quality', 'BL/AWB/CMR', 'Allocation',
                'MinimumSize', 'Origin Pallet Number', 'Supplier'
            ]
            validate_excel_columns(df, required_columns, 'stock')
            
            # Basic data validation
            if df.empty:
                raise ValueError("Stock file is empty")
            if df['Stock Weight'].isnull().any():
                raise ValueError("Stock Weight cannot be empty")
            
            app.logger.info(f"Stock file processed successfully: {len(df)} rows")
            return jsonify({"status": "success", "rows": len(df)}), 200
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
                
    except pd.errors.EmptyDataError:
        app.logger.error("Empty Excel file uploaded")
        return jsonify({"error": "The Excel file is empty"}), 400
    except pd.errors.ParserError as e:
        app.logger.error(f"Excel parsing error: {str(e)}")
        return jsonify({"error": "Invalid Excel file format"}), 400
    except ValueError as e:
        app.logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error in upload_stock: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/upload_orders', methods=['POST'])
def upload_orders():
    """Upload and validate orders Excel file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file format. Only .xlsx files are allowed"}), 400

        # Save with consistent name
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'orders.xlsx')
        try:
            file.save(temp_path)
            df = pd.read_excel(temp_path, engine='openpyxl')
            
            # Validate required columns
            required_columns = [
                'Loading Date', 'Sales Document Item', 'Sales Document',
                'Order', 'Sold-to Party', 'Description material', 'Quantity KG'
            ]
            validate_excel_columns(df, required_columns, 'orders')
            
            # Basic data validation
            if df.empty:
                raise ValueError("Orders file is empty")
            if df['Quantity KG'].isnull().any():
                raise ValueError("Quantity cannot be empty")
            if (df['Quantity KG'] < 0).any():
                raise ValueError("Quantity cannot be negative")
            
            orders = [{
                "loading_date": row['Loading Date'].strftime('%Y-%m-%d') if pd.notnull(row['Loading Date']) else None,
                "sales_document": str(row['Sales Document']),
                "sold_to_party": str(row['Sold-to Party']),
                "description_material": str(row['Description material']),
                "quantity": float(row['Quantity KG'])
            } for _, row in df.iterrows()]
            
            app.logger.info(f"Orders file processed successfully: {len(orders)} orders")
            return jsonify({"status": "success", "orders": len(orders)}), 200
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
                
    except pd.errors.EmptyDataError:
        app.logger.error("Empty Excel file uploaded")
        return jsonify({"error": "The Excel file is empty"}), 400
    except pd.errors.ParserError as e:
        app.logger.error(f"Excel parsing error: {str(e)}")
        return jsonify({"error": "Invalid Excel file format"}), 400
    except ValueError as e:
        app.logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error in upload_orders: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/allocate', methods=['POST'])
def allocate():
    """Allocate stock based on orders and restrictions."""
    try:
        # Get the latest uploaded files from temp storage
        stock_file = os.path.join(app.config['UPLOAD_FOLDER'], 'stock.xlsx')
        orders_file = os.path.join(app.config['UPLOAD_FOLDER'], 'orders.xlsx')
        
        if not (os.path.exists(stock_file) and os.path.exists(orders_file)):
            return jsonify({"error": "Please upload both stock and orders files first"}), 400

        # Read the Excel files
        stock_df = pd.read_excel(stock_file)
        orders_df = pd.read_excel(orders_file)
        
        # Get default restrictions
        restrictions = get_restrictions("default")

        # Ensure column names match stock data
        stock_df.columns = [col.strip() for col in stock_df.columns]
        stock_df['Stock Weight'] = stock_df['Stock Weight'].apply(
            lambda x: float(str(x).split()[0]) if isinstance(x, str) else float(x)
        )
        stock_df['Real Stock Age'] = stock_df['Real Stock Age'].astype(int)

        # Convert orders DataFrame to list of dictionaries
        orders = []
        for _, row in orders_df.iterrows():
            order = {
                "loading_date": row['Loading Date'].strftime('%Y-%m-%d') if pd.notnull(row['Loading Date']) else None,
                "sales_document": str(row['Order Number']),
                "sold_to_party": str(row['Customer']),
                "description_material": str(row['Material ID']),
                "quantity": float(row['Order Weight'])
            }
            orders.append(order)

        # Perform allocation
        allocation = allocate_fruits(stock_df, orders, restrictions)
        
        return jsonify({"allocation": allocation}), 200

    except Exception as e:
        app.logger.error(f"Error during allocation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_restrictions', methods=['GET'])
def get_restrictions_endpoint():
    """Retrieve customer restrictions from SQLite."""
    customer_id = request.args.get('customer_id', 'default')
    restrictions = get_restrictions(customer_id)
    return jsonify({"restrictions": restrictions}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=PORT)
