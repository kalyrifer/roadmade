# Промпт для реализации системы отзывов в RoadMate

## 📋 Контекст проекта

**RoadMate** — это веб-приложение для совместных поездок (аналог BlaBlaCar).  
Стек технологий:
- **Backend**: Python, FastAPI, PostgreSQL, SQLAlchemy (async), Alembic (миграции)
- **Frontend**: React + TypeScript, Vite, TanStack Query, React Router, i18next
- **Архитектура**: Чистая архитектура (Clean Architecture) с разделением на слои: models → repositories → services → API routers

---

## 📊 Текущее состояние системы отзывов

### ✅ Уже реализовано (Backend)

1. **Модель Review** (`app/models/reviews/model.py`)
   - Поля: `id`, `trip_id`, `author_id`, `target_id`, `rating` (1-5), `text`, `status` (pending/published/rejected)
   - Связи: Trip, User (author и target)
   - Ограничения: уникальный constraint на (`trip_id`, `author_id`)
   - Индексы для поиска

2. **Pydantic схемы** (`app/schemas/reviews.py`)
   - `ReviewBase`, `ReviewCreate`, `ReviewRead`, `ReviewList`, `ReviewStatusUpdate`, `ReviewFilter`, `ReviewReadWithUsers`

3. **API роутер** (`app/api/v1/reviews/router.py`) — эндпоинты:
   - `POST /reviews/` — создание отзыва
   - `GET /reviews/user/{user_id}` — отзывы о пользователе (с фильтром по статусу, пагинацией)
   - `GET /reviews/trip/{trip_id}` — отзывы о поездке
   - `PUT /reviews/{id}` — обновление статуса (модерация)
   - `DELETE /reviews/{id}` — удаление отзыва
   - `GET /reviews/me/trip/{trip_id}/can-review` — проверка возможности оставить отзыв

4. **Сервисный слой** (`app/services/reviews/service.py`)
   - Бизнес-логика создания отзыва с валидациями:
     - Поездка должна быть завершена (`status=completed`)
     - Автор должен быть участником поездки (водитель или подтверждённый пассажир)
     - Нельзя оставить отзыв о себе
     - Один пользователь — один отзыв на поездку
   - Методы: `get_user_reviews`, `get_trip_reviews`, `update_review_status`, `delete_review`, `check_user_can_review`

5. **Repository слой** (`app/repositories/reviews/repository.py`)
   - CRUD операции + пагинация + фильтрация

### ✅ Уже реализовано (Frontend)

1. **API клиент** (`frontend/src/services/api/reviews.ts`)
   - Все методы для работы с API

2. **Интеграция в TripPage** (`frontend/src/pages/TripPage.tsx`)
   - Модальное окно для создания отзыва
   - Отображение отзывов о водителе (до 5 штук)
   - Кнопка "Оставить отзыв" (только для завершённых поездок, если пользователь может оставить отзыв)
   - Звёздный рейтинг (кликабельные звёзды)
   - Текстовое поле для отзыва

3. **Интеграция в ProfilePage** (`frontend/src/pages/ProfilePage.tsx`)
   - Отображение списка отзывов о пользователе
   - Показ рейтинга (средний) и количества отзывов

4. **Переводы** (`frontend/src/locales/ru.json`, `en.json`)
   - Есть базовые строки: `"reviews": "Отзывов"`, `"reviewsTitle": "Отзывы"`, `"noReviews": "Отзывов пока нет"`

---

## 🎯 Задачи для полной реализации системы отзывов

### **Приоритет 1 — Критически важные недостающие функции**

#### 1.1. Реализовать отсутствующие эндпоинты (Backend)

**A. Получение отзывов, оставленных текущим пользователем**
- **Эндпоинт**: `GET /reviews/me`
- **Описание**: Получить все отзывы, которые текущий пользователь оставил о других (как автор)
- **Параметры запроса**: `status` (опционально), `page`, `page_size`
- **Ответ**: `ReviewList` с данными отзывов, включая информацию о поездке и получателе
- **Доступ**: Только авторизованный пользователь (свои отзывы)

**B. Улучшить схему `ReviewReadWithUsers`**
- Добавить поля: `author_first_name`, `author_last_name`, `author_avatar_url`, `target_first_name`, `target_last_name`, `target_avatar_url`
- Или создать отдельную схему `ReviewDetail` с вложенными объектами `author` и `target` (полная информация о пользователях)

**C. Endpoint для статистики отзывов о пользователе**
- **Эндпоинт**: `GET /reviews/users/{user_id}/stats`
- **Ответ**: `{ "rating_average": float, "rating_count": int, "rating_distribution": {5: 10, 4: 5, 3: 2, 2: 1, 1: 0} }`
- **Использование**: Для отображения статистики в профиле

**D. Endpoint для bulk-получения отзывов по списку ID**
- **Эндпоинт**: `POST /reviews/batch`
- **Тело**: `{ "ids": ["uuid1", "uuid2", ...] }`
- **Ответ**: массив `ReviewReadWithUsers`
- **Использование**: Для отображения отзывов на карточках поездок/пользователей

#### 1.2. Создать переиспользуемые UI компоненты (Frontend)

**A. Компонент `StarRating`** (`frontend/src/components/ui/StarRating.tsx`)
- **Props**: `rating` (number), `onChange` (optional), `readonly` (boolean), `size` (sm/md/lg)
- **Функционал**:
  - Отображение 5 звёзд (заполненные/пустые)
  - При `onChange` — кликабельные звёзды
  - Поддержка half-star (для отображения, не для установки)
  - Hover-эффекты
- **Стили**: CSS Module или Tailwind (если будет добавлен)

**B. Компонент `ReviewCard`** (`frontend/src/components/ReviewCard.tsx`)
- **Props**: `review: ReviewReadWithUsers`, `showAuthorInfo` (boolean)
- **Отображает**:
  - Аватар автора (или placeholder)
  - Имя автора (кликабельно → переход в профиль)
  - Звёздный рейтинг (StarRating, readonly)
  - Текст отзыва (с ограничением по длине, "Показать ещё")
  - Дата отзыва (относительное время: "2 дня назад")
  - При необходимости — статус отзыва (для модераторов/админов)
- **Стили**: Карточка с тенью, отступами

**C. Компонент `ReviewList`** (`frontend/src/components/ReviewList.tsx`)
- **Props**: `userId` | `tripId`, `filterStatus?`, `initialPage?`
- **Функционал**:
  - Загрузка отзывов через React Query
  - Пагинация (инфинити-скролл или кнопки "След./Пред.")
  - Фильтр по статусу (только published, только pending и т.д.)
  - Сортировка: по дате (новые/старые), по рейтингу (высокие/низкие)
  - Отображение пустого состояния
  - Skeleton-загрузка
- **Использование**: На странице профиля и на странице поездки

**D. Компонент `ReviewModal`** (`frontend/src/components/ReviewModal.tsx`)
- **Props**: `isOpen`, `onClose`, `tripId`, `targetUserId`, `existingReview?`
- **Функционал**:
  - Форма с полями: рейтинг (StarRating), текст отзыва (textarea с лимитом 2000 символов, счётчик)
  - Валидация: рейтинг обязателен, текст необязателен
  - Предпросмотр отзыва (опционально)
  - Кнопки: "Отправить", "Отмена"
  - Обработка ошибок от API
  - После успешного создания — обновление кэша React Query
- **Замена**: Удалить инлайн-логику из TripPage.tsx

#### 1.3. Добавить страницу "Мои отзывы" (Frontend)

**Файл**: `frontend/src/pages/MyReviewsPage.tsx`
- **Маршрут**: `/reviews/me` (добавить в `App.tsx` или `routes.tsx`)
- **Отображает**:
  - Две вкладки: "Оставленные" (мои отзывы) и "Полученные" (отзывы обо мне)
  - Для каждой вкладки — `ReviewList` с фильтрами по статусу
  - Для "Оставленные": список отзывов с информацией о поездке и получателе
  - Для "Полученные": список отзывов с информацией об авторе и поездке
  - При клике на отзыв/пользователя/поездку — переход на соответствующую страницу
- **Навигация**: Добавить ссылку в профиле (например, "Мои отзывы") и в меню (опционально)

---

### **Приоритет 2 — Важные улучшения**

#### 2.1. Модерация отзывов (Backend + Frontend)

**A. Роли и права**
- Только `admin` может менять статус отзыва на `published` или `rejected`
- Автор отзыва может изменить статус с `pending` на `deleted` (удаление)
- Эндпоинт `PUT /reviews/{id}` должен проверять роль пользователя

**B. Endpoint для модерации (Admin)**
- **Роутер**: `app/api/v1/admin/reviews/router.py` (создать)
- **Эндпоинты**:
  - `GET /admin/reviews/pending` — список отзывов на модерации (с пагинацией, фильтрами)
  - `PUT /admin/reviews/{id}/approve` — одобрить (status=published)
  - `PUT /admin/reviews/{id}/reject` — отклонить (status=rejected)
  - `POST /admin/reviews/batch-action` — массовые действия
- **Доступ**: Только `admin` роль

**C. Frontend: Страница модерации** (`frontend/src/pages/AdminReviewsPage.tsx`)
- Таблица отзывов: ID, автор, получатель, поездка, рейтинг, текст, дата
- Фильтры: по статусу (pending), по дате
- Действия: Одобрить / Отклонить (с возможностью указать причину отклонения)
- Кнопки в каждой строке

#### 2.2. Автоматическое обновление рейтинга пользователя

**A. Backend: Триггер или сервисный метод**
- При изменении статуса отзыва на `published` — пересчитывать `rating_average` и `rating_count` у `target` пользователя
- При удалении/отклонении отзыва — также пересчитывать
- Формула: `rating_average = SUM(rating * count) / total_count` (всего published отзывов)
- **Где вызывать**:
  - В `ReviewService.update_review_status` (при переходе на published/rejected)
  - В `ReviewService.delete_review` (при удалении)
  - В `ReviewService.create_review` (при создании published отзыва, если обойти модерацию)

**B. Альтернатива: Materialized view или вычисляемое поле**
- Можно хранить агрегаты в таблице `user_rating_stats` и обновлять через триггеры или периодически

#### 2.3. Уведомления (Notifications)

**Интеграция с существующей системой уведомлений** (`app/services/notifications/`)
- Событие: `review_received` — когда пользователь получает новый отзыв
- Событие: `review_status_changed` — когда статус отзыва изменён (модерация)
- Типы уведомлений в БД: добавить `REVIEW_RECEIVED`, `REVIEW_PUBLISHED`, `REVIEW_REJECTED`
- Шаблоны писем/уведомлений:
  - "Вы получили новый отзыв от {author_name} с оценкой {rating}★"
  - "Ваш отзыв был {одобрен/отклонён} модератором"

#### 2.4. Отзывы о пассажирах

**Текущая логика**: Отзыв можно оставить только водителю (target_id = driver_id)
**Расширение**: Разрешить водителю оставлять отзыв пассажирам
- Изменить валидацию: участники поездки могут оставлять отзывы друг другу
- Ограничение: 1 отзыв на пару (автор, target, trip_id)
- В интерфейсе: на странице поездки отображать отзывы и о пассажирах (если они есть)

#### 2.5. Редактирование отзыва

**Backend**:
- `PUT /reviews/{id}` — обновление текста отзыва (только автор, только если статус `pending`)
- Нельзя менять рейтинг после создания (или можно? уточнить)

**Frontend**:
- Кнопка "Редактировать" на своём отзыве (в разделе "Мои отзывы")
- Модальное окно с формой (аналогично созданию)

---

### **Приоритет 3 — UX/UI улучшения**

#### 3.1. Улучшить отображение отзывов

**A. Сортировка и фильтрация**
- Сортировка: по дате (новые/старые), по рейтингу (высокие/низкие)
- Фильтр по рейтингу (5 звёзд, 4 звезды и т.д.)
- Фильтр по наличию текста

**B. Группировка отзывов**
- На странице профиля: группировать по поездкам (все отзывы от одного пассажира/водителя по одной поездке)
- Или показывать все отзывы в хронологическом порядке

**C. Статистика в профиле**
- Распределение оценок (гистограмма): 5★ (10), 4★ (5), 3★ (2), 2★ (1), 1★ (0)
- График динамики рейтинга (по месяцам)

#### 3.2. Улучшить модальное окно отзыва

**A. UX-улучшения**
- Показывать информацию о поездке (маршрут, дата, машина) в заголовке модального окна
- Показывать фото/аватар target-пользователя
- Подсказки: "Отзыв будет опубликован после проверки модератором"
- Счётчик символов: "Осталось 2000 символов"
- Кнопка "Очистить" для сброса формы

**B. Валидация**
- Рейтинг обязателен (выделить красным, если не выбран)
- При отправке — показать лоадер на кнопке
- Обработка ошибок: "Вы уже оставляли отзыв на эту поездку", "Поездка не завершена" и т.д.

#### 3.3. Анимации и микро-взаимодействия

- Плавное появление звёзд при hover
- Анимация отправки отзыва (спиннер, затем success-галочка)
- Skeleton-загрузка для списка отзывов
- Empty state: иконка, текст "Отзывов пока нет", призыв "Станьте первым, кто оставит отзыв"

---

### **Приоритет 4 — Дополнительные фичи**

#### 4.1. Ответы на отзывы (Reply)

**Backend**:
- Добавить в модель `Review` поле `parent_id` (ссылка на родительский отзыв, для цепочки)
- Или создать отдельную модель `ReviewReply` с полями: `id`, `review_id`, `author_id`, `text`, `created_at`
- Ограничение: только один ответ на отзыв (или несколько? уточнить)
- Ответ может оставить:
  - Автор отзыва (на отзыв о себе) — да
  - Получатель отзыва (на отзыв о нём) — да
  - Админ — да (как модератор)

**Frontend**:
- Под каждым отзывом — кнопка "Ответить" (только если вы — автор или получатель)
- Модальное окно/инлайн-форма для ответа
- Отображение ответа сразу под отзывом (с отступом, другим фоном)

#### 4.2. Голосование "Полезен/Не полезен"

**Backend**:
- Модель `ReviewVote`: `id`, `review_id`, `user_id`, `is_helpful` (boolean), `created_at`
- Unique constraint: (`review_id`, `user_id`)
- Endpoint: `POST /reviews/{id}/vote`, `DELETE /reviews/{id}/vote`
- Счётчики: `helpful_count`, `unhelpful_count` в модели `Review` (кэшируемые поля)

**Frontend**:
- Кнопки "Полезно" / "Не полезно" под каждым отзывом
- Подсветка активной кнопки (если пользователь уже проголосовал)
- Отображение счётчика: "12 человек считают полезным"

#### 4.3. Жалобы на отзывы (Report)

**Backend**:
- Модель `ReviewReport`: `id`, `review_id`, `reporter_id`, `reason` (enum: spam, offensive, irrelevant, other), `description`, `status` (pending, reviewed, dismissed), `created_at`
- Endpoint: `POST /reviews/{id}/report` (создание жалобы)
- Endpoint (admin): `GET /admin/reviews/reports`, `PUT /admin/reviews/reports/{id}/resolve`

**Frontend**:
- Кнопка "Пожаловаться" под отзывом
- Модальное окно с выбором причины и текстовым полем
- После отправки — "Жалоба отправлена, спасибо"

#### 4.4. Флаги и улучшения

- **Оптимистичные обновления** в React Query (optimistic updates)
- **Кэширование** агрегированных данных рейтинга (Redis, если нужна производительность)
- **Поиск** по тексту отзывов (Full-text search в PostgreSQL)
- **Экспорт** отзывов (PDF/CSV для водителя — его отзывы)
- **Рейтинг-символы**: кроме звёзд — можно добавить "сердечки" или другие эмодзи (опционально)

---

## 🛠️ Технические требования и ограничения

### Backend
- **Python 3.11+**, FastAPI, async/await везде
- **База данных**: PostgreSQL 15+
- **Миграции**: Alembic (файлы в `app/db/migration/versions/`)
- **Валидация**: Pydantic v2
- **Авторизация**: JWT токены, зависимость `get_current_user`
- **Роли**: `user`, `admin` (из `UserRole`)

### Frontend
- **React 18+**, TypeScript
- **State management**: TanStack Query (React Query) для серверного состояния, Zustand для клиентского (auth store)
- **Роутинг**: React Router v6
- **Стили**: CSS Modules (существующие файлы `.module.css`)
- **i18n**: react-i18next, переводы в `locales/`

---

## 📁 Структура файлов (рекомендуемая)

### Backend (новые/изменяемые файлы)
```
app/
├── api/
│   ├── v1/
│   │   ├── reviews/
│   │   │   └── router.py          ← расширить существующий
│   │   └── admin/
│   │       └── reviews/
│   │           └── router.py       ← НОВЫЙ
├── models/
│   └── reviews/
│       └── model.py               ← добавить поля: helpful_count, unhelpful_count, parent_id (опционально)
├── schemas/
│   └── reviews.py                 ← добавить: ReviewDetail, ReviewStats, ReviewVote, ReviewReply
├── services/
│   └── reviews/
│       └── service.py             ← добавить: update_rating_stats, create_reply, vote, report
├── repositories/
│   └── reviews/
│       └── repository.py          ← добавить методы для новых фич
└── db/
    └── migration/
        └── versions/              ← НОВЫЕ миграции для новых таблиц/полей
```

### Frontend (новые/изменяемые файлы)
```
frontend/src/
├── components/
│   ├── ui/
│   │   ├── StarRating.tsx          ← НОВЫЙ
│   │   ├── ReviewCard.tsx          ← НОВЫЙ
│   │   └── ReviewList.tsx          ← НОВЫЙ
│   ├── ReviewModal.tsx             ← НОВЫЙ (вынести из TripPage)
│   └── ReviewReplyForm.tsx         ← НОВЫЙ (опционально)
├── pages/
│   ├── MyReviewsPage.tsx           ← НОВЫЙ
│   ├── AdminReviewsPage.tsx        ← НОВЫЙ (для админов)
│   ├── TripPage.tsx                ← ИЗМЕНИТЬ: заменить инлайн-модалку на ReviewModal
│   └── ProfilePage.tsx             ← ИЗМЕНИТЬ: использовать ReviewList компонент
├── services/
│   └── api/
│       └── reviews.ts              ← расширить методы
├── types/
│   └── index.ts                    ← добавить типы Review, ReviewStats
└── locales/
    ├── ru.json                     ← добавить переводы для reviews
    └── en.json                     ← добавить переводы для reviews
```

---

## 🧪 Тестирование

### Backend (pytest)
- **Unit-тесты** для `ReviewService`:
  - `test_create_review_success()`
  - `test_create_review_trip_not_completed()`
  - `test_create_review_self_review()`
  - `test_create_review_not_participant()`
  - `test_create_review_duplicate()`
  - `test_update_rating_stats()`
- **Интеграционные тесты** для эндпоинтов (TestClient):
  - `test_create_review_endpoint()`
  - `test_get_user_reviews()`
  - `test_get_trip_reviews()`
  - `test_admin_moderation()`

### Frontend (Vitest + React Testing Library)
- **Компоненты**:
  - `StarRating`: клики, hover, readonly
  - `ReviewCard`: отображение данных, переходы
  - `ReviewList`: пагинация, фильтры
  - `ReviewModal`: валидация, отправка
- **Страницы**:
  - `MyReviewsPage`: загрузка, вкладки
  - `TripPage`: отзывы о водителе, модалка

---

## 📝 План реализации (пошагово)

### Этап 1 — Бэкенд (основной функционал)
1. ✅ Добавить в `Review` модель: `helpful_count` (default=0), `unhelpful_count` (default=0)
2. ✅ Добавить в `schemas/reviews.py`:
   - `ReviewDetail` (с вложенными author/target)
   - `ReviewStats` (статистика)
   - `ReviewVoteBase`, `ReviewVoteCreate`
3. ✅ Создать `app/models/reviews/vote.py` (модель ReviewVote)
4. ✅ Создать/обновить `app/repositories/reviews/repository.py`:
   - `get_by_id_with_users()`
   - `get_user_reviews_with_details()`
   - `get_trip_reviews_with_details()`
   - `update_helpful_counts()`
   - `get_review_stats()`
5. ✅ Обновить `app/services/reviews/service.py`:
   - Добавить `get_review_details()`
   - Добавить `get_user_review_stats()`
   - Добавить `vote_review()`
   - Обновить `create_review()` для возврата полных данных
6. ✅ Добавить эндпоинты в `router.py`:
   - `GET /reviews/me` (мои отзывы)
   - `GET /reviews/user/{user_id}/stats` (статистика)
   - `POST /reviews/{id}/vote` (голосование)
7. ✅ Создать `app/api/v1/admin/reviews/router.py`:
   - `GET /admin/reviews/pending`
   - `PUT /admin/reviews/{id}/approve`
   - `PUT /admin/reviews/{id}/reject`
8. ✅ Написать миграции Alembic для новых таблиц/полей

### Этап 2 — Фронтенд (основной функционал)
1. ✅ Создать `components/ui/StarRating.tsx`
2. ✅ Создать `components/ReviewCard.tsx`
3. ✅ Создать `components/ReviewList.tsx`
4. ✅ Создать `components/ReviewModal.tsx` (вынести логику из TripPage)
5. ✅ Обновить `TripPage.tsx`: заменить инлайн-логику на `ReviewModal` и `ReviewList`
6. ✅ Обновить `ProfilePage.tsx`: заменить инлайн-логику на `ReviewList`
7. ✅ Создать `pages/MyReviewsPage.tsx`
8. ✅ Добавить маршрут в `App.tsx`: `/reviews/me`
9. ✅ Добавить ссылку "Мои отзывы" в профиль (меню или страницу профиля)
10. ✅ Обновить локализацию: `locales/ru.json`, `locales/en.json`

### Этап 3 — Дополнительные фичи (по приоритету)
1. Ответы на отзывы (ReviewReply)
2. Жалобы на отзывы (ReviewReport)
3. Редактирование отзыва
4. Отзывы о пассажирах
5. Уведомления о новых отзывах

---

## 🎨 Дизайн-система (стили)

Использовать существующую CSS-архитектуру:
- **Модули CSS**: `ReviewCard.module.css`, `ReviewList.module.css`, `StarRating.module.css`
- **Цвета** (из существующих файлов):
  - Основной: `#007bff` (синий)
  - Успех: `#28a745` (зелёный)
  - Ошибка: `#dc3545` (красный)
  - Предупреждение: `#ffc107` (жёлтый)
  - Текст: `#333`, `#666`, `#999`
  - Фон: `#f8f9fa`, `#fff`
- **Звёзды**: цвет `#ffc107` (жёлтый) для заполненных, `#e0e0e0` для пустых
- **Размеры**:
  - StarRating: `sm` (16px), `md` (24px), `lg` (32px)
  - Card: padding `16px`, margin-bottom `12px`, border-radius `8px`, box-shadow `0 2px 4px rgba(0,0,0,0.1)`

---

## 🔐 Безопасность и валидация

- **Авторизация**: Все эндпоинты требуют `get_current_user`
- **Права**:
  - Создание отзыва: только участник поездки
  - Удаление: только автор
  - Обновление статуса: автор (только свой) или admin
  - Просмотр: любые (можно ограничить только published для чужих профилей)
- **Валидация**:
  - Рейтинг: 1-5
  - Текст: max 2000 символов
  - Защита от дублей: UniqueConstraint на уровне БД + проверка в сервисе
- **SQL-инъекции**: Использовать параметризованные запросы (SQLAlchemy)
- **XSS**: Экранирование текста отзыва при отображении (React по умолчанию экранирует)

---

## 📈 Производительность

- **Индексы** в БД: уже есть (`trip_id`, `author_id`, `target_id`, `status`, `created_at`)
- **Пагинация**: 20 записей на страницу (настраиваемо)
- **Кэширование**:
  - React Query: кэшировать списки отзывов (5 мин)
  - Кэшировать статистику пользователя (10 мин)
- **N+1 проблема**: Использовать `selectinload` в repository для загрузки связанных сущностей (author, target, trip)
- **Ленивая загрузка**: На странице профиля загружать только первые 5 отзывов, остальные по клику "Показать ещё"

---

## 🌐 Интернационализация (i18n)

Добавить в `locales/ru.json` и `locales/en.json`:

```json
{
  "reviews": {
    "title": "Отзывы",
    "reviews": "отзывов",
    "reviewsTitle": "Отзывы",
    "noReviews": "Отзывов пока нет",
    "writeReview": "Оставить отзыв",
    "reviewPlaceholder": "Расскажите о вашей поездке...",
    "reviewAbout": "Отзыв о {name}",
    "reviewForTrip": "За поездку от {date}",
    "rating": "Оценка",
    "yourReview": "Ваш отзыв",
    "reviewsAboutMe": "Отзывы обо мне",
    "reviewsWritten": "Оставленные отзывы",
    "charactersLeft": "{count} символов осталось",
    "maxLength": "Максимум 2000 символов",
    "submit": "Отправить отзыв",
    "submitting": "Отправка...",
    "success": "Отзыв успешно отправлен на модерацию",
    "pending": "На модерации",
    "published": "Опубликован",
    "rejected": "Отклонён",
    "editReview": "Редактировать отзыв",
    "deleteReview": "Удалить отзыв",
    "confirmDelete": "Вы уверены, что хотите удалить этот отзыв?",
    "reply": "Ответить",
    "replyPlaceholder": "Напишите ответ...",
    "helpful": "Полезно",
    "notHelpful": "Не полезно",
    "report": "Пожаловаться",
    "reportReason": "Причина жалобы",
    "reportSpam": "Спам",
    "reportOffensive": "Оскорбительный контент",
    "reportIrrelevant": "Не относится к поездке",
    "reportOther": "Другое",
    "reportDescription": "Опишите проблему (необязательно)",
    "reportSubmit": "Отправить жалобу",
    "moderation": "Модерация отзывов",
    "pendingCount": "Ожидают модерации: {count}",
    "approve": "Одобрить",
    "reject": "Отклонить",
    "rejectReason": "Причина отклонения (необязательно)",
    "stats": "Статистика отзывов",
    "ratingDistribution": "Распределение оценок",
    "basedOnCount": "на основе {count} отзывов"
  }
}
```

---

## 🧪 Acceptance Criteria (Definition of Done)

### Для базовой реализации (MVP):
- [ ] Backend: Все эндпоинты работают, валидация на месте
- [ ] Backend: Миграции применены, данные не теряются
- [ ] Frontend: Компоненты `StarRating`, `ReviewCard`, `ReviewList`, `ReviewModal` созданы и работают
- [ ] Frontend: Страница `MyReviewsPage` доступна по `/reviews/me`
- [ ] Frontend: На странице поездки отзывы о водителе отображаются, модалка создания работает
- [ ] Frontend: На странице профиля отзывы отображаются через `ReviewList`
- [ ] Переводы: все строки на русском и английском
- [ ] Тесты: unit-тесты для сервиса (покрытие >80%), компонентные тесты для StarRating и ReviewCard
- [ ] Документация: обновлён `ARCHITECTURE.md` (если нужно) и `DATABASE_SCHEMA.md`

### Для полной реализации:
- [ ] Модерация отзывов (админ-панель)
- [ ] Автоматическое обновление рейтинга пользователя
- [ ] Уведомления о новых отзывах
- [ ] Голосование "Полезен/Не полезен"
- [ ] Ответы на отзывы
- [ ] Жалобы на отзывы
- [ ] Отзывы о пассажирах

---

## 🚀 Запуск и разработка

### Backend
```bash
cd D:/RoadMate
# Активация venv
.venv\Scripts\activate  # Windows
# или source .venv/bin/activate  # Linux/Mac

# Установка зависимостей
pip install -r requirements.txt

# Запуск миграций
alembic upgrade head

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# или yarn dev
```

### Документация API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📚 Ссылки на существующий код

- **Модель Review**: `app/models/reviews/model.py:35-165`
- **Схемы**: `app/schemas/reviews.py:1-78`
- **API роутер**: `app/api/v1/reviews/router.py:1-213`
- **Сервис**: `app/services/reviews/service.py:1-260`
- **Repository**: `app/repositories/reviews/repository.py:1-187`
- **Frontend API**: `frontend/src/services/api/reviews.ts:1-101`
- **TripPage (отзывы)**: `frontend/src/pages/TripPage.tsx:31-203, 327-345, 678-748`
- **ProfilePage (отзывы)**: `frontend/src/pages/ProfilePage.tsx:288-325`
- **Переводы**: `frontend/src/locales/ru.json:240-242`, `frontend/src/locales/en.json:239-241`

---

## 💡 Рекомендации и best practices

1. **Сначала бэкенд, потом фронтенд** — реализовать API, протестировать через Swagger, затем подключать фронтенд
2. **Миграции** — всегда создавать новую миграцию при изменении моделей: `alembic revision --autogenerate -m "description"`
3. **Тесты** — писать тесты параллельно с кодом (TDD подход)
4. **Коммиты** — атомарные, с понятными сообщениями: `feat(reviews): add user reviews endpoint`
5. **Код-ревью** — проверить коллег, особенно бизнес-логику валидаций
6. **i18n** — все строки в интерфейсе через `t('key')`, добавлять в оба языковых файла
7. **Документация** — обновлять docstrings в Python и JSDoc в TypeScript
8. **Обработка ошибок** — единый формат ошибок API (FastAPI `HTTPException` с `detail`)
9. **Логирование** — добавить логи в сервисе (создание, удаление, модерация)
10. **Мониторинг** — опционально: метрики (количество отзывов, средний рейтинг)

---

## 🎯 Критерии приёмки (Acceptance Criteria)

### Сценарий: Пользователь оставляет отзыв после поездки
1. Поездка имеет статус `completed`
2. Пользователь (пассажир или водитель) заходит на страницу поездки
3. Видит кнопку "Оставить отзыв" (если ещё не оставлял)
4. Нажимает → открывается модальное окно
5. Выбирает рейтинг (1-5 звёзд)
6. Пишет текст (опционально, до 2000 символов)
7. Нажимает "Отправить"
8. Отзыв создаётся со статусом `pending`
9. Получает уведомление "Отзыв отправлен на модерацию"
10. Отзыв появляется в списке "Мои отзывы" на странице `/reviews/me`

### Сценарий: Админ модерирует отзывы
1. Админ заходит в админ-панель → "Отзывы"
2. Видит список отзывов со статусом `pending`
3. Может:
   - Одобрить → статус меняется на `published`, пользователь получает уведомление
   - Отклонить → статус меняется на `rejected`, пользователь получает уведомление с причиной (опционально)
4. После одобрения рейтинг пользователя обновляется автоматически

### Сценарий: Просмотр отзывов о пользователе
1. Пользователь заходит на страницу профиля любого пользователя
2. Видит вкладку "Отзывы" или секцию с отзывами
3. Видит список отзывов (только `published` для чужих, все для своего профиля)
4. Может фильтровать по рейтингу, сортировать по дате
5. Видит средний рейтинг и гистограмму распределения

---

## 📞 Контакты и поддержка

При возникновении вопросов по реализации:
- Архитектура: `ARCHITECTURE.md`
- Схема БД: `DATABASE_SCHEMA.md`
- Модели: `MODELS_DOCUMENTATION.md`
- existing code: см. ссылки выше

---

**Удачи в реализации! 🚀**
