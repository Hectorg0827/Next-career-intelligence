"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  Sparkles,
  Target,
  Activity,
  Users,
  Award,
  ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useRouter } from 'next/navigation'

interface CareerHealthScore {
  overall_score: number
  grade: string
  breakdown: {
    profile_completeness: number
    skill_currency: number
    market_activity: number
    goal_progress: number
    network_strength: number
  }
  recommendations: string[]
  trend?: 'improving' | 'stable' | 'declining' | null
}

export function CareerHealthScoreWidget() {
  const router = useRouter()
  const [score, setScore] = useState<CareerHealthScore | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchScore()
  }, [])

  const fetchScore = async () => {
    try {
      const response = await fetch('/api/career-health/score', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setScore(data)
      }
    } catch (error) {
      console.error('Failed to fetch Career Health Score:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      const response = await fetch('/api/career-health/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })

      if (response.ok) {
        await fetchScore()
      }
    } catch (error) {
      console.error('Failed to refresh score:', error)
    } finally {
      setRefreshing(false)
    }
  }

  if (loading) {
    return (
      <Card className="col-span-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-500" />
                Career Health Score
              </CardTitle>
              <CardDescription>Loading your career metrics...</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 animate-pulse">
            <div className="h-32 bg-gray-200 rounded-lg" />
            <div className="h-20 bg-gray-200 rounded-lg" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!score) {
    return (
      <Card className="col-span-2">
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <p className="text-gray-500">Unable to load Career Health Score</p>
            <Button onClick={fetchScore} variant="outline" className="mt-4">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const getTrendIcon = () => {
    if (!score.trend) return null

    switch (score.trend) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case 'declining':
        return <TrendingDown className="w-4 h-4 text-red-500" />
      case 'stable':
        return <Minus className="w-4 h-4 text-gray-500" />
      default:
        return null
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getGradeBadgeVariant = (grade: string) => {
    if (grade === 'A') return 'default'
    if (grade === 'B') return 'secondary'
    return 'outline'
  }

  const componentIcons = {
    profile_completeness: Target,
    skill_currency: Sparkles,
    market_activity: Activity,
    goal_progress: Award,
    network_strength: Users
  }

  const componentLabels = {
    profile_completeness: 'Profile Completeness',
    skill_currency: 'Skill Currency',
    market_activity: 'Market Activity',
    goal_progress: 'Goal Progress',
    network_strength: 'Network Strength'
  }

  return (
    <Card className="col-span-2 hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-500" />
              Career Health Score
            </CardTitle>
            <CardDescription>
              Your overall career vitality and positioning
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            disabled={refreshing}
            className="rounded-full"
          >
            <RefreshCw className={cn("w-4 h-4", refreshing && "animate-spin")} />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Main Score Display */}
        <div className="relative">
          <div className="flex items-center justify-center">
            <div className="relative">
              {/* Circular Progress */}
              <svg className="w-40 h-40 transform -rotate-90">
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  stroke="currentColor"
                  strokeWidth="10"
                  fill="none"
                  className="text-gray-200"
                />
                <circle
                  cx="80"
                  cy="80"
                  r="70"
                  stroke="currentColor"
                  strokeWidth="10"
                  fill="none"
                  strokeDasharray={`${2 * Math.PI * 70}`}
                  strokeDashoffset={`${2 * Math.PI * 70 * (1 - score.overall_score / 100)}`}
                  className={cn(
                    "transition-all duration-1000 ease-out",
                    score.overall_score >= 80 ? "text-green-500" :
                    score.overall_score >= 60 ? "text-yellow-500" :
                    "text-red-500"
                  )}
                  strokeLinecap="round"
                />
              </svg>

              {/* Score Text */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className={cn("text-5xl font-bold", getScoreColor(score.overall_score))}>
                  {score.overall_score}
                </div>
                <div className="text-sm text-gray-500 mt-1">out of 100</div>
                <Badge
                  variant={getGradeBadgeVariant(score.grade)}
                  className="mt-2"
                >
                  Grade {score.grade}
                </Badge>
              </div>
            </div>
          </div>

          {/* Trend Indicator */}
          {score.trend && (
            <div className="absolute top-0 right-0">
              <div className={cn(
                "flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
                score.trend === 'improving' && "bg-green-100 text-green-700",
                score.trend === 'declining' && "bg-red-100 text-red-700",
                score.trend === 'stable' && "bg-gray-100 text-gray-700"
              )}>
                {getTrendIcon()}
                <span className="capitalize">{score.trend}</span>
              </div>
            </div>
          )}
        </div>

        {/* Breakdown */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-700">Score Breakdown</h4>
          {Object.entries(score.breakdown).map(([key, value]) => {
            const Icon = componentIcons[key as keyof typeof componentIcons]
            const label = componentLabels[key as keyof typeof componentLabels]

            return (
              <div key={key} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">{label}</span>
                  </div>
                  <span className="font-medium">{Math.round(value)}%</span>
                </div>
                <Progress value={value} className="h-2" />
              </div>
            )
          })}
        </div>

        {/* Recommendations */}
        {score.recommendations && score.recommendations.length > 0 && (
          <div className="space-y-2 pt-4 border-t">
            <h4 className="text-sm font-semibold text-gray-700">Top Recommendations</h4>
            <div className="space-y-2">
              {score.recommendations.slice(0, 3).map((rec, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2 text-sm text-gray-600 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-1.5 flex-shrink-0" />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* View Details Button */}
        <Button
          variant="outline"
          className="w-full group"
          onClick={() => router.push('/career-health')}
        >
          View Detailed Insights
          <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
        </Button>
      </CardContent>
    </Card>
  )
}
