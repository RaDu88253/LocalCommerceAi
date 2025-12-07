import React, { useState } from 'react';
import './ChangePasswordModal.css';

function ChangePasswordModal({ onClose }) {
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (newPassword !== confirmPassword) {
            setError('Parolele noi nu se potrivesc.');
            return;
        }

        // TODO: Implement API call to backend to change password
        // For now, we'll simulate a success
        console.log({
            currentPassword,
            newPassword,
        });

        setSuccess('Parola a fost schimbată cu succes!');
        // Optionally close the modal after a delay
        setTimeout(() => {
            onClose();
        }, 2000);
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h2 className="modal-title">Schimbă Parola</h2>
                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="input-group">
                        <label htmlFor="current-password">Parola curentă</label>
                        <input
                            id="current-password"
                            type={showPassword ? 'text' : 'password'}
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                            required
                        />
                    </div>
                    <div className="input-group">
                        <label htmlFor="new-password">Parola nouă</label>
                        <input
                            id="new-password"
                            type={showPassword ? 'text' : 'password'}
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            required
                        />
                    </div>
                    <div className="input-group">
                        <label htmlFor="confirm-password">Confirmă parola nouă</label>
                        <input
                            id="confirm-password"
                            type={showPassword ? 'text' : 'password'}
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>

                    <div className="flex items-center mt-2">
                        <input
                            id="show-password-modal"
                            type="checkbox"
                            checked={showPassword}
                            onChange={() => setShowPassword(!showPassword)}
                            className="h-4 w-4 rounded border-slate-300 text-[#752699] focus:ring-[#752699]"
                        />
                        <label htmlFor="show-password-modal" className="ml-2 block text-sm text-slate-600">
                            Afișează parolele
                        </label>
                    </div>

                    {error && <p className="modal-error">{error}</p>}
                    {success && <p className="modal-success">{success}</p>}

                    <div className="modal-actions">
                        <button type="button" onClick={onClose} className="modal-button cancel">
                            Anulează
                        </button>
                        <button type="submit" className="modal-button save">
                            Salvează
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default ChangePasswordModal;