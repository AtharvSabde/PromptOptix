import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageLayout } from '../components/layout/PageLayout';
import { PromptInput } from '../components/analysis/PromptInput';
import { ScoreDisplay } from '../components/analysis/ScoreDisplay';
import { DefectCard } from '../components/analysis/DefectCard';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Alert } from '../components/common/Alert';
import { Loading } from '../components/common/Spinner';
import { useAnalysis } from '../hooks/useAnalysis';
import type { TaskType, Domain } from '../types/analysis.types';
import { TASK_TYPES, DOMAINS } from '../types/analysis.types';
import { validatePrompt, getErrorMessage, getErrorTitle, isRetryableError } from '../utils/errorHandlers';
import { AGENT_ICONS, AGENT_NAMES } from '../utils/constants';
import { formatScore, formatConfidence, formatProcessingTime, formatCost } from '../utils/formatters';

export const AnalyzePage: React.FC = () => {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [taskType, setTaskType] = useState<TaskType>('general');
  const [domain, setDomain] = useState<Domain>('general');

  const { analyzePrompt, isLoading, error, data, reset } = useAnalysis();

  const handleAnalyze = async () => {
    const validationError = validatePrompt(prompt);
    if (validationError) {
      return;
    }

    try {
      await analyzePrompt({
        prompt,
        task_type: taskType,
        domain,
        include_agent_breakdown: true,
      });
    } catch (err) {
      // Error is already set by the hook
      console.error('Analysis error:', err);
    }
  };

  const handleReset = () => {
    setPrompt('');
    setTaskType('general');
    setDomain('general');
    reset();
  };

  const handleOptimize = () => {
    if (data) {
      navigate('/optimize', {
        state: {
          analysis: data,
          prompt: prompt
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analyze Prompt</h1>
          <p className="text-gray-600">
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
        <div className="grid md:grid-cols-2 gap-4">
          <Card padding="md">
            <label htmlFor="task-type" className="block text-sm font-medium text-gray-700 mb-2">
              Task Type
            </label>
            <select
              id="task-type"
              value={taskType}
              onChange={(e) => setTaskType(e.target.value as TaskType)}
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
            >
              {TASK_TYPES.map(type => (
                <option key={type} value={type}>
                  {type.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </Card>

          <Card padding="md">
            <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-2">
              Domain
            </label>
            <select
              id="domain"
              value={domain}
              onChange={(e) => setDomain(e.target.value as Domain)}
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
            >
              {DOMAINS.map(d => (
                <option key={d} value={d}>
                  {d.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </Card>
        </div>

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

        {/* Loading State */}
        {isLoading && (
          <Card padding="lg">
            <Loading
              message="Running multi-agent analysis..."
              subMessage="4 specialized agents are analyzing your prompt..."
            />
            <div className="mt-6 space-y-2 text-sm text-gray-600">
              <p>• 👁️ Clarity Agent: Checking specification & intent</p>
              <p>• 📋 Structure Agent: Analyzing structure & formatting</p>
              <p>• 🧠 Context Agent: Evaluating context & memory</p>
              <p>• 🛡️ Security Agent: Running security scan</p>
            </div>
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
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Summary</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Overall Score:</span>
                      <span className="font-semibold">{formatScore(data.overall_score)} / 10</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Defects Found:</span>
                      <span className="font-semibold">{data.defects.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Consensus Level:</span>
                      <span className="font-semibold">{formatConfidence(data.consensus)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Processing Time:</span>
                      <span className="font-semibold">{formatProcessingTime(data.metadata.processing_time_ms)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Cost:</span>
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
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
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
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Breakdown</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {Object.entries(data.agent_results).map(([agentName, result]) => (
                    <Card key={agentName} padding="md" shadow="sm">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{AGENT_ICONS[agentName as keyof typeof AGENT_ICONS]}</span>
                          <div>
                            <h4 className="font-semibold text-gray-900">
                              {AGENT_NAMES[agentName as keyof typeof AGENT_NAMES]}
                            </h4>
                            <p className="text-xs text-gray-500">{result.focus_area}</p>
                          </div>
                        </div>
                        <span className="text-lg font-bold text-blue-600">
                          {formatScore(result.score)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">
                        Found {result.defects.length} defect(s) · Confidence: {formatConfidence(result.confidence)}
                      </p>
                      <p className="text-sm text-gray-700">{result.summary}</p>
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
