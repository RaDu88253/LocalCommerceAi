import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Header from './Header';

// Import the new pages
import MainPage from './MainPage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';

// Layout-ul principal care include header-ul
const MainLayout = ({ children }) => (
  <>
    <Header />
    <main>{children}</main>
  </>
);

// Un layout simplu pentru paginile care nu au nevoie de elemente comune (cum e chat-ul)
const SimpleLayout = ({ children }) => <>{children}</>;

function App() {
  const location = useLocation();
  return (
    <Routes>
      {/* Pagina de chat are propriul ei layout complet */}
      <Route path="/" element={<MainLayout><MainPage /></MainLayout>} />
      
      {/* Paginile de login și register folosesc un layout cu Header */}
      <Route path="/login" element={<MainLayout><LoginPage /></MainLayout>} />
      <Route path="/register" element={<MainLayout><RegisterPage /></MainLayout>} />
    </Routes>
  );
}

export default App
