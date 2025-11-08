'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedVideo, setRecordedVideo] = useState<string | null>(null);
  const [uploadedVideo, setUploadedVideo] = useState<string | null>(null);
  const [context, setContext] = useState('');
  const [audience, setAudience] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const videoFile = files.find(file => file.type.startsWith('video/'));
    
    if (videoFile) {
      handleVideoFile(videoFile);
    }
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('video/')) {
      handleVideoFile(file);
    }
  }, []);

  const handleVideoFile = (file: File) => {
    const url = URL.createObjectURL(file);
    setUploadedVideo(url);
    setRecordedVideo(null);
    localStorage.setItem('uploadedVideo', url);
    localStorage.removeItem('recordedVideo');
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: true, 
        audio: true 
      });
      
      streamRef.current = stream;
      setIsRecording(true);

      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play().catch(err => {
            console.error('Error playing video:', err);
          });
        }
      }, 0);

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        setRecordedVideo(url);
        setUploadedVideo(null);
        localStorage.setItem('recordedVideo', url);
        localStorage.removeItem('uploadedVideo');
        
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
        if (videoRef.current) {
          videoRef.current.srcObject = null;
        }
      };

      mediaRecorder.start();
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Unable to access camera. Please check permissions.');
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  useEffect(() => {
    if (isRecording && streamRef.current && videoRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(err => {
        console.error('Error playing video:', err);
      });
    }
  }, [isRecording]);

  const resetVideo = () => {
    setUploadedVideo(null);
    setRecordedVideo(null);
    setContext('');
    setAudience('');
    localStorage.removeItem('recordedVideo');
    localStorage.removeItem('uploadedVideo');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = () => {
    console.log('Submitting:', {
      video: currentVideo,
      context,
      audience,
    });
    // Navigate to analysis page
    router.push('/analysis');
  };

  const currentVideo = uploadedVideo || recordedVideo;

  return (
    <div className="min-h-screen relative text-white flex items-center justify-center p-6 overflow-hidden">
      {/* Static dark gradient background */}
      <div className="fixed inset-0 static-gradient"></div>
      
      {/* Static subtle orbs for depth */}
      <div className="fixed top-0 left-1/4 w-[500px] h-[500px] bg-purple-950/8 rounded-full blur-3xl"></div>
      <div className="fixed bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-950/8 rounded-full blur-3xl"></div>
      {/* Colored orb in the middle */}
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-600/20 rounded-full blur-3xl"></div>
      <div className="fixed top-1/3 right-1/3 w-[300px] h-[300px] bg-purple-950/5 rounded-full blur-3xl"></div>
      
      <div className="relative z-10 w-full max-w-6xl">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-light mb-4 tracking-tight text-white/95">
            Speech Coach
          </h1>
          <p className="text-gray-400 text-xl font-light">
            Upload a speech video and get instant feedback
          </p>
        </div>

        {!currentVideo ? (
          <div className="space-y-8">
            {isRecording ? (
              <>
                {/* Live Video Preview */}
                <div className="flex justify-center">
                  <div className="relative rounded-2xl overflow-hidden bg-gray-900/50 backdrop-blur-xl aspect-video w-full max-w-md shadow-2xl border border-white/10">
                    <video
                      ref={videoRef}
                      autoPlay
                      muted
                      playsInline
                      className="w-full h-full object-cover"
                    />
                    {/* Recording indicator */}
                    <div className="absolute top-5 left-5 flex items-center gap-2.5 bg-black/70 backdrop-blur-md px-4 py-2 rounded-full border border-white/10">
                      <span className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse shadow-lg shadow-red-500/50"></span>
                      <span className="text-sm text-white font-medium">Recording</span>
                    </div>
                  </div>
                </div>
                {/* Stop Recording Button */}
                <div className="text-center">
                  <button
                    onClick={stopRecording}
                    className="px-10 py-3.5 rounded-full font-medium transition-all duration-300 bg-red-500 hover:bg-red-600 text-white cursor-pointer shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/40 hover:scale-105 active:scale-95"
                  >
                    <span className="flex items-center gap-2.5 justify-center">
                      <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
                      Stop Recording
                    </span>
                  </button>
                </div>
              </>
            ) : (
              <>
                {/* Upload Area */}
                <div
                  className={`relative rounded-3xl transition-all duration-500 ${
                    isDragging
                      ? 'bg-white/5 border-2 border-white/30 shadow-2xl scale-[1.02]'
                      : 'bg-white/5 backdrop-blur-xl border-2 border-white/10 hover:border-white/20 hover:bg-white/[0.07]'
                  }`}
                  onDragEnter={handleDragEnter}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <div className="p-20 text-center">
                    <div className="w-20 h-20 mx-auto mb-8 rounded-full bg-white/10 flex items-center justify-center backdrop-blur-sm border border-white/20">
                      <svg
                        className="w-10 h-10 text-white/70"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={1.5}
                          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                      </svg>
                    </div>
                    <p className="text-white/90 mb-2 text-xl font-light">
                      Drop your video here
                    </p>
                    <p className="text-white/40 text-sm mb-8 font-light">or</p>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="px-8 py-3 rounded-full bg-white text-black hover:bg-white/90 transition-all duration-300 text-sm font-medium cursor-pointer shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
                    >
                      Browse Files
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="video/*"
                      onChange={handleFileInput}
                      className="hidden"
                    />
                  </div>
                </div>

                {/* Divider */}
                <div className="flex items-center gap-6">
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
                  <span className="text-white/40 text-sm font-light">or</span>
                  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
                </div>

                {/* Record Button */}
                <div className="text-center">
                  <button
                    onClick={startRecording}
                    className="px-10 py-3.5 rounded-full font-medium transition-all duration-300 bg-white/10 hover:bg-white/15 text-white border border-white/20 hover:border-white/30 cursor-pointer backdrop-blur-sm hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl"
                  >
                    Record Video
                  </button>
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-start">
            {/* Left Side - Video */}
            <div className="flex flex-col items-center md:items-start">
              <div className="relative rounded-2xl overflow-hidden bg-gray-900/50 backdrop-blur-xl w-full max-w-sm shadow-2xl border border-white/10">
                <video
                  src={currentVideo}
                  controls
                  className="w-full h-auto"
                />
              </div>
            </div>
            
            {/* Right Side - Form Fields */}
            <div className="space-y-6">
              <div className="space-y-5">
                <div>
                  <label htmlFor="context" className="block text-sm text-white/70 mb-3 font-medium">
                    Context <span className="text-white/40 font-normal">(optional)</span>
                  </label>
                  <input
                    id="context"
                    type="text"
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="e.g., Job interview, presentation to investors..."
                    className="w-full px-5 py-3.5 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-white/30 focus:bg-white/10 transition-all duration-300"
                  />
                </div>
                
                <div>
                  <label htmlFor="audience" className="block text-sm text-white/70 mb-3 font-medium">
                    Audience <span className="text-white/40 font-normal">(optional)</span>
                  </label>
                  <input
                    id="audience"
                    type="text"
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                    placeholder="e.g., Hiring managers, potential clients..."
                    className="w-full px-5 py-3.5 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:border-white/30 focus:bg-white/10 transition-all duration-300"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-2">
                <button
                  onClick={resetVideo}
                  className="flex-1 px-6 py-3.5 bg-white/5 hover:bg-white/10 text-white rounded-xl transition-all duration-300 border border-white/10 hover:border-white/20 cursor-pointer backdrop-blur-sm font-medium hover:scale-105 active:scale-95"
                >
                  Upload Another
                </button>
                <button
                  onClick={handleSubmit}
                  className="flex-1 px-8 py-3.5 bg-white hover:bg-white/90 text-black rounded-xl transition-all duration-300 font-medium cursor-pointer shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
                >
                  Submit
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
