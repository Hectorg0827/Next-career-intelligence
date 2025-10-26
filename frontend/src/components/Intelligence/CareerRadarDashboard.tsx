/**
 * Career Radar Dashboard
 * 
 * Real-time intelligence dashboard showing:
 * - Risk scan results
 * - Market trends
 * - Peer benchmarking
 * - Career trajectory forecast
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, TrendingUp, Users, Target, Award, Activity } from 'lucide-react';

interface RiskThreat {
  type: string;
  severity: string;
  title: string;
  description: string;
  urgency: string;
}

interface RiskScanData {
  overall_risk_score: number;
  risk_level: string;
  threat_count: number;
  threats: RiskThreat[];
  top_priority_actions: string[];
}

interface MarketSnapshot {
  demand_level: string;
  salary_trend: string;
  competition_level: string;
  hot_skills: string[];
  market_insights: string[];
}

interface PeerBenchmark {
  overall_percentile: number;
  overall_rating: string;
  strengths: string[];
  improvement_areas: string[];
}

interface CareerRadarProps {
  userId: string;
  apiUrl?: string;
}

export default function CareerRadarDashboard({ userId, apiUrl = '/api/intelligence' }: CareerRadarProps) {
  const [riskData, setRiskData] = useState<RiskScanData | null>(null);
  const [marketData, setMarketData] = useState<MarketSnapshot | null>(null);
  const [benchmarkData, setBenchmarkData] = useState<PeerBenchmark | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIntelligenceData();
  }, [userId]);

  const loadIntelligenceData = async () => {
    try {
      setLoading(true);
      
      // Load risk scan
      const riskResponse = await fetch(`${apiUrl}/risk-scan`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (riskResponse.ok) {
        const riskResult = await riskResponse.json();
        setRiskData(riskResult.risk_report);
      }

      // Load peer benchmark
      const benchmarkResponse = await fetch(`${apiUrl}/peer-benchmark`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (benchmarkResponse.ok) {
        const benchmarkResult = await benchmarkResponse.json();
        setBenchmarkData(benchmarkResult.benchmark);
      }

    } catch (error) {
      console.error('Failed to load intelligence data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    const colors: { [key: string]: string } = {
      'critical': 'bg-red-500',
      'high': 'bg-orange-500',
      'medium': 'bg-yellow-500',
      'low': 'bg-green-500'
    };
    return colors[level?.toLowerCase()] || 'bg-gray-500';
  };

  const getSeverityColor = (severity: string) => {
    const colors: { [key: string]: string } = {
      'critical': 'text-red-600 border-red-600',
      'high': 'text-orange-600 border-orange-600',
      'medium': 'text-yellow-600 border-yellow-600',
      'low': 'text-green-600 border-green-600'
    };
    return colors[severity?.toLowerCase()] || 'text-gray-600 border-gray-600';
  };

  const getPercentileColor = (percentile: number) => {
    if (percentile >= 75) return 'text-green-600';
    if (percentile >= 50) return 'text-blue-600';
    if (percentile >= 25) return 'text-yellow-600';
    return 'text-orange-600';
  };

  if (loading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Career Radar</h2>
        <p className="text-muted-foreground">
          Real-time intelligence and predictive insights for your career
        </p>
      </div>

      {/* Risk Overview */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {riskData && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Risk Score</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{riskData.overall_risk_score}/100</div>
                <div className="flex items-center gap-2 mt-2">
                  <div className={`h-2 w-2 rounded-full ${getRiskColor(riskData.risk_level)}`}></div>
                  <p className="text-xs text-muted-foreground capitalize">{riskData.risk_level} Risk</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Threats</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{riskData.threat_count}</div>
                <p className="text-xs text-muted-foreground">
                  Requires attention
                </p>
              </CardContent>
            </Card>
          </>
        )}

        {benchmarkData && (
          <>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Peer Rank</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getPercentileColor(benchmarkData.overall_percentile)}`}>
                  {benchmarkData.overall_percentile}th
                </div>
                <p className="text-xs text-muted-foreground capitalize">
                  {benchmarkData.overall_rating.replace('_', ' ')}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Strengths</CardTitle>
                <Award className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{benchmarkData.strengths.length}</div>
                <p className="text-xs text-muted-foreground">
                  Areas excelling
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Threats & Warnings */}
      {riskData && riskData.threats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Active Threats & Warnings
            </CardTitle>
            <CardDescription>
              Issues requiring your attention
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {riskData.threats.slice(0, 5).map((threat, index) => (
                <div key={index} className="flex gap-4 p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline" className={getSeverityColor(threat.severity)}>
                        {threat.severity}
                      </Badge>
                      <span className="text-sm text-muted-foreground capitalize">{threat.type.replace('_', ' ')}</span>
                    </div>
                    <h4 className="font-semibold mb-1">{threat.title}</h4>
                    <p className="text-sm text-muted-foreground">{threat.description}</p>
                  </div>
                  <div className="text-xs text-muted-foreground capitalize">
                    {threat.urgency}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Priority Actions */}
      {riskData && riskData.top_priority_actions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Priority Actions
            </CardTitle>
            <CardDescription>
              Recommended steps to improve your career health
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {riskData.top_priority_actions.map((action, index) => (
                <li key={index} className="flex items-start gap-3">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500"></div>
                  <span className="text-sm">{action}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Peer Benchmarking Details */}
      {benchmarkData && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-green-600">Your Strengths</CardTitle>
              <CardDescription>Areas where you excel vs peers</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {benchmarkData.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <Award className="h-4 w-4 text-green-600 mt-0.5" />
                    <span className="text-sm">{strength}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-orange-600">Improvement Areas</CardTitle>
              <CardDescription>Opportunities to close gaps</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {benchmarkData.improvement_areas.map((area, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <TrendingUp className="h-4 w-4 text-orange-600 mt-0.5" />
                    <span className="text-sm">{area}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
