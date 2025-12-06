import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './Header.jsx';
import './App.css'
import API_URL from './config';

// Import the new pages
import MainPage from './MainPage.jsx';
import LoginPage from './LoginPage.jsx';
import RegisterPage from './RegisterPage.jsx';

function App() {
  const [backendStatus, setBackendStatus] = useState('Connecting...');

  useEffect(() => {
    // Funcție pentru a verifica starea backend-ului
    const checkBackendStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/`);
        if (response.ok) {
          const data = await response.json();
          setBackendStatus(`Connected! Status: ${data.status}`);
        } else {
          setBackendStatus('Backend is not connected yet!');
        }
      } catch (error) {
        console.error("Connection error:", error);
        setBackendStatus('Failed to connect to backend. Is it running?');
      }
    };

    checkBackendStatus();
  }, []); // [] asigură că acest efect se rulează o singură dată, la montarea componentei

  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<MainPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Routes>
        </main>
        <h2>{backendStatus}</h2>
      </div>
    </Router>
  )
}

export default App
