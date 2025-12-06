import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

function Header() {
    return (
        <header className="app-header">
            {/* Logo on the left */}
            <div className="logo">
                <Link to="/" className="logo-link">find.</Link>
            </div>
            {/* Navigation links on the right */}
            <nav className="header-nav">
                <Link to="/login">Login</Link>
                <Link to="/register">Register</Link>
            </nav>
        </header>
    );
}

export default Header;