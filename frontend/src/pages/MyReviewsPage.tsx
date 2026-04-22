import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { reviewsApi, ReviewStats } from '../services/api/reviews';
import { ReviewList } from '../components/ReviewList';
import { StarRating } from '../components/ui/StarRating';
import { Skeleton } from '../components/ui/Skeleton';
import styles from './MyReviewsPage.module.css';

export function MyReviewsPage() {
  const [activeTab, setActiveTab] = useState<'given' | 'received'>('given');
  
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['reviews', 'stats'],
    queryFn: () => reviewsApi.getUserStats('me'),
    enabled: activeTab === 'received',
  });

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Мои отзывы</h1>

      <div className={styles.tabs}>
        <button
          type="button"
          className={`${styles.tab} ${activeTab === 'given' ? styles.active : ''}`}
          onClick={() => setActiveTab('given')}
        >
          Оставленные
        </button>
        <button
          type="button"
          className={`${styles.tab} ${activeTab === 'received' ? styles.active : ''}`}
          onClick={() => setActiveTab('received')}
        >
          Полученные
        </button>
      </div>

      {activeTab === 'received' && (
        <div className={styles.stats}>
          {statsLoading ? (
            <Skeleton height={80} />
          ) : stats ? (
            <>
              <div className={styles.statsMain}>
                <span className={styles.ratingValue}>
                  {stats.rating_average.toFixed(1)}
                </span>
                <StarRating rating={Math.round(stats.rating_average)} readonly size="md" />
                <span className={styles.reviewsCount}>
                  {stats.rating_count} отзывов
                </span>
              </div>
              <div className={styles.distribution}>
                {[5, 4, 3, 2, 1].map((rating) => {
                  const count = stats.rating_distribution[rating] || 0;
                  const percent = stats.rating_count > 0 
                    ? (count / stats.rating_count) * 100 
                    : 0;
                  return (
                    <div key={rating} className={styles.distributionRow}>
                      <span className={styles.distributionLabel}>{rating}</span>
                      <div className={styles.distributionBar}>
                        <div 
                          className={styles.distributionFill} 
                          style={{ width: `${percent}%` }} 
                        />
                      </div>
                      <span className={styles.distributionCount}>{count}</span>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            <p className={styles.noStats}>Нет отзывов</p>
          )}
        </div>
      )}

      {activeTab === 'given' ? (
        <ReviewList showAuthorInfo={true} showTargetInfo={true} />
      ) : (
        <ReviewList userId="me" showAuthorInfo={true} showTargetInfo={false} />
      )}
    </div>
  );
}

export default MyReviewsPage;