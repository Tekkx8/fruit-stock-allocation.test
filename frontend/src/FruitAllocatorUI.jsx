import React, { useCallback } from 'react';
import { useRestrictions } from './hooks/useRestrictions';
import { useAllocation } from './hooks/useAllocation';
import { useFileUpload } from './hooks/useFileUpload';
import './FruitAllocatorUI.css';

function FileUpload({
  label,
  file,
  error,
  getRootProps,
  getInputProps,
  isDragActive,
  onClear,
}) {
  return (
    <div className="file-upload">
      <label>{label}</label>
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${error ? 'error' : ''}`}
        role="button"
        aria-label={`Upload ${label}`}
        tabIndex="0"
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          {file ? (
            <>
              <span className="file-name">{file.name}</span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onClear();
                }}
                className="clear-button"
                aria-label="Clear file"
              >
                ×
              </button>
            </>
          ) : (
            <span>
              {isDragActive
                ? 'Drop the file here'
                : `Drag and drop ${label} Excel file or click to select`}
            </span>
          )}
        </div>
      </div>
      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}
    </div>
  );
}

function RestrictionSelect({
  label,
  value,
  options,
  onChange,
  isDisabled,
  className = '',
}) {
  return (
    <div className={`restriction-select ${className}`}>
      <label htmlFor={`select-${label}`}>{label}:</label>
      <select
        id={`select-${label}`}
        value={Array.isArray(value) ? value.join(',') : value}
        onChange={(e) => onChange(e.target.value.split(','))}
        disabled={isDisabled}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

function AllocationResults({ allocation, onClose }) {
  if (!allocation) return null;

  return (
    <div
      className="allocation-result"
      role="region"
      aria-label="Allocation Results"
    >
      <div className="result-header">
        <h3>Allocation Results</h3>
        <button
          type="button"
          onClick={onClose}
          className="close-button"
          aria-label="Close results"
        >
          ×
        </button>
      </div>
      <div className="result-content">
        {Object.entries(allocation).map(([customer, data]) => (
          <div key={customer} className="customer-allocation">
            <h4>Customer: {customer}</h4>
            <p>
              Status: {' '}
              <span className={`status-${data.status}`}>{data.status}</span>
            </p>
            <p>Allocated Weight: {data.weight} KG</p>
            {data.batches && data.batches.length > 0 && (
              <div className="batches">
                <h5>Allocated Batches:</h5>
                <ul>
                  {data.batches.map((batch, index) => (
                    <li key={index}>
                      Batch {batch.id} - {batch.weight} KG 
                      (Age: {batch.age} days)
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function FruitAllocatorUI() {
  const {
    restrictions,
    isLoading: isLoadingRestrictions,
    error: restrictionsError,
    updateRestrictions,
  } = useRestrictions();

  const {
    allocate,
    isAllocating,
    allocation,
    error: allocationError,
    reset: resetAllocation,
  } = useAllocation();

  const stockUpload = useFileUpload();
  const ordersUpload = useFileUpload();

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      if (!stockUpload.file || !ordersUpload.file) {
        return;
      }

      try {
        await allocate({
          stockFile: stockUpload.file,
          ordersFile: ordersUpload.file,
        });
      } catch (error) {
        console.error('Allocation failed:', error);
      }
    },
    [stockUpload.file, ordersUpload.file, allocate]
  );

  const handleRestrictionChange = useCallback(
    (field, value) => {
      const newRestrictions = {
        ...restrictions,
        [field]: value,
      };
      updateRestrictions(newRestrictions);
    },
    [restrictions, updateRestrictions]
  );

  if (isLoadingRestrictions) {
    return <div className="loading">Loading...</div>;
  }

  if (restrictionsError) {
    return (
      <div className="error-state" role="alert">
        Error loading restrictions: {restrictionsError.message}
      </div>
    );
  }

  return (
    <div className="fruit-allocator" role="main">
      <form onSubmit={handleSubmit}>
        <h2>Fruit Stock Allocation</h2>

        <div className="upload-section">
          <h3>Upload Files</h3>
          <FileUpload
            label="Stock"
            file={stockUpload.file}
            error={stockUpload.error}
            getRootProps={stockUpload.getRootProps}
            getInputProps={stockUpload.getInputProps}
            isDragActive={stockUpload.isDragActive}
            onClear={stockUpload.clear}
          />
          <FileUpload
            label="Orders"
            file={ordersUpload.file}
            error={ordersUpload.error}
            getRootProps={ordersUpload.getRootProps}
            getInputProps={ordersUpload.getInputProps}
            isDragActive={ordersUpload.isDragActive}
            onClear={ordersUpload.clear}
          />
        </div>

        <div className="restrictions-section">
          <h3>Restrictions</h3>
          <RestrictionSelect
            label="Quality"
            value={restrictions?.quality || []}
            options={[
              { value: 'Good Q/S,Fair M/C', label: 'Good Q/S, Fair M/C' },
              { value: 'Poor M/C', label: 'Poor M/C' },
            ]}
            onChange={(value) => handleRestrictionChange('quality', value)}
            isDisabled={isAllocating}
          />
          <RestrictionSelect
            label="Origin"
            value={restrictions?.origin || []}
            options={[
              { value: 'Chile', label: 'Chile' },
              { value: 'Peru', label: 'Peru' },
            ]}
            onChange={(value) => handleRestrictionChange('origin', value)}
            isDisabled={isAllocating}
          />
          <RestrictionSelect
            label="Variety"
            value={restrictions?.variety || []}
            options={[
              { value: 'LEGACY', label: 'Legacy' },
              { value: 'BLUE RIBBON', label: 'Blue Ribbon' },
            ]}
            onChange={(value) => handleRestrictionChange('variety', value)}
            isDisabled={isAllocating}
          />
        </div>

        {allocationError && (
          <div className="error-message" role="alert">
            {allocationError.message}
          </div>
        )}

        <button
          type="submit"
          disabled={!stockUpload.file || !ordersUpload.file || isAllocating}
          className="submit-button"
        >
          {isAllocating ? 'Allocating...' : 'Allocate'}
        </button>
      </form>

      {allocation && (
        <AllocationResults
          allocation={allocation}
          onClose={() => {
            resetAllocation();
            stockUpload.clear();
            ordersUpload.clear();
          }}
        />
      )}
    </div>
  );
}

export default FruitAllocatorUI;
