import React from 'react';
import { Link, useNavigate } from 'react-router-dom'; // Am curățat importul duplicat
import './Header.css';

function Header() {
    const navigate = useNavigate();
    const token = localStorage.getItem('accessToken');

    const handleLogout = () => {
        // Ștergem token-ul din localStorage
        localStorage.removeItem('accessToken');
        // Redirecționăm utilizatorul la pagina de login
        navigate('/login');
    };

    return (
        <header className="app-header">
            {/* Logo on the left */}
            <Link to={token ? "/" : "/login"} className="logo-link">find.</Link>

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