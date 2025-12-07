import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ProfilePage.css';
import API_URL from './config'; // Import the API URL
import ChangePasswordModal from './ChangePasswordModal'; // Import the new modal component

// --- Icons ---
const LogoutIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
);

function ProfilePage() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem('accessToken');
            if (!token) {
                setError('Authentication token not found.');
                setLoading(false);
                navigate('/login');
                return;
            }

            try {
                const response = await fetch(`${API_URL}/api/users/me/`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch user data.');
                }

                const data = await response.json();
                setUser(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchUserData();
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('accessToken');
        navigate('/login');
    };

    const getInitials = (firstName, lastName) => {
        if (!firstName || !lastName) return '';
        return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
    };

    const formatPhoneNumber = (phoneNumber) => {
        if (!phoneNumber || typeof phoneNumber !== 'string') {
            return '';
        }

        // Remove all non-digit characters, but keep the leading '+'
        const cleaned = phoneNumber.replace(/[^\d+]/g, '');

        // Format for standard Romanian mobile numbers (+407xx xxx xxx)
        if (cleaned.startsWith('+40') && cleaned.length === 12) {
            return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6, 9)} ${cleaned.slice(9, 12)}`;
        }

        return phoneNumber; // Return original if it doesn't match the format
    };

    if (loading) {
        return <div className="profile-page-background"><div className="loading-spinner"></div></div>;
    }

    if (error) {
        return <div className="profile-page-background"><p className="error-message">{error}</p></div>;
    }

    return (
        <div className="profile-page-background">
            <div className="profile-card">
                {/* --- Header Section --- */}
                <div className="profile-header">
                    <div className="avatar">
                        <span>{getInitials(user.first_name, user.last_name)}</span>
                    </div>
                    <h2 className="user-name">{`${user.first_name} ${user.last_name}`}</h2>
                </div>

                {/* --- Account Management Section --- */}
                <div className="profile-section">
                    <h3 className="section-title">MANAGEMENT CONT</h3>
                    <div className="input-group">
                        <label htmlFor="phone">Telefon</label>
                        <input id="phone" type="tel" value={formatPhoneNumber(user.phone_number)} readOnly />
                    </div>
                    <div className="input-group">
                        <label htmlFor="email">Adresă de email</label>
                        <input id="email" type="email" value={user.email} readOnly />
                    </div>
                    <div className="action-row">
                        <button className="save-button">Salvează Modificările</button>
                    </div>
                </div>

                {/* --- Security Section --- */}
                <div className="profile-section">
                    <h3 className="section-title">SECURITATE</h3>
                    <div className="security-row">
                        <div className="input-group">
                            <label>Parolă</label>
                            <input type="password" value="••••••••" readOnly />
                        </div>
                        <button className="change-link" onClick={() => setIsModalOpen(true)}>Schimbă</button>
                    </div>
                </div>

                {/* --- Footer Section --- */}
                <div className="profile-footer">
                    <button onClick={handleLogout} className="logout-button-profile">
                        <LogoutIcon />
                        <span>DECONECTARE</span>
                    </button>
                </div>
            </div>

            {isModalOpen && (
                <ChangePasswordModal 
                    onClose={() => setIsModalOpen(false)} 
                />
            )}
        </div>
    );
}

export default ProfilePage;