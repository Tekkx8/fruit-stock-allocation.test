import React, { useReducer, useState } from "react";
import { Alert, Spinner } from "react-bootstrap";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:5000";

// Reducer function to manage customers state
const customerReducer = (state, action) => {
  switch (action.type) {
    case "SET_CUSTOMERS":
      return action.payload;
    case "UPDATE_RESTRICTIONS":
      return state.map((customer) =>
        customer.id === action.customerId
          ? {
              ...customer,
              order_types: {
                ...customer.order_types,
                [action.orderType]: {
                  ...customer.order_types[action.orderType],
                  restrictions: action.restrictions,
                },
              },
            }
          : customer
      );
    default:
      return state;
  }
};

const FruitAllocatorUI = () => {
  const [customers, dispatch] = useReducer(customerReducer, []);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Enhanced fetch function with retry logic
  const fetchWithRetry = async (url, options, retries = 3, delay = 1000) => {
    for (let i = 0; i < retries; i++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const response = await fetch(url, { ...options, signal: controller.signal });

        clearTimeout(timeoutId);
        if (!response.ok) throw new Error("Server error. Please try again.");

        return await response.json();
      } catch (err) {
        if (i === retries - 1) throw err;
        await new Promise((resolve) => setTimeout(resolve, delay * (i + 1)));
      }
    }
  };

  // File Upload Handler
  const handleFileUpload = async (file, endpoint) => {
    setError(null); // Clear previous errors
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const data = await fetchWithRetry(`${API_BASE_URL}/${endpoint}`, {
        method: "POST",
        body: formData,
      });

      console.log("Upload successful:", data);
    } catch (err) {
      setError("Upload failed. " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Get order number (prioritize "Order", fallback to "Sales Document")
  const getOrderNumber = (order) => {
    return order["Order"] || order["Sales Document"] || "N/A";
  };

  return (
    <div className="container">
      <h2>Fruit Stock Allocation</h2>

      {/* Error Message */}
      {error && <Alert variant="danger">{error}</Alert>}

      {/* File Upload Buttons */}
      <input
        type="file"
        onChange={(e) => handleFileUpload(e.target.files[0], "upload_orders")}
      />
      <input
        type="file"
        onChange={(e) => handleFileUpload(e.target.files[0], "upload_stock")}
      />

      {/* Loading Indicator */}
      {isLoading && <Spinner animation="border" />}

      {/* Display Customers */}
      <table className="table">
        <thead>
          <tr>
            <th>Customer</th>
            <th>Order</th>
            <th>Restrictions</th>
          </tr>
        </thead>
        <tbody>
          {customers.map((customer) => (
            <tr key={customer.id}>
              <td>{customer.id}</td>
              <td>{getOrderNumber(customer)}</td>
              <td>{JSON.stringify(customer.order_types)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FruitAllocatorUI;
