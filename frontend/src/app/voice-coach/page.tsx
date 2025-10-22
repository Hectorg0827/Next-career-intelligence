'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Volume2, VolumeX, Loader2, Bot, User, Settings, ArrowLeft, Sparkles } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { coachChat } from '@/lib/api';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Link from 'next/link';
import { NextLogo } from '@/components/branding/NextLogo';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// Check browser support for speech features
const isSpeechRecognitionSupported = () => {
  return typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);
};

const isSpeechSynthesisSupported = () => {
  return typeof window !== 'undefined' && 'speechSynthesis' in window;
};

export default function VoiceCoachPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  
  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  
  // Voice input state
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [interimTranscript, setInterimTranscript] = useState('');
  
  // Voice output state
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [autoPlay, setAutoPlay] = useState(false);
  const [speechRate, setSpeechRate] = useState(1.0);
  
  // Audio visualization
  const [audioLevels, setAudioLevels] = useState<number[]>([0, 0, 0, 0, 0]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  // Initialize speech recognition
  useEffect(() => {
    if (!isSpeechRecognitionSupported()) {
      console.warn('Speech recognition not supported');
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognitionInstance = new SpeechRecognition();
    
    recognitionInstance.continuous = false;
    recognitionInstance.interimResults = true;
    recognitionInstance.lang = 'en-US';
    recognitionInstance.maxAlternatives = 1;

    recognitionInstance.onresult = (event: any) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      if (final) {
        setInputMessage(prev => prev + ' ' + final);
        setInterimTranscript('');
      } else {
        setInterimTranscript(interim);
      }
    };

    recognitionInstance.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsRecording(false);
      setInterimTranscript('');
      
      if (event.error === 'not-allowed') {
        toast.error('Microphone permission denied. Please enable it in your browser settings.');
      } else if (event.error === 'no-speech') {
        toast.error('No speech detected. Please try again.');
      }
    };

    recognitionInstance.onend = () => {
      setIsRecording(false);
      setInterimTranscript('');
      // Stop audio visualization
      setAudioLevels([0, 0, 0, 0, 0]);
    };

    setRecognition(recognitionInstance);

    return () => {
      if (recognitionInstance) {
        recognitionInstance.stop();
      }
    };
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Toggle voice recording
  const toggleRecording = () => {
    if (!recognition) {
      toast.error('Speech recognition not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    if (isRecording) {
      recognition.stop();
      setIsRecording(false);
    } else {
      try {
        recognition.start();
        setIsRecording(true);
        // Simulate audio levels while recording
        const interval = setInterval(() => {
          setAudioLevels(prev => prev.map(() => Math.random() * 0.8 + 0.2));
        }, 100);
        
        recognition.onend = () => {
          clearInterval(interval);
          setAudioLevels([0, 0, 0, 0, 0]);
        };
      } catch (error) {
        console.error('Failed to start recording:', error);
        toast.error('Failed to start recording. Please try again.');
        setIsRecording(false);
      }
    }
  };

  // Speak text using TTS
  const speakText = (text: string) => {
    if (!isSpeechSynthesisSupported()) {
      toast.error('Text-to-speech not supported in this browser.');
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = speechRate;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    // Get available voices and use a preferred one
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
      v.name.includes('Samantha') || 
      v.name.includes('Google US English') ||
      v.name.includes('Microsoft Zira')
    );
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => {
      setIsSpeaking(false);
      toast.error('Speech playback failed');
    };

    window.speechSynthesis.speak(utterance);
  };

  // Stop speaking
  const stopSpeaking = () => {
    if (isSpeechSynthesisSupported()) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  // Send message
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !user || isLoading) return;

    const messageContent = inputMessage.trim();
    setInputMessage('');
    setInterimTranscript('');

    // Add user message to UI
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageContent,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      setIsLoading(true);

      // Call coach API
      const response = await coachChat({
        user_id: user.uid,
        message: messageContent,
        conversation_id: conversationId || undefined,
        conversation_type: 'general'
      });

      // Add assistant message to UI
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.reply || 'I apologize, but I encountered an issue. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Save conversation ID for continuity
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      // Auto-play response if enabled
      if (autoPlay && isSpeechSynthesisSupported()) {
        setTimeout(() => {
          speakText(assistantMessage.content);
        }, 500);
      }

    } catch (error: any) {
      console.error('Coach chat error:', error);
      
      // Handle profile not found error
      if (error.response?.status === 404) {
        toast.error('Career profile not found. Redirecting to Quick Profile setup...');
        
        // Add helpful message to chat
        const errorMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `👋 Hi! I noticed you don't have a career profile yet. Let me help you set one up quickly so we can have a great conversation about your career!\n\nRedirecting you to Quick Profile setup in 2 seconds...`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMsg]);
        
        // Redirect to quick profile after showing message
        setTimeout(() => {
          router.push('/quick-profile');
        }, 2000);
        
        return;
      }
      
      // Generic error
      const errorMessage = 'Failed to get response. Please try again.';
      toast.error(errorMessage);
      
      // Add error message to chat
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ ${errorMessage}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-next-hero">
      {/* Header */}
      <header className="bg-gradient-next border-b border-white/10 shadow-next-md">
        <div className="container mx-auto px-4 py-6">
          <nav className="flex justify-between items-center">
            <Link href="/dashboard" className="flex items-center gap-2 text-white/80 hover:text-white transition-colors">
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm font-body">Back to Dashboard</span>
            </Link>
            <div className="flex items-center gap-3">
              <NextLogo variant="icon" size="md" />
              <span className="text-xl font-heading font-semibold text-white">AI Coach</span>
            </div>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-4">
        {/* Settings Card */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-next-lg p-6 mb-4 border border-next-bg-light">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-next-gold rounded-xl flex items-center justify-center">
                <Bot className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-heading font-bold text-next-deep-blue">NextAI Coach</h1>
                <p className="text-sm text-next-text-muted font-body">Your AI career conversation partner</p>
              </div>
            </div>

            {/* Voice settings and actions */}
            <div className="flex items-center gap-3 flex-wrap">
              {/* Quick Profile Button */}
              <button
                onClick={() => router.push('/quick-profile')}
                className="flex items-center gap-2 px-3 py-2 bg-next-gold/10 text-next-gold rounded-lg hover:bg-next-gold/20 transition-colors font-heading"
                title="Create or update your career profile"
              >
                <User className="w-4 h-4" />
                <span className="text-sm font-medium hidden sm:inline">Profile</span>
              </button>

              {/* Auto-play toggle */}
              <button
                onClick={() => setAutoPlay(!autoPlay)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors font-heading ${
                  autoPlay 
                    ? 'bg-next-gold/10 text-next-gold' 
                    : 'bg-next-text-muted/10 text-next-text-muted hover:bg-next-text-muted/20'
                }`}
                title={autoPlay ? 'Auto-play enabled' : 'Auto-play disabled'}
              >
                {autoPlay ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                <span className="text-sm font-medium hidden sm:inline">Auto-play</span>
              </button>

              {/* Speech rate */}
              <div className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-next-text-muted" />
                <select
                  value={speechRate}
                  onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
                  className="text-sm border border-next-text-muted/30 rounded-lg px-2 py-1 font-body focus:ring-2 focus:ring-next-gold focus:border-next-gold"
                >
                  <option value="0.75">0.75x</option>
                  <option value="1.0">1.0x</option>
                  <option value="1.25">1.25x</option>
                  <option value="1.5">1.5x</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Info Banner for New Users */}
        {messages.length === 0 && (
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 mb-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-10 h-10 bg-next-royal-blue rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-next-deep-blue font-heading mb-1">👋 New to Voice Coach?</h4>
                <p className="text-sm text-gray-700 mb-2">
                  To get personalized career advice, you&apos;ll need a profile. You can either:
                </p>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => router.push('/quick-profile')}
                    className="px-3 py-1.5 bg-next-royal-blue text-white text-sm rounded-lg hover:bg-blue-600 font-medium"
                  >
                    Quick Profile (2 min)
                  </button>
                  <button
                    onClick={() => router.push('/resume-studio')}
                    className="px-3 py-1.5 bg-white text-blue-700 text-sm rounded-lg hover:bg-blue-50 border border-blue-300 font-medium"
                  >
                    Resume Studio (Full Details)
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Chat messages */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-next-lg border border-next-bg-light p-6 mb-4 h-[500px] overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot className="w-16 h-16 text-blue-500 mb-4" />
              <h3 className="text-xl font-semibold text-next-deep-blue font-heading mb-2">Start Your Career Conversation</h3>
              <p className="text-next-text-muted font-body mb-4">
                Ask me about career transitions, skill development, or job search strategies
              </p>
              <div className="flex flex-wrap gap-2 justify-center max-w-lg">
                <button
                  onClick={() => setInputMessage("I want to transition my career")}
                  className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 text-sm"
                >
                  Career transition help
                </button>
                <button
                  onClick={() => setInputMessage("What skills should I learn?")}
                  className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 text-sm"
                >
                  Skill recommendations
                </button>
                <button
                  onClick={() => setInputMessage("How do I negotiate salary?")}
                  className="px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 text-sm"
                >
                  Salary negotiation
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                  
                  <div className={`flex-1 max-w-[80%] ${message.role === 'user' ? 'text-right' : ''}`}>
                    <div
                      className={`inline-block p-4 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-next-royal-blue text-white'
                          : 'bg-next-bg-light text-next-deep-blue font-heading'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>
                    
                    {/* Voice controls for assistant messages */}
                    {message.role === 'assistant' && !message.content.startsWith('❌') && (
                      <div className="flex gap-2 mt-2">
                        <button
                          onClick={() => speakText(message.content)}
                          disabled={isSpeaking}
                          className="text-blue-500 hover:text-next-royal-blue text-sm flex items-center gap-1 disabled:opacity-50"
                        >
                          <Volume2 className="w-4 h-4" />
                          Listen
                        </button>
                        {isSpeaking && (
                          <button
                            onClick={stopSpeaking}
                            className="text-red-500 hover:text-red-600 text-sm flex items-center gap-1"
                          >
                            <VolumeX className="w-4 h-4" />
                            Stop
                          </button>
                        )}
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-next-text-muted font-body" />
                    </div>
                  )}
                </div>
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-next-bg-light p-4 rounded-lg">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input area */}
        <form onSubmit={handleSendMessage} className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-next-lg border border-next-bg-light p-4">
          <div className="flex items-center gap-3">
            {/* Voice input button */}
            {isSpeechRecognitionSupported() && (
              <button
                type="button"
                onClick={toggleRecording}
                className={`p-3 rounded-full transition-all flex items-center justify-center ${
                  isRecording
                    ? 'bg-red-500 text-white animate-pulse'
                    : 'bg-next-royal-blue text-white hover:bg-blue-600'
                }`}
                title={isRecording ? 'Stop recording' : 'Start voice input'}
              >
                {isRecording ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
              </button>
            )}

            {/* Text input */}
            <div className="flex-1">
              <input
                type="text"
                value={inputMessage + (interimTranscript ? ' ' + interimTranscript : '')}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={isRecording ? 'Listening...' : 'Type your message or use voice...'}
                disabled={isLoading || isRecording}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-next-bg-light"
              />
              
              {/* Audio visualizer */}
              {isRecording && (
                <div className="flex gap-1 items-center justify-center mt-2 h-8">
                  {audioLevels.map((level, i) => (
                    <div
                      key={i}
                      className="w-1 bg-next-royal-blue rounded-full transition-all"
                      style={{ height: `${level * 100}%` }}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Send button */}
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim() || isRecording}
              className="p-3 bg-next-royal-blue text-white rounded-full hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <Send className="w-6 h-6" />
              )}
            </button>
          </div>

          {/* Browser compatibility notice */}
          {!isSpeechRecognitionSupported() && (
            <p className="text-xs text-gray-500 mt-2 text-center">
              💡 Voice input works best in Chrome or Edge. Text input is available in all browsers.
            </p>
          )}
        </form>
      </div>
    </div>
  );
}
