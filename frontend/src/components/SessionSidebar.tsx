import React, { useEffect, useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { getChatSessions, createChatSession } from '../api/client';
import { toast } from 'react-toastify';

interface Session {
  id: string;
  name: string;
  created_at: string;
}

interface SessionSidebarProps {
  onSelectSession: (id: string) => void;
  activeSessionId?: string;
}

const SessionSidebar: React.FC<SessionSidebarProps> = ({ onSelectSession, activeSessionId }) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await getChatSessions();
        setSessions(response.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
      } catch (err) {
        setError('Failed to fetch sessions');
        toast.error('Failed to fetch sessions');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  const handleNewChat = async () => {
    try {
      const newSession = await createChatSession();
      setSessions((prev) => [newSession, ...prev]);
      onSelectSession(newSession.id);
    } catch (err) {
      toast.error('Failed to create new chat session');
    }
  };

  return (
    <div className="w-64 bg-gray-100 h-full flex flex-col">
      <button
        onClick={handleNewChat}
        className="p-4 bg-blue-500 text-white font-semibold hover:bg-blue-600 transition"
      >
        New Chat
      </button>
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 space-y-4">
            <div className="h-6 bg-gray-300 rounded animate-pulse"></div>
            <div className="h-6 bg-gray-300 rounded animate-pulse"></div>
            <div className="h-6 bg-gray-300 rounded animate-pulse"></div>
          </div>
        ) : error ? (
          <div className="p-4 text-red-500">{error}</div>
        ) : (
          <ul>
            {sessions.map((session) => (
              <li
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`p-4 cursor-pointer ${
                  activeSessionId === session.id
                    ? 'bg-gray-200 border-l-4 border-blue-500'
                    : 'hover:bg-gray-200'
                }`}
              >
                <div className="font-semibold truncate">{session.name.slice(0, 30)}</div>
                <div className="text-sm text-gray-500">
                  {formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default SessionSidebar;