"use client";

import React, { useEffect, useState } from "react";
import { Zap, Star, Cpu } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8099";

interface GeminiModel {
  id: string;
  name: string;
  description: string;
  price_per_million_tokens: number;
  tokens_per_second: number;
  default: boolean;
}

interface ModelSelectorProps {
  videoDuration?: number; // seconds
  onSelect: (modelId: string) => void;
  selectedModel: string;
}

const modelIcons: Record<string, React.ReactNode> = {
  "gemini-2.5-flash": <Zap className="w-5 h-5 text-yellow-400" />,
  "gemini-2.0-flash-001": <Cpu className="w-5 h-5 text-blue-400" />,
  "gemini-2.5-pro": <Star className="w-5 h-5 text-purple-400" />,
};

export default function ModelSelector({ videoDuration, onSelect, selectedModel }: ModelSelectorProps) {
  const [models, setModels] = useState<GeminiModel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/models`)
      .then((r) => r.json())
      .then((data) => {
        setModels(data);
        // Auto-select default model
        const defaultModel = data.find((m: GeminiModel) => m.default);
        if (defaultModel) onSelect(defaultModel.id);
      })
      .catch(() => setModels([]))
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const estimateCost = (model: GeminiModel): string => {
    if (!videoDuration || model.price_per_million_tokens === null) return "—";
    const tokens = videoDuration * model.tokens_per_second;
    const cost = (tokens / 1_000_000) * model.price_per_million_tokens;
    if (cost < 0.001) return "< $0.001";
    return `~$${cost.toFixed(3)}`;
  };

  if (loading) {
    return <div className="text-zinc-500 text-sm">Loading models...</div>;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-zinc-400">Select AI Model</h3>
        {videoDuration && (
          <span className="text-xs text-zinc-600">
            Video: {Math.round(videoDuration)}s
          </span>
        )}
      </div>
      <div className="grid grid-cols-1 gap-3">
        {models.map((model) => {
          const isSelected = selectedModel === model.id;
          return (
            <button
              key={model.id}
              onClick={() => onSelect(model.id)}
              className={`flex items-center justify-between p-4 rounded-lg border text-left transition-all ${
                isSelected
                  ? "border-blue-500 bg-blue-500/10"
                  : "border-zinc-800 bg-zinc-900/50 hover:border-zinc-600"
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-zinc-800 flex items-center justify-center flex-shrink-0">
                  {modelIcons[model.id] ?? <Cpu className="w-5 h-5 text-zinc-400" />}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-zinc-200">{model.name}</span>
                    {model.default && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-green-500/20 text-green-400 font-medium">
                        Recommended
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-zinc-500 mt-0.5">{model.description}</p>
                </div>
              </div>
              <div className="text-right ml-4 flex-shrink-0">
                <div className="text-sm font-semibold text-zinc-200">{estimateCost(model)}</div>
                <div className="text-xs text-zinc-600">
                  {model.price_per_million_tokens !== null ? `$${model.price_per_million_tokens}/1M tokens` : "Pricing unknown"}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
