import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HomePage } from './pages/HomePage';
import { AnalyzePage } from './pages/AnalyzePage';
import { OptimizePage } from './pages/OptimizePage';
import { TechniquesPage } from './pages/TechniquesPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analyze" element={<AnalyzePage />} />
        <Route path="/optimize" element={<OptimizePage />} />
        <Route path="/techniques" element={<TechniquesPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
