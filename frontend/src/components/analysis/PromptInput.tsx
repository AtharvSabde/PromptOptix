import React from 'react';
import { Card } from '../common/Card';
import { VALIDATION_LIMITS } from '../../utils/constants';
import { validatePrompt } from '../../utils/errorHandlers';

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const PromptInput: React.FC<PromptInputProps> = ({
  value,
  onChange,
  placeholder = 'Enter your prompt here...',
  disabled = false,
}) => {
  const charCount = value.length;
  const validationError = validatePrompt(value);
  const isOverLimit = charCount > VALIDATION_LIMITS.MAX_PROMPT_LENGTH;

  return (
    <Card padding="md">
      <div className="space-y-2">
        <label htmlFor="prompt" className="block text-sm font-medium text-gray-700">
          Prompt
        </label>
        <textarea
          id="prompt"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          rows={8}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <div className="flex justify-between items-center text-sm">
          <div>
            {validationError && charCount >= VALIDATION_LIMITS.MIN_PROMPT_LENGTH && (
              <span className="text-red-600">{validationError}</span>
            )}
          </div>
          <div className={`${isOverLimit ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
            {charCount.toLocaleString()} / {VALIDATION_LIMITS.MAX_PROMPT_LENGTH.toLocaleString()} characters
          </div>
        </div>
      </div>
    </Card>
  );
};
