/**
 * Device ID Manager
 * 
 * Generates and persists a unique device identifier in localStorage
 * to isolate chat history per browser/device.
 * 
 * This prevents chat history from appearing across different devices.
 */

const DEVICE_ID_KEY = 'pdfpixie_device_id';

/**
 * Generate a unique device ID
 * Format: device_<timestamp>_<random>
 */
function generateDeviceId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 15);
  return `device_${timestamp}_${random}`;
}

/**
 * Device ID Manager Class
 */
export class DeviceIdManager {
  private static STORAGE_KEY = DEVICE_ID_KEY;

  /**
   * Get or create a unique device identifier
   */
  static getDeviceId(): string {
    try {
      let deviceId = localStorage.getItem(this.STORAGE_KEY);
      
      if (!deviceId) {
        // Generate new device ID if none exists
        deviceId = generateDeviceId();
        localStorage.setItem(this.STORAGE_KEY, deviceId);
        console.log('🆔 Generated NEW device ID:', deviceId);
      } else {
        console.log('🆔 Using EXISTING device ID:', deviceId);
      }
      
      return deviceId;
    } catch (error) {
      // Fallback if localStorage is not available (e.g., private browsing)
      console.error('Failed to access localStorage for device ID:', error);
      return generateDeviceId();
    }
  }

  /**
   * Clear device ID (for testing)
   */
  static clearDeviceId(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
      console.log('🗑️ Device ID cleared');
    } catch (error) {
      console.error('Failed to clear device ID:', error);
    }
  }

  /**
   * Get device info for debugging
   */
  static getDeviceInfo(): {
    deviceId: string;
    userAgent: string;
    platform: string;
    language: string;
    timestamp: string;
  } {
    return {
      deviceId: this.getDeviceId(),
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      timestamp: new Date().toISOString()
    };
  }
}

// Export functions for backward compatibility
export function getDeviceId(): string {
  return DeviceIdManager.getDeviceId();
}

export function clearDeviceId(): void {
  DeviceIdManager.clearDeviceId();
}

export function getDeviceInfo() {
  return DeviceIdManager.getDeviceInfo();
}

// Make it available in browser console for debugging
if (typeof window !== 'undefined') {
  (window as any).DeviceIdManager = DeviceIdManager;
}
