import { motion } from 'framer-motion'
import './SplashScreen.css'

interface SplashScreenProps {
  onComplete: () => void
}

const SplashScreen = ({ onComplete }: SplashScreenProps) => {
  return (
    <motion.div
      className="splash-screen"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.5 }}
    >
      <motion.div
        className="splash-content"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      >
        <motion.h1
          className="app-name"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{
            duration: 1,
            ease: 'easeOut',
            delay: 0.2,
          }}
        >
          <motion.span
            className="app-name-pdf"
            animate={{
              textShadow: [
                '0 0 20px rgba(79, 70, 229, 0.5)',
                '0 0 40px rgba(79, 70, 229, 0.8)',
                '0 0 20px rgba(79, 70, 229, 0.5)',
              ],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            PDF
          </motion.span>
          {' '}
          <motion.span
            className="app-name-pal"
            animate={{
              color: ['#4f46e5', '#818cf8', '#4f46e5'],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          >
            Pal
          </motion.span>
        </motion.h1>

        <motion.p
          className="app-tagline"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
        >
          Your intelligent document companion
        </motion.p>

        <motion.button
          className="splash-button"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5, duration: 0.5 }}
          whileHover={{ scale: 1.05, boxShadow: '0 10px 30px rgba(79, 70, 229, 0.3)' }}
          whileTap={{ scale: 0.95 }}
          onClick={onComplete}
        >
          Get Started
          <motion.span
            className="button-arrow"
            animate={{ x: [0, 5, 0] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          >
            →
          </motion.span>
        </motion.button>
      </motion.div>

      <motion.div
        className="splash-background-effect"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.1, 0.2, 0.1],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
    </motion.div>
  )
}

export default SplashScreen
