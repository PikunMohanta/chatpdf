import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({
      error,
      errorInfo
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          padding: '2rem',
          textAlign: 'center'
        }}>
          <div style={{
            background: '#fee',
            border: '2px solid #fcc',
            borderRadius: '12px',
            padding: '2rem',
            maxWidth: '600px'
          }}>
            <h2 style={{ color: '#c33', marginBottom: '1rem' }}>
              ⚠️ Something went wrong
            </h2>
            <p style={{ color: '#666', marginBottom: '1rem' }}>
              The application encountered an error. Please try refreshing the page.
            </p>
            {this.state.error && (
              <details style={{ 
                marginTop: '1rem', 
                padding: '1rem', 
                background: '#fff',
                borderRadius: '8px',
                textAlign: 'left'
              }}>
                <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                  Error Details
                </summary>
                <pre style={{ 
                  marginTop: '0.5rem',
                  fontSize: '0.875rem',
                  color: '#c33',
                  overflow: 'auto'
                }}>
                  {this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
            <button
              onClick={this.handleReset}
              style={{
                marginTop: '1.5rem',
                padding: '0.75rem 1.5rem',
                background: '#4f46e5',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              🔄 Refresh Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
