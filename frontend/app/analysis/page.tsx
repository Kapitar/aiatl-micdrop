'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';

interface ImprovementTimestamp {
  time: string;
  text: string;
  issue: string;
  suggestion: string;
}

interface ScoreBreakdown {
  category: string;
  score: number;
  color: string;
}

interface AnalysisData {
  score: number;
  transcribedSpeech: string;
  feedback: string;
  timestamps: ImprovementTimestamp[];
  breakdown: ScoreBreakdown[];
}

function AnalysisContent() {
  const searchParams = useSearchParams();
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  useEffect(() => {
    // Try to get video URL from URL params first, then localStorage
    const urlParam = searchParams.get('video');
    if (urlParam) {
      setVideoUrl(urlParam);
    } else {
      // Fallback to localStorage
      const storedVideo = localStorage.getItem('recordedVideo') || localStorage.getItem('uploadedVideo');
      if (storedVideo) {
        setVideoUrl(storedVideo);
      }
    }
  }, [searchParams]);

  // Mock data - replace with actual API call
  const [analysisData] = useState<AnalysisData>({
    score: 78,
    transcribedSpeech: "Hello everyone, thank you for coming today. I'm here to talk about, um, our new product launch. So, basically, we've been working on this for, like, a really long time. And, you know, I think it's going to be really great. So, yeah, let me tell you more about it.",
    feedback: "Your speech shows good structure and enthusiasm. However, there are several areas for improvement: frequent use of filler words ('um', 'like', 'you know'), some repetitive phrases, and pacing could be more dynamic. Focus on eliminating filler words and varying your sentence structure for better engagement.",
    breakdown: [
      { category: "Clarity", score: 82, color: "rgb(34, 197, 94)" },
      { category: "Pace", score: 75, color: "rgb(59, 130, 246)" },
      { category: "Confidence", score: 80, color: "rgb(168, 85, 247)" },
      { category: "Engagement", score: 72, color: "rgb(236, 72, 153)" },
      { category: "Structure", score: 85, color: "rgb(251, 146, 60)" },
    ],
    timestamps: [
      {
        time: "0:15",
        text: "I'm here to talk about, um, our new product launch.",
        issue: "Filler word usage",
        suggestion: "Remove 'um' and pause briefly instead. Try: 'I'm here to talk about our new product launch.'"
      },
      {
        time: "0:22",
        text: "So, basically, we've been working on this for, like, a really long time.",
        issue: "Multiple filler words",
        suggestion: "Eliminate 'So', 'basically', and 'like'. Try: 'We've been working on this for a significant period.'"
      },
      {
        time: "0:35",
        text: "And, you know, I think it's going to be really great.",
        issue: "Filler phrase and weak language",
        suggestion: "Remove 'you know' and strengthen the statement. Try: 'I'm confident it will be exceptional.'"
      },
      {
        time: "0:42",
        text: "So, yeah, let me tell you more about it.",
        issue: "Weak transition and filler word",
        suggestion: "Use a stronger transition. Try: 'Let me share the key details with you.'"
      }
    ]
  });

  const [improvedSpeech, setImprovedSpeech] = useState<string | null>(null);
  const [isImproving, setIsImproving] = useState(false);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);

  const handleImproveSpeech = async () => {
    setIsImproving(true);
    // Simulate API call
    setTimeout(() => {
      setImprovedSpeech("Hello everyone, thank you for coming today. I'm here to discuss our new product launch. We've been developing this innovation for a significant period, and I'm confident it will be exceptional. Let me share the key details with you.");
      setIsImproving(false);
    }, 1500);
  };

  const handleGenerateVideo = async () => {
    setIsGeneratingVideo(true);
    // Simulate API call
    setTimeout(() => {
      alert('Video generation started! This feature will create a video with perfect speech delivery.');
      setIsGeneratingVideo(false);
    }, 2000);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-500/20 border-green-500/30';
    if (score >= 60) return 'bg-yellow-500/20 border-yellow-500/30';
    return 'bg-red-500/20 border-red-500/30';
  };

  // Circular progress component
  const CircularProgress = ({ score, size = 120, strokeWidth = 8 }: { score: number; size?: number; strokeWidth?: number }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (score / 100) * circumference;
    const color = analysisData.score >= 80 ? '#22c55e' : analysisData.score >= 60 ? '#eab308' : '#ef4444';
    
    return (
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="transform -rotate-90" width={size} height={size}>
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(255, 255, 255, 0.1)"
            strokeWidth={strokeWidth}
            fill="none"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
            style={{ filter: `drop-shadow(0 0 8px ${color}40)` }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={`text-3xl font-light ${getScoreColor(score)}`}>
              {score}
            </div>
            <div className="text-xs text-white/40">/100</div>
          </div>
        </div>
      </div>
    );
  };

  // Mini progress bar for breakdown
  const MiniProgressBar = ({ category, score, color }: ScoreBreakdown) => {
    const [animatedWidth, setAnimatedWidth] = useState(0);

    useEffect(() => {
      // Trigger animation after component mounts
      const timer = setTimeout(() => {
        setAnimatedWidth(score);
      }, 100);
      return () => clearTimeout(timer);
    }, [score]);

    return (
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-xs text-white/70 font-medium">{category}</span>
          <span className="text-xs font-medium" style={{ color }}>{score}%</span>
        </div>
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden relative">
          <div
            className="h-full rounded-full transition-all duration-700 ease-out"
            style={{
              width: `${animatedWidth}%`,
              backgroundColor: color,
              background: `linear-gradient(90deg, ${color}, ${color}dd)`,
              boxShadow: `0 0 8px ${color}40`,
              minWidth: animatedWidth > 0 ? '2px' : '0',
            }}
          />
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen relative text-white flex items-center justify-center p-6 overflow-hidden">
      {/* Static dark gradient background */}
      <div className="fixed inset-0 static-gradient"></div>
      
      {/* Static subtle orbs for depth */}
      <div className="fixed top-0 left-1/4 w-[500px] h-[500px] bg-purple-950/8 rounded-full blur-3xl"></div>
      <div className="fixed bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-950/8 rounded-full blur-3xl"></div>
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-3xl"></div>
      <div className="fixed top-1/3 right-1/3 w-[300px] h-[300px] bg-purple-950/5 rounded-full blur-3xl"></div>
      
      <div className="relative z-10 w-full max-w-7xl">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-4xl font-light mb-2 tracking-tight text-white/95">
            Speech Analysis
          </h1>
          <p className="text-gray-400 text-lg font-light">
            Detailed feedback and improvement suggestions
          </p>
        </div>

        <div className="space-y-4">
          {/* Top Row: Score + Video */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Score Card with Creative Visualization */}
            <div className={`rounded-xl bg-white/5 backdrop-blur-xl border-2 ${getScoreBgColor(analysisData.score)} p-6`}>
              <div className="space-y-4">
                {/* Main Circular Score */}
                <div className="flex flex-col items-center">
                  <h2 className="text-xs text-white/60 mb-4 font-medium uppercase tracking-wide">Overall Score</h2>
                  <CircularProgress score={analysisData.score} size={140} strokeWidth={10} />
                  <div className={`mt-4 text-sm font-medium ${getScoreColor(analysisData.score)}`}>
                    {analysisData.score >= 80 ? 'Excellent' : analysisData.score >= 60 ? 'Good' : 'Needs Improvement'}
                  </div>
                </div>
                
                {/* Breakdown Metrics */}
                <div className="space-y-3 pt-4 border-t border-white/10">
                  <h3 className="text-xs text-white/50 font-medium uppercase tracking-wide">Breakdown</h3>
                  {analysisData.breakdown.map((item, index) => (
                    <MiniProgressBar key={index} {...item} />
                  ))}
                </div>
              </div>
            </div>

            {/* Video Player */}
            <div className="lg:col-span-2 rounded-xl bg-white/5 backdrop-blur-xl border border-white/10 p-4">
              <h2 className="text-sm text-white/70 mb-3 font-medium uppercase tracking-wide">Recorded Video</h2>
              {videoUrl ? (
                <div className="relative rounded-lg overflow-hidden bg-black/20 aspect-video">
                  <video
                    src={videoUrl}
                    controls
                    className="w-full h-full object-contain"
                  />
                </div>
              ) : (
                <div className="relative rounded-lg overflow-hidden bg-black/20 aspect-video flex items-center justify-center border border-white/10">
                  <p className="text-white/40 text-sm">No video available</p>
                </div>
              )}
            </div>
          </div>

          {/* Middle Row: Feedback + Transcribed Speech */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Feedback Section */}
            <div className="rounded-xl bg-white/5 backdrop-blur-xl border border-white/10 p-5">
              <h2 className="text-lg font-light mb-3 text-white/95">Feedback</h2>
              <p className="text-white/80 leading-relaxed font-light text-sm">
                {analysisData.feedback}
              </p>
            </div>

            {/* Transcribed Speech Section */}
            <div className="rounded-xl bg-white/5 backdrop-blur-xl border border-white/10 p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-light text-white/95">Transcribed Speech</h2>
                <button
                  onClick={handleImproveSpeech}
                  disabled={isImproving || improvedSpeech !== null}
                  className="px-4 py-1.5 text-xs rounded-lg bg-white/10 hover:bg-white/15 text-white border border-white/20 hover:border-white/30 transition-all duration-300 font-medium cursor-pointer backdrop-blur-sm hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  {isImproving ? 'Improving...' : improvedSpeech ? 'Improved ✓' : 'Improve'}
                </button>
              </div>
              
              <div className="space-y-3">
                <div>
                  <div className="text-xs text-white/50 mb-1.5 font-medium">Original</div>
                  <div className="bg-black/20 rounded-lg p-3 border border-white/5 max-h-32 overflow-y-auto">
                    <p className="text-white/70 leading-relaxed font-light text-xs">
                      {analysisData.transcribedSpeech}
                    </p>
                  </div>
                </div>
                
                {improvedSpeech && (
                  <div>
                    <div className="text-xs text-white/50 mb-1.5 font-medium">Improved Version</div>
                    <div className="bg-green-500/10 rounded-lg p-3 border border-green-500/20 max-h-32 overflow-y-auto">
                      <p className="text-white/90 leading-relaxed font-light text-xs">
                        {improvedSpeech}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Timestamps Section - More Compact */}
          <div className="rounded-xl bg-white/5 backdrop-blur-xl border border-white/10 p-5">
            <h2 className="text-lg font-light mb-4 text-white/95">Areas to Improve</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {analysisData.timestamps.map((timestamp, index) => (
                <div
                  key={index}
                  className="bg-black/20 rounded-lg p-4 border border-white/5 hover:border-white/10 transition-all duration-300"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
                        <span className="text-purple-300 font-medium text-xs">{timestamp.time}</span>
                      </div>
                    </div>
                    <div className="flex-1 space-y-2 min-w-0">
                      <div>
                        <div className="text-xs text-white/50 mb-1 font-medium uppercase tracking-wide">
                          {timestamp.issue}
                        </div>
                        <p className="text-white/80 leading-relaxed font-light text-xs mb-2">
                          "{timestamp.text}"
                        </p>
                      </div>
                      <div className="bg-green-500/10 rounded-md p-2.5 border border-green-500/20">
                        <div className="text-xs text-green-300/70 mb-1 font-medium uppercase tracking-wide">
                          Suggestion
                        </div>
                        <p className="text-green-200/90 leading-relaxed font-light text-xs">
                          {timestamp.suggestion}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Generate Video Section */}
          <div className="rounded-xl bg-gradient-to-r from-purple-500/10 to-blue-500/10 backdrop-blur-xl border border-purple-500/20 p-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-light mb-1 text-white/95">Perfect Speech Video</h2>
                <p className="text-white/60 font-light text-sm">
                  Generate a video with improved speech delivery
                </p>
              </div>
              <button
                onClick={handleGenerateVideo}
                disabled={isGeneratingVideo}
                className="px-6 py-2.5 rounded-xl bg-white hover:bg-white/90 text-black transition-all duration-300 font-medium cursor-pointer shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 text-sm"
              >
                {isGeneratingVideo ? 'Generating...' : 'Generate Video'}
              </button>
            </div>
          </div>

          {/* Back Button */}
          <div className="text-center pt-2">
            <button
              onClick={() => window.history.back()}
              className="px-6 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-white border border-white/10 hover:border-white/20 transition-all duration-300 font-medium cursor-pointer backdrop-blur-sm hover:scale-105 active:scale-95 text-sm"
            >
              Back to Upload
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AnalysisPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen relative text-white flex items-center justify-center p-6 overflow-hidden">
        <div className="fixed inset-0 static-gradient"></div>
        <div className="relative z-10 text-center">
          <p className="text-white/60">Loading analysis...</p>
        </div>
      </div>
    }>
      <AnalysisContent />
    </Suspense>
  );
}
