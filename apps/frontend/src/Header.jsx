import React from 'react';
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom';
import './Header.css';

// Plus Icon SVG for the "New Conversation" button
const PlusIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
    </svg>
);

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

    const handleNewConversation = () => {
        // Reloads the page to reset the chat state
        window.location.reload();
    };

    // Logo-ul este un link doar dacă utilizatorul este logat ȘI nu se află pe pagina principală.
    const isLogoActiveLink = token && location.pathname !== '/';

    return (
        <header className="app-header">
            {/* Logo on the left */}
            {token ? (
                <Link to="/" className="logo-link">find.</Link>
            ) : (
                <span className="logo-link">find.</span>
            )}

            {/* Navigation links on the right */}
            <nav className="header-nav">
                {token ? (
                    <>
                        <button onClick={handleNewConversation} className="new-convo-button">
                            <PlusIcon />
                            <span className="new-convo-text">Conversație nouă</span>
                        </button>
                        {/* Link-uri pentru utilizatorul autentificat */}
                        <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>Chat</NavLink>
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