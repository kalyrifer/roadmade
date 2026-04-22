import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReviewCreate, reviewsApi } from '../services/api/reviews';
import { StarRating } from './ui/StarRating';
import { Modal } from './ui/Modal';
import Button from './ui/Button';
import styles from './ReviewModal.module.css';

interface ReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  tripId: string;
  targetUserId: string;
  targetUserName?: string;
  existingReview?: {
    id: string;
    rating: number;
    text?: string;
  };
}

export function ReviewModal({
  isOpen,
  onClose,
  tripId,
  targetUserId,
  targetUserName = 'пользователя',
  existingReview,
}: ReviewModalProps) {
  const queryClient = useQueryClient();
  const [rating, setRating] = useState(existingReview?.rating || 0);
  const [text, setText] = useState(existingReview?.text || '');
  const [error, setError] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: (data: ReviewCreate) => reviewsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      onClose();
      setRating(0);
      setText('');
    },
    onError: (err: Error) => {
      setError(err.message || 'Ошибка при создании отзыва');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (rating === 0) {
      setError('Пожалуйста, выберите оценку');
      return;
    }

    createMutation.mutate({
      trip_id: tripId,
      target_id: targetUserId,
      rating,
      text: text.trim() || undefined,
    });
  };

  const handleClose = () => {
    setError(null);
    onClose();
  };

  const charCount = text.length;
  const maxChars = 2000;

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Оставить отзыв">
      <form onSubmit={handleSubmit} className={styles.form}>
        <p className={styles.description}>
          Вы оставляете отзыв о {targetUserName}
        </p>

        <div className={styles.field}>
          <label className={styles.label}>Оценка *</label>
          <StarRating
            rating={rating}
            onChange={setRating}
            size="lg"
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Текст отзыва (необязательно)</label>
          <textarea
            className={styles.textarea}
            value={text}
            onChange={(e) => setText(e.target.value.slice(0, maxChars))}
            placeholder="Поделитесь своими впечатлениями..."
            rows={4}
          />
          <span className={styles.charCount}>
            {charCount}/{maxChars}
          </span>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <div className={styles.actions}>
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
          >
            Отмена
          </Button>
          <Button
            type="submit"
            loading={createMutation.isPending}
            disabled={rating === 0}
          >
            Отправить
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default ReviewModal;