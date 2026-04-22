import { Link } from 'react-router-dom';
import { useState } from 'react';
import { formatDistanceToNow } from '../locales/i18n';
import { ReviewWithUsers } from '../services/api/reviews';
import { StarRating } from './ui/StarRating';
import styles from './ReviewCard.module.css';

export interface ReviewCardProps {
  review: ReviewWithUsers;
  showAuthorInfo?: boolean;
  showTargetInfo?: boolean;
  maxTextLength?: number;
}

export function ReviewCard({
  review,
  showAuthorInfo = true,
  showTargetInfo = false,
  maxTextLength = 200,
}: ReviewCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const authorName = showAuthorInfo
    ? `${review.author_first_name || ''} ${review.author_last_name || ''}`.trim()
    : '';
  
  const targetName = showTargetInfo
    ? `${review.target_first_name || ''} ${review.target_last_name || ''}`.trim()
    : '';

  const displayName = showAuthorInfo ? authorName : targetName;
  const avatarUrl = showAuthorInfo ? review.author_avatar_url : review.target_avatar_url;
  const relativeTime = formatDistanceToNow(review.created_at);
  const text = review.text || '';
  const isLongText = text.length > maxTextLength;
  const displayText = isLongText && !isExpanded ? text.slice(0, maxTextLength) + '...' : text;

  const statusLabels: Record<string, string> = {
    pending: 'На модерации',
    published: 'Опубликован',
    rejected: 'Отклонён',
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        {showAuthorInfo && (
          <Link to={`/profile/${review.author_id}`} className={styles.avatarLink}>
            {avatarUrl ? (
              <img src={avatarUrl} alt={displayName} className={styles.avatar} />
            ) : (
              <div className={styles.avatarPlaceholder}>
                {displayName.charAt(0).toUpperCase()}
              </div>
            )}
          </Link>
        )}
        
        <div className={styles.info}>
          <div className={styles.nameRow}>
            {showAuthorInfo ? (
              <Link to={`/profile/${review.author_id}`} className={styles.name}>
                {displayName}
              </Link>
            ) : (
              <span className={styles.name}>{displayName}</span>
            )}
            <StarRating rating={review.rating} readonly size="sm" />
          </div>
          
          <div className={styles.meta}>
            <span className={styles.date}>{relativeTime}</span>
            {review.status !== 'published' && (
              <span className={`${styles.status} ${styles[review.status]}`}>
                {statusLabels[review.status]}
              </span>
            )}
          </div>
        </div>
      </div>

      {text && (
        <div className={styles.text}>
          {displayText}
          {isLongText && (
            <button
              type="button"
              className={styles.expandButton}
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? 'Скрыть' : 'Показать ещё'}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default ReviewCard;