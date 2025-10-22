import { useState } from 'react';
import { Mic, Volume2, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface InterviewQuestionProps {
  question: string;
  questionNumber: number;
  totalQuestions: number;
  onAnswer: (answer: string) => void;
  onSkip: () => void;
  isRecording?: boolean;
  onStartRecording?: () => void;
  onStopRecording?: () => void;
}

export function InterviewQuestion({
  question,
  questionNumber,
  totalQuestions,
  onAnswer,
  onSkip,
  isRecording = false,
  onStartRecording,
  onStopRecording,
}: InterviewQuestionProps) {
  const [answer, setAnswer] = useState('');
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const handlePlayAudio = () => {
    setIsPlayingAudio(true);
    // Simulate audio playback
    setTimeout(() => setIsPlayingAudio(false), 3000);
  };

  const handleSubmitAnswer = () => {
    onAnswer(answer);
    setAnswer('');
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <CardTitle className="text-xl">Question {questionNumber} of {totalQuestions}</CardTitle>
          <div className="text-sm text-slate-400">
            {Math.round((questionNumber / totalQuestions) * 100)}%
          </div>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all"
            style={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
          />
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Question Display */}
        <div className="bg-slate-700 rounded-lg p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white flex-1">{question}</h3>
            <Button
              variant="ghost"
              size="icon"
              onClick={handlePlayAudio}
              disabled={isPlayingAudio}
              className="text-blue-400 hover:text-blue-300"
            >
              <Volume2 className={`w-5 h-5 ${isPlayingAudio ? 'animate-pulse' : ''}`} />
            </Button>
          </div>
          <p className="text-slate-400 text-sm">Think carefully about your answer. You have 2 minutes to respond.</p>
        </div>

        {/* Recording Controls */}
        <div className="flex gap-3">
          <Button
            onClick={onStartRecording}
            disabled={isRecording}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white"
          >
            <Mic className="w-4 h-4 mr-2" />
            {isRecording ? 'Recording...' : 'Start Recording'}
          </Button>
          {isRecording && (
            <Button
              onClick={onStopRecording}
              className="flex-1 bg-slate-700 hover:bg-slate-600 text-white"
            >
              Stop Recording
            </Button>
          )}
        </div>

        {/* Answer Text Input (Alternative) */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-slate-300">
            Or type your answer:
          </label>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here..."
            className="w-full h-32 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            onClick={handleSubmitAnswer}
            disabled={!answer.trim()}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
          >
            Submit Answer
          </Button>
          <Button
            onClick={onSkip}
            variant="outline"
            className="flex-1 text-slate-300 border-slate-600 hover:bg-slate-700"
          >
            Skip Question
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
