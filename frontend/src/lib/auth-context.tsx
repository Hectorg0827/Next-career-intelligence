/**
 * Authentication Context Provider
 * Manages user auth state across the application
 */

'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User } from 'firebase/auth';
import { 
  signInWithGoogle, 
  signInWithEmail, 
  signUpWithEmail, 
  signOut,
  resetPassword,
  confirmPasswordResetWithCode,
  verifyPasswordResetCodeFunc,
  sendEmailVerificationFunc,
  applyActionCodeFunc,
  onAuthChange,
  getCurrentToken
} from './firebase';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<User | undefined>;
  signInWithGoogle: () => Promise<User | undefined>;
  signUp: (email: string, password: string, displayName?: string) => Promise<User | undefined>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  confirmPasswordReset: (code: string, newPassword: string) => Promise<void>;
  verifyPasswordResetCode: (code: string) => Promise<string>;
  sendEmailVerification: () => Promise<void>;
  applyActionCode: (code: string) => Promise<void>;
  getToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Listen to auth state changes
    const unsubscribe = onAuthChange(async (user) => {
      setUser(user);
      setLoading(false);
      
      // Store user data in localStorage
      if (user) {
        localStorage.setItem('userId', user.uid);
        const token = await user.getIdToken();
        localStorage.setItem('authToken', token);
      } else {
        localStorage.removeItem('userId');
        localStorage.removeItem('authToken');
      }
    });

    return unsubscribe;
  }, []);

  const handleSignIn = async (email: string, password: string) => {
    try {
      return await signInWithEmail(email, password);
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  };

  const handleSignInWithGoogle = async () => {
    try {
      return await signInWithGoogle();
    } catch (error) {
      console.error('Google sign in error:', error);
      throw error;
    }
  };

  const handleSignUp = async (email: string, password: string, displayName?: string) => {
    try {
      return await signUpWithEmail(email, password, displayName);
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  };

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  };

  const handleResetPassword = async (email: string) => {
    try {
      await resetPassword(email);
    } catch (error) {
      console.error('Reset password error:', error);
      throw error;
    }
  };

  const handleConfirmPasswordReset = async (code: string, newPassword: string) => {
    try {
      await confirmPasswordResetWithCode(code, newPassword);
    } catch (error) {
      console.error('Confirm password reset error:', error);
      throw error;
    }
  };

  const handleVerifyPasswordResetCode = async (code: string) => {
    try {
      return await verifyPasswordResetCodeFunc(code);
    } catch (error) {
      console.error('Verify password reset code error:', error);
      throw error;
    }
  };

  const handleSendEmailVerification = async () => {
    try {
      await sendEmailVerificationFunc();
    } catch (error) {
      console.error('Send email verification error:', error);
      throw error;
    }
  };

  const handleApplyActionCode = async (code: string) => {
    try {
      await applyActionCodeFunc(code);
    } catch (error) {
      console.error('Apply action code error:', error);
      throw error;
    }
  };

  const getToken = async () => {
    return await getCurrentToken();
  };

  const value = {
    user,
    loading,
    signIn: handleSignIn,
    signInWithGoogle: handleSignInWithGoogle,
    signUp: handleSignUp,
    signOut: handleSignOut,
    resetPassword: handleResetPassword,
    confirmPasswordReset: handleConfirmPasswordReset,
    verifyPasswordResetCode: handleVerifyPasswordResetCode,
    sendEmailVerification: handleSendEmailVerification,
    applyActionCode: handleApplyActionCode,
    getToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to access auth context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
