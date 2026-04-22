import { clsx } from 'clsx';
import { useState } from 'react';
import styles from './StarRating.module.css';

export interface StarRatingProps {
  rating: number;
  onChange?: (rating: number) => void;
  readonly?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function StarRating({
  rating,
  onChange,
  readonly = false,
  size = 'md',
  className,
}: StarRatingProps) {
  const [hoverRating, setHoverRating] = useState<number | null>(null);

  const displayRating = hoverRating ?? rating;

  const handleClick = (index: number) => {
    if (!readonly && onChange) {
      onChange(index + 1);
    }
  };

  const handleMouseEnter = (index: number) => {
    if (!readonly) {
      setHoverRating(index + 1);
    }
  };

  const handleMouseLeave = () => {
    setHoverRating(null);
  };

  return (
    <div className={clsx(styles.container, styles[size], className)}>
      {[0, 1, 2, 3, 4].map((index) => {
        const filled = displayRating > index;
        const partial = !filled && displayRating > index && displayRating < index + 1;
        const isInteractive = !readonly;

        return (
          <button
            key={index}
            type="button"
            className={clsx(
              styles.star,
              filled && styles.filled,
              partial && styles.partial,
              isInteractive && styles.interactive
            )}
            onClick={() => handleClick(index)}
            onMouseEnter={() => handleMouseEnter(index)}
            onMouseLeave={handleMouseLeave}
            disabled={readonly}
            aria-label={`${index + 1} звезд${index === 0 ? 'а' : index < 3 ? 'ы' : ''}`}
          >
            <svg
              viewBox="0 0 24 24"
              className={styles.starIcon}
            >
              <defs>
                <linearGradient id={`half-${index}`}>
                  <stop offset="50%" stopColor="currentColor" />
                  <stop offset="50%" stopColor="transparent" />
                </linearGradient>
              </defs>
              <path
                d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                fill={filled ? 'currentColor' : partial ? `url(#half-${index})` : 'none'}
                stroke="currentColor"
                strokeWidth={partial ? 0 : 1}
              />
            </svg>
          </button>
        );
      })}
    </div>
  );
}

export default StarRating;