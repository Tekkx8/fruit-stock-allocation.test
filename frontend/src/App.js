import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import FruitAllocatorUI from './FruitAllocatorUI';
import './App.css';

// Create a client with better error handling and caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // Data stays fresh for 5 minutes
      cacheTime: 10 * 60 * 1000, // Cache persists for 10 minutes
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
      suspense: false,
    },
  },
});

// Error boundary component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Application error:', error);
    console.error('Error info:', errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message || 'An unexpected error occurred'}</p>
          <button
            onClick={() => {
              this.setState({ hasError: false });
              window.location.reload();
            }}
          >
            Reload Application
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  const [darkMode, setDarkMode] = useState(false);

  const toggleTheme = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark', !darkMode);
  };

  return (
    <div className={`min-h-screen flex ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-black'}`}>
      <aside className="w-64 bg-gray-800 text-white p-4">
        <h2 className="text-xl font-bold mb-4">Navigation</h2>
        <ul>
          <li className="mb-2"><a href="#" className="hover:underline">Dashboard</a></li>
          <li className="mb-2"><a href="#" className="hover:underline">Settings</a></li>
          <li className="mb-2"><a href="#" className="hover:underline">Profile</a></li>
        </ul>
        <button onClick={toggleTheme} className="mt-4 p-2 bg-blue-500 rounded">Toggle {darkMode ? 'Light' : 'Dark'} Mode</button>
      </aside>
      <main className="flex-1 p-8">
        <QueryClientProvider client={queryClient}>
          <ErrorBoundary>
            <FruitAllocatorUI />
          </ErrorBoundary>
          <ReactQueryDevtools initialIsOpen={false} />
          <ToastContainer position="bottom-right" />
        </QueryClientProvider>
      </main>
    </div>
  );
}

export default App;
