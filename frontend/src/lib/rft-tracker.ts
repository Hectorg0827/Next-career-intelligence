/**
 * RFT (Reinforcement Fine-Tuning) Tracker
 *
 * Collects user feedback signals for AI model improvement.
 * Every time a user accepts/rejects an AI suggestion, we record it.
 */

interface RFTFeedbackData {
  event_type: string
  agent_name: string
  prompt: string
  model_output: string
  preferred_output?: string
  user_rating?: number
  user_accepted?: boolean
  user_edited?: boolean
  context_data?: Record<string, any>
  related_job_id?: string
  related_application_id?: string
  related_session_id?: string
}

class RFTTrackerClass {
  private baseUrl: string

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }

  private async sendFeedback(data: RFTFeedbackData): Promise<void> {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        console.warn('No auth token - RFT feedback not recorded')
        return
      }

      const response = await fetch(`${this.baseUrl}/api/rft/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        console.error('Failed to record RFT feedback:', response.statusText)
      }
    } catch (error) {
      console.error('RFT tracking error:', error)
    }
  }

  /**
   * Track when user accepts an AI-generated resume bullet
   */
  async trackResumeBulletAccepted(data: {
    bulletId: string
    originalBullet: string
    aiRewrittenBullet: string
    jobDescription: string
  }): Promise<void> {
    await this.sendFeedback({
      event_type: 'resume_bullet_accepted',
      agent_name: 'resume_studio',
      prompt: `Job Description:\n${data.jobDescription}\n\nOriginal Bullet:\n${data.originalBullet}`,
      model_output: data.aiRewrittenBullet,
      preferred_output: data.aiRewrittenBullet,
      user_accepted: true,
      context_data: {
        bullet_id: data.bulletId,
        job_description: data.jobDescription
      }
    })
  }

  /**
   * Track when user rejects AI suggestion and manually edits
   */
  async trackResumeBulletRejected(data: {
    bulletId: string
    originalBullet: string
    aiRewrittenBullet: string
    userFinalEdit: string
    jobDescription: string
  }): Promise<void> {
    await this.sendFeedback({
      event_type: 'resume_bullet_rejected',
      agent_name: 'resume_studio',
      prompt: `Job Description:\n${data.jobDescription}\n\nOriginal Bullet:\n${data.originalBullet}`,
      model_output: data.aiRewrittenBullet,
      preferred_output: data.userFinalEdit,
      user_accepted: false,
      user_edited: true,
      context_data: {
        bullet_id: data.bulletId,
        job_description: data.jobDescription
      }
    })
  }

  /**
   * Track when user rates AI-generated interview feedback
   */
  async trackInterviewAnswerRated(data: {
    sessionId: string
    question: string
    userAnswer: string
    aiFeedback: string
    userRating: 1 | 2 | 3 | 4 | 5
  }): Promise<void> {
    await this.sendFeedback({
      event_type: 'interview_answer_rated',
      agent_name: 'interviewer_ai',
      prompt: `Question:\n${data.question}\n\nUser Answer:\n${data.userAnswer}`,
      model_output: data.aiFeedback,
      user_rating: data.userRating,
      related_session_id: data.sessionId,
      context_data: {
        session_id: data.sessionId
      }
    })
  }

  /**
   * Track when user accepts cover letter
   */
  async trackCoverLetterAccepted(data: {
    originalCoverLetter: string
    aiGeneratedCoverLetter: string
    jobDescription: string
    jobId?: string
  }): Promise<void> {
    await this.sendFeedback({
      event_type: 'cover_letter_accepted',
      agent_name: 'resume_studio',
      prompt: `Job Description:\n${data.jobDescription}\n\nOriginal:\n${data.originalCoverLetter}`,
      model_output: data.aiGeneratedCoverLetter,
      preferred_output: data.aiGeneratedCoverLetter,
      user_accepted: true,
      related_job_id: data.jobId,
      context_data: {
        job_description: data.jobDescription
      }
    })
  }

  /**
   * Track when user accepts career advice
   */
  async trackCareerAdviceAccepted(data: {
    userQuestion: string
    aiResponse: string
    wasHelpful: boolean
  }): Promise<void> {
    await this.sendFeedback({
      event_type: 'career_advice_rated',
      agent_name: 'career_coach',
      prompt: data.userQuestion,
      model_output: data.aiResponse,
      user_accepted: data.wasHelpful,
      context_data: {
        was_helpful: data.wasHelpful
      }
    })
  }

  /**
   * ULTIMATE SUCCESS SIGNAL: User got interview or offer
   * This retroactively updates all related feedback
   */
  async markApplicationSuccess(data: {
    applicationId: string
    status: 'interview' | 'offer'
  }): Promise<void> {
    try {
      const token = localStorage.getItem('token')
      if (!token) return

      await fetch(`${this.baseUrl}/api/rft/application-success`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      })
    } catch (error) {
      console.error('Failed to mark application success:', error)
    }
  }

  /**
   * Get user's feedback statistics
   */
  async getMyStats(): Promise<any> {
    try {
      const token = localStorage.getItem('token')
      if (!token) return null

      const response = await fetch(`${this.baseUrl}/api/rft/feedback/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        return await response.json()
      }
    } catch (error) {
      console.error('Failed to get RFT stats:', error)
    }
    return null
  }
}

// Export singleton instance
export const RFTTracker = new RFTTrackerClass()
