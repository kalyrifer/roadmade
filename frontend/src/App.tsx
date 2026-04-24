import { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ErrorBoundary from './components/ErrorBoundary';
import { useAuthStore } from './stores/auth';
import { Skeleton } from './components/ui';
import { ToastContainer } from './components/ui/Toast';

// Lazy loaded pages
const HomePage = lazy(() => import('./pages/HomePage'));
const TripsPage = lazy(() => import('./pages/TripsPage'));
const TripPage = lazy(() => import('./pages/TripPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const MyTripsPage = lazy(() => import('./pages/MyTripsPage'));
const NewTripPage = lazy(() => import('./pages/NewTripPage'));
const MyRequestsPage = lazy(() => import('./pages/MyRequestsPage'));
const DriverRequestsPage = lazy(() => import('./pages/DriverRequestsPage'));
const EditTripPage = lazy(() => import('./pages/EditTripPage'));
const ChatListPage = lazy(() => import('./pages/ChatListPage'));
const ChatPage = lazy(() => import('./pages/ChatPage'));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'));

// Loading fallback
function PageLoader() {
  return (
    <div style={{ padding: '40px', display: 'flex', justifyContent: 'center' }}>
      <Skeleton width="100%" height={200} />
    </div>
  );
}

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function App() {
  return (
    <Layout>
      <ErrorBoundary>
        <Suspense fallback={<PageLoader />}>
          <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/trips" element={<TripsPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes - must be before /trips/:id */}
          <Route
            path="/trips/my"
            element={
              <ProtectedRoute>
                <MyTripsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/requests/my"
            element={
              <ProtectedRoute>
                <MyRequestsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/requests/driver"
            element={
              <ProtectedRoute>
                <DriverRequestsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trips/new"
            element={
              <ProtectedRoute>
                <NewTripPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trips/:id/edit"
            element={
              <ProtectedRoute>
                <EditTripPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <ChatListPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat/:id"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/notifications"
            element={
              <ProtectedRoute>
                <NotificationsPage />
              </ProtectedRoute>
            }
          />

          {/* Dynamic route - must be after specific routes */}
          <Route path="/trips/:id" element={<TripPage />} />
          
          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </Suspense>
      </ErrorBoundary>
      <ToastContainer />
    </Layout>
  );
}

export default App;
