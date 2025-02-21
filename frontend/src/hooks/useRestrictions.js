import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getRestrictions, setRestrictions } from '../api/client';

const defaultRestrictions = {
  quality: [],
  origin: [],
  variety: [],
  ggn: '',
  supplier: [],
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
  });

  const { mutate: updateRestrictions } = useMutation(
    (newRestrictions) => setRestrictions(customerId, newRestrictions),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(queryKey);
      },
    }
  );

  return {
    restrictions: restrictions || defaultRestrictions,
    isLoading,
    error,
    updateRestrictions,
  };
};
