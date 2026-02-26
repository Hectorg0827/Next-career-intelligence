'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

// Types
export interface User {
  uid: string;       // Unique user identifier (derived from email for custom auth)
  email: string;
  name?: string;
  subscriptionTier: 'free' | 'premium' | 'enterprise';
  createdAt?: string;
  lastLogin?: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
  clearError: () => void;
  hasPremiumAccess: boolean;
}

// Create Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const STORAGE_KEYS = {
  USER: 'next_user',
  TOKEN: 'next_auth_token',
  SESSION_EXPIRY: 'next_session_expiry',
} as const;

// Session duration (7 days in milliseconds)
const SESSION_DURATION = 7 * 24 * 60 * 60 * 1000;

/**
 * AuthProvider Component
 * Manages authentication state and provides auth methods to the app
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  });

  /**
   * Check if session is valid (not expired)
   */
  const isSessionValid = useCallback((): boolean => {
    const expiry = localStorage.getItem(STORAGE_KEYS.SESSION_EXPIRY);
    if (!expiry) return false;
    
    const expiryTime = parseInt(expiry, 10);
    return Date.now() < expiryTime;
  }, []);

  /**
   * Load user from localStorage on mount
   */
  const loadUserFromStorage = useCallback(() => {
    try {
      const userStr = localStorage.getItem(STORAGE_KEYS.USER);
      const token = localStorage.getItem(STORAGE_KEYS.TOKEN);
      
      if (userStr && token && isSessionValid()) {
        const user = JSON.parse(userStr) as User;
        setState({
          user,
          isLoading: false,
          isAuthenticated: true,
          error: null,
        });
      } else {
        // Clear expired session
        if (userStr || token) {
          localStorage.removeItem(STORAGE_KEYS.USER);
          localStorage.removeItem(STORAGE_KEYS.TOKEN);
          localStorage.removeItem(STORAGE_KEYS.SESSION_EXPIRY);
        }
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
          error: null,
        });
      }
    } catch (error) {
      console.error('Error loading user from storage:', error);
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: 'Failed to load session',
      });
    }
  }, [isSessionValid]);

  /**
   * Initialize auth state on mount
   */
  useEffect(() => {
    loadUserFromStorage();
  }, [loadUserFromStorage]);

  /**
   * Auto-refresh session before expiry
   */
  useEffect(() => {
    if (!state.isAuthenticated) return;

    const checkInterval = setInterval(() => {
      if (!isSessionValid()) {
        // Call logout without creating dependency cycle
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
          error: null,
        });
        router.push('/');
      }
    }, 60000); // Check every minute

    return () => clearInterval(checkInterval);
  }, [state.isAuthenticated, isSessionValid, router]);

  /**
   * Save user to localStorage
   */
  const saveUserToStorage = (user: User, token: string) => {
    const expiryTime = Date.now() + SESSION_DURATION;
    
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    localStorage.setItem(STORAGE_KEYS.TOKEN, token);
    localStorage.setItem(STORAGE_KEYS.SESSION_EXPIRY, expiryTime.toString());
  };

  /**
   * Login function
   * In production, this would call your backend API
   */
  const login = async (email: string, password: string): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // In production, this would be a real API call:
      // const response = await fetch('/api/auth/login', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, password }),
      // });
      
      // TODO: Validate password with backend
      console.log('Login attempt with password:', password.length, 'characters');
      
      // For demo purposes, create a mock user
      const user: User = {
        uid: email,
        email,
        subscriptionTier: email.includes('premium') ? 'premium' : 'free',
        lastLogin: new Date().toISOString(),
      };

      const token = `mock_token_${Date.now()}`;
      
      saveUserToStorage(user, token);
      
      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      });

      // Redirect to dashboard or intended page
      const intendedPath = localStorage.getItem('intended_path');
      if (intendedPath) {
        localStorage.removeItem('intended_path');
        router.push(intendedPath);
      } else {
        router.push('/dashboard');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  /**
   * Signup function
   * In production, this would call your backend API
   */
  const signup = async (email: string, password: string, name?: string): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // In production, this would be a real API call:
      // const response = await fetch('/api/auth/signup', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, password, name }),
      // });
      
      const user: User = {
        uid: email,
        email,
        name,
        subscriptionTier: 'free',
        createdAt: new Date().toISOString(),
        lastLogin: new Date().toISOString(),
      };

      const token = `mock_token_${Date.now()}`;
      
      saveUserToStorage(user, token);
      
      setState({
        user,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      });

      // Check for pending job analysis
      const pendingJob = localStorage.getItem('pendingJobTitle');
      if (pendingJob) {
        localStorage.removeItem('pendingJobTitle');
        router.push(`/analyze?job=${encodeURIComponent(pendingJob)}`);
      } else {
        router.push('/dashboard');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Signup failed';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw error;
    }
  };

  /**
   * Logout function
   */
  const logout = async (): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      // In production, call logout API to invalidate token:
      // await fetch('/api/auth/logout', {
      //   method: 'POST',
      //   headers: { Authorization: `Bearer ${token}` },
      // });

      // Clear all auth data
      localStorage.removeItem(STORAGE_KEYS.USER);
      localStorage.removeItem(STORAGE_KEYS.TOKEN);
      localStorage.removeItem(STORAGE_KEYS.SESSION_EXPIRY);
      
      // Clear legacy storage keys
      localStorage.removeItem('userEmail');
      localStorage.removeItem('authToken');
      localStorage.removeItem('subscriptionTier');

      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: null,
      });

      router.push('/');
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
        error: null,
      });
      router.push('/');
    }
  };

  /**
   * Update user information
   */
  const updateUser = (updates: Partial<User>) => {
    setState(prev => {
      if (!prev.user) return prev;
      
      const updatedUser = { ...prev.user, ...updates };
      
      // Update localStorage
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(updatedUser));
      
      return {
        ...prev,
        user: updatedUser,
      };
    });
  };

  /**
   * Clear error message
   */
  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };

  /**
   * Check if user has premium access
   */
  const hasPremiumAccess = state.user?.subscriptionTier === 'premium' || 
                           state.user?.subscriptionTier === 'enterprise';

  const value: AuthContextType = {
    ...state,
    login,
    signup,
    logout,
    updateUser,
    clearError,
    hasPremiumAccess,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Custom hook to use auth context
 * Throws error if used outside AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

/**
 * Hook to require authentication
 * Redirects to login if not authenticated
 */
export function useRequireAuth(redirectTo = '/login'): AuthContextType {
  const auth = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      // Save intended destination
      if (typeof window !== 'undefined') {
        localStorage.setItem('intended_path', window.location.pathname);
      }
      router.push(redirectTo);
    }
  }, [auth.isLoading, auth.isAuthenticated, router, redirectTo]);

  return auth;
}
