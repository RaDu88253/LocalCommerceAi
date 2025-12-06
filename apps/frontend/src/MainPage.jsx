import React, { useState, useEffect, useRef } from 'react';
import './MainPage.css';

// Plus Icon SVG
const PlusIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
    </svg>
);

function MainPage() {
    const [messages, setMessages] = useState([
        // Initial AI message
        { id: 1, text: "La ce te-ai gândit? Poate o piesă vestimentară de la un designer local?", sender: 'ai' },
    ]);
    const [input, setInput] = useState('');
    const [isChatActive, setIsChatActive] = useState(false);
    const chatEndRef = useRef(null);

    // Scroll to the bottom of the chat on new messages
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = (e) => {
        e.preventDefault();
        if (input.trim()) {
            // Add user message
            if (!isChatActive) setIsChatActive(true);
            const userMessage = { id: Date.now(), text: input, sender: 'user' };
            setMessages(prev => [...prev, userMessage]);
            setInput('');

            // Simulate AI response after a short delay
            setTimeout(() => {
                const aiResponse = { id: Date.now() + 1, text: "Aceasta este o simulare. Conectarea la backend va urma.", sender: 'ai' };
                setMessages(prev => [...prev, aiResponse]);
            }, 1000);
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setInput(suggestion);
        // Focus on the input after clicking a suggestion
        document.querySelector('.chat-input')?.focus();
    };

    const handleNewConversation = () => {
        // For now, it just reloads the page to reset the state
        window.location.reload();
    };

    return (
        <div className="main-page-container">
            {/* New Conversation Button - positioned absolutely */}
            <button onClick={handleNewConversation} className="new-convo-button">
                <PlusIcon />
                <span>Conversație nouă</span>
            </button>
            <div className="chat-window">
                {/* Welcome screen, which will fade out */}
                {!isChatActive && (
                    <div className="welcome-container" onAnimationEnd={() => { if(isChatActive) document.querySelector('.welcome-container').style.display = 'none'; }}>
                        <div className="welcome-logo">find.</div>
                        <h1 className="welcome-title">Cum te pot ajuta astăzi?</h1>
                        <h3 className="suggestions-label">Câteva sugestii:</h3>
                        <div className="suggestion-chips">
                            <button onClick={() => handleSuggestionClick('Caut o rochie de seară unică')} className="chip">"Caut o rochie de seară unică"</button>
                            <button onClick={() => handleSuggestionClick('Găsește-mi un cadou de la un artizan local')} className="chip">"Găsește-mi un cadou de la un artizan local"</button>
                            <button onClick={() => handleSuggestionClick('Recomandă-mi un designer roman')} className="chip">"Recomandă-mi un designer roman"</button>
                        </div>
                    </div>
                )}

                <div className="messages-list">
                    {/* Render messages only after the chat becomes active */}
                    {isChatActive && messages.map(message => (
                            <div key={message.id} className={`message-container ${message.sender}`}>
                                <div className="message-bubble">
                                    {message.text}
                                </div>
                            </div>
                        ))
                    }
                    {/* Empty div to scroll to */}
                    <div ref={chatEndRef} />
                </div>

            </div>
            <div className="chat-input-area">
                <form onSubmit={handleSend} className="chat-form">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Scrie-i ceva lui find..."
                        className="chat-input"
                    />
                    <button type="submit" className="send-button">
                        {/* Send Icon SVG */}
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                            <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    );
}

export default MainPage;