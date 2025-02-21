import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

export function useFileUpload() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles && rejectedFiles.length > 0) {
      setError('Please upload a valid Excel file');
      return;
    }

    const uploadedFile = acceptedFiles[0];
    if (!uploadedFile) {
      setError('No file selected');
      return;
    }

    if (uploadedFile.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setFile(uploadedFile);
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': [
        '.xlsx',
      ],
    },
    maxFiles: 1,
  });

  const clearFile = useCallback(() => {
    setFile(null);
    setError(null);
  }, []);

  return {
    file,
    error,
    getRootProps,
    getInputProps,
    isDragActive,
    clearFile,
  };
}
