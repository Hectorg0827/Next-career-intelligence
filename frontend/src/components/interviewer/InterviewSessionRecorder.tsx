import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface InterviewSessionRecorderProps {
  onRecordingComplete: (audioData: Blob, transcript: string) => void;
  maxDuration?: number; // in seconds
  onTimeWarning?: (remaining: number) => void;
}

export function InterviewSessionRecorder({
  onRecordingComplete,
  maxDuration = 120,
  onTimeWarning,
}: InterviewSessionRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const timeIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        let interim_transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const { transcript } = event.results[i][0];
          if (event.results[i].isFinal) {
            setTranscript((prev) => prev + transcript + ' ');
          } else {
            interim_transcript += transcript;
          }
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setError(`Speech recognition error: ${event.error}`);
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (timeIntervalRef.current) clearInterval(timeIntervalRef.current);
    };
  }, []);

  const startRecording = async () => {
    try {
      setError(null);
      setTranscript('');
      setRecordingTime(0);
      setAudioChunks([]);

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create MediaRecorder
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        setAudioChunks([audioBlob]);
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);

      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }

      // Timer
      timeIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          const newTime = prev + 1;

          // Warning at 10 seconds remaining
          if (newTime === maxDuration - 10) {
            onTimeWarning?.(10);
          }

          // Auto stop at max duration
          if (newTime >= maxDuration) {
            stopRecording();
            return maxDuration;
          }

          return newTime;
        });
      }, 1000);
    } catch (err) {
      setError('Failed to access microphone. Please check permissions.');
      console.error('Recording error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach((track) => track.stop());

      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }

      if (timeIntervalRef.current) {
        clearInterval(timeIntervalRef.current);
      }

      setIsRecording(false);

      // Call completion handler after short delay for data to be ready
      setTimeout(() => {
        if (audioChunks.length > 0) {
          onRecordingComplete(audioChunks[0], transcript);
        }
      }, 500);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const isNearLimit = recordingTime >= maxDuration - 10;

  return (
    <div className="space-y-4">
      {/* Recording Status */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              {isRecording ? (
                <>
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-red-400 font-semibold">Recording...</span>
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-green-400 font-semibold">Ready to record</span>
                </>
              )}
            </div>
            <div className={`flex items-center gap-2 text-2xl font-mono font-bold ${
              isNearLimit ? 'text-red-400' : 'text-slate-300'
            }`}>
              <Clock className="w-6 h-6" />
              {formatTime(recordingTime)}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                isNearLimit ? 'bg-red-500' : 'bg-blue-500'
              }`}
              style={{ width: `${(recordingTime / maxDuration) * 100}%` }}
            />
          </div>

          {/* Time Warning */}
          {isNearLimit && (
            <div className="mt-3 flex items-center gap-2 text-red-400 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span>{maxDuration - recordingTime} seconds remaining</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Transcript Preview */}
      {transcript && (
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <p className="text-sm text-slate-400 mb-2">Live Transcript:</p>
            <div className="bg-slate-700 rounded p-3 text-slate-300 text-sm max-h-24 overflow-y-auto">
              {transcript}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="bg-red-500/20 border-red-500/30">
          <CardContent className="p-4 flex gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-red-300 text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Control Buttons */}
      <div className="flex gap-3">
        {!isRecording ? (
          <Button
            onClick={startRecording}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white py-6 text-lg"
          >
            <Mic className="w-5 h-5 mr-2" />
            Start Recording
          </Button>
        ) : (
          <>
            <Button
              onClick={stopRecording}
              className="flex-1 bg-slate-700 hover:bg-slate-600 text-white py-6 text-lg"
            >
              <MicOff className="w-5 h-5 mr-2" />
              Stop Recording
            </Button>
          </>
        )}
      </div>

      {/* Browser Compatibility Note */}
      <p className="text-xs text-slate-500 text-center">
        Chrome, Firefox, and Edge recommended for best recording quality
      </p>
    </div>
  );
}
