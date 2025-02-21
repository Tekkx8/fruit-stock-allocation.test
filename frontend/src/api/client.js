import axios from 'axios';

// Create axios instance with default config
const isDevelopment = process.env.NODE_ENV === 'development';
const API_BASE_URL = isDevelopment 
  ? 'http://localhost:5001'  // Development default
  : (process.env.REACT_APP_API_URL || 'http://localhost:5001'); // Production from env

console.log('Current environment:', process.env.NODE_ENV);
console.log('API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

// Request interceptor for API calls
api.interceptors.request.use(
  (config) => {
    // You could add auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for API calls
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const handleError = (error) => {
      const errorMessage =
        error.response?.data?.error ||
        error.message ||
        'An unexpected error occurred';
      throw new Error(errorMessage);
    };
    return handleError(error);
  }
);

export const uploadStock = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload_stock', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    const handleError = (error) => {
      const errorMessage =
        error.response?.data?.error ||
        error.message ||
        'Error uploading stock file';
      throw new Error(errorMessage);
    };
    throw handleError(error);
  }
};

export const uploadOrders = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload_orders', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    const handleError = (error) => {
      const errorMessage =
        error.response?.data?.error ||
        error.message ||
        'Error uploading orders file';
      throw new Error(errorMessage);
    };
    throw handleError(error);
  }
};

export const allocateStock = async (stockFile, ordersFile) => {
  try {
    // First upload the stock file
    const stockUploadResponse = await uploadStock(stockFile);
    
    // Then upload the orders file
    const ordersUploadResponse = await uploadOrders(ordersFile);
    
    // Finally, trigger allocation
    const response = await api.post('/allocate', {}, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return response;
  } catch (error) {
    const handleError = (error) => {
      const errorMessage =
        error.response?.data?.error ||
        error.message ||
        'An unexpected error occurred during allocation';
      throw new Error(errorMessage);
    };
    return handleError(error);
  }
};

export const getRestrictions = async (customerId = 'default') => {
  try {
    const response = await api.get(`/get_restrictions?customer_id=${customerId}`);
    if (!response.restrictions) {
      console.warn('No restrictions data in response:', response);
      return {
        quality: ["Good Q/S", "Fair M/C"],
        origin: ["Chile"],
        variety: ["LEGACY"],
        ggn: null,
        supplier: []
      };
    }
    return response.restrictions;
  } catch (error) {
    console.error('Error fetching restrictions:', error);
    const errorMessage =
      error.response?.data?.error ||
      error.message ||
      'Error fetching restrictions';
    throw new Error(errorMessage);
  }
};

export const setRestrictions = async (customerId, restrictions) => {
  try {
    return await api.post('/set_restrictions', {
      customer_id: customerId,
      restrictions,
    });
  } catch (error) {
    const handleError = (error) => {
      const errorMessage =
        error.response?.data?.error ||
        error.message ||
        'Error setting restrictions';
      throw new Error(errorMessage);
    };
    throw handleError(error);
  }
};

export const deleteRestrictions = async (customerId) => {
  try {
    return await api.delete(`/restrictions/${customerId}`);
  } catch (error) {
    const handleError = (error) => {
      const errorMessage =
        error.response?.data?.error ||
        error.message ||
        'Error deleting restrictions';
      throw new Error(errorMessage);
    };
    throw handleError(error);
  }
};
