/**
 * useAuth Hook
 * Manages Firebase authentication state and user data
 */

'use client';

import { useState, useEffect } from 'react';
import { User } from 'firebase/auth';
import { onAuthChange } from '@/lib/firebase';

interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
}

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthChange(async (firebaseUser: User | null) => {
      try {
        if (firebaseUser) {
          setUser({
            uid: firebaseUser.uid,
            email: firebaseUser.email,
            displayName: firebaseUser.displayName,
            photoURL: firebaseUser.photoURL,
          });
          
          // Store auth token
          const token = await firebaseUser.getIdToken();
          localStorage.setItem('authToken', token);
          localStorage.setItem('userId', firebaseUser.uid);
        } else {
          setUser(null);
          localStorage.removeItem('authToken');
          localStorage.removeItem('userId');
        }
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, []);

  return { user, loading, error, isAuthenticated: !!user };
}
