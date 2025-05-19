import { useState, useEffect } from 'react';
import './Chatbot.css';

function Chatbot() {
  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);

  const [currentChatId, setCurrentChatId] = useState(() => {
    const savedId = parseInt(localStorage.getItem('currentChatId'), 10);
    console.log('chat_id from localStorage:', savedId);
    return savedId || null;
  });


  const saveMessageToDB = async (msg) => {
    try {
      console.log('Posting on /messages:', JSON.stringify(msg));
      await fetch('http://localhost:8000/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(msg),
      });
      console.log('Posted on /messages!')
    } catch (err) {
      console.error('Error saving message', err);
    }
  };

  useEffect(() => {
    const loadMessages = async () => {
      try {
        const res = await fetch('http://localhost:8000/messages');
        const data = await res.json();
        console.log("Mensajes desde el backend:", data);
  
        const chatMap = {};
        data.forEach(msg => {
          if (!chatMap[msg.chat_id]) {
            chatMap[msg.chat_id] = [];
          }
          chatMap[msg.chat_id].push(msg);
        });
  
        const chatsList = Object.entries(chatMap).map(([id, messages]) => ({
          id,
          messages: messages.sort((a, b) => new Date(a.timestamp || 0) - new Date(b.timestamp || 0)) // opcional
        }));
  
        setChats(chatsList);
  
        const savedId = localStorage.getItem('currentChatId');
        if (!savedId && chatsList.length > 0) {
          const firstId = chatsList[0].id;
          setCurrentChatId(firstId);
          localStorage.setItem('currentChatId', firstId.toString);
        }
  
      } catch (err) {
        console.error('Error loading chats', err);
      }
    };
  
    loadMessages();
  }, []);

  useEffect(() => {
    if (!currentChatId || chats.length === 0) return;
  
    const selectedChat = chats.find(chat => chat.id === currentChatId);
    if (selectedChat && Array.isArray(selectedChat.messages)) {
      console.log("Mensajes del chat:", selectedChat.messages);
      setMessages(selectedChat.messages);
    } else {
      console.log("No se encontró el chat o no tiene mensajes.");
      setMessages([]);
    }
  }, [currentChatId, chats]);

  const handleNewChat = () => {
    const newId = Date.now()
    const newChat = {
      id: newId,
      messages: [],
    };
  
    setChats(prev => [...prev, newChat]);
    setCurrentChatId(newId);
    setMessages([]); 
    localStorage.setItem('currentChatId', newId.toString);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!question.trim() || !currentChatId) return;
  
    setLoading(true);
  
    const userMsg = { chat_id: currentChatId, sender: 'user', text: question };
    setMessages(prev => [...prev, userMsg]);
    saveMessageToDB(userMsg);

  
    setChats(prevChats => {
      return prevChats.map(chat => {
        if (chat.id === currentChatId) {
          return {
            ...chat,
            messages: [...chat.messages, userMsg]
          };
        }
        return chat;
      });
    });
  
    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, chat_id: currentChatId }),
      });
  
      const data = await response.json();
      
      const botMsg = { chat_id: currentChatId, sender: 'bot', text: data.response };
      setMessages(prev => [...prev, botMsg]);
      saveMessageToDB(botMsg);
  
      setChats(prevChats => {
        return prevChats.map(chat => {
          if (chat.id === currentChatId) {
            return {
              ...chat,
              messages: [...chat.messages, botMsg]
            };
          }
          return chat;
        });
      });
  
      setQuestion('');
    } catch (error) {
      console.error('Error:', error);
      const errorMsg = { chat_id: currentChatId, sender: 'bot', text: 'There was an error trying to connect with Watsonx.ai' };
      setMessages(prev => [...prev, errorMsg]);
      saveMessageToDB(errorMsg);
  
      setChats(prevChats => {
        return prevChats.map(chat => {
          if (chat.id === currentChatId) {
            return {
              ...chat,
              messages: [...chat.messages, errorMsg]
            };
          }
          return chat;
        });
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChat = (idToDelete) => {
    setChats(prevChats => prevChats.filter(chat => chat.id !== idToDelete));

    if (idToDelete === currentChatId) {
      setCurrentChatId(null);
      setMessages([]);
      localStorage.removeItem('currentChatId');
    }

    fetch(`http://localhost:8000/messages/${idToDelete}`, {
      method: 'DELETE',
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to delete chat from backend');
      else console.log('Deleted chat');
    })
    .catch(err => console.error('Error deleting chat:', err));
  };

  return (
    <div className="app-container">
      <aside className="sidebar">
        <h2>Chats</h2>
        <button onClick={handleNewChat}>+ New Chat</button>
        <ul className="chat-list">
            {chats.map(chat => (
                <li
                key={chat.id}
                className={chat.id === currentChatId ? 'active' : ''}
                >
                <span onClick={() => {
                    setCurrentChatId(chat.id);
                    localStorage.setItem('currentChatId', chat.id.toString); 
                }}>
                    Chat {chat.id}
                </span>
                <button 
                    onClick={() => handleDeleteChat(chat.id)} 
                    className="delete-chat-btn"
                >
                    x
                </button>
                </li>
            ))}
        </ul>
      </aside>

      <div className="chat-container">
        <header className="chat-header">
          <img src="/watsonx-logo.png" alt="Watsonx" className="logo" />
          <h1>Watsonx.ai Assistant</h1>
          <img src="/ibm-logo.png" alt="IBM" className="logo" />
        </header>

        <div className="chat-box">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.sender === 'user' ? 'user' : 'bot'}`}>
            {msg.text}
          </div>
          ))}
          {loading && <div className="message bot">Generating an answer...</div>}
        </div>

        <div className="chat-input">
          <input
            type="text"
            placeholder="Ask me anything about Watsonx.ai..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <button onClick={handleSend}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;