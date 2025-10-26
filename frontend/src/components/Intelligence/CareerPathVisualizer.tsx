/**
 * Career Path Visualizer
 * 
 * Interactive visualization of predicted career trajectories
 * Shows multiple potential paths with probabilities
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TrendingUp, Calendar, DollarSign, Star, ChevronRight } from 'lucide-react';

interface PredictedRole {
  title: string;
  year: number;
  probability: number;
  salary_range: string;
  requirements: string[];
}

interface CareerForecast {
  predicted_roles: PredictedRole[];
  skill_evolution: { [key: string]: string[] };
  key_milestones: string[];
  alternative_paths: string[];
}

interface CareerPathVisualizerProps {
  userId: string;
  timeHorizon?: number;
  apiUrl?: string;
}

export default function CareerPathVisualizer({
  userId,
  timeHorizon = 3,
  apiUrl = '/api/intelligence'
}: CareerPathVisualizerProps) {
  const [forecast, setForecast] = useState<CareerForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPath, setSelectedPath] = useState<number>(0);

  useEffect(() => {
    loadCareerForecast();
  }, [userId, timeHorizon]);

  const loadCareerForecast = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`${apiUrl}/career-forecast?time_horizon=${timeHorizon}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        setForecast(result.forecast);
      }
    } catch (error) {
      console.error('Failed to load career forecast:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProbabilityColor = (probability: number) => {
    if (probability >= 70) return 'text-green-600 bg-green-50 border-green-200';
    if (probability >= 50) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (probability >= 30) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-gray-600 bg-gray-50 border-gray-200';
  };

  if (loading) {
    return (
      <Card className="animate-pulse">
        <CardHeader>
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3 mt-2"></div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!forecast) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Career Path Forecast</CardTitle>
          <CardDescription>Unable to load forecast data</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-6 w-6" />
            Your Career Trajectory
          </CardTitle>
          <CardDescription>
            AI-predicted career paths over the next {timeHorizon} years
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Timeline Visualization */}
          <div className="relative">
            {forecast.predicted_roles && forecast.predicted_roles.length > 0 ? (
              <div className="space-y-8">
                {/* Current Position */}
                <div className="flex items-start gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-4 h-4 rounded-full bg-blue-600"></div>
                    <div className="w-0.5 h-20 bg-gray-300"></div>
                  </div>
                  <div className="flex-1 pt-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold">Current Position</span>
                      <Badge variant="outline" className="text-xs">Now</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Your starting point</p>
                  </div>
                </div>

                {/* Predicted Roles */}
                {forecast.predicted_roles.map((role, index) => (
                  <div key={index} className="flex items-start gap-4">
                    <div className="flex flex-col items-center">
                      <div className={`w-4 h-4 rounded-full ${
                        role.probability >= 70 ? 'bg-green-600' :
                        role.probability >= 50 ? 'bg-blue-600' :
                        role.probability >= 30 ? 'bg-yellow-600' :
                        'bg-gray-400'
                      }`}></div>
                      {index < forecast.predicted_roles.length - 1 && (
                        <div className="w-0.5 h-20 bg-gray-300"></div>
                      )}
                    </div>
                    <div className="flex-1 -mt-1">
                      <Card className={`border-2 ${getProbabilityColor(role.probability)}`}>
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h4 className="font-semibold text-lg">{role.title}</h4>
                              <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                                <span className="flex items-center gap-1">
                                  <Calendar className="h-3 w-3" />
                                  Year {role.year}
                                </span>
                                <span className="flex items-center gap-1">
                                  <DollarSign className="h-3 w-3" />
                                  {role.salary_range}
                                </span>
                              </div>
                            </div>
                            <Badge className={getProbabilityColor(role.probability)}>
                              {role.probability}% likely
                            </Badge>
                          </div>
                          
                          {role.requirements && role.requirements.length > 0 && (
                            <div className="mt-3">
                              <p className="text-xs font-medium mb-2">Key Requirements:</p>
                              <div className="flex flex-wrap gap-2">
                                {role.requirements.slice(0, 4).map((req, i) => (
                                  <Badge key={i} variant="secondary" className="text-xs">
                                    {req}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">
                No career predictions available. Complete your profile for personalized forecasts.
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Skill Evolution */}
      {forecast.skill_evolution && Object.keys(forecast.skill_evolution).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5" />
              Skill Evolution Plan
            </CardTitle>
            <CardDescription>
              Skills to develop year by year
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(forecast.skill_evolution).map(([year, skills]) => (
                <div key={year} className="flex gap-4">
                  <div className="font-semibold text-sm w-20 capitalize">{year.replace('_', ' ')}</div>
                  <div className="flex-1 flex flex-wrap gap-2">
                    {Array.isArray(skills) && skills.map((skill, i) => (
                      <Badge key={i} variant="outline">{skill}</Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Milestones */}
      {forecast.key_milestones && forecast.key_milestones.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Key Milestones</CardTitle>
            <CardDescription>
              Important achievements to target
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {forecast.key_milestones.map((milestone, index) => (
                <li key={index} className="flex items-start gap-3">
                  <ChevronRight className="h-4 w-4 text-blue-600 mt-0.5" />
                  <span className="text-sm">{milestone}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Alternative Paths */}
      {forecast.alternative_paths && forecast.alternative_paths.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Alternative Career Paths</CardTitle>
            <CardDescription>
              Other viable directions to consider
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2">
              {forecast.alternative_paths.map((path, index) => (
                <div key={index} className="p-3 border rounded-lg hover:border-blue-500 transition-colors cursor-pointer">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">{path}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
