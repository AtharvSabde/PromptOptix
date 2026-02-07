import React from 'react';
import { PageLayout } from '../components/layout/PageLayout';
import { Card } from '../components/common/Card';

export const TechniquesPage: React.FC = () => {
  return (
    <PageLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Prompt Engineering Techniques</h1>
        <Card padding="lg">
          <p className="text-gray-600 text-center py-12">
            Techniques library coming soon...
          </p>
        </Card>
      </div>
    </PageLayout>
  );
};
