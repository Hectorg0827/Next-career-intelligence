import { useState } from 'react';
import { Settings, Plus, Trash2, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

export interface InterviewSetup {
  jobRole: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  duration: number;
  topics: string[];
}

interface InterviewSetupProps {
  onStart: (setup: InterviewSetup) => void;
  isLoading?: boolean;
}

export function InterviewSetupComponent({ onStart, isLoading }: InterviewSetupProps) {
  const [setup, setSetup] = useState<InterviewSetup>({
    jobRole: '',
    difficulty: 'Medium',
    duration: 45,
    topics: [],
  });
  const [newTopic, setNewTopic] = useState('');

  const availableTopics = [
    'Behavioral',
    'Technical',
    'System Design',
    'Algorithms',
    'Data Structures',
    'Problem Solving',
    'Leadership',
    'Communication',
  ];

  const handleAddTopic = () => {
    if (newTopic.trim() && !setup.topics.includes(newTopic)) {
      setSetup({
        ...setup,
        topics: [...setup.topics, newTopic],
      });
      setNewTopic('');
    }
  };

  const handleRemoveTopic = (topic: string) => {
    setSetup({
      ...setup,
      topics: setup.topics.filter((t) => t !== topic),
    });
  };

  const handleStart = () => {
    if (setup.jobRole.trim() && setup.topics.length > 0) {
      onStart(setup);
    }
  };

  return (
    <div className="space-y-6">
      {/* Job Role */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle>Job Role</CardTitle>
          <CardDescription>What position are you interviewing for?</CardDescription>
        </CardHeader>
        <CardContent>
          <Input
            placeholder="e.g., Senior Full Stack Engineer, Product Manager, Data Scientist"
            value={setup.jobRole}
            onChange={(e) => setSetup({ ...setup, jobRole: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400"
          />
        </CardContent>
      </Card>

      {/* Difficulty Level */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle>Difficulty Level</CardTitle>
          <CardDescription>Choose the difficulty of the interview</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-3">
            {(['Easy', 'Medium', 'Hard'] as const).map((level) => (
              <button
                key={level}
                onClick={() => setSetup({ ...setup, difficulty: level })}
                className={`p-3 rounded-lg transition ${
                  setup.difficulty === level
                    ? 'bg-blue-600 text-white border-2 border-blue-500'
                    : 'bg-slate-700 text-slate-300 border-2 border-transparent hover:bg-slate-600'
                }`}
              >
                <p className="font-semibold">{level}</p>
                <p className="text-sm mt-1">
                  {level === 'Easy' && '15-20 min'}
                  {level === 'Medium' && '30-45 min'}
                  {level === 'Hard' && '45-60 min'}
                </p>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Interview Duration */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle>Interview Duration</CardTitle>
          <CardDescription>How long should the interview be?</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="15"
              max="60"
              step="5"
              value={setup.duration}
              onChange={(e) => setSetup({ ...setup, duration: parseInt(e.target.value) })}
              className="flex-1"
            />
            <span className="text-2xl font-bold text-white w-16 text-right">{setup.duration}m</span>
          </div>
        </CardContent>
      </Card>

      {/* Topics Selection */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle>Interview Topics</CardTitle>
          <CardDescription>Select topics to focus on during the interview</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Current Topics */}
          {setup.topics.length > 0 && (
            <div className="flex flex-wrap gap-2 p-3 bg-slate-700 rounded-lg">
              {setup.topics.map((topic) => (
                <Badge key={topic} className="bg-blue-600 hover:bg-blue-700 pl-3">
                  {topic}
                  <button
                    onClick={() => handleRemoveTopic(topic)}
                    className="ml-2 hover:text-red-300"
                  >
                    ×
                  </button>
                </Badge>
              ))}
            </div>
          )}

          {/* Quick Select */}
          <div>
            <p className="text-sm text-slate-400 mb-2">Quick select:</p>
            <div className="flex flex-wrap gap-2">
              {availableTopics.map((topic) => (
                <button
                  key={topic}
                  onClick={() => {
                    if (!setup.topics.includes(topic)) {
                      setSetup({
                        ...setup,
                        topics: [...setup.topics, topic],
                      });
                    }
                  }}
                  disabled={setup.topics.includes(topic)}
                  className="px-3 py-1 text-sm bg-slate-700 text-slate-300 rounded hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  + {topic}
                </button>
              ))}
            </div>
          </div>

          {/* Add Custom Topic */}
          <div className="flex gap-2">
            <Input
              placeholder="Add custom topic..."
              value={newTopic}
              onChange={(e) => setNewTopic(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddTopic()}
              className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400"
            />
            <Button
              onClick={handleAddTopic}
              disabled={!newTopic.trim()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Start Button */}
      <Button
        onClick={handleStart}
        disabled={
          !setup.jobRole.trim() || setup.topics.length === 0 || isLoading
        }
        className="w-full bg-gradient-to-r from-blue-600 to-gold-primary hover:from-blue-700 hover:to-gold-accent text-white py-6 text-lg"
      >
        {isLoading ? 'Starting Interview...' : 'Start Interview'}
      </Button>
    </div>
  );
}
