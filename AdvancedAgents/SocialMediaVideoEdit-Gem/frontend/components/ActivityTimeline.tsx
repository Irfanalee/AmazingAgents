"use client";

import React, { useEffect } from 'react';
import { CheckCircle, Circle, Loader2, XCircle } from 'lucide-react';

interface TimelineEvent {
    event: string;
    status: 'completed' | 'in_progress' | 'failed';
    timestamp: string;
}

interface ActivityTimelineProps {
    jobId: string;
    timeline: TimelineEvent[];
}

export default function ActivityTimeline({ jobId, timeline }: ActivityTimelineProps) {
    const [events, setEvents] = React.useState<TimelineEvent[]>(timeline || []);
    const wsRef = React.useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!jobId) return;

        const ws = new WebSocket(`ws://localhost:8000/ws/${jobId}`);
        wsRef.current = ws;

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'timeline') {
                setEvents(data.timeline);
            }
        };

        return () => {
            ws.close();
        };
    }, [jobId]);

    const getStatusIcon = (status: string, isLast: boolean) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="w-5 h-5 text-green-500" />;
            case 'in_progress':
                return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
            case 'failed':
                return <XCircle className="w-5 h-5 text-red-500" />;
            default:
                return <Circle className="w-5 h-5 text-zinc-600" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'border-green-500';
            case 'in_progress':
                return 'border-blue-500';
            case 'failed':
                return 'border-red-500';
            default:
                return 'border-zinc-700';
        }
    };

    return (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-zinc-200 mb-6">Activity Timeline</h3>
            <div className="space-y-4">
                {events.map((event, index) => {
                    const isLast = index === events.length - 1;
                    return (
                        <div key={index} className="flex gap-4">
                            <div className="flex flex-col items-center">
                                {getStatusIcon(event.status, isLast)}
                                {!isLast && (
                                    <div className={`w-0.5 h-12 mt-2 border-l-2 ${getStatusColor(event.status)}`} />
                                )}
                            </div>
                            <div className="flex-1 pb-4">
                                <p className="text-sm font-medium text-zinc-200">{event.event}</p>
                                <p className="text-xs text-zinc-500 mt-1">
                                    {new Date(event.timestamp).toLocaleTimeString()}
                                </p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
