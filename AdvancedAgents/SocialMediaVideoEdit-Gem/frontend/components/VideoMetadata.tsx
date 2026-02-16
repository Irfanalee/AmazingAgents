"use client";

import React from 'react';
import { FileVideo, Clock, Film, Gauge, HardDrive, Code } from 'lucide-react';

interface VideoMetadataProps {
    metadata: {
        filename: string;
        file_size_mb: number;
        duration_formatted: string;
        width?: number;
        height?: number;
        fps?: number;
        codec?: string;
        bitrate?: number;
        format?: string;
    };
}

export default function VideoMetadata({ metadata }: VideoMetadataProps) {
    const items = [
        { icon: FileVideo, label: 'Filename', value: metadata.filename },
        { icon: Clock, label: 'Duration', value: metadata.duration_formatted },
        { icon: HardDrive, label: 'File Size', value: `${metadata.file_size_mb} MB` },
        { icon: Film, label: 'Resolution', value: metadata.width && metadata.height ? `${metadata.width}x${metadata.height}` : 'N/A' },
        { icon: Gauge, label: 'Frame Rate', value: metadata.fps ? `${Math.round(metadata.fps)} fps` : 'N/A' },
        { icon: Code, label: 'Codec', value: metadata.codec || 'N/A' },
    ];

    return (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-zinc-200 mb-4">Video Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {items.map((item, index) => (
                    <div key={index} className="flex items-start gap-3">
                        <div className="p-2 bg-zinc-800 rounded-lg">
                            <item.icon className="w-4 h-4 text-blue-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-xs text-zinc-500">{item.label}</p>
                            <p className="text-sm text-zinc-200 truncate">{item.value}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
