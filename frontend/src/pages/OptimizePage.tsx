import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { PageLayout } from '../components/layout/PageLayout';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { useAdvancedOptimization } from '../hooks/useAdvancedOptimization';
import type { PipelinePhase } from '../hooks/useAdvancedOptimization';
import { useAnalysis } from '../hooks/useAnalysis';
import { EvolutionViewer } from '../components/optimization/EvolutionViewer';
import { TrajectoryViewer } from '../components/optimization/TrajectoryViewer';
import { CritiqueViewer } from '../components/optimization/CritiqueViewer';
import { PromptDiff } from '../components/optimization/PromptDiff';
import { Sparkles, ArrowRight, RefreshCw, TestTube, Zap, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import type { AnalysisResponse } from '../types/analysis.types';
import { OptimizationLevel } from '../types/optimization.types';
import { LLM_PROVIDERS } from '../types/advanced.types';
import type { LLMProvider } from '../types/advanced.types';

const PipelineProgress: React.FC<{ phases: PipelinePhase[] }> = ({ phases }) => (
  <Card padding="lg">
    <h3 className="text-lg font-semibold text-white mb-4">
      Optimization Pipeline Progress
    </h3>
    <div className="space-y-3">
      {phases.map((phase) => (
        <div
          key={phase.phase}
          className={`flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 ${
            phase.status === 'complete'
              ? 'bg-green-500/10 border-green-500/30'
              : phase.status === 'failed'
              ? 'bg-red-500/10 border-red-500/30'
              : phase.status === 'running'
              ? 'bg-blue-500/10 border-blue-500/30 animate-pulse'
              : 'bg-dark-card border-dark-border opacity-50'
          }`}
        >
          <div className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm ${
            phase.status === 'complete'
              ? 'bg-green-500 text-white'
              : phase.status === 'failed'
              ? 'bg-red-500 text-white'
              : phase.status === 'running'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-700 text-gray-400'
          }`}>
            {phase.status === 'complete' ? <CheckCircle className="w-4 h-4" /> :
             phase.status === 'failed' ? <XCircle className="w-4 h-4" /> :
             phase.status === 'running' ? <Loader2 className="w-4 h-4 animate-spin" /> :
             phase.phase}
          </div>
          <div className="flex-1">
            <span className="font-medium text-white text-sm">{phase.name}</span>
            {phase.skipped && <span className="text-xs text-gray-400 ml-2">(skipped)</span>}
          </div>
          {phase.status === 'complete' && phase.score !== undefined && (
            <span className="text-sm font-bold text-green-400">{phase.score.toFixed(1)}</span>
          )}
          {phase.status === 'failed' && (
            <span className="text-xs text-red-400">Failed</span>
          )}
        </div>
      ))}
    </div>
    <p className="text-xs text-gray-500 mt-4 text-center">
      Each phase builds on the previous one for maximum improvement
    </p>
  </Card>
);

export const OptimizePage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const passedAnalysis = location.state?.analysis as AnalysisResponse | undefined;
  const passedPrompt = location.state?.prompt as string | undefined;
  const passedUserIssues = location.state?.user_issues as string[] | undefined;

  const [originalPrompt, setOriginalPrompt] = useState(passedPrompt || '');
  const [analysis, setAnalysis] = useState<AnalysisResponse | undefined>(passedAnalysis);
  const [optimizationLevel, setOptimizationLevel] = useState<OptimizationLevel>(OptimizationLevel.BALANCED);
  const [selectedProvider, setSelectedProvider] = useState<LLMProvider>('groq');

  // Testing feature state
  const [testInput, setTestInput] = useState('');
  const [isTestingOriginal, setIsTestingOriginal] = useState(false);
  const [isTestingOptimized, setIsTestingOptimized] = useState(false);
  const [originalOutput, setOriginalOutput] = useState('');
  const [optimizedOutput, setOptimizedOutput] = useState('');

  const { analyzePrompt, isLoading: isAnalyzing } = useAnalysis();
  const {
    streamOptimize,
    isLoading: isOptimizing,
    isStreaming,
    error: optimizationError,
    data: result,
    pipelinePhases,
    reset: resetOptimization
  } = useAdvancedOptimization();

  const hasResult = result !== null;

  const handleAnalyze = async () => {
    if (!originalPrompt.trim()) return;

    try {
      const res = await analyzePrompt({
        prompt: originalPrompt,
        task_type: 'general',
        domain: 'general',
        provider: selectedProvider
      });
      setAnalysis(res);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  const handleOptimize = async () => {
    if (!originalPrompt.trim() || !analysis) return;

    try {
      const techMap: Record<string, number> = { minimal: 3, balanced: 5, aggressive: 8 };
      await streamOptimize({
        prompt: originalPrompt,
        analysis: analysis as unknown as Record<string, unknown>,
        strategy: 'auto',
        optimization_level: optimizationLevel,
        max_techniques: techMap[optimizationLevel] ?? 5,
        provider: selectedProvider,
        user_issues: passedUserIssues,
      });
    } catch (error) {
      console.error('Optimization failed:', error);
    }
  };

  const handleTest = async (promptToTest: string, isOriginal: boolean) => {
    if (!testInput.trim()) return;

    const setLoading = isOriginal ? setIsTestingOriginal : setIsTestingOptimized;
    const setOutput = isOriginal ? setOriginalOutput : setOptimizedOutput;

    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      const mockOutput = `[Simulated output for: "${testInput}"]\n\nPrompt used:\n${promptToTest.substring(0, 100)}...\n\nThis is a placeholder for actual LLM output.`;
      setOutput(mockOutput);
    } catch (error) {
      console.error('Test failed:', error);
      setOutput('Error: Test failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    resetOptimization();
    setOriginalPrompt('');
    setAnalysis(undefined);
    setTestInput('');
    setOriginalOutput('');
    setOptimizedOutput('');
  };

  const scoreBefore = result?.score_before ?? 0;
  const scoreAfter = result?.score_after ?? 0;
  const improvement = result?.improvement ?? 0;
  const techniquesApplied = result?.techniques_applied || [];

  const canOptimize = originalPrompt.trim().length >= 10 && analysis !== undefined;

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Optimize Prompt</h1>
            <p className="text-gray-400">
              Multi-strategy optimization: Standard + DGEO + SHDT + CDRAF in one pass
            </p>
          </div>
          {hasResult && (
            <Button
              variant="outline"
              onClick={handleReset}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Start Over
            </Button>
          )}
        </div>

        {/* Step 1: Input Prompt */}
        {!hasResult && !isStreaming && (
          <Card padding="lg">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-semibold">
                  1
                </div>
                <h2 className="text-xl font-semibold text-white">
                  Enter Prompt to Optimize
                </h2>
              </div>

              <textarea
                value={originalPrompt}
                onChange={(e) => setOriginalPrompt(e.target.value)}
                placeholder="Enter your prompt here (minimum 10 characters)..."
                className="w-full h-40 px-4 py-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none placeholder-gray-500"
              />

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  LLM Provider
                </label>
                <div className="flex gap-2 flex-wrap">
                  {LLM_PROVIDERS.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => setSelectedProvider(p.id)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
                        selectedProvider === p.id
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-gray-800 text-gray-300 border-gray-600 hover:border-blue-400'
                      }`}
                    >
                      {p.name}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {LLM_PROVIDERS.find(p => p.id === selectedProvider)?.description}
                </p>
              </div>

              {!analysis && (
                <div className="flex gap-3">
                  <Button
                    onClick={handleAnalyze}
                    isLoading={isAnalyzing}
                    disabled={originalPrompt.trim().length < 10}
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    {isAnalyzing ? 'Analyzing...' : 'Analyze Prompt'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => navigate('/analyze')}
                  >
                    Back to Analyze
                  </Button>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Step 2: Analysis Results */}
        {analysis && !hasResult && !isStreaming && (
          <Card padding="lg">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-semibold">
                  2
                </div>
                <h2 className="text-xl font-semibold text-white">
                  Analysis Results
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
                  <p className="text-sm text-gray-400 mb-1">Overall Score</p>
                  <p className="text-3xl font-bold text-white">{analysis.overall_score.toFixed(1)}</p>
                  <p className="text-xs text-gray-400 mt-1">out of 10</p>
                </div>
                <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
                  <p className="text-sm text-gray-400 mb-1">Defects Found</p>
                  <p className="text-3xl font-bold text-white">{analysis.defects.length}</p>
                  <p className="text-xs text-gray-400 mt-1">issues detected</p>
                </div>
                <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
                  <p className="text-sm text-gray-400 mb-1">Agent Consensus</p>
                  <p className="text-3xl font-bold text-white">
                    {((analysis.consensus || 0) * 100).toFixed(0)}%
                  </p>
                  <p className="text-xs text-gray-400 mt-1">agreement level</p>
                </div>
              </div>

              {passedUserIssues && passedUserIssues.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-300 mb-2">
                    Your reported issues:
                  </p>
                  <div className="flex gap-2 flex-wrap">
                    {passedUserIssues.map((issue, i) => (
                      <span
                        key={i}
                        className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-amber-500/20 text-amber-300 border border-amber-500/30"
                      >
                        {issue}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {analysis.defects.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-300 mb-2">
                    Defects to fix:
                  </p>
                  <div className="space-y-2">
                    {analysis.defects.slice(0, 5).map((defect) => (
                      <div key={defect.id} className="flex items-start gap-2 text-sm">
                        <span className="text-red-500">•</span>
                        <span className="text-gray-300">
                          <strong>{defect.name}:</strong> {defect.description}
                        </span>
                      </div>
                    ))}
                    {analysis.defects.length > 5 && (
                      <p className="text-sm text-gray-400 italic">
                        ...and {analysis.defects.length - 5} more
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Step 3: Optimization Settings + Run */}
        {analysis && !hasResult && !isStreaming && (
          <Card padding="lg">
            <div className="space-y-6">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-semibold">
                  3
                </div>
                <h2 className="text-xl font-semibold text-white">
                  Optimization Settings
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {([
                  {
                    level: OptimizationLevel.MINIMAL,
                    icon: '\u26A1',
                    name: 'Quick Fix',
                    description: 'Fast single-pass fix for minor issues',
                    time: '~30s',
                    techniques: 'Up to 3',
                    stages: '2 stages',
                  },
                  {
                    level: OptimizationLevel.BALANCED,
                    icon: '\u2696\uFE0F',
                    name: 'Balanced',
                    tag: 'Recommended',
                    description: 'All 4 pipeline stages with smart defaults',
                    time: '~2 min',
                    techniques: 'Up to 5',
                    stages: '4 stages',
                  },
                  {
                    level: OptimizationLevel.AGGRESSIVE,
                    icon: '\uD83D\uDD2C',
                    name: 'Deep Optimize',
                    description: 'Maximum effort with extended search and iterations',
                    time: '~4 min',
                    techniques: 'Up to 8',
                    stages: '4 stages',
                  },
                ] as const).map((preset) => {
                  const isSelected = optimizationLevel === preset.level;
                  return (
                    <button
                      key={preset.level}
                      onClick={() => setOptimizationLevel(preset.level)}
                      className={`relative text-left p-5 rounded-xl border-2 transition-all duration-200 ${
                        isSelected
                          ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10'
                          : 'border-dark-border bg-dark-card hover:border-gray-500'
                      }`}
                    >
                      {preset.tag && (
                        <span className="absolute top-3 right-3 text-[10px] font-semibold uppercase tracking-wider text-blue-400 bg-blue-500/20 px-2 py-0.5 rounded-full">
                          {preset.tag}
                        </span>
                      )}
                      <div className="text-2xl mb-3">{preset.icon}</div>
                      <h3 className="text-base font-semibold text-white mb-1">{preset.name}</h3>
                      <p className="text-xs text-gray-400 mb-4 leading-relaxed">{preset.description}</p>
                      <div className="space-y-1.5 text-xs">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Time</span>
                          <span className="font-medium text-gray-300">{preset.time}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Techniques</span>
                          <span className="font-medium text-gray-300">{preset.techniques}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Pipeline</span>
                          <span className="font-medium text-gray-300">{preset.stages}</span>
                        </div>
                      </div>
                    </button>
                  );
                })}</div>

              <Button
                onClick={handleOptimize}
                isLoading={isOptimizing}
                disabled={!canOptimize}
                className="w-full md:w-auto"
              >
                <Zap className="w-4 h-4 mr-2" />
                {isOptimizing ? 'Optimizing...' : 'Optimize Prompt'}
              </Button>

              {optimizationError && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                  <p className="text-sm text-red-300">
                    <strong>Error:</strong> {optimizationError.message}
                  </p>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Streaming Pipeline Progress */}
        {isStreaming && (
          <PipelineProgress phases={pipelinePhases} />
        )}

        {/* Optimization Results */}
        {hasResult && result && (
          <>
            {/* Improvement Summary */}
            <Card padding="lg">
              <div className="text-center space-y-4">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/10 text-green-400 mb-2">
                  <Sparkles className="w-8 h-8" />
                </div>
                <h2 className="text-2xl font-bold text-white">
                  Optimization Complete!
                </h2>
                <div className="flex items-center justify-center gap-4 text-center">
                  <div>
                    <p className="text-4xl font-bold text-gray-300">
                      {scoreBefore.toFixed(1)}
                    </p>
                    <p className="text-sm text-gray-400">Before</p>
                  </div>
                  <ArrowRight className="w-6 h-6 text-gray-400" />
                  <div>
                    <p className="text-4xl font-bold text-green-400">
                      {scoreAfter.toFixed(1)}
                    </p>
                    <p className="text-sm text-gray-400">After</p>
                  </div>
                  <div className="ml-4">
                    <p className="text-2xl font-bold text-green-400">
                      +{improvement.toFixed(1)}
                    </p>
                    <p className="text-sm text-gray-400">Improvement</p>
                  </div>
                </div>

                {techniquesApplied.length > 0 && (
                  <div className="flex gap-2 justify-center flex-wrap">
                    {techniquesApplied.map((tech) => (
                      <span
                        key={tech.technique_id}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-500/20 text-purple-300"
                      >
                        {tech.technique_name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </Card>

            {/* Side-by-Side Prompt Comparison */}
            <PromptDiff
              original={result.original_prompt}
              optimized={result.optimized_prompt}
              scoreBefore={scoreBefore}
              scoreAfter={scoreAfter}
            />

            {/* Pipeline stage viewers */}
            {result.evolution_history && result.evolution_history.length > 0 && (
              <EvolutionViewer
                generations={result.evolution_history}
                finalPopulation={result.population_final}
              />
            )}

            {result.trajectory && result.trajectory.length > 0 && (
              <TrajectoryViewer trajectory={result.trajectory} />
            )}

            {result.critique_rounds && result.critique_rounds.length > 0 && (
              <CritiqueViewer rounds={result.critique_rounds} />
            )}

            {/* Techniques Applied */}
            {techniquesApplied.length > 0 && (
              <Card padding="lg">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Techniques Applied ({techniquesApplied.length})
                </h3>
                <div className="space-y-4">
                  {techniquesApplied.map((technique) => (
                    <div key={technique.technique_id} className="border-l-4 border-purple-500 pl-4 py-2">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-white">{technique.technique_name}</h4>
                          <p className="text-sm text-gray-300 mt-1">{technique.modification}</p>
                          {technique.target_defects.length > 0 && (
                            <p className="text-xs text-gray-500 mt-2">
                              Fixes: {technique.target_defects.join(', ')}
                            </p>
                          )}
                        </div>
                        {technique.technique_id && (
                          <span className="text-xs text-purple-400 font-medium px-2 py-1 bg-purple-500/20 rounded">
                            {technique.technique_id}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Testing Feature */}
            <Card padding="lg">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <TestTube className="w-6 h-6 text-blue-400" />
                  <h3 className="text-lg font-semibold text-white">
                    Test with Real Input
                  </h3>
                </div>
                <p className="text-sm text-gray-300">
                  Provide test input to compare how both prompts perform side-by-side
                </p>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Test Input
                  </label>
                  <textarea
                    value={testInput}
                    onChange={(e) => setTestInput(e.target.value)}
                    placeholder="Enter your test input here..."
                    className="w-full h-32 px-4 py-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none placeholder-gray-500"
                  />
                </div>

                <div className="flex gap-3">
                  <Button
                    onClick={() => handleTest(result.original_prompt, true)}
                    isLoading={isTestingOriginal}
                    disabled={!testInput.trim()}
                    variant="outline"
                  >
                    Test Original
                  </Button>
                  <Button
                    onClick={() => handleTest(result.optimized_prompt, false)}
                    isLoading={isTestingOptimized}
                    disabled={!testInput.trim()}
                  >
                    Test Optimized
                  </Button>
                </div>

                {/* Test Results */}
                {(originalOutput || optimizedOutput) && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-6">
                    {originalOutput && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-300 mb-2">Original Output</h4>
                        <div className="bg-dark-card rounded-lg p-4 max-h-64 overflow-y-auto border border-dark-border">
                          <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                            {originalOutput}
                          </pre>
                        </div>
                      </div>
                    )}
                    {optimizedOutput && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-300 mb-2">Optimized Output</h4>
                        <div className="bg-green-500/10 rounded-lg p-4 max-h-64 overflow-y-auto border-2 border-green-500/30">
                          <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                            {optimizedOutput}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card>
          </>
        )}
      </div>
    </PageLayout>
  );
};
