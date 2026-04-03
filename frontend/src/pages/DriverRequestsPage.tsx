import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button, Card, Input, Modal, Skeleton } from '../components/ui';
import { requestsApi } from '../services/api/requests';
import type { RequestStatus, TripRequest } from '../types';
import styles from './DriverRequestsPage.module.css';

type RequestsFilter = RequestStatus | 'all';

function formatStatusLabel(t: (key: string) => string, status: RequestStatus): string {
  switch (status) {
    case 'pending':
      return t('requests.pending');
    case 'confirmed':
      return t('requests.confirmed');
    case 'rejected':
      return t('requests.rejected');
    case 'cancelled':
      return t('requests.cancelled');
    default:
      return status;
  }
}

export default function DriverRequestsPage() {
  const { t } = useTranslation();

  const [statusFilter, setStatusFilter] = useState<RequestsFilter>('pending');
  const [actionError, setActionError] = useState<string | null>(null);
  const filterValue = useMemo(
    () => (statusFilter === 'all' ? undefined : statusFilter),
    [statusFilter]
  );

  const {
    data: requests,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['driverRequests', statusFilter],
    queryFn: () => requestsApi.getDriverRequests(filterValue),
  });

  const confirmMutation = useMutation({
    mutationFn: (requestId: string) => requestsApi.confirm(requestId),
    onSuccess: () => {
      setActionError(null);
      refetch();
    },
    onError: (e: any) => setActionError(e?.response?.data?.detail || t('errors.serverError')),
  });

  const rejectMutation = useMutation({
    mutationFn: async (args: { tripId: string; requestId: string; reason?: string }) =>
      requestsApi.reject(args.tripId, args.requestId, args.reason),
    onSuccess: () => {
      setActionError(null);
      setRejectModalOpen(false);
      setSelectedRequest(null);
      setRejectionReason('');
      refetch();
    },
    onError: (e: any) => setActionError(e?.response?.data?.detail || t('errors.serverError')),
  });

  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [viewModalOpen, setViewModalOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<TripRequest | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');

  const openView = (req: TripRequest) => {
    setSelectedRequest(req);
    setViewModalOpen(true);
  };

  const openReject = (req: TripRequest) => {
    if (req.status !== 'pending') return;
    setActionError(null);
    setSelectedRequest(req);
    setRejectionReason('');
    setRejectModalOpen(true);
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>{t('requests.requestsToMe')}</h1>
        </div>
        <div className={styles.list}>
          {[1, 2, 3].map((i) => (
            <Card key={i} className={styles.card}>
              <Skeleton variant="text" width="60%" height={20} />
              <Skeleton variant="text" width="80%" />
              <Skeleton variant="rounded" height={36} />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <Card className={styles.card}>
          <div className={styles.error}>{t('errors.serverError')}</div>
        </Card>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>{t('requests.requestsToMe')}</h1>
      </div>

      <div className={styles.filterRow}>
        <select
          className={styles.filterSelect}
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as RequestsFilter)}
        >
          <option value="all">{t('requests.title')}</option>
          <option value="pending">{t('requests.pending')}</option>
          <option value="confirmed">{t('requests.confirmed')}</option>
          <option value="rejected">{t('requests.rejected')}</option>
          <option value="cancelled">{t('requests.cancelled')}</option>
        </select>
      </div>

      {requests && requests.length === 0 && (
        <div className={styles.emptyState}>{t('common.noResults')}</div>
      )}

      {requests && requests.length > 0 && (
        <div className={styles.list}>
          {requests.map((req) => (
            <Card key={req.id} className={styles.card}>
              <div className={styles.cardTop}>
                <div className={styles.status}>{formatStatusLabel(t, req.status as RequestStatus)}</div>
                <div className={styles.date}>
                  {req.created_at ? new Date(req.created_at).toLocaleString() : ''}
                </div>
              </div>

              <div className={styles.row}>
                <span className={styles.label}>{t('trips.book')}</span>
                <span className={styles.value}>#{req.trip_id}</span>
              </div>

              <div className={styles.row}>
                <span className={styles.label}>{t('requests.seatsRequested')}</span>
                <span className={styles.value}>{req.seats_requested}</span>
              </div>

              {req.message && (
                <div className={styles.message}>
                  <div className={styles.messageLabel}>{t('requests.message')}</div>
                  <div className={styles.messageText}>{req.message}</div>
                </div>
              )}

              {req.status === 'pending' && (
                <div className={styles.actions}>
                  <Button variant="outline" onClick={() => openView(req)}>
                    {t('requests.view')}
                  </Button>
                </div>
              )}

              {req.status !== 'pending' && (
                <div className={styles.actions}>
                  <Button variant="outline" onClick={() => openView(req)}>
                    {t('requests.view')}
                  </Button>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={viewModalOpen}
        onClose={() => setViewModalOpen(false)}
        title={t('requests.requestDetails')}
      >
        <div className={styles.modalBody}>
          {selectedRequest && (
            <>
              <div className={styles.viewRow}>
                <span className={styles.label}>{t('trips.book')}</span>
                <span className={styles.value}>#{selectedRequest.trip_id}</span>
              </div>

              <div className={styles.viewRow}>
                <span className={styles.label}>{t('requests.seatsRequested')}</span>
                <span className={styles.value}>{selectedRequest.seats_requested}</span>
              </div>

              {selectedRequest.message && (
                <div className={styles.message}>
                  <div className={styles.messageLabel}>{t('requests.message')}</div>
                  <div className={styles.messageText}>{selectedRequest.message}</div>
                </div>
              )}

              <div className={styles.viewActions}>
                <Button variant="outline" onClick={() => setViewModalOpen(false)}>
                  {t('common.cancel')}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setViewModalOpen(false);
                    openReject(selectedRequest);
                  }}
                >
                  {t('requests.reject')}
                </Button>
                <Button
                  variant="primary"
                  onClick={() => confirmMutation.mutate(selectedRequest.id)}
                  loading={confirmMutation.isPending}
                >
                  {t('requests.approve')}
                </Button>
              </div>
            </>
          )}
        </div>
      </Modal>

      <Modal
        isOpen={rejectModalOpen}
        onClose={() => setRejectModalOpen(false)}
        title={t('requests.reject')}
      >
        <div className={styles.modalBody}>
          <div className={styles.modalText}>
            {selectedRequest ? `#${selectedRequest.trip_id} / ${selectedRequest.id}` : ''}
          </div>

          <Input
            label={t('requests.reject')}
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            placeholder={t('requests.message')}
          />

          {actionError && <div className={styles.error}>{actionError}</div>}

          <div className={styles.modalActions}>
            <Button variant="secondary" onClick={() => setRejectModalOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              variant="primary"
              loading={rejectMutation.isPending}
              onClick={() => {
                if (!selectedRequest) return;
                rejectMutation.mutate({
                  tripId: selectedRequest.trip_id,
                  requestId: selectedRequest.id,
                  reason: rejectionReason.trim() ? rejectionReason.trim() : undefined,
                });
              }}
            >
              {t('requests.reject')}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

