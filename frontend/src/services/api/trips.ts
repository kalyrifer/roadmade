import { api } from './client';
import type { Trip, TripFormData, PaginatedResponse, TripRequest, CreateRequestData } from '../../types';

export interface TripSearchParams {
  from_city?: string;
  to_city?: string;
  date?: string;
  page?: number;
  page_size?: number;
}

export const tripsApi = {
  search: async (params: TripSearchParams): Promise<PaginatedResponse<Trip>> => {
    const response = await api.get<PaginatedResponse<Trip>>('/trips', { params });
    return response.data;
  },

  searchTrips: async (params: {
    from?: string;
    to?: string;
    date?: string;
  }): Promise<Trip[]> => {
    const searchParams: TripSearchParams = {
      from_city: params.from,
      to_city: params.to,
      date: params.date,
      page_size: 20,
    };
    const response = await api.get<{ items: Array<{ trip: Trip; driver: any }> }>('/trips', { params: searchParams });
    // Backend returns { items: [{ trip, driver, ... }] }
    return response.data.items.map((item: any) => ({
      ...item.trip,
      driver: item.driver,
    }));
  },

  getById: async (id: string): Promise<Trip> => {
    const response = await api.get<any>(`/trips/${id}`);
    const data = response.data;
    if (data.trip && data.driver) {
      const trip = {
        ...data.trip,
        driver: data.driver,
      };
      // Fetch passengers separately
      try {
        const passengersResponse = await api.get<any[]>(`/trips/${id}/passengers`);
        trip.passengers = passengersResponse.data;
      } catch {
        trip.passengers = [];
      }
      return trip;
    }
    return data;
  },

  create: async (data: TripFormData): Promise<Trip> => {
    try {
      const response = await api.post<Trip>('/trips', {
        ...data,
        status: 'draft',
      });
      const createdTrip = response.data;
      await api.patch(`/trips/${createdTrip.id}/publish`);
      return tripsApi.getById(createdTrip.id);
    } catch (error) {
      console.error('Error creating trip:', error);
      throw error;
    }
  },

  update: async (id: string, data: Partial<TripFormData>): Promise<Trip> => {
    try {
      const response = await api.put<Trip>(`/trips/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating trip:', error);
      throw error;
    }
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/trips/${id}`);
  },

  publish: async (id: string): Promise<Trip> => {
    const response = await api.patch<Trip>(`/trips/${id}/publish`);
    return response.data;
  },

  getMyTrips: async (status?: string): Promise<Trip[]> => {
    try {
      const response = await api.get<{ items: Trip[] }>('/trips/my/driver', {
        params: status ? { status, limit: 100 } : { limit: 100 },
      });
      return response.data.items;
    } catch (error) {
      console.error('Error fetching my trips:', error);
      return [];
    }
  },

  getUserTrips: async (userId: string): Promise<Trip[]> => {
    const response = await api.get<PaginatedResponse<Trip>>(`/users/${userId}/trips`);
    return response.data.items;
  },

  createRequest: async (tripId: string, data: CreateRequestData): Promise<TripRequest> => {
    // Backend ожидает JSON body: { seats_requested, message }
    // и возвращает обёртку: { data: TripRequest, message: string }
    const response = await api.post<{ data: TripRequest }>(
      `/trips/${tripId}/requests`,
      data
    );
    return response.data.data;
  },
};

export default tripsApi;
