import type { ApiError } from '../api/client';

/**
 * Get user-friendly error message from API error
 * @param error API error object
 * @returns User-friendly error message
 */
export const getErrorMessage = (error: ApiError): string => {
  // Network errors
  if (!error.status) {
    return 'Network error. Please check your connection and ensure the backend server is running.';
  }

  // Specific status codes
  switch (error.status) {
    case 503:
      return 'Service unavailable. The multi-agent system is currently unavailable. Please try again.';
    case 422:
      return error.message || 'Validation error. Please check your input and try again.';
    case 500:
      return 'Internal server error. Please try again or contact support.';
    case 404:
      return 'Resource not found.';
    default:
      return error.message || 'An unexpected error occurred. Please try again.';
  }
};

/**
 * Get error title from API error
 * @param error API error object
 * @returns Error title
 */
export const getErrorTitle = (error: ApiError): string => {
  if (!error.status) {
    return 'Connection Error';
  }

  switch (error.status) {
    case 503:
      return 'Service Unavailable';
    case 422:
      return 'Validation Error';
    case 500:
      return 'Server Error';
    case 404:
      return 'Not Found';
    default:
      return error.error || 'Error';
  }
};

/**
 * Check if error is retryable
 * @param error API error object
 * @returns True if error can be retried
 */
export const isRetryableError = (error: ApiError): boolean => {
  // Network errors are retryable
  if (!error.status) return true;

  // Service unavailable and server errors are retryable
  return error.status === 503 || error.status === 500;
};

/**
 * Validate prompt before submission
 * @param prompt Prompt text
 * @returns Validation error message or null if valid
 */
export const validatePrompt = (prompt: string): string | null => {
  const trimmedPrompt = prompt.trim();

  if (!trimmedPrompt) {
    return 'Prompt cannot be empty';
  }

  if (trimmedPrompt.length < 10) {
    return 'Prompt must be at least 10 characters long';
  }

  if (trimmedPrompt.length > 50000) {
    return 'Prompt cannot exceed 50,000 characters';
  }

  return null;
};
