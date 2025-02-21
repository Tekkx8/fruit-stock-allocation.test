import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import './FruitAllocatorUI.css';

function FruitAllocatorUI({ onAllocate, allocation }) {
  const [stockFile, setStockFile] = useState(null);
  const [ordersFile, setOrdersFile] = useState(null);
  const [restrictions, setRestrictions] = useState({
    quality: ['Good Q/S', 'Fair M/C'],
    origin: ['Chile'],
    variety: ['LEGACY'],
    ggn: '4063061591012',
    supplier: ['HORTIFRUT CHILE S.A.'],
  });

  const { getRootProps: getStockProps, getInputProps: getStockInputProps } =
    useDropzone({
      onDrop: (acceptedFiles) => setStockFile(acceptedFiles[0]),
    });

  const { getRootProps: getOrdersProps, getInputProps: getOrdersInputProps } =
    useDropzone({
      onDrop: (acceptedFiles) => setOrdersFile(acceptedFiles[0]),
    });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!stockFile || !ordersFile) {
      alert('Please upload both stock and orders files.');
      return;
    }

    const formData = new FormData();
    formData.append('stock_file', stockFile);
    formData.append('orders_file', ordersFile);

    const response = await fetch('http://localhost:5000/allocate_stock', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    onAllocate(data.allocation);
  };

  const updateRestriction = (field, value) => {
    const updatedRestrictions = { ...restrictions, [field]: value };
    setRestrictions(updatedRestrictions);

    fetch('http://localhost:5000/set_restrictions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer_id: 'default',
        restrictions: updatedRestrictions,
      }),
    });
  };

  return (
    <div className="fruit-allocator" aria-label="Fruit Stock Allocator">
      <form onSubmit={handleSubmit}>
        <h2>Fruit Stock Allocation</h2>

        <div>
          <h3>Upload Files</h3>
          <div {...getStockProps()} className="dropzone">
            <input {...getStockInputProps()} />
            {stockFile
              ? stockFile.name
              : 'Drag and drop stock Excel file or click to select'}
          </div>
          <div {...getOrdersProps()} className="dropzone">
            <input {...getOrdersInputProps()} />
            {ordersFile
              ? ordersFile.name
              : 'Drag and drop orders Excel file or click to select'}
          </div>
        </div>

        <h3>Restrictions</h3>
        <div>
          <label>Quality:</label>
          <select
            value={restrictions.quality.join(',')}
            onChange={(e) =>
              updateRestriction('quality', e.target.value.split(','))
            }
          >
            <option value="Good Q/S,Fair M/C">Good Q/S, Fair M/C</option>
            <option value="Poor M/C">Poor M/C</option>
          </select>
        </div>

        <button type="submit">Allocate</button>
      </form>

      {allocation && (
        <div className="allocation-result" aria-live="polite">
          <h3>Allocation Results:</h3>
          {Object.entries(allocation).map(([customer, data]) => (
            <div key={customer}>
              {customer}: {data.status === 'fully_allocated' && '✅'}
              {data.status === 'partially_allocated' && '⚠️'}
              {data.status === 'unfulfilled' && '❌'}
              Weight: {data.weight} KG, Batches: {JSON.stringify(data.batches)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FruitAllocatorUI;
