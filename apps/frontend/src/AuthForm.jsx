import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './AuthForm.css';

function AuthForm({ mode }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const isRegisterMode = mode === 'register';

    const validatePassword = (password) => {
        // Regex: minim 8 caractere, o majusculă, o cifră, un caracter special
        const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/;
        return passwordRegex.test(password);
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        setError(''); // Resetează eroarea la fiecare încercare

        if (isRegisterMode) {
            if (password !== confirmPassword) {
                setError('Parolele nu se potrivesc.');
                return;
            }
            if (!validatePassword(password)) {
                setError('Parola trebuie să aibă minim 8 caractere, o majusculă, o cifră și un caracter special.');
                return;
            }
        }

        // Aici vine logica de trimitere a datelor către server (API call)
        console.log('Formular trimis:', { email, password });
        // Exemplu: după succes, redirecționează către pagina principală
        // navigate('/'); 
    };

    return (
        <div className="auth-container">
            <form onSubmit={handleSubmit} className="auth-form">
                <h2>{isRegisterMode ? 'Create Account' : 'Login'}</h2>

                {error && <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}

                <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>

                {isRegisterMode && (
                    <div className="form-group">
                        <label htmlFor="confirmPassword">Confirm Password</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>
                )}

                <button type="submit">{isRegisterMode ? 'Register' : 'Login'}</button>

                <div className="auth-switch">
                    {isRegisterMode ? "Already have an account? " : "Don't have an account? "}
                    <Link to={isRegisterMode ? '/login' : '/register'}>{isRegisterMode ? 'Login' : 'Register'}</Link>
                </div>
            </form>
        </div>
    );
}

export default AuthForm;