import { HTMLAttributes, ReactNode } from 'react';
import { clsx } from 'clsx';
import styles from './Card.module.css';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: 'default' | 'outlined' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
}

export function Card({
  children,
  className,
  variant = 'default',
  padding = 'md',
  hoverable = false,
  ...props
}: CardProps) {
  return (
    <div
      className={clsx(
        styles.card,
        styles[variant],
        styles[`padding-${padding}`],
        hoverable && styles.hoverable,
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export default Card;
