'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Plus, Trash2, Settings, Volume2, Loader } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/lib/auth-context';
import { coachChat, getCoachConversations } from '@/lib/api';
import apiClient from '@/lib/api';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
}

export default function CareerCoachPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadingConversations, setLoadingConversations] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  // Load conversations on mount
  useEffect(() => {
    if (user) {
      loadConversations();
    }
  }, [user]);

  const loadConversations = async () => {
    if (!user) return;
    
    try {
      setLoadingConversations(true);
      const data = await getCoachConversations(user.uid);
      
      // Transform backend data to frontend format
      const transformedConversations: Conversation[] = data.conversations?.map((conv: any) => ({
        id: conv.id,
        title: conv.title || 'New Conversation',
        messages: conv.messages?.map((msg: any) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp)
        })) || [],
        createdAt: new Date(conv.created_at)
      })) || [];
      
      setConversations(transformedConversations);
      
      // Set current conversation to the most recent one
      if (transformedConversations.length > 0 && !currentConversationId) {
        setCurrentConversationId(transformedConversations[0].id);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
      toast.error('Failed to load conversation history');
    } finally {
      setLoadingConversations(false);
    }
  };

  const currentConversation = conversations.find((c) => c.id === currentConversationId);

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentConversation?.messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !user) return;

    const messageContent = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    // Add user message optimistically
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    // Update UI immediately
    if (currentConversationId) {
      setConversations(
        conversations.map((c) =>
          c.id === currentConversationId
            ? {
                ...c,
                messages: [...c.messages, userMessage],
              }
            : c
        )
      );
    }

    try {
      // Call real API
      const response = await coachChat({
        user_id: user.uid,
        message: messageContent,
        conversation_id: currentConversationId || undefined,
      });

      // Add AI response
      const assistantMessage: Message = {
        id: response.message_id || Date.now().toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };

      // Update conversation with AI response
      setConversations(
        conversations.map((c) =>
          c.id === (response.conversation_id || currentConversationId)
            ? {
                ...c,
                messages: [...c.messages, assistantMessage],
              }
            : c
        )
      );

      // Update conversation ID if it's a new conversation
      if (!currentConversationId && response.conversation_id) {
        setCurrentConversationId(response.conversation_id);
        
        // Update conversation title based on first message
        setConversations(conversations.map((c) =>
          c.id === response.conversation_id
            ? {
                ...c,
                title: messageContent.substring(0, 50) + (messageContent.length > 50 ? '...' : ''),
              }
            : c
        ));
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      toast.error(error.response?.data?.detail || 'Failed to send message. Please try again.');
      
      // Remove optimistic user message on error
      if (currentConversationId) {
        setConversations(
          conversations.map((c) =>
            c.id === currentConversationId
              ? {
                  ...c,
                  messages: c.messages.filter(m => m.id !== userMessage.id),
                }
              : c
          )
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  const startNewConversation = () => {
    const newConversation: Conversation = {
      id: `temp-${Date.now()}`,
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
    };
    setConversations([newConversation, ...conversations]);
    setCurrentConversationId(newConversation.id);
  };

  const deleteConversation = async (id: string) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return;
    
    try {
      // Call API to delete
      await apiClient.deleteCoachConversation(id);
      
      // Remove from local state
      setConversations(conversations.filter((c) => c.id !== id));
      
      // If current conversation was deleted, select another
      if (currentConversationId === id) {
        const remaining = conversations.filter((c) => c.id !== id);
        setCurrentConversationId(remaining[0]?.id || null);
      }
      
      toast.success('Conversation deleted');
    } catch (error) {
      console.error('Error deleting conversation:', error);
      toast.error('Failed to delete conversation');
    }
  };

  const deleteConversationOld = (id: string) => {
    const filtered = conversations.filter((c) => c.id !== id);
    setConversations(filtered);
    if (currentConversationId === id) {
      setCurrentConversationId(filtered[0]?.id || '');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-slate-700">
            <h1 className="text-xl font-bold text-white mb-4">Career Coach</h1>
            <Button onClick={startNewConversation} className="w-full bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              New Chat
            </Button>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => setCurrentConversationId(conv.id)}
                className={`p-3 rounded-lg cursor-pointer transition group relative ${
                  currentConversationId === conv.id ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                <p className="text-sm font-medium truncate">{conv.title}</p>
                <p className="text-xs text-slate-400 mt-1">
                  {conv.messages.length} messages
                </p>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteConversation(conv.id);
                  }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition"
                >
                  <Trash2 className="w-4 h-4 text-red-400 hover:text-red-300" />
                </button>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-slate-700 space-y-2">
            <Button variant="ghost" className="w-full justify-start text-slate-400 hover:text-white">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          {currentConversation ? (
            <>
              {/* Header */}
              <div className="p-4 border-b border-slate-700 bg-slate-800">
                <h2 className="text-lg font-semibold text-white">{currentConversation.title}</h2>
                <p className="text-sm text-slate-400">Career guidance and advice</p>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {currentConversation.messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <h3 className="text-xl font-semibold text-slate-400 mb-2">Start Your Career Conversation</h3>
                      <p className="text-slate-500">Ask me anything about career development, skills, and growth</p>
                    </div>
                  </div>
                ) : (
                  <>
                    {currentConversation.messages.map((msg) => (
                      <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div
                          className={`max-w-md px-4 py-2 rounded-lg ${
                            msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-100'
                          }`}
                        >
                          <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                          <p className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-200' : 'text-slate-400'}`}>
                            {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-slate-700 text-slate-100 px-4 py-2 rounded-lg">
                          <Loader className="w-4 h-4 animate-spin" />
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              {/* Input */}
              <div className="p-4 border-t border-slate-700 bg-slate-800">
                <form onSubmit={handleSendMessage} className="flex gap-3">
                  <Input
                    placeholder="Ask me about your career..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    disabled={isLoading}
                    className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400"
                  />
                  <Button
                    type="submit"
                    disabled={isLoading || !inputMessage.trim()}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </form>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <h3 className="text-2xl font-semibold text-slate-400 mb-2">No conversations yet</h3>
                <p className="text-slate-500 mb-4">Start a new chat to get career advice</p>
                <Button onClick={startNewConversation} className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="w-4 h-4 mr-2" />
                  New Chat
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
