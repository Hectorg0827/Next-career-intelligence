"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  Target,
  TrendingUp,
  Clock,
  DollarSign,
  Zap,
  BookOpen,
  AlertCircle,
  ExternalLink
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SkillGap {
  skill: string
  category: string
  demand_score: number
  salary_premium: number
  learning_curve: string
  importance: number
  required_level: string
  substitutable: boolean
  learning_time_estimate: number
  priority: 'high' | 'medium' | 'low'
}

interface SkillGapData {
  target_role: string
  target_seniority: string
  skill_gaps: SkillGap[]
  total_gaps: number
  high_priority_gaps: SkillGap[]
  estimated_learning_time: number
}

export function SkillGapVisualization({ targetRole, targetSeniority = 'mid' }: {
  targetRole: string
  targetSeniority?: string
}) {
  const [data, setData] = useState<SkillGapData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSkillGaps()
  }, [targetRole, targetSeniority])

  const fetchSkillGaps = async () => {
    try {
      setLoading(true)
      setError(null)

      const token = localStorage.getItem('token')
      const response = await fetch(
        `/api/talent-graph/skill-gaps?target_role=${encodeURIComponent(targetRole)}&target_seniority=${targetSeniority}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      if (!response.ok) {
        if (response.status === 503) {
          throw new Error('Talent Graph is currently unavailable. Please try again later.')
        }
        throw new Error('Failed to fetch skill gaps')
      }

      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Skill Gap Analysis
          </CardTitle>
          <CardDescription>Loading your personalized skill gaps...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 animate-pulse">
            <div className="h-20 bg-gray-200 rounded-lg" />
            <div className="h-20 bg-gray-200 rounded-lg" />
            <div className="h-20 bg-gray-200 rounded-lg" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={fetchSkillGaps} variant="outline">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!data || data.total_gaps === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5 text-green-500" />
            No Skill Gaps Found
          </CardTitle>
          <CardDescription>
            You already have all the skills needed for {targetRole}!
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-700">
              ✓ You're ready to apply for {targetRole} ({targetSeniority}) positions!
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getPriorityBadgeVariant = (priority: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (priority) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'outline'
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-purple-500" />
              Skill Gaps for {targetRole}
            </CardTitle>
            <CardDescription>
              {data.total_gaps} skill{data.total_gaps !== 1 ? 's' : ''} to acquire •
              ~{data.estimated_learning_time} weeks estimated learning time
            </CardDescription>
          </div>
          <Badge variant="outline" className="text-sm">
            {targetSeniority} level
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="text-2xl font-bold text-red-600">
              {data.high_priority_gaps.length}
            </div>
            <div className="text-xs text-red-600">High Priority</div>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <div className="text-2xl font-bold text-purple-600">
              {data.total_gaps}
            </div>
            <div className="text-xs text-purple-600">Total Gaps</div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="text-2xl font-bold text-blue-600">
              {data.estimated_learning_time}
            </div>
            <div className="text-xs text-blue-600">Weeks to Learn</div>
          </div>
        </div>

        {/* High Priority Skills */}
        {data.high_priority_gaps.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              🔥 High Priority Skills
            </h3>
            <div className="space-y-3">
              {data.high_priority_gaps.map((gap, index) => (
                <SkillGapCard key={index} gap={gap} />
              ))}
            </div>
          </div>
        )}

        {/* Other Skills */}
        {data.skill_gaps.filter(g => g.priority !== 'high').length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              📚 Other Skills to Consider
            </h3>
            <div className="space-y-3">
              {data.skill_gaps
                .filter(g => g.priority !== 'high')
                .slice(0, 5)
                .map((gap, index) => (
                  <SkillGapCard key={index} gap={gap} />
                ))}
            </div>
          </div>
        )}

        {/* Learning Path Recommendation */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
          <h4 className="font-semibold text-purple-900 mb-2 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Recommended Learning Path
          </h4>
          <ol className="space-y-1 text-sm text-purple-800">
            {data.high_priority_gaps.slice(0, 3).map((gap, index) => (
              <li key={index}>
                {index + 1}. Start with <strong>{gap.skill}</strong> ({gap.learning_time_estimate} weeks)
              </li>
            ))}
          </ol>
          <Button className="w-full mt-4" size="sm">
            Create Learning Plan
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function SkillGapCard({ gap }: { gap: SkillGap }) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-500 bg-red-50'
      case 'medium': return 'border-yellow-500 bg-yellow-50'
      case 'low': return 'border-blue-500 bg-blue-50'
      default: return 'border-gray-300 bg-gray-50'
    }
  }

  const getPriorityBadge = (priority: string): "default" | "secondary" | "destructive" => {
    switch (priority) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      default: return 'secondary'
    }
  }

  return (
    <div className={cn(
      "border-l-4 rounded-lg p-4 hover:shadow-md transition-shadow",
      getPriorityColor(gap.priority)
    )}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-gray-900">{gap.skill}</h4>
            <Badge variant={getPriorityBadge(gap.priority)} className="text-xs">
              {gap.priority}
            </Badge>
          </div>
          <p className="text-xs text-gray-600">{gap.category}</p>
        </div>
        <div className="text-right">
          <div className="text-sm font-semibold text-gray-700">
            {Math.round(gap.importance * 100)}%
          </div>
          <div className="text-xs text-gray-500">importance</div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3 text-xs">
        <div className="flex items-center gap-1 text-gray-600">
          <TrendingUp className="w-3 h-3" />
          <span>Demand: {gap.demand_score}/100</span>
        </div>
        <div className="flex items-center gap-1 text-gray-600">
          <Clock className="w-3 h-3" />
          <span>{gap.learning_time_estimate}w to learn</span>
        </div>
        <div className="flex items-center gap-1 text-gray-600">
          <DollarSign className="w-3 h-3" />
          <span>+${(gap.salary_premium / 1000).toFixed(0)}k</span>
        </div>
        <div className="flex items-center gap-1 text-gray-600">
          <BookOpen className="w-3 h-3" />
          <span className="capitalize">{gap.learning_curve}</span>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-2">
        <Badge variant="outline" className="text-xs">
          {gap.required_level}
        </Badge>
        {gap.substitutable && (
          <Badge variant="secondary" className="text-xs">
            Substitutable
          </Badge>
        )}
      </div>

      <Button
        variant="ghost"
        size="sm"
        className="w-full mt-3 text-xs"
        onClick={() => window.open(`https://www.coursera.org/search?query=${encodeURIComponent(gap.skill)}`, '_blank')}
      >
        Find Courses <ExternalLink className="w-3 h-3 ml-1" />
      </Button>
    </div>
  )
}
