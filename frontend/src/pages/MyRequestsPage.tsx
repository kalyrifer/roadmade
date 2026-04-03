import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Button, Card, Modal, Skeleton } from '../components/ui';
import { requestsApi } from '../services/api/requests';
import { chatApi } from '../services/api/chat';
import type { RequestStatus, TripRequest } from '../types';
import styles from './MyRequestsPage.module.css';

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

export default function MyRequestsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<RequestsFilter>('all');
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
    queryKey: ['myRequests', statusFilter],
    queryFn: () => requestsApi.getMyRequests(filterValue),
  });

  const cancelMutation = useMutation({
    mutationFn: (requestId: string) => requestsApi.cancel(requestId),
    onSuccess: () => {
      setActionError(null);
      refetch();
    },
    onError: (e: any) => {
      setActionError(e?.response?.data?.detail || t('errors.serverError'));
    },
  });

  const openChatMutation = useMutation({
    mutationFn: (tripId: string) => chatApi.createOrGetConversation(tripId, ''),
    onSuccess: (conversation) => {
      navigate(`/chat/${conversation.id}`);
    },
  });

  const [confirmCancelId, setConfirmCancelId] = useState<string | null>(null);

  const handleCancel = (req: TripRequest) => {
    if (req.status !== 'pending') return;
    setActionError(null);
    setConfirmCancelId(req.id);
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>{t('requests.myRequests')}</h1>
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
        <h1>{t('requests.myRequests')}</h1>
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
                <div className={styles.status}>
                  {formatStatusLabel(t, req.status)}
                </div>
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
                  <Button
                    variant="outline"
                    onClick={() => handleCancel(req)}
                    loading={cancelMutation.isPending && confirmCancelId === req.id}
                  >
                    {t('common.cancel')}
                  </Button>
                  {req.trip_id && (
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => openChatMutation.mutate(req.trip_id)}
                      loading={openChatMutation.isPending}
                    >
                      {t('trips.contactDriver')}
                    </Button>
                  )}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={confirmCancelId !== null}
        onClose={() => setConfirmCancelId(null)}
        title={t('common.cancel')}
      >
        <div className={styles.modalBody}>
          <div className={styles.modalText}>
            {t('requests.cancelled')} #{confirmCancelId}
          </div>
          {actionError && <div className={styles.error}>{actionError}</div>}
          <div className={styles.modalActions}>
            <Button variant="secondary" onClick={() => setConfirmCancelId(null)}>
              {t('common.close')}
            </Button>
            <Button
              variant="primary"
              loading={cancelMutation.isPending}
              onClick={() => {
                if (!confirmCancelId) return;
                cancelMutation.mutate(confirmCancelId, {
                  onSuccess: () => setConfirmCancelId(null),
                });
              }}
            >
              {t('common.cancel')}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

