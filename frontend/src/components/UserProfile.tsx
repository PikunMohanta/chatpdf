import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './UserProfile.css'

const UserProfile = () => {
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen)
  }

  return (
    <div className="user-profile">
      <motion.button
        className="profile-avatar"
        onClick={toggleDropdown}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <img
          src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
          alt="User Avatar"
          className="avatar-image"
        />
      </motion.button>

      <AnimatePresence>
        {dropdownOpen && (
          <>
            <motion.div
              className="dropdown-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setDropdownOpen(false)}
            />
            <motion.div
              className="profile-dropdown"
              initial={{ opacity: 0, y: -10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
            >
              <div className="dropdown-header">
                <img
                  src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
                  alt="User Avatar"
                  className="dropdown-avatar"
                />
                <div className="dropdown-user-info">
                  <p className="dropdown-name">Demo User</p>
                  <p className="dropdown-email">demo@pdfpal.com</p>
                </div>
              </div>

              <div className="dropdown-divider" />

              <div className="dropdown-menu">
                <motion.button
                  className="dropdown-item"
                  whileHover={{ backgroundColor: 'rgba(79, 70, 229, 0.05)', x: 4 }}
                  onClick={() => {
                    console.log('Settings clicked')
                    setDropdownOpen(false)
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                    />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Settings
                </motion.button>

                <motion.button
                  className="dropdown-item"
                  whileHover={{ backgroundColor: 'rgba(79, 70, 229, 0.05)', x: 4 }}
                  onClick={() => {
                    console.log('Help clicked')
                    setDropdownOpen(false)
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Help & Support
                </motion.button>

                <div className="dropdown-divider" />

                <motion.button
                  className="dropdown-item logout"
                  whileHover={{ backgroundColor: 'rgba(239, 68, 68, 0.05)', x: 4 }}
                  onClick={() => {
                    console.log('Logout clicked')
                    setDropdownOpen(false)
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                    />
                  </svg>
                  Logout
                </motion.button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

export default UserProfile
