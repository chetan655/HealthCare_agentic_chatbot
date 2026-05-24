import { useState, useRef, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { sendMessage, getLocation, inferAgent, getChatHistory } from './api/api';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import AgentBadge from './components/AgentBadge';
import { HeartPulse, Menu, X } from 'lucide-react';

export default function App() {
  const [threadId, setThreadId] = useState(() => {
    const saved = sessionStorage.getItem('thread_id');
    if (saved) return saved;
    const newId = uuidv4();
    sessionStorage.setItem('thread_id', newId);
    return newId;
  });
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [activeAgent, setActiveAgent] = useState('general');
  const [location, setLocation] = useState({ lat: '29.9478', long: '76.8170' });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    getLocation().then(setLocation);
    
    // Load chat history for the current session threadId
    getChatHistory(threadId)
      .then((data) => {
        if (data && data.messages && data.messages.length > 0) {
          const loadedMessages = data.messages.map((msg) => ({
            role: msg.role === 'assistant' ? 'ai' : 'user',
            content: msg.content,
          }));
          setMessages(loadedMessages);
        }
      })
      .catch((err) => console.error("Failed to load history:", err));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleNewChat = useCallback(() => {
    const newId = uuidv4();
    sessionStorage.setItem('thread_id', newId);
    setThreadId(newId);
    setMessages([]);
    setActiveAgent('general');
    setMobileMenuOpen(false);
  }, []);

  const handleSend = useCallback(
    async (text, imageFile) => {
      if (isStreaming) return;

      const agent = inferAgent(text, !!imageFile);
      setActiveAgent(agent);

      const userMsg = {
        role: 'user',
        content: text,
        imageName: imageFile?.name || null,
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsStreaming(true);

      try {
        const response = await sendMessage(
          text,
          threadId,
          location.lat,
          location.long,
          imageFile
        );

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiContent = '';

        setMessages((prev) => [...prev, { role: 'ai', content: '' }]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          aiContent += chunk;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = { role: 'ai', content: aiContent };
            return updated;
          });
        }
      } catch (err) {
        console.error('Stream error:', err);
        setMessages((prev) => [
          ...prev,
          {
            role: 'ai',
            content:
              'I apologize, but I encountered an issue processing your request. Please try again.',
          },
        ]);
      } finally {
        setIsStreaming(false);
      }
    },
    [isStreaming, threadId, location]
  );

  const handleSuggestionClick = useCallback(
    (prompt) => {
      handleSend(prompt, null);
    },
    [handleSend]
  );

  const handleImageTrigger = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleHiddenFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleSend('Analyze this medicine image', file);
      e.target.value = '';
    }
  };

  return (
    <div className="h-dvh flex bg-surface">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleHiddenFileChange}
        className="hidden"
      />

      <Sidebar onNewChat={handleNewChat} messageCount={messages.length} />

      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
      {mobileMenuOpen && (
        <div className="fixed inset-y-0 left-0 z-50 w-72 lg:hidden animate-slide-in-left">
          <Sidebar onNewChat={handleNewChat} messageCount={messages.length} />
        </div>
      )}

      <main className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-between px-4 sm:px-6 py-3 border-b border-border bg-white/80 backdrop-blur-lg">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden w-9 h-9 rounded-lg bg-surface-alt hover:bg-brand-50 flex items-center justify-center transition-colors cursor-pointer"
            >
              {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
            <div className="flex items-center gap-2 lg:hidden">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand to-brand-dark flex items-center justify-center">
                <HeartPulse size={16} className="text-white" />
              </div>
              <span className="text-sm font-bold text-text-primary">
                Acharya
              </span>
            </div>
            <div className="hidden lg:block">
              <AgentBadge agent={activeAgent} />
            </div>
          </div>
          <div className="lg:hidden">
            <AgentBadge agent={activeAgent} />
          </div>
        </header>

        <ChatWindow
          messages={messages}
          isStreaming={isStreaming}
          onSuggestionClick={handleSuggestionClick}
          onImageTrigger={handleImageTrigger}
        />

        <ChatInput onSend={handleSend} disabled={isStreaming} />
      </main>
    </div>
  );
}
