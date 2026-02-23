import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// VULNERABILITY: console.log exposes sensitive data
console.log('App starting with config:', {
    apiUrl: 'http://localhost:5000',
    version: '1.0.0',
    apiKey: 'sk_live_51HxyzABCDEF123456789'
});

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
)
