import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { PageLayout } from '../components/layout/PageLayout';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { useOptimization } from '../hooks/useOptimization';
import { useAnalysis } from '../hooks/useAnalysis';
import { Sparkles, ArrowRight, RefreshCw, TestTube, Code2, Zap } from 'lucide-react';
import type { AnalysisResponse } from '../types/analysis.types';

export const OptimizePage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Get analysis from navigation state (from Analyze page)
  const passedAnalysis = location.state?.analysis as AnalysisResponse | undefined;
  const passedPrompt = location.state?.prompt as string | undefined;

  const [originalPrompt, setOriginalPrompt] = useState(passedPrompt || '');
  const [analysis, setAnalysis] = useState<AnalysisResponse | undefined>(passedAnalysis);
  const [optimizationLevel, setOptimizationLevel] = useState<'minimal' | 'balanced' | 'aggressive'>('balanced');
  const [maxTechniques, setMaxTechniques] = useState(5);

  // Testing feature state
  const [testInput, setTestInput] = useState('');
  const [isTestingOriginal, setIsTestingOriginal] = useState(false);
  const [isTestingOptimized, setIsTestingOptimized] = useState(false);
  const [originalOutput, setOriginalOutput] = useState('');
  const [optimizedOutput, setOptimizedOutput] = useState('');

  const { analyzePrompt, isLoading: isAnalyzing } = useAnalysis();
  const {
    optimizePrompt,
    isLoading: isOptimizing,
    error: optimizationError,
    data: optimizationResult,
    reset: resetOptimization
  } = useOptimization();

  const handleAnalyze = async () => {
    if (!originalPrompt.trim()) return;

    try {
      const result = await analyzePrompt({
        prompt: originalPrompt,
        task_type: 'general',
        domain: 'general'
      });
      setAnalysis(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  const handleOptimize = async () => {
    if (!originalPrompt.trim() || !analysis) return;

    try {
      await optimizePrompt({
        prompt: originalPrompt,
        analysis: analysis,
        optimization_level: optimizationLevel,
        max_techniques: maxTechniques,
        preserve_intent: true
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
      // Simulate API call to test the prompt
      // In real implementation, this would call an LLM API
      await new Promise(resolve => setTimeout(resolve, 1500));

      const mockOutput = `[Simulated output for: "${testInput}"]\n\nPrompt used:\n${promptToTest.substring(0, 100)}...\n\nThis is a placeholder for actual LLM output. In production, this would call your LLM API with the prompt and test input.`;

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

  const canOptimize = originalPrompt.trim().length >= 10 && analysis !== undefined;
  const hasOptimizationResult = optimizationResult !== null;

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Optimize Prompt</h1>
            <p className="text-gray-600">
              Apply prompt engineering techniques to improve your prompt quality
            </p>
          </div>
          {hasOptimizationResult && (
            <Button
              variant="outline"
              onClick={handleReset}
              icon={RefreshCw}
            >
              Start Over
            </Button>
          )}
        </div>

        {/* Step 1: Input Prompt */}
        {!hasOptimizationResult && (
          <Card padding="lg">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-semibold">
                  1
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Enter Prompt to Optimize
                </h2>
              </div>

              <textarea
                value={originalPrompt}
                onChange={(e) => setOriginalPrompt(e.target.value)}
                placeholder="Enter your prompt here (minimum 10 characters)..."
                className="w-full h-40 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />

              {!analysis && (
                <div className="flex gap-3">
                  <Button
                    onClick={handleAnalyze}
                    isLoading={isAnalyzing}
                    disabled={originalPrompt.trim().length < 10}
                    icon={Sparkles}
                  >
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
        {analysis && !hasOptimizationResult && (
          <Card padding="lg">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-semibold">
                  2
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Analysis Results
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Overall Score</p>
                  <p className="text-3xl font-bold text-gray-900">{analysis.overall_score.toFixed(1)}</p>
                  <p className="text-xs text-gray-500 mt-1">out of 10</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Defects Found</p>
                  <p className="text-3xl font-bold text-gray-900">{analysis.defects.length}</p>
                  <p className="text-xs text-gray-500 mt-1">issues detected</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Agent Consensus</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {((analysis.consensus || 0) * 100).toFixed(0)}%
                  </p>
                  <p className="text-xs text-gray-500 mt-1">agreement level</p>
                </div>
              </div>

              {analysis.defects.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Defects to fix:
                  </p>
                  <div className="space-y-2">
                    {analysis.defects.slice(0, 5).map((defect) => (
                      <div key={defect.id} className="flex items-start gap-2 text-sm">
                        <span className="text-red-500">•</span>
                        <span className="text-gray-700">
                          <strong>{defect.name}:</strong> {defect.description}
                        </span>
                      </div>
                    ))}
                    {analysis.defects.length > 5 && (
                      <p className="text-sm text-gray-500 italic">
                        ...and {analysis.defects.length - 5} more
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Step 3: Optimization Settings */}
        {analysis && !hasOptimizationResult && (
          <Card padding="lg">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-semibold">
                  3
                </div>
                <h2 className="text-xl font-semibold text-gray-900">
                  Optimization Settings
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Optimization Level
                  </label>
                  <select
                    value={optimizationLevel}
                    onChange={(e) => setOptimizationLevel(e.target.value as any)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="minimal">Minimal (Up to 3 techniques)</option>
                    <option value="balanced">Balanced (Up to 5 techniques) - Recommended</option>
                    <option value="aggressive">Aggressive (Up to 7 techniques)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Techniques: {maxTechniques}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={maxTechniques}
                    onChange={(e) => setMaxTechniques(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Conservative</span>
                    <span>Aggressive</span>
                  </div>
                </div>
              </div>

              <Button
                onClick={handleOptimize}
                isLoading={isOptimizing}
                disabled={!canOptimize}
                icon={Zap}
                className="w-full md:w-auto"
              >
                {isOptimizing ? 'Optimizing...' : 'Optimize Prompt'}
              </Button>

              {optimizationError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-sm text-red-800">
                    <strong>Error:</strong> {optimizationError.message}
                  </p>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Optimization Results */}
        {hasOptimizationResult && optimizationResult && (
          <>
            {/* Improvement Summary */}
            <Card padding="lg">
              <div className="text-center space-y-4">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-2">
                  <Sparkles className="w-8 h-8" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">
                  Optimization Complete!
                </h2>
                <div className="flex items-center justify-center gap-4 text-center">
                  <div>
                    <p className="text-4xl font-bold text-gray-900">
                      {optimizationResult.before_analysis.overall_score.toFixed(1)}
                    </p>
                    <p className="text-sm text-gray-600">Before</p>
                  </div>
                  <ArrowRight className="w-6 h-6 text-gray-400" />
                  <div>
                    <p className="text-4xl font-bold text-green-600">
                      {optimizationResult.after_analysis.overall_score.toFixed(1)}
                    </p>
                    <p className="text-sm text-gray-600">After</p>
                  </div>
                  <div className="ml-4">
                    <p className="text-2xl font-bold text-green-600">
                      +{optimizationResult.improvement_score.toFixed(1)}
                    </p>
                    <p className="text-sm text-gray-600">Improvement</p>
                  </div>
                </div>

                <div className="flex gap-2 justify-center flex-wrap">
                  {optimizationResult.techniques_applied.map((tech) => (
                    <span
                      key={tech.technique_id}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-100 text-purple-700"
                    >
                      {tech.technique_name}
                    </span>
                  ))}
                </div>
              </div>
            </Card>

            {/* Side-by-Side Comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Original Prompt */}
              <Card padding="lg">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Code2 className="w-5 h-5 text-gray-600" />
                  Original Prompt
                </h3>
                <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                    {optimizationResult.original_prompt}
                  </pre>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>Defects:</span>
                    <span className="font-semibold">{optimizationResult.metadata.defects_before}</span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>Tokens:</span>
                    <span className="font-semibold">{optimizationResult.metadata.original_tokens}</span>
                  </div>
                </div>
              </Card>

              {/* Optimized Prompt */}
              <Card padding="lg">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-green-600" />
                  Optimized Prompt
                </h3>
                <div className="bg-green-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                    {optimizationResult.optimized_prompt}
                  </pre>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>Defects:</span>
                    <span className="font-semibold text-green-600">{optimizationResult.metadata.defects_after}</span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>Tokens:</span>
                    <span className="font-semibold">{optimizationResult.metadata.optimized_tokens}</span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Techniques Applied */}
            <Card padding="lg">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Techniques Applied ({optimizationResult.techniques_applied.length})
              </h3>
              <div className="space-y-4">
                {optimizationResult.techniques_applied.map((technique) => (
                  <div key={technique.technique_id} className="border-l-4 border-purple-500 pl-4 py-2">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{technique.technique_name}</h4>
                        <p className="text-sm text-gray-600 mt-1">{technique.modification}</p>
                        {technique.target_defects.length > 0 && (
                          <p className="text-xs text-gray-500 mt-2">
                            Fixes: {technique.target_defects.join(', ')}
                          </p>
                        )}
                      </div>
                      <span className="text-xs text-purple-600 font-medium px-2 py-1 bg-purple-50 rounded">
                        {technique.technique_id}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Testing Feature */}
            <Card padding="lg">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <TestTube className="w-6 h-6 text-blue-600" />
                  <h3 className="text-lg font-semibold text-gray-900">
                    Test with Real Input
                  </h3>
                </div>
                <p className="text-sm text-gray-600">
                  Provide test input to compare how both prompts perform side-by-side
                </p>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test Input
                  </label>
                  <textarea
                    value={testInput}
                    onChange={(e) => setTestInput(e.target.value)}
                    placeholder="Enter your test input here..."
                    className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                </div>

                <div className="flex gap-3">
                  <Button
                    onClick={() => handleTest(optimizationResult.original_prompt, true)}
                    isLoading={isTestingOriginal}
                    disabled={!testInput.trim()}
                    variant="outline"
                  >
                    Test Original
                  </Button>
                  <Button
                    onClick={() => handleTest(optimizationResult.optimized_prompt, false)}
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
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Original Output</h4>
                        <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                          <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                            {originalOutput}
                          </pre>
                        </div>
                      </div>
                    )}
                    {optimizedOutput && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Optimized Output</h4>
                        <div className="bg-green-50 rounded-lg p-4 max-h-64 overflow-y-auto border-2 border-green-200">
                          <pre className="text-sm text-gray-800 whitespace-pre-wrap">
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
