/**
 * Performance monitoring utilities for PDFPixie
 */

interface PerformanceMetric {
  name: string
  value: number
  timestamp: number
  metadata?: Record<string, any>
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = []
  private isEnabled: boolean

  constructor() {
    this.isEnabled = import.meta.env.VITE_ENABLE_ANALYTICS === 'true'
  }

  /**
   * Record a performance metric
   */
  recordMetric(name: string, value: number, metadata?: Record<string, any>) {
    if (!this.isEnabled) return

    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: Date.now(),
      metadata
    }

    this.metrics.push(metric)

    // In production, send to analytics service
    if (import.meta.env.PROD) {
      this.sendToAnalytics(metric)
    } else {
      console.debug('Performance metric:', metric)
    }
  }

  /**
   * Measure component render time
   */
  measureRender<T>(componentName: string, renderFn: () => T): T {
    const startTime = performance.now()
    const result = renderFn()
    const renderTime = performance.now() - startTime

    this.recordMetric(`render.${componentName}`, renderTime, {
      type: 'render',
      component: componentName
    })

    return result
  }

  /**
   * Measure async operation duration
   */
  async measureAsync<T>(operationName: string, asyncFn: () => Promise<T>): Promise<T> {
    const startTime = performance.now()
    try {
      const result = await asyncFn()
      const duration = performance.now() - startTime
      
      this.recordMetric(`async.${operationName}`, duration, {
        type: 'async',
        operation: operationName,
        success: true
      })

      return result
    } catch (error) {
      const duration = performance.now() - startTime
      
      this.recordMetric(`async.${operationName}`, duration, {
        type: 'async',
        operation: operationName,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      })

      throw error
    }
  }

  /**
   * Measure bundle load times
   */
  measureBundleLoad() {
    if (typeof window === 'undefined') return

    // Measure various loading metrics
    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming

      if (navigation) {
        this.recordMetric('page.domContentLoaded', navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart)
        this.recordMetric('page.loadComplete', navigation.loadEventEnd - navigation.loadEventStart)
        this.recordMetric('page.ttfb', navigation.responseStart - navigation.requestStart)
      }

      // Measure resource loading
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[]
      resources.forEach(resource => {
        if (resource.name.includes('.js') || resource.name.includes('.css')) {
          this.recordMetric(`resource.${this.getResourceType(resource.name)}`, resource.duration, {
            url: resource.name,
            size: resource.transferSize
          })
        }
      })
    })
  }

  /**
   * Measure Core Web Vitals
   */
  measureWebVitals() {
    if (typeof window === 'undefined') return

    // First Contentful Paint
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'first-contentful-paint') {
          this.recordMetric('webvitals.fcp', entry.startTime)
        }
        if (entry.name === 'largest-contentful-paint') {
          this.recordMetric('webvitals.lcp', entry.startTime)
        }
      }
    })

    try {
      observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] })
    } catch (e) {
      // Browser doesn't support the API
      console.debug('Performance Observer not supported')
    }

    // First Input Delay (FID)
    if ('PerformanceEventTiming' in window) {
      const fidObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          // Type assertion for PerformanceEventTiming
          const eventEntry = entry as any
          if (eventEntry.processingStart && eventEntry.startTime) {
            const fid = eventEntry.processingStart - eventEntry.startTime
            this.recordMetric('webvitals.fid', fid)
          }
        }
      })

      try {
        fidObserver.observe({ entryTypes: ['first-input'] })
      } catch (e) {
        console.debug('First Input Delay not supported')
      }
    }
  }

  /**
   * Get all recorded metrics
   */
  getMetrics(): PerformanceMetric[] {
    return [...this.metrics]
  }

  /**
   * Clear all metrics
   */
  clearMetrics() {
    this.metrics = []
  }

  /**
   * Get performance summary
   */
  getSummary() {
    const summary: Record<string, { count: number; avg: number; min: number; max: number }> = {}

    this.metrics.forEach(metric => {
      if (!summary[metric.name]) {
        summary[metric.name] = { count: 0, avg: 0, min: Infinity, max: -Infinity }
      }

      const stat = summary[metric.name]
      stat.count++
      stat.min = Math.min(stat.min, metric.value)
      stat.max = Math.max(stat.max, metric.value)
      stat.avg = (stat.avg * (stat.count - 1) + metric.value) / stat.count
    })

    return summary
  }

  private getResourceType(url: string): string {
    if (url.includes('.js')) return 'javascript'
    if (url.includes('.css')) return 'stylesheet'
    if (url.includes('.woff') || url.includes('.ttf')) return 'font'
    if (url.includes('.png') || url.includes('.jpg') || url.includes('.svg')) return 'image'
    return 'other'
  }

  private sendToAnalytics(metric: PerformanceMetric) {
    // Replace with your analytics service
    // Example: Google Analytics, Mixpanel, or custom endpoint
    console.debug('Send to analytics:', metric)
    
    // Example implementation:
    // fetch('/api/analytics', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(metric)
    // })
  }
}

// Create global instance
export const performanceMonitor = new PerformanceMonitor()

// Initialize monitoring
if (typeof window !== 'undefined') {
  performanceMonitor.measureBundleLoad()
  performanceMonitor.measureWebVitals()
}

// React Hook for component performance
export function usePerformanceMonitor(componentName: string) {
  return {
    measure: <T>(fn: () => T) => performanceMonitor.measureRender(componentName, fn),
    measureAsync: <T>(operationName: string, fn: () => Promise<T>) => 
      performanceMonitor.measureAsync(`${componentName}.${operationName}`, fn)
  }
}

export default PerformanceMonitor