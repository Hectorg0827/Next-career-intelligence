'use client'

import { useState, useEffect } from 'react'
import { X } from 'lucide-react'

type CookiePreferences = {
  essential: boolean
  analytics: boolean
  functional: boolean
  marketing: boolean
}

const defaultPreferences: CookiePreferences = {
  essential: true, // Always true, can't be disabled
  analytics: false,
  functional: false,
  marketing: false,
}

export function CookieConsentBanner() {
  const [isVisible, setIsVisible] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  const [preferences, setPreferences] = useState<CookiePreferences>(defaultPreferences)

  useEffect(() => {
    // Check if user has already set preferences
    const consentGiven = localStorage.getItem('cookie_consent')
    if (!consentGiven) {
      // Show banner after 1 second delay for better UX
      const timer = setTimeout(() => {
        setIsVisible(true)
      }, 1000)
      return () => clearTimeout(timer)
    } else {
      // Load saved preferences
      try {
        const savedPreferences = JSON.parse(localStorage.getItem('cookie_preferences') || '{}')
        setPreferences({ ...defaultPreferences, ...savedPreferences })
      } catch (e) {
        console.error('Failed to load cookie preferences:', e)
      }
    }
  }, [])

  const savePreferences = (prefs: CookiePreferences) => {
    localStorage.setItem('cookie_consent', 'true')
    localStorage.setItem('cookie_preferences', JSON.stringify(prefs))
    localStorage.setItem('cookie_consent_date', new Date().toISOString())

    // Apply preferences
    applyPreferences(prefs)

    setIsVisible(false)
  }

  const acceptAll = () => {
    const allAccepted: CookiePreferences = {
      essential: true,
      analytics: true,
      functional: true,
      marketing: true,
    }
    savePreferences(allAccepted)
  }

  const acceptEssential = () => {
    savePreferences(defaultPreferences)
  }

  const saveCustom = () => {
    savePreferences(preferences)
  }

  const applyPreferences = (prefs: CookiePreferences) => {
    // Initialize or disable analytics based on preferences
    if (prefs.analytics) {
      // Initialize Google Analytics
      if (typeof window !== 'undefined' && (window as any).gtag) {
        (window as any).gtag('consent', 'update', {
          analytics_storage: 'granted',
        })
      }
    } else {
      // Disable analytics
      if (typeof window !== 'undefined' && (window as any).gtag) {
        (window as any).gtag('consent', 'update', {
          analytics_storage: 'denied',
        })
      }
    }

    // Handle functional cookies
    if (!prefs.functional) {
      // Remove functional cookies
      document.cookie.split(';').forEach((cookie) => {
        const name = cookie.split('=')[0].trim()
        if (name.includes('theme_preference') || name.includes('language_pref') || name.includes('dashboard_layout')) {
          document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
        }
      })
    }

    // Handle marketing cookies (currently not used, but prepared)
    if (!prefs.marketing) {
      // Would remove marketing cookies here
    }
  }

  if (!isVisible) return null

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/20 z-40" />

      {/* Banner */}
      <div className="fixed bottom-0 left-0 right-0 z-50 p-4 sm:p-6">
        <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-2xl border border-gray-200">
          <div className="p-6 sm:p-8">
            {!showDetails ? (
              /* Simple View */
              <>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start space-x-3">
                    <div className="text-3xl">🍪</div>
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900 mb-2">
                        We Value Your Privacy
                      </h2>
                      <p className="text-gray-600 text-sm sm:text-base">
                        We use cookies to enhance your experience, analyze site traffic, and provide personalized content.
                        By clicking "Accept All", you consent to our use of cookies.{' '}
                        <a href="/privacy" className="text-blue-600 hover:underline" target="_blank">
                          Learn more in our Privacy Policy
                        </a>
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={acceptEssential}
                    className="text-gray-400 hover:text-gray-600 transition"
                    aria-label="Accept essential only and close"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={acceptAll}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition"
                  >
                    Accept All Cookies
                  </button>
                  <button
                    onClick={acceptEssential}
                    className="flex-1 bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition"
                  >
                    Essential Only
                  </button>
                  <button
                    onClick={() => setShowDetails(true)}
                    className="flex-1 border-2 border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:border-gray-400 transition"
                  >
                    Customize
                  </button>
                </div>
              </>
            ) : (
              /* Detailed View */
              <>
                <div className="flex items-start justify-between mb-6">
                  <h2 className="text-2xl font-semibold text-gray-900">Cookie Preferences</h2>
                  <button
                    onClick={() => setShowDetails(false)}
                    className="text-gray-400 hover:text-gray-600 transition"
                    aria-label="Go back"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="space-y-6 mb-6">
                  {/* Essential Cookies */}
                  <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="font-semibold text-gray-900">Essential Cookies</h3>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Required</span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        These cookies are necessary for the website to function properly. They enable core features like
                        authentication, security, and account access.
                      </p>
                      <p className="text-xs text-gray-500">
                        Examples: Session token, authentication, CSRF protection
                      </p>
                    </div>
                    <div className="ml-4">
                      <input
                        type="checkbox"
                        checked={true}
                        disabled
                        className="w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded cursor-not-allowed"
                      />
                    </div>
                  </div>

                  {/* Analytics Cookies */}
                  <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-2">Analytics Cookies</h3>
                      <p className="text-sm text-gray-600 mb-2">
                        These cookies help us understand how visitors interact with our platform by collecting and reporting
                        information anonymously.
                      </p>
                      <p className="text-xs text-gray-500">
                        Examples: Google Analytics (_ga, _ga_*), page views, feature usage
                      </p>
                    </div>
                    <div className="ml-4">
                      <input
                        type="checkbox"
                        checked={preferences.analytics}
                        onChange={(e) =>
                          setPreferences({ ...preferences, analytics: e.target.checked })
                        }
                        className="w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
                      />
                    </div>
                  </div>

                  {/* Functional Cookies */}
                  <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-2">Functional Cookies</h3>
                      <p className="text-sm text-gray-600 mb-2">
                        These cookies enable enhanced functionality and personalization, such as remembering your preferences
                        and settings.
                      </p>
                      <p className="text-xs text-gray-500">
                        Examples: Dark mode preference, language, dashboard layout
                      </p>
                    </div>
                    <div className="ml-4">
                      <input
                        type="checkbox"
                        checked={preferences.functional}
                        onChange={(e) =>
                          setPreferences({ ...preferences, functional: e.target.checked })
                        }
                        className="w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
                      />
                    </div>
                  </div>

                  {/* Marketing Cookies */}
                  <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg opacity-50">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="font-semibold text-gray-900">Marketing Cookies</h3>
                        <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">Not Used</span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">
                        We currently do not use marketing or advertising cookies. If we choose to use them in the future,
                        we will ask for your consent.
                      </p>
                    </div>
                    <div className="ml-4">
                      <input
                        type="checkbox"
                        checked={false}
                        disabled
                        className="w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded cursor-not-allowed"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={acceptAll}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition"
                  >
                    Accept All
                  </button>
                  <button
                    onClick={saveCustom}
                    className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
                  >
                    Save My Preferences
                  </button>
                  <button
                    onClick={acceptEssential}
                    className="flex-1 bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition"
                  >
                    Essential Only
                  </button>
                </div>

                <div className="mt-4 text-center">
                  <a
                    href="/cookies"
                    target="_blank"
                    className="text-sm text-blue-600 hover:underline"
                  >
                    Read our Cookie Policy
                  </a>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

// Hook to check if analytics is enabled
export function useAnalyticsEnabled(): boolean {
  const [enabled, setEnabled] = useState(false)

  useEffect(() => {
    try {
      const preferences = JSON.parse(localStorage.getItem('cookie_preferences') || '{}')
      setEnabled(preferences.analytics === true)
    } catch {
      setEnabled(false)
    }
  }, [])

  return enabled
}

// Hook to check if functional cookies are enabled
export function useFunctionalCookiesEnabled(): boolean {
  const [enabled, setEnabled] = useState(false)

  useEffect(() => {
    try {
      const preferences = JSON.parse(localStorage.getItem('cookie_preferences') || '{}')
      setEnabled(preferences.functional === true)
    } catch {
      setEnabled(false)
    }
  }, [])

  return enabled
}
