import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { Card, Skeleton } from '../components/ui';
import { chatApi } from '../services/api/chat';
import { useAuthStore } from '../stores/auth';
import styles from './ChatListPage.module.css';

interface ConversationWithOther {
  id: string;
  trip_id: string;
  last_message_at?: string;
  last_message?: {
    id: string;
    content: string;
    created_at: string;
    sender_id: string;
  };
  trip?: {
    id: string;
    from_city: string;
    to_city: string;
    departure_date?: string;
    departure_time_start?: string;
  };
  participants?: Array<{
    user_id: string;
    user?: {
      id: string;
      first_name: string;
      last_name: string;
      avatar_url?: string;
    };
  }>;
  chatTitle: string;
  participantCount: number;
}

export default function ChatListPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const userId = useAuthStore((state) => state.user?.id);

  const {
    data: conversationsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => chatApi.getConversations(1, 50),
  });

  const conversations = useMemo<ConversationWithOther[]>(() => {
    if (!conversationsData?.items || !userId) return [];
    
    return conversationsData.items.map((conv) => {
      const participants = conv.participants || [];
      const participantCount = participants.length;
      
      // Build list of participant names (excluding current user)
      const otherParticipants = participants.filter(p => p.user_id !== userId);
      let chatTitle = '';
      
      if (conv.trip?.from_city && conv.trip?.to_city) {
        // Use trip route as base
        chatTitle = `${conv.trip.from_city} → ${conv.trip.to_city}`;
        
        // Add participant count if more than 1
        if (participantCount > 2) {
          chatTitle = `${chatTitle} (${participantCount} участников)`;
        } else if (participantCount === 2) {
          // For 1:1 chats, show other person's name
          const other = otherParticipants[0]?.user;
          if (other?.first_name || other?.last_name) {
            const name = `${other.first_name || ''} ${other.last_name || ''}`.trim();
            chatTitle = name;
          }
        }
      }
      
      return {
        ...conv,
        chatTitle: chatTitle || 'Chat',
        participantCount,
      };
    });
  }, [conversationsData, userId]);

  const formatTime = (dateStr?: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (days === 1) {
      return t('chat.yesterday');
    } else if (days < 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    }
    return date.toLocaleDateString([], { day: 'numeric', month: 'short' });
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>{t('chat.title')}</h1>
        </div>
        <div className={styles.list}>
          {[1, 2, 3].map((i) => (
            <Card key={i} className={styles.card}>
              <div className={styles.avatar}>
                <Skeleton variant="circular" width={48} height={48} />
              </div>
              <div className={styles.content}>
                <Skeleton variant="text" width="60%" height={20} />
                <Skeleton variant="text" width="80%" />
              </div>
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
        <h1>{t('chat.title')}</h1>
      </div>

      {conversations.length === 0 && (
        <div className={styles.emptyState}>{t('chat.empty')}</div>
      )}

      {conversations.length > 0 && (
        <div className={styles.list}>
          {conversations.map((conv) => (
            <Card 
              key={conv.id} 
              className={styles.card}
              onClick={() => navigate(`/chat/${conv.id}`)}
            >
              <div className={styles.avatar}>
                <div className={styles.avatarPlaceholder}>
                  {conv.chatTitle.charAt(0).toUpperCase()}
                </div>
              </div>
              
              <div className={styles.content}>
                <div className={styles.topRow}>
                  <span className={styles.name}>{conv.chatTitle}</span>
                  <span className={styles.time}>
                    {formatTime(conv.last_message?.created_at || conv.last_message_at)}
                  </span>
                </div>
                
                <div className={styles.trip}>
                  {conv.trip?.departure_date && (
                    <span className={styles.date}>
                      {new Date(conv.trip.departure_date).toLocaleDateString('ru-RU', {
                        day: 'numeric',
                        month: 'short',
                      })}
                    </span>
                  )}
                  {conv.participantCount > 0 && (
                    <span className={styles.date}>
                      {' · '}{conv.participantCount} участников
                    </span>
                  )}
                </div>
                
                <div className={styles.lastMessage}>
                  {conv.last_message?.content || conv.last_message_at ? t('chat.noMessages') : ''}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}