import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getRestrictions, setRestrictions } from '../api/client';
import { toast } from 'react-toastify';

const defaultRestrictions = {
  quality: ["Good Q/S", "Fair M/C"],
  origin: ["Chile"],
  variety: ["LEGACY"],
  ggn: null,
  supplier: []
};

export const useRestrictions = (customerId = 'default') => {
  const queryClient = useQueryClient();
  const queryKey = ['restrictions', customerId];

  const {
    data: restrictions,
    isLoading,
    error,
  } = useQuery(queryKey, () => getRestrictions(customerId), {
    staleTime: 5 * 60 * 1000,
    cacheTime: 10 * 60 * 1000,
    retry: 2,
    onError: (error) => {
      console.error('Error fetching restrictions:', error);
      toast.error('Failed to load restrictions. Using default values.');
    },
    initialData: defaultRestrictions
  });

  const { mutate: updateRestrictions } = useMutation(
    (newRestrictions) => setRestrictions(customerId, newRestrictions),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(queryKey);
        toast.success('Restrictions updated successfully');
      },
      onError: (error) => {
        console.error('Error updating restrictions:', error);
        toast.error('Failed to update restrictions');
      }
    }
  );

  return {
    restrictions: restrictions || defaultRestrictions,
    isLoading,
    error,
    updateRestrictions,
  };
};
