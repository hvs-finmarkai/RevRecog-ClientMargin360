import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getContracts,
  getContract,
  createContract,
  uploadContract,
  ContractFilters,
  CreateContractPayload,
} from '../services/api/contracts';

export function useContracts(filters?: ContractFilters) {
  return useQuery({
    queryKey: ['contracts', filters],
    queryFn: () => getContracts(filters),
    staleTime: 30000,
  });
}

export function useContract(id: string) {
  return useQuery({
    queryKey: ['contract', id],
    queryFn: () => getContract(id),
    enabled: !!id,
  });
}

export function useCreateContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateContractPayload) => createContract(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}

export function useUploadContract() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadContract(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts'] });
    },
  });
}
