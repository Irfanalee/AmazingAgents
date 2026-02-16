"use client";

import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Upload, FileVideo, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface UploadComponentProps {
    onUploadComplete: (uploadData: any) => void;
}

export default function UploadComponent({ onUploadComplete }: UploadComponentProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            validateAndSetFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            validateAndSetFile(e.target.files[0]);
        }
    };

    const validateAndSetFile = (file: File) => {
        if (!file.type.startsWith('video/')) {
            setError('Please upload a valid video file.');
            return;
        }
        setFile(file);
        setError(null);
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setProgress(0);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
                    setProgress(percentCompleted);
                },
            });

            onUploadComplete(response.data);
        } catch (err) {
            console.error(err);
            setError('Upload failed. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="w-full max-w-xl mx-auto p-6 bg-zinc-900/50 border border-zinc-800 rounded-xl backdrop-blur-sm">
            <div
                className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors ${isDragging ? 'border-blue-500 bg-blue-500/10' : 'border-zinc-700 hover:border-zinc-600'
                    }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    accept="video/*"
                    onChange={handleFileSelect}
                />

                {!file ? (
                    <div className="space-y-4">
                        <div className="flex justify-center">
                            <div className="p-4 bg-zinc-800 rounded-full">
                                <Upload className="w-8 h-8 text-zinc-400" />
                            </div>
                        </div>
                        <div>
                            <p className="text-lg font-medium text-zinc-200">Drag and drop your video here</p>
                            <p className="text-sm text-zinc-500 mt-1">or click to browse</p>
                        </div>
                        <Button
                            variant="secondary"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            Select Video
                        </Button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="flex items-center justify-center gap-3 text-zinc-200">
                            <FileVideo className="w-6 h-6 text-blue-500" />
                            <span className="font-medium truncate max-w-[200px]">{file.name}</span>
                            <button
                                onClick={() => setFile(null)}
                                className="text-zinc-500 hover:text-red-400 text-sm underline"
                            >
                                Change
                            </button>
                        </div>

                        {uploading && (
                            <div className="w-full bg-zinc-800 rounded-full h-2.5 overflow-hidden">
                                <div
                                    className="bg-blue-500 h-2.5 rounded-full transition-all duration-300"
                                    style={{ width: `${progress}%` }}
                                ></div>
                            </div>
                        )}

                        <Button
                            onClick={handleUpload}
                            disabled={uploading}
                            className="w-full"
                        >
                            {uploading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Uploading {progress}%
                                </>
                            ) : (
                                'Start Processing'
                            )}
                        </Button>
                    </div>
                )}
            </div>

            {error && (
                <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2 text-red-400 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    {error}
                </div>
            )}
        </div>
    );
}
