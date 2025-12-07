import React from 'react';
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom';
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
                        {/* Link-uri pentru utilizatorul autentificat */}
                        <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>Chat with find</NavLink>
                        <NavLink to="/profile" className={({ isActive }) => (isActive ? 'active' : '')}>Profil</NavLink>
                        <button onClick={handleLogout} className="logout-button">Logout</button>
                    </>
                ) : (
                    <>
                        {/* Link-uri pentru vizitator */}
                        <NavLink to="/login" className={({ isActive }) => (isActive ? 'active' : '')}>Login</NavLink>
                        <NavLink to="/register" className={({ isActive }) => (isActive ? 'active' : '')}>Register</NavLink>
                    </>
                )}
            </nav>
        </header>
    );
}

export default Header;