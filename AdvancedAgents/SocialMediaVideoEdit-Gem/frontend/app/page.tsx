"use client";

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import UploadComponent from '@/components/UploadComponent';
import VideoLibrary from '@/components/VideoLibrary';
import VideoMetadata from '@/components/VideoMetadata';
import ProcessingLogs from '@/components/ProcessingLogs';
import ManualClipper from '@/components/ManualClipper';
import ActivityTimeline from '@/components/ActivityTimeline';
import { Loader2, CheckCircle, Play, AlertTriangle, Upload, Library, Bot, Scissors } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface JobStatus {
  id: string;
  file_id: string;
  status: 'queued' | 'analyzing' | 'processing' | 'completed' | 'failed';
  output_url?: string;
  error?: string;
  highlights?: any[];
  timeline?: any[];
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<'upload' | 'library'>('upload');
  const [jobId, setJobId] = useState<string | null>(null);
  const [fileId, setFileId] = useState<string | null>(null);
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [polling, setPolling] = useState(false);
  const [uploadedMetadata, setUploadedMetadata] = useState<any>(null);
  const [refreshLibrary, setRefreshLibrary] = useState(0);
  const [processingMode, setProcessingMode] = useState<'agentic' | 'manual' | null>(null);

  const handleUploadComplete = async (uploadData: any) => {
    setFileId(uploadData.id);
    setUploadedMetadata({ ...uploadData.metadata, path: uploadData.path });
    setProcessingMode(null); // Reset mode on new upload
  };

  const handleStartProcessing = async () => {
    if (!fileId) return;
    try {
      const response = await axios.post(`http://localhost:8000/process/${fileId}`);
      setJobId(response.data.id);
      setPolling(true);
    } catch (error) {
      console.error("Failed to start processing:", error);
    }
  };

  const handleManualProcessingStart = (newJobId: string) => {
    setJobId(newJobId);
    setPolling(true);
  };

  const handleProcessFromLibrary = async (selectedFileId: string) => {
    setFileId(selectedFileId);
    setActiveTab('upload');
    setProcessingMode(null);
    // Fetch metadata for the selected video
    try {
      const response = await axios.get(`http://localhost:8000/videos/${selectedFileId}/metadata`);
      setUploadedMetadata(response.data);
    } catch (error) {
      console.error("Failed to fetch metadata:", error);
    }
  };

  const handleReset = () => {
    setJobId(null);
    setFileId(null);
    setStatus(null);
    setPolling(false);
    setUploadedMetadata(null);
    setProcessingMode(null);
    setRefreshLibrary(prev => prev + 1);
  };

  useEffect(() => {
    if (!polling || !jobId) return;

    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`http://localhost:8000/jobs/${jobId}`);
        setStatus(response.data);

        if (['completed', 'failed'].includes(response.data.status)) {
          setPolling(false);
        }
      } catch (error) {
        console.error("Polling error:", error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [polling, jobId]);

  return (
    <main className="min-h-screen bg-background p-8">
      <div className="w-full max-w-7xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold tracking-tighter bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Agentic Video Editor
          </h1>
          <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
            Upload your long-form video and let our AI agents extract the most viral highlights and create a social media ready teaser.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-zinc-800">
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-6 py-3 font-medium transition-colors flex items-center gap-2 ${activeTab === 'upload'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-zinc-500 hover:text-zinc-300'
              }`}
          >
            <Upload className="w-4 h-4" />
            New Upload
          </button>
          <button
            onClick={() => setActiveTab('library')}
            className={`px-6 py-3 font-medium transition-colors flex items-center gap-2 ${activeTab === 'library'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-zinc-500 hover:text-zinc-300'
              }`}
          >
            <Library className="w-4 h-4" />
            Video Library
          </button>
        </div>

        {/* Content */}
        {activeTab === 'library' ? (
          <VideoLibrary onVideoSelect={handleProcessFromLibrary} refreshTrigger={refreshLibrary} />
        ) : (
          <div className="space-y-8">
            {!fileId && !jobId && (
              <div className="max-w-xl mx-auto">
                <UploadComponent onUploadComplete={handleUploadComplete} />
              </div>
            )}

            {fileId && !jobId && uploadedMetadata && !processingMode && (
              <div className="max-w-4xl mx-auto space-y-8">
                <div className="text-center space-y-2">
                  <h2 className="text-2xl font-bold text-zinc-200">Choose Processing Mode</h2>
                  <p className="text-zinc-400">How would you like to create your highlight reel?</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Agentic Mode Card */}
                  <div
                    onClick={() => setProcessingMode('agentic')}
                    className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 cursor-pointer hover:border-blue-500/50 hover:bg-zinc-900 transition-all group"
                  >
                    <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <Bot className="w-6 h-6 text-blue-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-zinc-200 mb-2">Agentic AI</h3>
                    <p className="text-zinc-400 text-sm">
                      Let our AI agents analyze the video, find the most viral moments, and edit them together automatically.
                    </p>
                  </div>

                  {/* Manual Mode Card */}
                  <div
                    onClick={() => setProcessingMode('manual')}
                    className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 cursor-pointer hover:border-purple-500/50 hover:bg-zinc-900 transition-all group"
                  >
                    <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                      <Scissors className="w-6 h-6 text-purple-400" />
                    </div>
                    <h3 className="text-xl font-semibold text-zinc-200 mb-2">Manual Clipping</h3>
                    <p className="text-zinc-400 text-sm">
                      Watch the video yourself, select specific start and end times, and create a custom reel.
                    </p>
                  </div>
                </div>

                <div className="flex justify-center">
                  <Button onClick={handleReset} variant="ghost" className="text-zinc-500">
                    Cancel & Upload New
                  </Button>
                </div>
              </div>
            )}

            {fileId && !jobId && uploadedMetadata && processingMode === 'agentic' && (
              <div className="max-w-2xl mx-auto space-y-6">
                <div className="flex items-center gap-2 text-blue-400 mb-4">
                  <Bot className="w-5 h-5" />
                  <span className="font-medium">Agentic Mode Selected</span>
                </div>
                <VideoMetadata metadata={uploadedMetadata} />
                <div className="flex gap-4">
                  <Button onClick={handleStartProcessing} className="flex-1">
                    <Play className="w-4 h-4 mr-2" />
                    Start AI Processing
                  </Button>
                  <Button onClick={() => setProcessingMode(null)} variant="outline">
                    Back
                  </Button>
                </div>
              </div>
            )}

            {fileId && !jobId && uploadedMetadata && processingMode === 'manual' && (
              <div className="max-w-5xl mx-auto space-y-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2 text-purple-400">
                    <Scissors className="w-5 h-5" />
                    <span className="font-medium">Manual Mode Selected</span>
                  </div>
                  <Button onClick={() => setProcessingMode(null)} variant="ghost" size="sm">
                    Change Mode
                  </Button>
                </div>
                <ManualClipper
                  fileId={fileId}
                  videoUrl={`http://localhost:8000/${uploadedMetadata.path}`}
                  onProcessingStart={handleManualProcessingStart}
                />
              </div>
            )}

            {jobId && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-6">
                  <ActivityTimeline jobId={jobId} timeline={status?.timeline || []} />

                  {status?.status === 'completed' && status.output_url && (
                    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 space-y-4">
                      <div className="flex items-center gap-3 text-green-400">
                        <CheckCircle className="w-5 h-5" />
                        <p className="font-medium">Video generated successfully!</p>
                      </div>

                      <div className="aspect-video bg-black rounded-lg overflow-hidden border border-zinc-800">
                        <video
                          src={`http://localhost:8000${status.output_url}`}
                          controls
                          className="w-full h-full"
                        />
                      </div>

                      <div className="flex gap-2">
                        <Button className="flex-1" onClick={() => window.open(`http://localhost:8000${status.output_url}`, '_blank')}>
                          Download Video
                        </Button>
                        <Button onClick={handleReset} variant="outline">
                          New Upload
                        </Button>
                      </div>
                    </div>
                  )}

                  {status?.status === 'failed' && (
                    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6">
                      <div className="flex items-center gap-3 text-red-400 mb-4">
                        <AlertTriangle className="w-5 h-5" />
                        <p className="font-medium">Processing Failed</p>
                      </div>
                      <p className="text-zinc-400 text-sm mb-4">{status.error}</p>
                      <Button onClick={handleReset} variant="outline" className="w-full">
                        Try Again
                      </Button>
                    </div>
                  )}
                </div>

                <div>
                  <ProcessingLogs jobId={jobId} />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
