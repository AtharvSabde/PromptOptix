import React from 'react';
import { Link } from 'react-router-dom';
import { PageLayout } from '../components/layout/PageLayout';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Sparkles, Search, Zap, BookOpen } from 'lucide-react';

export const HomePage: React.FC = () => {
  return (
    <PageLayout>
      {/* Hero Section */}
      <div className="text-center mb-12">
        <div className="flex justify-center mb-4">
          <Sparkles className="h-16 w-16 text-blue-600" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          PromptOptimizer Pro
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Multi-Agent Prompt Engineering System powered by AI.
          Analyze, optimize, and perfect your prompts with intelligent defect detection.
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/analyze">
            <Button size="lg">
              <Search className="mr-2 h-5 w-5" />
              Analyze Prompt
            </Button>
          </Link>
          <Link to="/optimize">
            <Button size="lg" variant="secondary">
              <Zap className="mr-2 h-5 w-5" />
              Optimize Prompt
            </Button>
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <Card padding="lg">
          <div className="text-center">
            <div className="flex justify-center mb-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Search className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Multi-Agent Analysis
            </h3>
            <p className="text-sm text-gray-600">
              4 specialized AI agents (Clarity, Structure, Context, Security) work in parallel
              to detect defects with consensus-based validation.
            </p>
          </div>
        </Card>

        <Card padding="lg">
          <div className="text-center">
            <div className="flex justify-center mb-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <Zap className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              28 Defect Types
            </h3>
            <p className="text-sm text-gray-600">
              Comprehensive defect taxonomy covering specification, structure, context,
              output guidance, examples, and security issues.
            </p>
          </div>
        </Card>

        <Card padding="lg">
          <div className="text-center">
            <div className="flex justify-center mb-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <BookOpen className="h-6 w-6 text-purple-600" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              15 Optimization Techniques
            </h3>
            <p className="text-sm text-gray-600">
              Proven prompt engineering techniques including role prompting, few-shot learning,
              chain-of-thought, and more.
            </p>
          </div>
        </Card>
      </div>

      {/* Stats */}
      <Card padding="lg" className="text-center bg-gradient-to-r from-blue-50 to-purple-50">
        <div className="grid grid-cols-3 gap-6">
          <div>
            <div className="text-3xl font-bold text-blue-600">4</div>
            <div className="text-sm text-gray-600">AI Agents</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-green-600">28</div>
            <div className="text-sm text-gray-600">Defect Types</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-purple-600">15</div>
            <div className="text-sm text-gray-600">Techniques</div>
          </div>
        </div>
      </Card>
    </PageLayout>
  );
};
