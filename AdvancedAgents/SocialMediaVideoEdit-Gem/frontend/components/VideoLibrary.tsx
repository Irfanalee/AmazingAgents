"use client";

import React, { useState } from 'react';
import axios from 'axios';
import { Trash2, Play, FileVideo, Calendar, HardDrive } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Video {
    file_id: string;
    filename: string;
    file_size_mb: number;
    duration_formatted: string;
    upload_time: string;
    width?: number;
    height?: number;
    fps?: number;
}

interface VideoLibraryProps {
    onVideoSelect?: (fileId: string) => void;
    refreshTrigger?: number;
}

export default function VideoLibrary({ onVideoSelect, refreshTrigger }: VideoLibraryProps) {
    // State for videos and loading status
    const [videos, setVideos] = React.useState<Video[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [deleteConfirm, setDeleteConfirm] = React.useState<string | null>(null);
    const [generatedVideos, setGeneratedVideos] = React.useState<any[]>([]);
    const [activeTab, setActiveTab] = React.useState<'uploads' | 'generated'>('uploads');

    const fetchVideos = async () => {
        try {
            const [uploadsRes, generatedRes] = await Promise.all([
                axios.get('http://localhost:8000/videos'),
                axios.get('http://localhost:8000/processed')
            ]);
            setVideos(uploadsRes.data.videos);
            setGeneratedVideos(generatedRes.data.videos);
        } catch (error) {
            console.error('Failed to fetch videos:', error);
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        fetchVideos();
    }, [refreshTrigger]);

    const handleDelete = async (fileId: string) => {
        try {
            await axios.delete(`http://localhost:8000/videos/${fileId}`);
            setVideos(videos.filter(v => v.file_id !== fileId));
            setDeleteConfirm(null);
        } catch (error) {
            console.error('Failed to delete video:', error);
        }
    };

    if (loading) {
        return <div className="text-zinc-400">Loading videos...</div>;
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-zinc-200">Video Library</h2>
                <div className="flex bg-zinc-900 rounded-lg p-1 border border-zinc-800">
                    <button
                        onClick={() => setActiveTab('uploads')}
                        className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${activeTab === 'uploads'
                            ? 'bg-zinc-800 text-white'
                            : 'text-zinc-400 hover:text-zinc-200'
                            }`}
                    >
                        Uploads
                    </button>
                    <button
                        onClick={() => setActiveTab('generated')}
                        className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${activeTab === 'generated'
                            ? 'bg-zinc-800 text-white'
                            : 'text-zinc-400 hover:text-zinc-200'
                            }`}
                    >
                        Generated
                    </button>
                </div>
            </div>

            {activeTab === 'uploads' ? (
                videos.length === 0 ? (
                    <div className="text-center py-12 text-zinc-500">
                        <FileVideo className="w-16 h-16 mx-auto mb-4 opacity-50" />
                        <p>No videos uploaded yet</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {videos.map((video) => (
                            <div
                                key={video.file_id}
                                className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4 hover:border-zinc-700 transition-colors"
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-sm font-medium text-zinc-200 truncate">
                                            {video.filename}
                                        </h3>
                                        <div className="flex items-center gap-2 mt-1 text-xs text-zinc-500">
                                            <Calendar className="w-3 h-3" />
                                            {new Date(video.upload_time).toLocaleDateString()}
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-2 text-xs text-zinc-400">
                                    <div className="flex justify-between">
                                        <span>Duration:</span>
                                        <span className="text-zinc-300">{video.duration_formatted}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Size:</span>
                                        <span className="text-zinc-300">{video.file_size_mb} MB</span>
                                    </div>
                                    {video.width && video.height && (
                                        <div className="flex justify-between">
                                            <span>Resolution:</span>
                                            <span className="text-zinc-300">{video.width}x{video.height}</span>
                                        </div>
                                    )}
                                </div>

                                <div className="flex gap-2 mt-4">
                                    {onVideoSelect && (
                                        <Button
                                            size="sm"
                                            variant="secondary"
                                            className="flex-1"
                                            onClick={() => onVideoSelect(video.file_id)}
                                        >
                                            <Play className="w-3 h-3 mr-1" />
                                            Process
                                        </Button>
                                    )}
                                    {deleteConfirm === video.file_id ? (
                                        <div className="flex gap-1 flex-1">
                                            <Button
                                                size="sm"
                                                variant="destructive"
                                                className="flex-1 text-xs"
                                                onClick={() => handleDelete(video.file_id)}
                                            >
                                                Confirm
                                            </Button>
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                className="flex-1 text-xs"
                                                onClick={() => setDeleteConfirm(null)}
                                            >
                                                Cancel
                                            </Button>
                                        </div>
                                    ) : (
                                        <Button
                                            size="sm"
                                            variant="ghost"
                                            onClick={() => setDeleteConfirm(video.file_id)}
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </Button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )
            ) : (
                generatedVideos.length === 0 ? (
                    <div className="text-center py-12 text-zinc-500">
                        <HardDrive className="w-16 h-16 mx-auto mb-4 opacity-50" />
                        <p>No generated videos yet</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {generatedVideos.map((video, idx) => (
                            <div
                                key={idx}
                                className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4 hover:border-zinc-700 transition-colors"
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex-1 min-w-0">
                                        <h3 className="text-sm font-medium text-zinc-200 truncate">
                                            {video.filename}
                                        </h3>
                                        <div className="flex items-center gap-2 mt-1 text-xs text-zinc-500">
                                            <Calendar className="w-3 h-3" />
                                            {new Date(video.created_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-2 text-xs text-zinc-400">
                                    <div className="flex justify-between">
                                        <span>Size:</span>
                                        <span className="text-zinc-300">{video.size_mb} MB</span>
                                    </div>
                                </div>

                                <div className="flex gap-2 mt-4">
                                    <a
                                        href={`http://localhost:8000${video.path}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex-1"
                                    >
                                        <Button
                                            size="sm"
                                            variant="secondary"
                                            className="w-full"
                                        >
                                            <Play className="w-3 h-3 mr-1" />
                                            Watch
                                        </Button>
                                    </a>
                                    {deleteConfirm === video.filename ? (
                                        <div className="flex gap-1 flex-1">
                                            <Button
                                                size="sm"
                                                variant="destructive"
                                                className="flex-1 text-xs"
                                                onClick={async () => {
                                                    try {
                                                        await axios.delete(`http://localhost:8000/processed/${video.filename}`);
                                                        setGeneratedVideos(generatedVideos.filter(v => v.filename !== video.filename));
                                                        setDeleteConfirm(null);
                                                    } catch (error) {
                                                        console.error('Failed to delete video:', error);
                                                    }
                                                }}
                                            >
                                                Confirm
                                            </Button>
                                            <Button
                                                size="sm"
                                                variant="ghost"
                                                className="flex-1 text-xs"
                                                onClick={() => setDeleteConfirm(null)}
                                            >
                                                Cancel
                                            </Button>
                                        </div>
                                    ) : (
                                        <Button
                                            size="sm"
                                            variant="ghost"
                                            onClick={() => setDeleteConfirm(video.filename)}
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </Button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )
            )}
        </div>
    );
}
