import React, { useState, useEffect, useRef } from 'react';
import './MainPage.css';
import API_URL from './config'; // Import the API URL

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
    const [isLoading, setIsLoading] = useState(false);
    const [isChatActive, setIsChatActive] = useState(false);
    const chatEndRef = useRef(null);

    // Scroll to the bottom of the chat on new messages
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (input.trim() && !isLoading) {
            if (!isChatActive) setIsChatActive(true);
            const userMessage = { id: Date.now(), text: input, sender: 'user' };
            setMessages(prev => [...prev, userMessage]);
            setInput('');
            setIsLoading(true);

            // Add a "typing..." indicator
            const typingMessageId = Date.now() + 1;
            setMessages(prev => [...prev, { id: typingMessageId, text: "...", sender: 'ai', typing: true }]);

            try {
                // 1. Get user's location with a fallback to a default location (Bucharest)
                let location;
                try {
                    location = await new Promise((resolve, reject) => {
                        if (!navigator.geolocation) {
                            return reject(new Error("Geolocation not supported."));
                        }
                        // Request location with a 5-second timeout
                        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
                    });
                    location = { latitude: location.coords.latitude, longitude: location.coords.longitude };
                } catch (locationError) {
                    console.warn(`Could not get user location: ${locationError.message}. Falling back to default.`);
                    location = {
                        latitude: 44.4268,
                        longitude: 26.1025,
                    };
                }

                // 2. Prepare the request
                const requestData = {
                    user_query: userMessage.text,
                    latitude: location.latitude,
                    longitude: location.longitude,
                };

                // 3. Call the backend API
                const response = await fetch(`${API_URL}/shopping-assistant`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData),
                });

                if (!response.ok) {
                    throw new Error(`API request failed with status ${response.status}`);
                }

                const responseData = await response.json();

                // 4. Replace "typing..." with the actual response
                setMessages(prev => prev.map(msg => 
                    msg.id === typingMessageId ? { ...msg, text: responseData.response, typing: false } : msg
                ));

            } catch (error) {
                console.error("Error calling shopping assistant:", error);
                const errorMessage = error.message || "Îmi pare rău, am întâmpinat o eroare. Te rog să încerci din nou.";
                setMessages(prev => prev.map(msg => msg.id === typingMessageId ? { ...msg, text: errorMessage, typing: false } : msg));
            } finally {
                setIsLoading(false);
            }
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
                                    {message.typing ? (
                                        <div className="typing-indicator"><span></span><span></span><span></span></div>
                                    ) : (
                                        message.text
                                    )}
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
                    <button type="submit" className="send-button" disabled={isLoading}>
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