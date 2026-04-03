import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Card, Skeleton, Modal } from '../components/ui';
import { notificationsApi, Notification } from '../services/api/notifications';
import { requestsApi } from '../services/api/requests';
import type { TripRequest } from '../types';
import styles from './NotificationsPage.module.css';

export default function NotificationsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [selectedRequest, setSelectedRequest] = useState<TripRequest | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Загрузка деталей заявки
  const { data: requestDetails, isLoading: isLoadingRequest } = useQuery({
    queryKey: ['request', selectedRequest?.id],
    queryFn: () => selectedRequest?.id ? requestsApi.getById(selectedRequest.id) : Promise.resolve(null),
    enabled: !!selectedRequest?.id,
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['notifications', page],
    queryFn: () => notificationsApi.getAll(page, 20),
  });

  const markAsReadMutation = useMutation({
    mutationFn: (notificationId: string) => notificationsApi.markAsRead(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const markAllAsReadMutation = useMutation({
    mutationFn: () => notificationsApi.markAllAsRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (notificationId: string) => notificationsApi.delete(notificationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const confirmMutation = useMutation({
    mutationFn: (requestId: string) => requestsApi.confirm(requestId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['request'] });
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      setIsModalOpen(false);
      setSelectedRequest(null);
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ requestId, tripId }: { requestId: string; tripId: string }) => 
      requestsApi.reject(tripId, requestId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['request'] });
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
      setIsModalOpen(false);
      setSelectedRequest(null);
    },
  });

  const handleConfirmRequest = (requestId: string, tripId: string) => {
    confirmMutation.mutate(requestId);
  };

  const handleRejectRequest = (requestId: string, tripId: string) => {
    rejectMutation.mutate({ requestId, tripId });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
      });
    } else if (diffDays === 1) {
      return t('chat.yesterday');
    } else if (diffDays < 7) {
      return date.toLocaleDateString('ru-RU', { weekday: 'long' });
    } else {
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
      });
    }
  };

  const getNotificationTypeIcon = (type: string) => {
    switch (type) {
      case 'request_received':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="8.5" cy="7" r="4" />
            <line x1="20" y1="8" x2="20" y2="14" />
            <line x1="23" y1="11" x2="17" y2="11" />
          </svg>
        );
      case 'request_confirmed':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
        );
      case 'request_rejected':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        );
      case 'trip_cancelled':
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
        );
      default:
        return (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
        );
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.is_read) {
      markAsReadMutation.mutate(notification.id);
    }

    // Для уведомлений о заявках показываем модальное окно с деталями
    if (notification.related_request_id && 
        (notification.type === 'request_new' || notification.type === 'request_confirmed' || notification.type === 'request_rejected')) {
      // Создаём объект TripRequest с ID заявки для загрузки деталей
      const request = {
        id: notification.related_request_id,
        trip_id: notification.related_trip_id || '',
        passenger_id: '',
        seats_requested: 0,
        status: 'pending',
        created_at: '',
      } as TripRequest;
      setSelectedRequest(request);
      setIsModalOpen(true);
    } else if (notification.related_trip_id) {
      navigate(`/trips/${notification.related_trip_id}`);
    }
  };

  const handleMarkAllRead = () => {
    markAllAsReadMutation.mutate();
  };

  const handleDelete = (e: React.MouseEvent, notificationId: number) => {
    e.stopPropagation();
    deleteMutation.mutate(notificationId);
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>{t('notifications.title')}</h1>
        </div>
        <div className={styles.notificationsList}>
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i} className={styles.notificationCard}>
              <Skeleton variant="circular" width={40} height={40} />
              <div className={styles.skeletonContent}>
                <Skeleton variant="text" width="60%" height={20} />
                <Skeleton variant="text" width="80%" height={16} />
                <Skeleton variant="text" width="30%" height={14} />
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>{t('notifications.title')}</h1>
        {data && data.stats.unread_count > 0 && (
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleMarkAllRead}
            disabled={markAllAsReadMutation.isPending}
          >
            {t('notifications.markAllRead')}
          </Button>
        )}
      </div>

      {error && (
        <div className={styles.error}>
          {t('common.error')}
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className={styles.emptyState}>
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          <p>{t('notifications.noNotifications')}</p>
        </div>
      )}

      {data && data.items.length > 0 && (
        <>
          <div className={styles.notificationsList}>
            {data.items.map((notification) => (
              <Card 
                key={notification.id} 
                className={`${styles.notificationCard} ${!notification.is_read ? styles.unread : ''}`}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className={styles.notificationIcon}>
                  {getNotificationTypeIcon(notification.type)}
                </div>
                <div className={styles.notificationContent}>
                  <div className={styles.notificationHeader}>
                    <h3 className={styles.notificationTitle}>{notification.title}</h3>
                    <span className={styles.notificationTime}>
                      {formatDate(notification.created_at)}
                    </span>
                  </div>
                  <p className={styles.notificationMessage}>{notification.message}</p>
                </div>
                <button 
                  className={styles.deleteButton}
                  onClick={(e) => handleDelete(e, notification.id)}
                  title={t('common.delete')}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              </Card>
            ))}
          </div>

          {data.total > page * 20 && (
            <div className={styles.pagination}>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
              >
                {t('common.prev')}
              </Button>
              <span className={styles.pageInfo}>
                {page} / {Math.ceil(data.total / 20)}
              </span>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setPage(page + 1)}
                disabled={page >= Math.ceil(data.total / 20)}
              >
                {t('common.next')}
              </Button>
            </div>
          )}
        </>
      )}

      {/* Модальное окно с деталями заявки */}
      <RequestDetailsModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedRequest(null);
        }}
        request={selectedRequest}
        requestDetails={requestDetails}
        isLoading={isLoadingRequest}
        onConfirm={handleConfirmRequest}
        onReject={handleRejectRequest}
        isConfirming={confirmMutation.isPending}
        isRejecting={rejectMutation.isPending}
      />
    </div>
  );
}

// Модальное окно с деталями заявки
function RequestDetailsModal({
  isOpen,
  onClose,
  request,
  requestDetails,
  isLoading,
  onConfirm,
  onReject,
  isConfirming,
  isRejecting,
}: {
  isOpen: boolean;
  onClose: () => void;
  request: TripRequest | null;
  requestDetails: TripRequest | null | undefined;
  isLoading: boolean;
  onConfirm?: (requestId: string, tripId: string) => void;
  onReject?: (requestId: string, tripId: string) => void;
  isConfirming?: boolean;
  isRejecting?: boolean;
}) {
  const { t } = useTranslation();

  if (!isOpen || !request) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Детали заявки">
      {isLoading ? (
        <div className={styles.modalLoading}>
          <Skeleton variant="text" width="100%" />
          <Skeleton variant="text" width="80%" />
          <Skeleton variant="text" width="60%" />
        </div>
      ) : requestDetails ? (
        <div className={styles.modalContent}>
          {/* Информация о пассажире */}
          <div className={styles.passengerCard}>
            <div className={styles.passengerAvatarLarge}>
              {requestDetails.passenger?.avatar_url ? (
                <img 
                  src={requestDetails.passenger.avatar_url} 
                  alt="Аватар" 
                />
              ) : (
                <div className={styles.avatarPlaceholderLarge}>
                  {requestDetails.passenger?.first_name?.charAt(0)}
                  {requestDetails.passenger?.last_name?.charAt(0)}
                </div>
              )}
            </div>
            <div className={styles.passengerInfoCard}>
              <h3 className={styles.passengerNameCard}>
                {requestDetails.passenger?.first_name} {requestDetails.passenger?.last_name}
              </h3>
              {requestDetails.passenger?.rating_average !== undefined && (
                <div className={styles.ratingDisplayCard}>
                  <span className={styles.ratingStarCard}>★</span>
                  <span className={styles.ratingValueCard}>{requestDetails.passenger.rating_average.toFixed(1)}</span>
                  <span className={styles.ratingCountCard}>({requestDetails.passenger.rating_count} отзывов)</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Детали заявки */}
          <div className={styles.requestDetailsCard}>
            <div className={styles.detailRow}>
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>Запрошено мест</span>
                <span className={styles.detailValue}>{requestDetails.seats_requested}</span>
              </div>
              
              <div className={styles.detailItem}>
                <span className={styles.detailLabel}>Статус</span>
                <span className={`${styles.statusBadge} ${styles[`status_${requestDetails.status}`]}`}>
                  {requestDetails.status === 'pending' && 'Ожидает'}
                  {requestDetails.status === 'confirmed' && 'Подтверждена'}
                  {requestDetails.status === 'rejected' && 'Отклонена'}
                  {requestDetails.status === 'cancelled' && 'Отменена'}
                </span>
              </div>
            </div>
          </div>
          
          {/* Маршрут */}
          {requestDetails.trip && (
            <div className={styles.routeCard}>
              <div className={styles.routeHeader}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                <span>Маршрут</span>
              </div>
              <div className={styles.routeDetails}>
                <div className={styles.routeCities}>
                  <span>{requestDetails.trip.from_city}</span>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="5" y1="12" x2="19" y2="12" />
                    <polyline points="12 5 19 12 12 19" />
                  </svg>
                  <span>{requestDetails.trip.to_city}</span>
                </div>
                <div className={styles.routeMeta}>
                  <div className={styles.routeDate}>
                    {new Date(requestDetails.trip.departure_date).toLocaleDateString('ru-RU', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric'
                    })}
                    {requestDetails.trip.departure_time_start && (
                      <span className={styles.routeTime}> в {requestDetails.trip.departure_time_start}</span>
                    )}
                  </div>
                  {requestDetails.trip.available_seats !== undefined && (
                    <div className={styles.availableSeats}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                      </svg>
                      <span>{requestDetails.trip.available_seats} мест</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {/* Сообщение */}
          {requestDetails.message && (
            <div className={styles.messageCard}>
              <div className={styles.messageHeader}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <span>Сообщение</span>
              </div>
              <p className={styles.messageTextCard}>{requestDetails.message}</p>
            </div>
          )}
          
          <div className={styles.modalActions}>
            {requestDetails.status === 'pending' && onConfirm && onReject && (
              <div className={styles.actionButtons}>
                <Button 
                  variant="primary" 
                  onClick={() => onConfirm(requestDetails.id, requestDetails.trip_id)}
                  disabled={isConfirming || isRejecting}
                >
                  {isConfirming ? 'Принятие...' : 'Принять'}
                </Button>
                <Button 
                  variant="danger" 
                  onClick={() => onReject(requestDetails.id, requestDetails.trip_id)}
                  disabled={isConfirming || isRejecting}
                >
                  {isRejecting ? 'Отклонение...' : 'Отклонить'}
                </Button>
              </div>
            )}
            <Button variant="outline" onClick={onClose}>
              Закрыть
            </Button>
          </div>
        </div>
      ) : (
        <p>Произошла ошибка при загрузке данных</p>
      )}
    </Modal>
  );
}
