'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown'; // npm install react-markdown
import remarkGfm from 'remark-gfm'; // 支持表格、任务列表等扩展，npm install remark-gfm
import rehypeHighlight from 'rehype-highlight'; // 支持代码高亮，npm install rehype-highlight

interface Message {
  role: 'user' | 'bot';
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:9999/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });

      const data = await res.json();
      const botMessage: Message = { role: 'bot', content: data.answer || 'No response' };
      setMessages(prev => [...prev, userMessage, botMessage]);
    } catch (error) {
      console.error(error);
      const botMessage: Message = { role: 'bot', content: 'Error connecting to server.' };
      setMessages(prev => [...prev, botMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div className="w-full max-w-xl bg-white rounded-lg shadow-md p-4 flex flex-col space-y-4">
        <div className="flex-1 overflow-y-auto max-h-[70vh] space-y-2">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-2 rounded-md ${msg.role === 'user' ? 'bg-blue-100 self-end' : 'bg-gray-200 self-start'}`}
            >
              {msg.role === 'bot' ? (
                <ReactMarkdown
                  children={msg.content}
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeHighlight]}
                />
              ) : (
                <span>{msg.content}</span>
              )}
            </div>
          ))}
        </div>

        <div className="flex space-x-2">
          <input
            type="text"
            className="flex-1 border rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Type your question..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:bg-blue-300"
            disabled={loading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

