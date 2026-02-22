import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageLayout } from '../components/layout/PageLayout';
import { PromptInput } from '../components/analysis/PromptInput';
import { ScoreDisplay } from '../components/analysis/ScoreDisplay';
import { DefectCard } from '../components/analysis/DefectCard';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Alert } from '../components/common/Alert';
import { useAnalysis } from '../hooks/useAnalysis';
import type { AgentStatus } from '../hooks/useAnalysis';
import type { TaskType, Domain } from '../types/analysis.types';
import { TASK_TYPES, DOMAINS } from '../types/analysis.types';
import { LLM_PROVIDERS } from '../types/advanced.types';
import type { LLMProvider } from '../types/advanced.types';
import { validatePrompt, getErrorMessage, getErrorTitle, isRetryableError } from '../utils/errorHandlers';
import { AGENT_ICONS, AGENT_NAMES } from '../utils/constants';
import { formatScore, formatConfidence, formatProcessingTime, formatCost } from '../utils/formatters';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

const AgentProgressCard: React.FC<{ agent: AgentStatus }> = ({ agent }) => {
  const icon = AGENT_ICONS[agent.name as keyof typeof AGENT_ICONS] || '🤖';
  const displayName = AGENT_NAMES[agent.name as keyof typeof AGENT_NAMES] || agent.name;

  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 ${
      agent.status === 'complete'
        ? 'bg-green-500/10 border-green-500/30'
        : agent.status === 'failed'
        ? 'bg-red-500/10 border-red-500/30'
        : agent.status === 'running'
        ? 'bg-blue-500/10 border-blue-500/30 animate-pulse'
        : 'bg-dark-card border-dark-border opacity-50'
    }`}>
      <span className="text-2xl">{icon}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium text-white text-sm">{displayName}</span>
          {agent.status === 'running' && <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />}
          {agent.status === 'complete' && <CheckCircle className="w-4 h-4 text-green-400" />}
          {agent.status === 'failed' && <XCircle className="w-4 h-4 text-red-400" />}
        </div>
        <p className="text-xs text-gray-500">{agent.focusArea}</p>
      </div>
      {agent.status === 'complete' && agent.score !== undefined && (
        <div className="text-right">
          <div className="text-lg font-bold text-white">{agent.score.toFixed(1)}</div>
          <div className="text-xs text-gray-400">{agent.defectsCount} defect{agent.defectsCount !== 1 ? 's' : ''}</div>
        </div>
      )}
      {agent.status === 'failed' && (
        <span className="text-xs text-red-400">Failed</span>
      )}
    </div>
  );
};

export const AnalyzePage: React.FC = () => {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [taskType, setTaskType] = useState<TaskType>('general');
  const [domain, setDomain] = useState<Domain>('general');
  const [userIssues, setUserIssues] = useState('');
  const [selectedProvider, setSelectedProvider] = useState<LLMProvider>('groq');

  const { streamAnalyze, isLoading, isStreaming, error, data, agentStatuses, reset } = useAnalysis();

  const handleAnalyze = async () => {
    const validationError = validatePrompt(prompt);
    if (validationError) {
      return;
    }

    try {
      const parsedIssues = userIssues.split('\n').map(s => s.trim()).filter(Boolean);
      await streamAnalyze({
        prompt,
        task_type: taskType,
        domain,
        provider: selectedProvider,
        include_agent_breakdown: true,
        user_issues: parsedIssues.length > 0 ? parsedIssues : undefined,
      });
    } catch (err) {
      console.error('Analysis error:', err);
    }
  };

  const handleReset = () => {
    setPrompt('');
    setTaskType('general');
    setDomain('general');
    setUserIssues('');
    setSelectedProvider('groq');
    reset();
  };

  const handleOptimize = () => {
    if (data) {
      const parsedIssues = userIssues.split('\n').map(s => s.trim()).filter(Boolean);
      navigate('/optimize', {
        state: {
          analysis: data,
          prompt: prompt,
          user_issues: parsedIssues.length > 0 ? parsedIssues : undefined,
        }
      });
    }
  };

  const canAnalyze = prompt.trim().length >= 10 && !isLoading;

  return (
    <PageLayout maxWidth="7xl">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Analyze Prompt</h1>
          <p className="text-gray-400">
            Analyze your prompt for defects using our multi-agent consensus system.
          </p>
        </div>

        {/* Input Section */}
        <PromptInput
          value={prompt}
          onChange={setPrompt}
          disabled={isLoading}
        />

        {/* Options */}
        <div className="grid md:grid-cols-3 gap-4">
          <Card padding="md">
            <label htmlFor="task-type" className="block text-sm font-medium text-gray-300 mb-2">
              Task Type
            </label>
            <select
              id="task-type"
              value={taskType}
              onChange={(e) => setTaskType(e.target.value as TaskType)}
              disabled={isLoading}
              className="w-full px-3 py-2 bg-gray-800 text-white border border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-700 disabled:text-gray-400"
            >
              {TASK_TYPES.map(type => (
                <option key={type} value={type}>
                  {type.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </Card>

          <Card padding="md">
            <label htmlFor="domain" className="block text-sm font-medium text-gray-300 mb-2">
              Domain
            </label>
            <select
              id="domain"
              value={domain}
              onChange={(e) => setDomain(e.target.value as Domain)}
              disabled={isLoading}
              className="w-full px-3 py-2 bg-gray-800 text-white border border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-700 disabled:text-gray-400"
            >
              {DOMAINS.map(d => (
                <option key={d} value={d}>
                  {d.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </Card>

          <Card padding="md">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              LLM Provider
            </label>
            <div className="flex gap-2 flex-wrap">
              {LLM_PROVIDERS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedProvider(p.id)}
                  disabled={isLoading}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                    selectedProvider === p.id
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-gray-800 text-gray-300 border-gray-600 hover:border-blue-400'
                  } disabled:opacity-50`}
                >
                  {p.name}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {LLM_PROVIDERS.find(p => p.id === selectedProvider)?.description}
            </p>
          </Card>
        </div>

        {/* User Issues (Optional) */}
        <Card padding="md">
          <label htmlFor="user-issues" className="block text-sm font-medium text-gray-300 mb-2">
            Issues You're Facing <span className="text-gray-500">(optional)</span>
          </label>
          <textarea
            id="user-issues"
            value={userIssues}
            onChange={(e) => setUserIssues(e.target.value)}
            disabled={isLoading}
            placeholder={"e.g., Output is too verbose\nMissing specific examples\nWrong output format"}
            className="w-full h-24 px-3 py-2 bg-gray-800 text-white border border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-700 disabled:text-gray-400 resize-none placeholder-gray-500 text-sm"
          />
          <p className="text-xs text-gray-500 mt-1">
            Describe problems with your prompt — one per line. These will be prioritized during optimization.
          </p>
        </Card>

        {/* Actions */}
        <div className="flex gap-4">
          <Button
            onClick={handleAnalyze}
            disabled={!canAnalyze}
            isLoading={isLoading}
            size="lg"
          >
            {isLoading ? 'Analyzing...' : 'Analyze Prompt'}
          </Button>
          {(data || error) && (
            <Button onClick={handleReset} variant="outline" size="lg">
              Reset
            </Button>
          )}
        </div>

        {/* Streaming Progress — Live Agent Cards */}
        {isStreaming && (
          <Card padding="lg">
            <h3 className="text-lg font-semibold text-white mb-4">
              Multi-Agent Analysis in Progress
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {agentStatuses.map((agent) => (
                <AgentProgressCard key={agent.name} agent={agent} />
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-4 text-center">
              Results stream in as each agent completes its analysis
            </p>
          </Card>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <Alert
            variant="error"
            title={getErrorTitle(error)}
            onClose={() => reset()}
          >
            <p>{getErrorMessage(error)}</p>
            {isRetryableError(error) && (
              <Button
                onClick={handleAnalyze}
                variant="outline"
                size="sm"
                className="mt-3"
              >
                Retry Analysis
              </Button>
            )}
          </Alert>
        )}

        {/* Results */}
        {data && !isLoading && (
          <div className="space-y-6">
            {/* Score & Metadata */}
            <div className="grid md:grid-cols-3 gap-6">
              <div className="md:col-span-1">
                <ScoreDisplay score={data.overall_score} />
              </div>
              <div className="md:col-span-2">
                <Card padding="lg">
                  <h3 className="text-lg font-semibold text-white mb-4">Analysis Summary</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Overall Score:</span>
                      <span className="font-semibold">{formatScore(data.overall_score)} / 10</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Defects Found:</span>
                      <span className="font-semibold">{data.defects.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Consensus Level:</span>
                      <span className="font-semibold">{formatConfidence(data.consensus)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Processing Time:</span>
                      <span className="font-semibold">{formatProcessingTime(data.metadata.processing_time_ms)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Cost:</span>
                      <span className="font-semibold">{formatCost(data.metadata.total_cost)}</span>
                    </div>
                  </div>

                  {/* Optimize Button */}
                  <div className="mt-4">
                    <Button
                      onClick={handleOptimize}
                      className="w-full"
                    >
                      Optimize This Prompt →
                    </Button>
                  </div>
                </Card>
              </div>
            </div>

            {/* Defects */}
            {data.defects.length > 0 ? (
              <div>
                <h2 className="text-2xl font-bold text-white mb-4">
                  Detected Defects ({data.defects.length})
                </h2>
                <div className="space-y-4">
                  {data.defects.map(defect => (
                    <DefectCard key={defect.id} defect={defect} />
                  ))}
                </div>
              </div>
            ) : (
              <Alert variant="success" title="No Defects Found">
                Your prompt looks great! No significant defects were detected.
              </Alert>
            )}

            {/* Agent Breakdown */}
            {data.agent_results && (
              <Card padding="lg">
                <h3 className="text-lg font-semibold text-white mb-4">Agent Breakdown</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {Object.entries(data.agent_results).map(([agentName, result]) => (
                    <Card key={agentName} padding="md" shadow="sm">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{AGENT_ICONS[agentName as keyof typeof AGENT_ICONS]}</span>
                          <div>
                            <h4 className="font-semibold text-white">
                              {AGENT_NAMES[agentName as keyof typeof AGENT_NAMES]}
                            </h4>
                            <p className="text-xs text-gray-500">{result.focus_area}</p>
                          </div>
                        </div>
                        <span className="text-lg font-bold text-blue-400">
                          {formatScore(result.score)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 mb-2">
                        Found {result.defects.length} defect(s) · Confidence: {formatConfidence(result.confidence)}
                      </p>
                      <p className="text-sm text-gray-300">{result.summary}</p>
                    </Card>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}
      </div>
    </PageLayout>
  );
};
