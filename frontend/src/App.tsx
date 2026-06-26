import { useState } from 'react';
import SessionSidebar from '@/components/SessionSidebar';
import DocumentUploader from '@/components/DocumentUploader';
import ChatWindow from '@/components/ChatWindow';

const App = () => {
  const [activeSessionId, setActiveSessionId] = useState<string | undefined>(undefined);

  const handleSelectSession = (id: string) => {
    setActiveSessionId(id);
  };

  return (
    <div className="h-screen flex flex-col">
      <header className="flex items-center justify-between bg-gray-800 text-white px-4 py-2">
        <h1 className="text-lg font-bold">Aakaar Project</h1>
        <button
          className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-1 px-3 rounded"
          onClick={() => setActiveSessionId(undefined)}
        >
          New Chat
        </button>
      </header>
      <div className="flex flex-1">
        <aside className="w-64 bg-gray-100 border-r border-gray-300 flex flex-col">
          <SessionSidebar
            onSelectSession={handleSelectSession}
            activeSessionId={activeSessionId}
          />
          <div className="flex-1 overflow-y-auto">
            <DocumentUploader sessionId={activeSessionId} />
          </div>
        </aside>
        <main className="flex-1 flex flex-col">
          <ChatWindow activeSessionId={activeSessionId} />
        </main>
      </div>
    </div>
  );
};

export default App;