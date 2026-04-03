import { api } from './client';
import type { CreateRequestData, RequestStatus, TripRequest } from '../../types';

type PaginatedTripRequestResponse = {
  items: TripRequest[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export const requestsApi = {
  getMyRequests: async (status?: RequestStatus): Promise<TripRequest[]> => {
    const response = await api.get<PaginatedTripRequestResponse>('/requests/my', {
      params: status ? { status } : undefined,
    });
    return response.data.items;
  },

  getDriverRequests: async (status?: RequestStatus): Promise<TripRequest[]> => {
    const response = await api.get<PaginatedTripRequestResponse>('/requests/driver', {
      params: status ? { status } : undefined,
    });
    return response.data.items;
  },

  confirm: async (requestId: string): Promise<TripRequest> => {
    const response = await api.put<{ data: TripRequest; message: string }>(
      `/requests/${requestId}/confirm`
    );
    return response.data.data;
  },

  reject: async (tripId: string, requestId: string, rejectionReason?: string): Promise<TripRequest> => {
    const body = rejectionReason ? { rejection_reason: rejectionReason } : {};
    const response = await api.put<{ data: TripRequest; message: string }>(
      `/trips/${tripId}/requests/${requestId}/reject`,
      body
    );
    return response.data.data;
  },

  cancel: async (requestId: string): Promise<TripRequest> => {
    const response = await api.delete<{ data: TripRequest; message: string }>(
      `/requests/${requestId}`
    );
    return response.data.data;
  },

  // На всякий случай: создание заявки делается через tripsApi, но можно и тут
  create: async (tripId: string, data: CreateRequestData): Promise<TripRequest> => {
    const response = await api.post<{ data: TripRequest; message: string }>(
      `/trips/${tripId}/requests`,
      data
    );
    return response.data.data;
  },

  // Получить одну заявку по ID
  getById: async (requestId: string): Promise<TripRequest> => {
    const response = await api.get<TripRequest>(`/requests/${requestId}`);
    return response.data;
  },
};

export default requestsApi;
