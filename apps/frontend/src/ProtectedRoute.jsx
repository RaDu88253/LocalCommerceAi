import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('accessToken');

  if (!token) {
    // Dacă utilizatorul nu este autentificat, îl redirecționăm către pagina de login
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;