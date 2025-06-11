import { useState } from 'react';
import { queryWell } from '../lib/api';

interface Props {
  wellId: string;
}

export default function WellChat({ wellId }: Props) {
  const [messages, setMessages] = useState<{ text: string; from: 'user' | 'bot' }[]>([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input) return;
    const userMsg = { text: input, from: 'user' as const };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    const res = await queryWell(wellId, userMsg.text);
    setMessages((m) => [...m, { text: res.answer || 'No answer', from: 'bot' }]);
  };

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded shadow h-80 flex flex-col">
      <h2 className="font-semibold mb-2">Talk to the Well</h2>
      <div className="flex-1 overflow-auto space-y-2 mb-2">
        {messages.map((m, idx) => (
          <div key={idx} className={m.from === 'user' ? 'text-right' : ''}>
            <span className="inline-block px-2 py-1 rounded bg-blue-100 dark:bg-blue-900">
              {m.text}
            </span>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded px-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question"
        />
        <button className="px-3 py-1 bg-blue-500 text-white rounded" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}
