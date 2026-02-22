import React from 'react';
import { Link } from 'react-router-dom';
import { PageLayout } from '../components/layout/PageLayout';
import { Button } from '../components/common/Button';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientText } from '../components/ui/GradientText';
import { Sparkles, Search, Zap, Rocket, Users, Target, Shield, TrendingUp, ArrowRight } from 'lucide-react';

export const HomePage: React.FC = () => {
  return (
    <PageLayout maxWidth="full">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center mb-20 mt-8">
        {/* Left: Hero Content */}
        <div>
          {/* Hero Headline */}
          <h1 className="text-6xl font-bold mb-6 leading-tight">
            Transform Your Prompts with{' '}
            <GradientText variant="text">
              AI-Powered Optimization
            </GradientText>
          </h1>

          {/* Hero Description */}
          <p className="text-xl text-gray-400 mb-8 max-w-2xl">
            Detect and fix prompt defects using multi-agent AI analysis.
            Four specialized agents work in parallel to identify issues and optimize your prompts.
          </p>

          {/* CTA Buttons */}
          <div className="flex gap-4">
            <Link to="/optimize">
              <Button size="lg">
                <Zap className="mr-2 h-5 w-5" />
                Start Optimizing
              </Button>
            </Link>
            <Link to="/analyze">
              <Button size="lg" variant="outline">
                <Search className="mr-2 h-5 w-5" />
                Analyze a Prompt
              </Button>
            </Link>
          </div>
        </div>

        {/* Right: Architecture Preview */}
        <div className="relative">
          <GlassCard className="relative overflow-hidden" glow>
            <div className="py-8 px-6">
              <h3 className="text-lg font-semibold text-white mb-6 text-center">Multi-Agent Architecture</h3>
              <div className="space-y-3">
                {[
                  { icon: '👁️', name: 'Clarity Agent', area: 'Specification & Intent', ids: 'D001–D004' },
                  { icon: '📋', name: 'Structure Agent', area: 'Structure & Formatting', ids: 'D005–D009' },
                  { icon: '🧠', name: 'Context Agent', area: 'Context & Memory', ids: 'D010–D014' },
                  { icon: '🛡️', name: 'Security Agent', area: 'Security & Safety', ids: 'D023–D028' },
                ].map((agent) => (
                  <div key={agent.name} className="flex items-center gap-3 bg-dark-bg/50 rounded-lg p-3 border border-dark-border">
                    <span className="text-2xl">{agent.icon}</span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-white">{agent.name}</p>
                      <p className="text-xs text-gray-500">{agent.area}</p>
                    </div>
                    <span className="text-xs text-gray-400 font-mono">{agent.ids}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 text-center">
                <p className="text-xs text-gray-500">Consensus-based defect detection with parallel execution</p>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="max-w-7xl mx-auto mb-20">
        <div className="grid md:grid-cols-3 gap-6">
          <GlassCard hover>
            <div className="flex items-start gap-4">
              <div className="bg-gradient-primary p-3 rounded-xl flex-shrink-0">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white mb-2">
                  Parallel Analysis
                </h3>
                <p className="text-sm text-gray-400">
                  4 specialized agents analyze your prompt simultaneously with real-time streaming progress
                </p>
              </div>
            </div>
          </GlassCard>

          <GlassCard hover>
            <div className="flex items-start gap-4">
              <div className="bg-gradient-primary p-3 rounded-xl flex-shrink-0">
                <Target className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white mb-2">
                  Multi-Model Testing
                </h3>
                <p className="text-sm text-gray-400">
                  Test across Claude, Llama, GPT-4 & Gemini with real-time comparison
                </p>
              </div>
            </div>
          </GlassCard>

          <GlassCard hover>
            <div className="flex items-start gap-4">
              <div className="bg-gradient-primary p-3 rounded-xl flex-shrink-0">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white mb-2">
                  4-Stage Pipeline
                </h3>
                <p className="text-sm text-gray-400">
                  Standard + DGEO + SHDT + CDRAF strategies chained for maximum improvement
                </p>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="max-w-7xl mx-auto mb-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-white mb-3">How It Works</h2>
          <p className="text-gray-400">Three simple steps to optimize any prompt</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary mb-4">
              <span className="text-2xl font-bold text-white">1</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Enter Your Prompt</h3>
            <p className="text-sm text-gray-400">
              Paste your prompt, select the task type and domain for context-aware analysis.
            </p>
          </div>

          <div className="text-center relative">
            <div className="hidden md:block absolute top-8 -left-4 w-8">
              <ArrowRight className="w-6 h-6 text-gray-600" />
            </div>
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary mb-4">
              <span className="text-2xl font-bold text-white">2</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Multi-Agent Analysis</h3>
            <p className="text-sm text-gray-400">
              4 AI agents detect defects in parallel using consensus voting. Watch results stream in real-time.
            </p>
          </div>

          <div className="text-center relative">
            <div className="hidden md:block absolute top-8 -left-4 w-8">
              <ArrowRight className="w-6 h-6 text-gray-600" />
            </div>
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-primary mb-4">
              <span className="text-2xl font-bold text-white">3</span>
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Get Optimized Result</h3>
            <p className="text-sm text-gray-400">
              Receive an improved prompt with before/after comparison, applied techniques, and score improvement.
            </p>
          </div>
        </div>

        <div className="text-center mt-8">
          <Link to="/optimize">
            <Button size="lg">
              <Sparkles className="mr-2 h-5 w-5" />
              Try It Now
            </Button>
          </Link>
        </div>
      </div>

      {/* Real Stats */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <GlassCard hover>
            <div className="text-center">
              <div className="inline-flex p-3 bg-primary-from/20 rounded-xl mb-4">
                <Users className="w-6 h-6 text-primary-from" />
              </div>
              <div className="text-3xl font-bold text-white mb-1">4</div>
              <div className="text-sm text-gray-400 font-medium">AI Agents</div>
              <p className="text-xs text-gray-500 mt-2">
                Clarity, Structure, Context & Security
              </p>
            </div>
          </GlassCard>

          <GlassCard hover>
            <div className="text-center">
              <div className="inline-flex p-3 bg-accent-cyan/20 rounded-xl mb-4">
                <Shield className="w-6 h-6 text-accent-cyan" />
              </div>
              <div className="text-3xl font-bold text-white mb-1">28</div>
              <div className="text-sm text-gray-400 font-medium">Defect Types</div>
              <p className="text-xs text-gray-500 mt-2">
                Based on Tian et al. taxonomy
              </p>
            </div>
          </GlassCard>

          <GlassCard hover>
            <div className="text-center">
              <div className="inline-flex p-3 bg-primary-to/20 rounded-xl mb-4">
                <Sparkles className="w-6 h-6 text-primary-to" />
              </div>
              <div className="text-3xl font-bold text-white mb-1">41+</div>
              <div className="text-sm text-gray-400 font-medium">Techniques</div>
              <p className="text-xs text-gray-500 mt-2">
                Proven optimization methods
              </p>
            </div>
          </GlassCard>

          <GlassCard hover>
            <div className="text-center">
              <div className="inline-flex p-3 bg-green-500/20 rounded-xl mb-4">
                <Target className="w-6 h-6 text-green-500" />
              </div>
              <div className="text-3xl font-bold text-white mb-1">4</div>
              <div className="text-sm text-gray-400 font-medium">Strategies</div>
              <p className="text-xs text-gray-500 mt-2">
                DGEO, SHDT, CDRAF & Standard
              </p>
            </div>
          </GlassCard>
        </div>
      </div>
    </PageLayout>
  );
};
