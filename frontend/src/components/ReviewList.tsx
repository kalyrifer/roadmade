import { useCallback, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ReviewStatus, ReviewWithUsers, reviewsApi } from '../services/api/reviews';
import { ReviewCard } from './ReviewCard';
import { Skeleton } from './ui/Skeleton';
import Button from './ui/Button';
import styles from './ReviewList.module.css';

export type SortOrder = 'newest' | 'oldest' | 'highest' | 'lowest';

export interface ReviewListProps {
  userId?: string;
  tripId?: string;
  filterStatus?: ReviewStatus;
  initialPage?: number;
  pageSize?: number;
  showAuthorInfo?: boolean;
  showTargetInfo?: boolean;
}

export function ReviewList({
  userId,
  tripId,
  filterStatus,
  initialPage = 1,
  pageSize = 20,
  showAuthorInfo = true,
  showTargetInfo = false,
}: ReviewListProps) {
  const [page, setPage] = useState(initialPage);
  const [statusFilter, setStatusFilter] = useState<ReviewStatus | undefined>(filterStatus);
  const [sortOrder, setSortOrder] = useState<SortOrder>('newest');

  const queryKey = userId
    ? ['reviews', 'user', userId, statusFilter, page, pageSize, sortOrder]
    : tripId
    ? ['reviews', 'trip', tripId, statusFilter, page, pageSize, sortOrder]
    : ['reviews', 'me', statusFilter, page, pageSize, sortOrder];

  const queryFn = useCallback(() => {
    if (userId) {
      return reviewsApi.getUserReviews(userId, {
        status_filter: statusFilter,
        page,
        page_size: pageSize,
      });
    }
    if (tripId) {
      return reviewsApi.getTripReviews(tripId, {
        status_filter: statusFilter,
        page,
        page_size: pageSize,
      });
    }
    return reviewsApi.getMyReviews({
      status_filter: statusFilter,
      page,
      page_size: pageSize,
    });
  }, [userId, tripId, statusFilter, page, pageSize]);

  const { data, isLoading, error } = useQuery({
    queryKey,
    queryFn,
  });

  const reviews = data?.items || [];
  const total = data?.total || 0;
  const totalPages = data?.pages || 0;

  const sortedReviews = [...reviews].sort((a, b) => {
    switch (sortOrder) {
      case 'newest':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      case 'oldest':
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      case 'highest':
        return b.rating - a.rating;
      case 'lowest':
        return a.rating - b.rating;
      default:
        return 0;
    }
  });

  const handlePrevPage = () => {
    if (page > 1) setPage(page - 1);
  };

  const handleNextPage = () => {
    if (page < totalPages) setPage(page + 1);
  };

  const statusOptions: { value: ReviewStatus | ''; label: string }[] = [
    { value: '', label: 'Все' },
    { value: 'published', label: 'Опубликованные' },
    { value: 'pending', label: 'На модерации' },
    { value: 'rejected', label: 'Отклонённые' },
  ];

  const sortOptions: { value: SortOrder; label: string }[] = [
    { value: 'newest', label: 'Новые' },
    { value: 'oldest', label: 'Старые' },
    { value: 'highest', label: 'Высокий рейтинг' },
    { value: 'lowest', label: 'Низкий рейтинг' },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.filters}>
        <select
          className={styles.select}
          value={statusFilter || ''}
          onChange={(e) => {
            setStatusFilter((e.target.value as ReviewStatus) || undefined);
            setPage(1);
          }}
        >
          {statusOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        <select
          className={styles.select}
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value as SortOrder)}
        >
          {sortOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className={styles.list}>
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} height={120} className={styles.skeleton} />
          ))}
        </div>
      ) : error ? (
        <div className={styles.error}>Ошибка загрузки отзывов</div>
      ) : sortedReviews.length === 0 ? (
        <div className={styles.empty}>Отзывов пока нет</div>
      ) : (
        <div className={styles.list}>
          {sortedReviews.map((review) => (
            <ReviewCard
              key={review.id}
              review={review}
              showAuthorInfo={showAuthorInfo}
              showTargetInfo={showTargetInfo}
            />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className={styles.pagination}>
          <span className={styles.pageInfo}>
            Страница {page} из {totalPages}
          </span>
          <div className={styles.pageButtons}>
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrevPage}
              disabled={page === 1}
            >
              Предыдущая
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNextPage}
              disabled={page >= totalPages}
            >
              Следующая
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReviewList;