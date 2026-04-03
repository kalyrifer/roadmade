import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div style={{ 
          padding: '40px', 
          textAlign: 'center',
          fontFamily: 'system-ui, sans-serif',
          backgroundColor: '#fff5f5',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <h1 style={{ color: '#d32f2f', marginBottom: '16px' }}>Что-то пошло не так</h1>
          <p style={{ color: '#666', marginBottom: '24px' }}>
            Произошла ошибка при отображении страницы. Попробуйте обновить страницу.
          </p>
          <details style={{ 
            background: '#fff', 
            padding: '16px', 
            borderRadius: '8px',
            maxWidth: '600px',
            textAlign: 'left'
          }}>
            <summary style={{ cursor: 'pointer', marginBottom: '8px', fontWeight: 600 }}>
              Технические детали
            </summary>
            <pre style={{ 
              fontSize: '12px', 
              overflow: 'auto',
              background: '#f5f5f5',
              padding: '8px',
              borderRadius: '4px'
            }}>
              {this.state.error?.toString()}
            </pre>
          </details>
          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '24px',
              padding: '12px 24px',
              background: '#FF8C42',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Обновить страницу
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;