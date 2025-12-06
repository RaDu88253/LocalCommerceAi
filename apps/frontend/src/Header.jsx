import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import './Header.css';

function Header() {
    const navigate = useNavigate();
    const location = useLocation();
    const token = localStorage.getItem('accessToken');

    const handleLogout = () => {
        // Ștergem token-ul din localStorage
        localStorage.removeItem('accessToken');
        // Redirecționăm utilizatorul la pagina de login
        navigate('/login');
    };

    // Logo-ul este un link doar dacă utilizatorul este logat ȘI nu se află pe pagina principală.
    const isLogoActiveLink = token && location.pathname !== '/';

    return (
        <header className="app-header">
            {/* Logo on the left */}
            {isLogoActiveLink ? (
                <Link to="/" className="logo-link">find.</Link>
            ) : (
                <span className="logo-link">find.</span>
            )}

            {/* Navigation links on the right */}
            <nav className="header-nav">
                {token ? (
                    <>
                        {/* Buton pentru utilizatorul autentificat */}
                        <button onClick={handleLogout} className="logout-button">Logout</button>
                    </>
                ) : (
                    <>
                        {/* Link-uri pentru vizitator */}
                        <Link to="/login">Login</Link>
                        <Link to="/register">Register</Link>
                    </>
                )}
            </nav>
        </header>
    );
}

export default Header;