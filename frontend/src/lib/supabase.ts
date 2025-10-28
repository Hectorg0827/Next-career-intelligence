import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://whxbxjpymksgvixudnjh.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

if (!supabaseAnonKey && process.env.NODE_ENV === 'production') {
  console.error('⚠️ NEXT_PUBLIC_SUPABASE_ANON_KEY is not set in production!')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// ============================================
// AUTH HELPERS
// ============================================

export const auth = {
  /**
   * Sign up a new user
   */
  signUp: async (email: string, password: string) => {
    return await supabase.auth.signUp({ email, password })
  },
  
  /**
   * Sign in existing user
   */
  signIn: async (email: string, password: string) => {
    return await supabase.auth.signInWithPassword({ email, password })
  },
  
  /**
   * Sign out current user
   */
  signOut: async () => {
    return await supabase.auth.signOut()
  },
  
  /**
   * Get current user
   */
  getUser: async () => {
    return await supabase.auth.getUser()
  },
  
  /**
   * Get current session
   */
  getSession: async () => {
    return await supabase.auth.getSession()
  },
  
  /**
   * Sign in with Google OAuth
   */
  signInWithGoogle: async () => {
    return await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/dashboard`
      }
    })
  }
}

// ============================================
// DATABASE HELPERS
// ============================================

export const db = {
  /**
   * Save career analysis to database
   */
  saveAnalysis: async (userId: string, data: any) => {
    return await supabase
      .from('analyses')
      .insert({
        user_id: userId,
        job_title: data.job_title,
        risk_score: data.ai_displacement_risk?.score,
        risk_level: data.ai_displacement_risk?.level,
        analysis_data: data,
        created_at: new Date().toISOString()
      })
  },
  
  /**
   * Get all analyses for a user
   */
  getUserAnalyses: async (userId: string) => {
    return await supabase
      .from('analyses')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
  },
  
  /**
   * Get single analysis by ID
   */
  getAnalysis: async (analysisId: string) => {
    return await supabase
      .from('analyses')
      .select('*')
      .eq('id', analysisId)
      .single()
  },
  
  /**
   * Save career roadmap
   */
  saveRoadmap: async (userId: string, analysisId: string, data: any) => {
    return await supabase
      .from('career_roadmaps')
      .insert({
        user_id: userId,
        analysis_id: analysisId,
        roadmap_data: data,
        created_at: new Date().toISOString()
      })
  },
  
  /**
   * Get user's roadmaps
   */
  getUserRoadmaps: async (userId: string) => {
    return await supabase
      .from('career_roadmaps')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
  }
}

// ============================================
// REAL-TIME SUBSCRIPTIONS (Optional)
// ============================================

export const subscribeToAnalyses = (userId: string, callback: (payload: any) => void) => {
  return supabase
    .channel('analyses_changes')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'analyses',
        filter: `user_id=eq.${userId}`
      },
      callback
    )
    .subscribe()
}
