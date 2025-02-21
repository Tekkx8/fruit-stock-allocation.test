import { useMutation } from 'react-query';
import { allocateStock } from '../api/client';

export function useAllocation() {
  const mutation = useMutation(
    async ({ stockFile, ordersFile }) => {
      return allocateStock(stockFile, ordersFile);
    },
    {
      onError: (error) => {
        console.error('Error during allocation:', error);
      },
    }
  );

  return {
    allocate: mutation.mutate,
    isAllocating: mutation.isLoading,
    allocation: mutation.data?.allocation,
    error: mutation.error,
    reset: mutation.reset,
  };
}
