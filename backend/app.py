from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from allocation_logic import allocate_fruits
from restrictions import load_restrictions
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend (adjust origins as needed)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log')
logger = logging.getLogger(__name__)

@app.route('/allocate', methods=['POST'])
def handle_allocation():
    """
    Handle POST requests to allocate fruit stock.

    Request JSON: {"stock": {"apples": 100}, "destinations": ["Store1"]}
    Response: JSON of allocation or error.
    """
    try:
        data = request.get_json()
        if not data or "stock" not in data or "destinations" not in data:
            return jsonify({"error": "Missing stock or destinations"}), 400

        stock = data["stock"]
        destinations = data["destinations"]
        restrictions = load_restrictions("customer_restrictions.json")

        allocation = allocate_fruits(stock, destinations, restrictions)
        logger.info(f"Successful allocation: {json.dumps(allocation, indent=2)}")
        return jsonify({"allocation": allocation}), 200

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
