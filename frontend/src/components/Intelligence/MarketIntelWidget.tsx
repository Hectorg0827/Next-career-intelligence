/**
 * Market Intelligence Widget
 * 
 * Displays real-time market data, salary trends, and emerging skills
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TrendingUp, TrendingDown, Minus, DollarSign, Zap, AlertCircle } from 'lucide-react';

interface MarketSnapshot {
  demand_level: string;
  salary_trend: string;
  competition_level: string;
  hot_skills: string[];
  market_insights: string[];
  timestamp: string;
}

interface SalaryData {
  current_range: {
    min: number;
    max: number;
    median: number;
  };
  trend_direction: string;
  percentile_breakdown: {
    '25th': number;
    '50th': number;
    '75th': number;
    '90th': number;
  };
}

interface EmergingSkill {
  skill_name: string;
  growth_rate: number;
  adoption_stage: string;
  related_roles: string[];
}

interface MarketIntelWidgetProps {
  role: string;
  location?: string;
  industry?: string;
  apiUrl?: string;
}

export default function MarketIntelWidget({
  role,
  location,
  industry,
  apiUrl = '/api/intelligence'
}: MarketIntelWidgetProps) {
  const [snapshot, setSnapshot] = useState<MarketSnapshot | null>(null);
  const [salaryData, setSalaryData] = useState<SalaryData | null>(null);
  const [emergingSkills, setEmergingSkills] = useState<EmergingSkill[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMarketData();
  }, [role, location, industry]);

  const loadMarketData = async () => {
    try {
      setLoading(true);

      // Load market snapshot
      const snapshotUrl = location
        ? `${apiUrl}/market-snapshot/${encodeURIComponent(role)}?location=${encodeURIComponent(location)}`
        : `${apiUrl}/market-snapshot/${encodeURIComponent(role)}`;
      
      const snapshotResponse = await fetch(snapshotUrl, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (snapshotResponse.ok) {
        const result = await snapshotResponse.json();
        setSnapshot(result.snapshot);
      }

      // Load salary trends
      const salaryUrl = location
        ? `${apiUrl}/salary-trends/${encodeURIComponent(role)}?location=${encodeURIComponent(location)}`
        : `${apiUrl}/salary-trends/${encodeURIComponent(role)}`;
      
      const salaryResponse = await fetch(salaryUrl, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (salaryResponse.ok) {
        const result = await salaryResponse.json();
        setSalaryData(result.salary_data);
      }

      // Load emerging skills
      if (industry) {
        const skillsResponse = await fetch(`${apiUrl}/emerging-skills/${encodeURIComponent(industry)}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        if (skillsResponse.ok) {
          const result = await skillsResponse.json();
          setEmergingSkills(result.emerging_skills || []);
        }
      }

    } catch (error) {
      console.error('Failed to load market data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDemandColor = (level: string) => {
    const normalized = level?.toLowerCase() || '';
    if (normalized.includes('high')) return 'text-green-600 bg-green-50';
    if (normalized.includes('medium')) return 'text-yellow-600 bg-yellow-50';
    return 'text-orange-600 bg-orange-50';
  };

  const getTrendIcon = (trend: string) => {
    const normalized = trend?.toLowerCase() || '';
    if (normalized.includes('increas') || normalized.includes('up')) {
      return <TrendingUp className="h-4 w-4 text-green-600" />;
    }
    if (normalized.includes('decreas') || normalized.includes('down')) {
      return <TrendingDown className="h-4 w-4 text-red-600" />;
    }
    return <Minus className="h-4 w-4 text-gray-600" />;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <Card className="animate-pulse">
        <CardHeader>
          <div className="h-6 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4 mt-2"></div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Market Intelligence
        </CardTitle>
        <CardDescription>
          Real-time insights for {role}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="salary">Salary</TabsTrigger>
            <TabsTrigger value="skills">Skills</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            {snapshot && (
              <>
                {/* Demand Level */}
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="text-sm font-medium">Market Demand</p>
                    <p className="text-xs text-muted-foreground mt-1">Current hiring activity</p>
                  </div>
                  <Badge className={getDemandColor(snapshot.demand_level)}>
                    {snapshot.demand_level}
                  </Badge>
                </div>

                {/* Salary Trend */}
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="text-sm font-medium">Salary Trend</p>
                    <p className="text-xs text-muted-foreground mt-1">12-month movement</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {getTrendIcon(snapshot.salary_trend)}
                    <span className="text-sm">{snapshot.salary_trend}</span>
                  </div>
                </div>

                {/* Competition */}
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="text-sm font-medium">Competition</p>
                    <p className="text-xs text-muted-foreground mt-1">Candidates per opening</p>
                  </div>
                  <span className="text-sm font-medium capitalize">{snapshot.competition_level}</span>
                </div>

                {/* Market Insights */}
                {snapshot.market_insights && snapshot.market_insights.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-medium mb-2">Market Insights</p>
                    <div className="space-y-2">
                      {snapshot.market_insights.map((insight, index) => (
                        <div key={index} className="flex gap-2 text-sm text-muted-foreground">
                          <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                          <span>{insight}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </TabsContent>

          {/* Salary Tab */}
          <TabsContent value="salary" className="space-y-4">
            {salaryData && (
              <>
                {/* Salary Range */}
                <div className="p-4 border rounded-lg bg-gradient-to-r from-blue-50 to-purple-50">
                  <p className="text-sm font-medium mb-3">Typical Salary Range</p>
                  <div className="flex items-center justify-between">
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Min</p>
                      <p className="text-lg font-bold">{formatCurrency(salaryData.current_range.min)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Median</p>
                      <p className="text-xl font-bold text-blue-600">{formatCurrency(salaryData.current_range.median)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Max</p>
                      <p className="text-lg font-bold">{formatCurrency(salaryData.current_range.max)}</p>
                    </div>
                  </div>
                </div>

                {/* Percentile Breakdown */}
                <div>
                  <p className="text-sm font-medium mb-3">Percentile Distribution</p>
                  <div className="space-y-2">
                    {Object.entries(salaryData.percentile_breakdown).map(([percentile, amount]) => (
                      <div key={percentile} className="flex items-center justify-between p-2 border rounded">
                        <span className="text-sm text-muted-foreground">{percentile} Percentile</span>
                        <span className="text-sm font-medium">{formatCurrency(amount)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Trend Direction */}
                <div className="flex items-center gap-2 p-3 border rounded-lg">
                  {getTrendIcon(salaryData.trend_direction)}
                  <div>
                    <p className="text-sm font-medium">Trend Direction</p>
                    <p className="text-xs text-muted-foreground">{salaryData.trend_direction}</p>
                  </div>
                </div>
              </>
            )}
          </TabsContent>

          {/* Skills Tab */}
          <TabsContent value="skills" className="space-y-4">
            {/* Hot Skills from Snapshot */}
            {snapshot && snapshot.hot_skills && snapshot.hot_skills.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-3">In-Demand Skills</p>
                <div className="flex flex-wrap gap-2">
                  {snapshot.hot_skills.map((skill, index) => (
                    <Badge key={index} variant="secondary" className="text-sm">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Emerging Skills */}
            {emergingSkills.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-3 flex items-center gap-2">
                  <Zap className="h-4 w-4 text-yellow-600" />
                  Emerging & Trending
                </p>
                <div className="space-y-3">
                  {emergingSkills.slice(0, 5).map((skill, index) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{skill.skill_name}</span>
                        <Badge variant="outline" className="text-green-600">
                          +{skill.growth_rate}%
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Badge variant="secondary" className="text-xs">{skill.adoption_stage}</Badge>
                        {skill.related_roles && skill.related_roles.length > 0 && (
                          <span>• {skill.related_roles.slice(0, 2).join(', ')}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
