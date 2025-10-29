import { ReactNode, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import styles from '../styles/AppLayout.module.css';
import { createModel, fetchModels, AppModel } from '../lib/api';
import { ChatInterface } from './ChatInterface';

interface AppLayoutProps {
  children: ReactNode;
  username?: string;
  userId?: string | null;
}

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
}

export function AppLayout({ children, username = 'User', userId }: AppLayoutProps) {
  const [showNewModelForm, setShowNewModelForm] = useState(false);
  const [newModelName, setNewModelName] = useState('');
  const [models, setModels] = useState<AppModel[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [modelFetchError, setModelFetchError] = useState('');
  const [modalError, setModalError] = useState('');
  const [isCreatingModel, setIsCreatingModel] = useState(false);
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const router = useRouter();

  const loadModels = useCallback(async () => {
    if (!userId) {
      setModels([]);
      return;
    }

    setIsLoadingModels(true);
    setModelFetchError('');

    try {
      const data = await fetchModels(userId);
      setModels(data);
    } catch (error) {
      console.error('Failed to load models', error);
      setModelFetchError('Unable to load models. Please try again.');
    } finally {
      setIsLoadingModels(false);
    }
  }, [userId]);

  useEffect(() => {
    loadModels();
  }, [loadModels]);

  const handleNewModel = () => {
    if (!userId) {
      setModalError('You need to be signed in to create a model.');
      return;
    }
    setModalError('');
    setShowNewModelForm(true);
  };

  const handleCloseModal = () => {
    setShowNewModelForm(false);
    setNewModelName('');
    setModalError('');
  };

  const handleCreateModel = async () => {
    const trimmedName = newModelName.trim();

    if (!trimmedName) {
      setModalError('Please enter a model name.');
      return;
    }

    if (!userId) {
      setModalError('You need to be signed in to create a model.');
      return;
    }

    setIsCreatingModel(true);
    setModalError('');

    try {
      const createdModel = await createModel({
        name: trimmedName,
        user_id: userId,
      });

      setModels(prev => [...prev, createdModel]);
      setShowNewModelForm(false);
      setNewModelName('');

      router.push({
        pathname: '/upload',
        query: { modelId: createdModel.id, modelName: createdModel.name },
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create model. Please try again.';
      setModalError(message);
    } finally {
      setIsCreatingModel(false);
    }
  };

  const handleNewChat = () => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: `Chat ${chats.length + 1}`,
      lastMessage: 'New chat started',
      timestamp: 'Just now'
    };
    
    setChats(prev => [newChat, ...prev]);
    setActiveChat(newChat.id);
  };

  const handleDeleteChat = (chatId: string) => {
    setChats(prev => prev.filter(c => c.id !== chatId));
    if (activeChat === chatId) {
      // If deleting currently active chat, clear selection so ChatInterface resets
      setActiveChat(null);
    }
  };

  const handleSignOut = () => {
    // Handle sign out logic
    router.push('/');
  };

  return (
    <div className={styles.appContainer}>
      {/* Left Panel - Models */}
      <div className={styles.leftPanel}>
        <div className={styles.panelHeader}>
          <h3>Models</h3>
          <button 
            className={styles.newButton}
            onClick={handleNewModel}
            disabled={!userId}
          >
            + New Model
          </button>
        </div>

        {modelFetchError && (
          <div className={styles.panelError}>{modelFetchError}</div>
        )}
        
        {showNewModelForm && (
          <div className={styles.modalOverlay}>
            <div className={styles.modalContent}>
              <h3>Create New Model</h3>
              <input
                type="text"
                value={newModelName}
                onChange={(e) => setNewModelName(e.target.value)}
                placeholder="Enter model name"
                className={styles.inputField}
              />
              {modalError && (
                <div className={styles.modalError}>{modalError}</div>
              )}
              <div className={styles.formActions}>
                <button 
                  className={styles.secondaryButton}
                  onClick={handleCloseModal}
                  disabled={isCreatingModel}
                >
                  Cancel
                </button>
                <button 
                  className={styles.primaryButton}
                  onClick={handleCreateModel}
                  disabled={!newModelName.trim() || isCreatingModel}
                >
                  {isCreatingModel ? 'Creating...' : 'Create'}
                </button>
              </div>
            </div>
          </div>
        )}
        
        <div className={styles.listContainer}>
          {isLoadingModels ? (
            <div className={styles.emptyState}>Loading models...</div>
          ) : models.length === 0 ? (
            <div className={styles.emptyState}>No models created yet.</div>
          ) : (
            models.map(model => (
            <div
              key={model.id}
              className={styles.listItem}
              onClick={() => router.push({ pathname: '/upload', query: { modelId: model.id, modelName: model.name } })}
            >
              <div className={styles.itemIcon}>📊</div>
              <div className={styles.itemContent}>
                <div className={styles.itemTitle}>{model.name}</div>
                <div className={styles.itemSubtitle}>
                  Created on {new Date(model.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>
            ))
          )}
        </div>
        
        <div className={styles.userSection}>
          <div className={styles.userInfo}>
            <div className={styles.userInitial}>
              {username.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className={styles.userName}>{username}</div>
              <button 
                className={styles.signOutButton}
                onClick={handleSignOut}
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Middle Panel - Chat History */}
      <div className={styles.middlePanel}>
        <div className={styles.panelHeader}>
          <h3>Chats</h3>
          <button 
            className={styles.newButton}
            onClick={handleNewChat}
          >
            + New Chat
          </button>
        </div>
        
        <div className={styles.listContainer}>
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`${styles.listItem} ${activeChat === chat.id ? styles.activeItem : ''}`}
              onClick={() => setActiveChat(chat.id)}
            >
              <div className={styles.itemIcon}>💬</div>
              <div className={styles.itemContent}>
                <div className={styles.itemTitle}>{chat.title}</div>
                <div className={styles.itemSubtitle}>
                  <span className={styles.truncate}>{chat.lastMessage}</span>
                  <span className={styles.timestamp}>{chat.timestamp}</span>
                </div>
              </div>
              <button
                className={styles.deleteButton}
                onClick={(e) => { e.stopPropagation(); handleDeleteChat(chat.id); }}
                title="Delete chat"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </div>
      
      {/* Right Panel - Chat Interface */}
      <div className={styles.rightPanel}>
        {/* Ensure ChatInterface resets on new/changed activeChat */}
        <ChatInterface onNewChat={handleNewChat} key={activeChat || 'no-chat'} />
      </div>
    </div>
  );
}
