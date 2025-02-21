import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from 'react-query';
import { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import FruitAllocatorUI from './FruitAllocatorUI';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

const queryClient = new QueryClient();

function App() {
  const [allocation, setAllocation] = useState(null);
  const [error, setError] = useState(null);

  const fetchRestrictions = useQuery('restrictions', () => 
    fetch('https://fruit-stock-allocation.onrender.com/get_restrictions?customer_id=default').then(res => res.json())
  );

  const allocateMutation = useMutation(data => 
    fetch('https://fruit-stock-allocation.onrender.com/allocate_stock', {
      method: 'POST',
      body: data,
    }).then(res => res.json()), {
      onSuccess: (data) => setAllocation(data.allocation),
      onError: (err) => setError(err.message),
    });

  const handleAllocate = (allocationData) => {
    const formData = new FormData();
    for (let key in allocationData) {
      formData.append(key, allocationData[key]);
    }
    allocateMutation.mutate(formData);
  };

  return (
    <div className="App">
      {error && <div className="error">Error: {error}</div>}
      {fetchRestrictions.isLoading ? <div>Loading restrictions...</div> : 
        <FruitAllocatorUI onAllocate={handleAllocate} allocation={allocation} />}
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
);

export default App;
