/**
 * Clear PDFPixie localStorage data
 * Run this in browser console to reset the application to fresh state
 */
function clearPDFPixieData() {
  try {
    // Clear chat sessions
    localStorage.removeItem('chat_sessions')
    
    // Clear any other PDFPixie related data
    const keysToRemove = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && (key.includes('pdf') || key.includes('chat') || key.includes('session'))) {
        keysToRemove.push(key)
      }
    }
    
    keysToRemove.forEach(key => localStorage.removeItem(key))
    
    console.log('✅ PDFPixie data cleared successfully!')
    console.log('📄 Refresh the page to see the clean welcome screen')
    
    return {
      cleared: true,
      removedKeys: ['chat_sessions', ...keysToRemove]
    }
  } catch (error) {
    console.error('❌ Error clearing data:', error)
    return { cleared: false, error: error.message }
  }
}

// Make function available globally
window.clearPDFPixieData = clearPDFPixieData

console.log('🧹 PDFPixie Storage Cleaner loaded!')
console.log('📋 Run clearPDFPixieData() to reset the application')