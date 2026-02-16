"use client";

import React, { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Play, Pause, Scissors, Trash2, Clock, CheckCircle } from 'lucide-react';
import axios from 'axios';

interface Clip {
    start: number;
    end: number;
    description?: string;
}

interface ManualClipperProps {
    fileId: string;
    videoUrl: string;
    onProcessingStart: (jobId: string) => void;
}

export default function ManualClipper({ fileId, videoUrl, onProcessingStart }: ManualClipperProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [currentTime, setCurrentTime] = useState(0);
    const [startTime, setStartTime] = useState<number | null>(null);
    const [endTime, setEndTime] = useState<number | null>(null);
    const [clips, setClips] = useState<Clip[]>([]);
    const [isPlaying, setIsPlaying] = useState(false);

    const handleTimeUpdate = () => {
        if (videoRef.current) {
            setCurrentTime(videoRef.current.currentTime);
        }
    };

    const togglePlay = async () => {
        if (videoRef.current) {
            try {
                if (isPlaying) {
                    videoRef.current.pause();
                } else {
                    await videoRef.current.play();
                }
                setIsPlaying(!isPlaying);
            } catch (error) {
                console.error("Playback failed:", error);
            }
        }
    };

    const setStart = () => {
        if (videoRef.current) {
            setStartTime(videoRef.current.currentTime);
            // Reset end time if it's before new start time
            if (endTime !== null && endTime <= videoRef.current.currentTime) {
                setEndTime(null);
            }
        }
    };

    const setEnd = () => {
        if (videoRef.current) {
            const time = videoRef.current.currentTime;
            if (startTime !== null && time > startTime) {
                setEndTime(time);
            }
        }
    };

    const addClip = () => {
        if (startTime !== null && endTime !== null) {
            if (clips.length >= 5) return;

            setClips([...clips, { start: startTime, end: endTime }]);
            setStartTime(null);
            setEndTime(null);
        }
    };

    const removeClip = (index: number) => {
        setClips(clips.filter((_, i) => i !== index));
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        const ms = Math.floor((seconds % 1) * 10);
        return `${mins}:${secs.toString().padStart(2, '0')}.${ms}`;
    };

    const handleProcess = async () => {
        if (clips.length === 0) return;

        try {
            const response = await axios.post(`http://localhost:8000/process/manual/${fileId}`, {
                clips: clips
            });
            onProcessingStart(response.data.id);
        } catch (error) {
            console.error("Failed to start manual processing:", error);
        }
    };

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Video Player Column */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="relative aspect-video bg-black rounded-xl overflow-hidden border border-zinc-800">
                        <video
                            ref={videoRef}
                            src={videoUrl}
                            className="w-full h-full"
                            controls
                            playsInline
                            onTimeUpdate={handleTimeUpdate}
                        />
                    </div>

                    {/* Clipping Controls */}
                    <div className="grid grid-cols-3 gap-4">
                        <Button
                            variant={startTime !== null ? "default" : "secondary"}
                            onClick={setStart}
                            className="w-full"
                        >
                            <Clock className="w-4 h-4 mr-2" />
                            {startTime !== null ? `Start: ${formatTime(startTime)}` : "Set Start"}
                        </Button>

                        <Button
                            variant={endTime !== null ? "default" : "secondary"}
                            onClick={setEnd}
                            disabled={startTime === null}
                            className="w-full"
                        >
                            <Clock className="w-4 h-4 mr-2" />
                            {endTime !== null ? `End: ${formatTime(endTime)}` : "Set End"}
                        </Button>

                        <Button
                            onClick={addClip}
                            disabled={startTime === null || endTime === null || clips.length >= 5}
                            className="w-full bg-blue-600 hover:bg-blue-700"
                        >
                            <Scissors className="w-4 h-4 mr-2" />
                            Add Clip
                        </Button>
                    </div>
                </div>

                {/* Clips List Column */}
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 flex flex-col h-full">
                    <h3 className="text-lg font-semibold text-zinc-200 mb-4 flex items-center justify-between">
                        <span>Selected Clips</span>
                        <span className="text-xs font-normal text-zinc-500">{clips.length}/5</span>
                    </h3>

                    <div className="flex-1 overflow-y-auto space-y-3 mb-4">
                        {clips.length === 0 ? (
                            <div className="text-center py-8 text-zinc-500 text-sm">
                                No clips added yet.<br />
                                Set start and end times to add clips.
                            </div>
                        ) : (
                            clips.map((clip, idx) => (
                                <div key={idx} className="bg-zinc-800/50 rounded-lg p-3 flex items-center justify-between group">
                                    <div className="flex items-center gap-3">
                                        <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs font-bold">
                                            {idx + 1}
                                        </div>
                                        <div className="text-sm text-zinc-300 font-mono">
                                            {formatTime(clip.start)} - {formatTime(clip.end)}
                                        </div>
                                    </div>
                                    <Button
                                        size="sm"
                                        variant="ghost"
                                        className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400"
                                        onClick={() => removeClip(idx)}
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </Button>
                                </div>
                            ))
                        )}
                    </div>

                    <Button
                        size="lg"
                        className="w-full"
                        disabled={clips.length === 0}
                        onClick={handleProcess}
                    >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Create Reel ({clips.length} clips)
                    </Button>
                </div>
            </div>
        </div>
    );
}
