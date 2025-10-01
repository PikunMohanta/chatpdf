# Newchat Frontend - React + TypeScript

A modern, responsive frontend for the Newchat AI-powered PDF chat application built with React, TypeScript, and Vite.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ installed
- Backend server running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The application will be available at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── UploadComponent.tsx       # PDF drag-and-drop upload
│   │   ├── UploadComponent.css
│   │   ├── ChatComponent.tsx         # Real-time AI chat interface
│   │   ├── ChatComponent.css
│   │   ├── PreviewComponent.tsx      # PDF preview with pagination
│   │   └── PreviewComponent.css
│   ├── App.tsx                       # Main application component
│   ├── App.css                       # Application styles
│   ├── main.tsx                      # Entry point
│   └── index.css                     # Global styles
├── index.html                        # HTML template
├── package.json                      # Dependencies
├── tsconfig.json                     # TypeScript configuration
├── vite.config.ts                    # Vite configuration
└── .env                              # Environment variables
```

## 🎨 Technologies

- **React 18** - Modern React with hooks
- **TypeScript 5** - Type-safe development
- **Vite** - Fast build tool and dev server
- **React Dropzone** - File upload with drag-and-drop
- **React-PDF** - PDF rendering
- **Socket.io-client** - Real-time WebSocket communication
- **Framer Motion** - Smooth animations
- **Axios** - HTTP client

## ✨ Features

### 1. Upload Component
- Drag-and-drop PDF upload
- Upload progress tracking
- File validation (PDF only, max 50MB)
- Visual feedback and error handling

### 2. Chat Component
- Real-time chat with AI via WebSocket
- Message history loading
- Typing indicators
- Suggested questions
- Auto-scroll to latest messages
- Connection status indicator

### 3. Preview Component
- PDF rendering with react-pdf
- Page navigation (previous/next)
- Direct page number input
- Responsive PDF viewer
- Loading and error states

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

### Vite Configuration

The `vite.config.ts` includes:
- React plugin for Fast Refresh
- Proxy configuration for API calls
- WebSocket proxy for Socket.io

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
  '/socket.io': {
    target: 'http://localhost:8000',
    ws: true,
  },
}
```

## 🔗 API Integration

### REST API Endpoints

- `POST /api/upload` - Upload PDF file
- `GET /api/chat/history/:documentId` - Get chat history
- `GET /api/document/:documentId/preview` - Get PDF file

### WebSocket Events

- `connect` - Establish connection
- `query` - Send chat message
- `response` - Receive AI response
- `error` - Handle errors

## 📱 Responsive Design

The application is fully responsive with breakpoints:
- Desktop: 1024px+
- Tablet: 768px - 1024px
- Mobile: < 768px

## 🎯 Component APIs

### UploadComponent

```typescript
interface UploadComponentProps {
  onUploadSuccess: (docInfo: {
    id: string;
    filename: string;
    file_path: string;
  }) => void;
}
```

### ChatComponent

```typescript
interface ChatComponentProps {
  documentId: string;
}
```

### PreviewComponent

```typescript
interface PreviewComponentProps {
  documentId: string;
}
```

## 🔍 TypeScript Configuration

- Strict mode enabled
- ES2020 target
- JSX: react-jsx
- Module resolution: bundler
- Source maps enabled for debugging

## 🛠️ Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR. Changes to components are reflected immediately without full page reloads.

### Type Checking

```bash
# Run TypeScript compiler to check types
npm run build

# Or use tsc in watch mode
npx tsc --noEmit --watch
```

### Linting

```bash
# Run ESLint
npm run lint
```

## 🐛 Troubleshooting

### PDF not loading

1. Check backend is running on correct port
2. Verify `VITE_API_URL` in `.env`
3. Check browser console for CORS errors
4. Ensure PDF.js worker is loaded correctly

### WebSocket not connecting

1. Verify backend WebSocket endpoint
2. Check `VITE_SOCKET_URL` in `.env`
3. Ensure `/socket.io` proxy is configured
4. Check browser console for connection errors

### Build errors

1. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Clear Vite cache:
   ```bash
   rm -rf .vite
   ```

## 📦 Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

The build output will be in the `dist/` directory.

## 🚢 Deployment

The frontend can be deployed to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Docker container

Make sure to update `VITE_API_URL` and `VITE_SOCKET_URL` for production.

## 📄 License

MIT

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.
