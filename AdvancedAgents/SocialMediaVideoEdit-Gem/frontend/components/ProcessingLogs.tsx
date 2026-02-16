"use client";

import React, { useEffect, useRef } from 'react';
import { Terminal, Info, AlertTriangle, XCircle, CheckCircle } from 'lucide-react';

interface LogEntry {
    type: 'log';
    level: string;
    message: string;
    timestamp: string;
}

interface ProcessingLogsProps {
    jobId: string;
}

export default function ProcessingLogs({ jobId }: ProcessingLogsProps) {
    const [logs, setLogs] = React.useState<LogEntry[]>([]);
    const [connected, setConnected] = React.useState(false);
    const logsEndRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!jobId) return;

        let reconnectTimeout: NodeJS.Timeout;
        let isMounted = true;

        const connect = () => {
            if (!isMounted) return;

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = apiUrl.startsWith('http')
                ? apiUrl.replace(/^http/, 'ws') + `/ws/${jobId}`
                : `${wsProtocol}//${window.location.host}/ws/${jobId}`;

            console.log(`Connecting to WebSocket URL: ${wsUrl}`);

            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                if (isMounted) {
                    setConnected(true);
                    console.log('WebSocket connected');
                }
            };

            ws.onmessage = (event) => {
                if (!isMounted) return;
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'log') {
                        setLogs(prev => [...prev, data]);
                    }
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            ws.onerror = (error) => {
                // Silently handle errors - onclose will handle reconnection
            };

            ws.onclose = () => {
                if (isMounted) {
                    setConnected(false);
                    console.log('WebSocket disconnected. Reconnecting in 3s...');
                    // Auto-reconnect
                    reconnectTimeout = setTimeout(connect, 3000);
                }
            };
        };

        connect();

        return () => {
            isMounted = false;
            clearTimeout(reconnectTimeout);
            if (wsRef.current) {
                // Remove listeners to prevent firing after unmount
                wsRef.current.onclose = null;
                wsRef.current.onerror = null;
                wsRef.current.close();
            }
        };
    }, [jobId]);

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    const getLogIcon = (level: string) => {
        switch (level) {
            case 'error':
                return <XCircle className="w-4 h-4 text-red-400" />;
            case 'warning':
                return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
            case 'success':
                return <CheckCircle className="w-4 h-4 text-green-400" />;
            default:
                return <Info className="w-4 h-4 text-blue-400" />;
        }
    };

    const getLogColor = (level: string) => {
        switch (level) {
            case 'error':
                return 'text-red-400';
            case 'warning':
                return 'text-yellow-400';
            case 'success':
                return 'text-green-400';
            default:
                return 'text-zinc-300';
        }
    };

    return (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900">
                <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-zinc-400" />
                    <span className="text-sm font-medium text-zinc-200">Processing Logs</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span className="text-xs text-zinc-500">{connected ? 'Connected' : 'Disconnected'}</span>
                </div>
            </div>
            <div className="p-4 font-mono text-xs max-h-96 overflow-y-auto bg-black/20">
                {logs.length === 0 ? (
                    <div className="text-zinc-600 text-center py-8">Waiting for logs...</div>
                ) : (
                    logs.map((log, index) => (
                        <div key={index} className="flex items-start gap-2 mb-2 group">
                            <span className="text-zinc-600 select-none">
                                {new Date(log.timestamp).toLocaleTimeString()}
                            </span>
                            {getLogIcon(log.level)}
                            <span className={getLogColor(log.level)}>{log.message}</span>
                        </div>
                    ))
                )}
                <div ref={logsEndRef} />
            </div>
        </div>
    );
}
