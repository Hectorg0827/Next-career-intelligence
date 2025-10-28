/**
 * Firebase configuration and initialization
 * Complete authentication system with Google OAuth and email/password
 */

'use client';

import { initializeApp, getApps, FirebaseApp } from 'firebase/app';
import { 
  getAuth, 
  Auth,
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
  confirmPasswordReset,
  verifyPasswordResetCode,
  sendEmailVerification,
  applyActionCode,
  User
} from 'firebase/auth';
import { useState, useEffect } from 'react';

// Firebase configuration
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyDIQ68KTtgSu0716r1X9p8XGGHJivdXY4Q",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "next-fc055.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "next-fc055",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "next-fc055.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "438736067565",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:438736067565:web:5ec706d253893954a0e5e4",
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID || "G-HQLTL9GQ5Y",
};

// Initialize Firebase
let app: FirebaseApp;
let auth: Auth;

if (typeof window !== 'undefined') {
  app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
  auth = getAuth(app);
} else {
  // Server-side: create a placeholder
  app = undefined as any;
  auth = undefined as any;
}

// Google Auth Provider
const googleProvider = new GoogleAuthProvider();
googleProvider.addScope('profile');
googleProvider.addScope('email');

// ============================================
// AUTH FUNCTIONS
// ============================================

/**
 * Sign in with Google OAuth
 */
export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const token = await result.user.getIdToken();
    
    // Store auth data
    localStorage.setItem('authToken', token);
    localStorage.setItem('userId', result.user.uid);
    
    // Create user in backend if first time
    await createUserInBackend(result.user);
    
    return result.user;
  } catch (error) {
    console.error('Google sign-in error:', error);
    throw error;
  }
};

/**
 * Sign in with email and password
 */
export const signInWithEmail = async (email: string, password: string) => {
  try {
    const result = await signInWithEmailAndPassword(auth, email, password);
    const token = await result.user.getIdToken();
    
    // Store auth data
    localStorage.setItem('authToken', token);
    localStorage.setItem('userId', result.user.uid);
    
    return result.user;
  } catch (error) {
    console.error('Email sign-in error:', error);
    throw error;
  }
};

/**
 * Sign up with email and password
 */
export const signUpWithEmail = async (email: string, password: string, displayName?: string) => {
  try {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    const token = await result.user.getIdToken();
    
    // Update profile if displayName provided
    if (displayName && result.user) {
      await updateProfile(result.user, { displayName });
    }
    
    // Store auth data
    localStorage.setItem('authToken', token);
    localStorage.setItem('userId', result.user.uid);
    
    // Create user in backend
    await createUserInBackend(result.user);
    
    return result.user;
  } catch (error) {
    console.error('Email sign-up error:', error);
    throw error;
  }
};

/**
 * Send password reset email
 */
export const resetPassword = async (email: string) => {
  try {
    await sendPasswordResetEmail(auth, email);
  } catch (error) {
    console.error('Password reset error:', error);
    throw error;
  }
};

/**
 * Confirm password reset with code and new password
 */
export const confirmPasswordResetWithCode = async (code: string, newPassword: string) => {
  try {
    await confirmPasswordReset(auth, code, newPassword);
  } catch (error) {
    console.error('Confirm password reset error:', error);
    throw error;
  }
};

/**
 * Verify password reset code
 */
export const verifyPasswordResetCodeFunc = async (code: string) => {
  try {
    const email = await verifyPasswordResetCode(auth, code);
    return email;
  } catch (error) {
    console.error('Verify password reset code error:', error);
    throw error;
  }
};

/**
 * Send email verification
 */
export const sendEmailVerificationFunc = async () => {
  try {
    if (auth.currentUser) {
      await sendEmailVerification(auth.currentUser);
    } else {
      throw new Error('No user signed in');
    }
  } catch (error) {
    console.error('Send email verification error:', error);
    throw error;
  }
};

/**
 * Apply action code (for email verification)
 */
export const applyActionCodeFunc = async (code: string) => {
  try {
    await applyActionCode(auth, code);
  } catch (error) {
    console.error('Apply action code error:', error);
    throw error;
  }
};

/**
 * Sign out current user
 */
export const signOut = async () => {
  try {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userId');
    await firebaseSignOut(auth);
  } catch (error) {
    console.error('Sign-out error:', error);
    throw error;
  }
};

/**
 * Listen to auth state changes
 */
export const onAuthChange = (callback: (user: User | null) => void) => {
  return onAuthStateChanged(auth, callback);
};

/**
 * Get current auth token
 */
export const getCurrentToken = async (): Promise<string | null> => {
  const { currentUser } = auth;
  if (!currentUser) return null;
  
  try {
    return await currentUser.getIdToken();
  } catch (error) {
    console.error('Error getting token:', error);
    return null;
  }
};

/**
 * Create user in backend database
 */
async function createUserInBackend(user: User): Promise<void> {
  try {
    const token = await user.getIdToken();
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    const response = await fetch(`${API_URL}/api/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        firebase_uid: user.uid,
        email: user.email,
        display_name: user.displayName || user.email?.split('@')[0],
        photo_url: user.photoURL,
      })
    });
    
    if (!response.ok && response.status !== 409) {
      // 409 means user already exists, which is fine
      console.error('Failed to create user in backend:', await response.text());
    }
  } catch (error) {
    console.error('Error creating user in backend:', error);
    // Don't throw - authentication succeeded, backend sync can be retried later
  }
}

/**
 * Custom hook for authentication state
 */
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  return { user, loading };
}

export { auth };
export default app;
