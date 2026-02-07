/**
 * Format a score to 1 decimal place
 * @param score Score value (0-10)
 * @returns Formatted score string
 */
export const formatScore = (score: number): string => {
  return score.toFixed(1);
};

/**
 * Format a percentage value
 * @param value Value between 0 and 1
 * @returns Formatted percentage string
 */
export const formatPercentage = (value: number): string => {
  return `${Math.round(value * 100)}%`;
};

/**
 * Format a confidence score
 * @param confidence Confidence value (0-1)
 * @returns Formatted confidence string
 */
export const formatConfidence = (confidence: number): string => {
  return `${Math.round(confidence * 100)}%`;
};

/**
 * Format processing time in milliseconds to human readable
 * @param ms Time in milliseconds
 * @returns Formatted time string
 */
export const formatProcessingTime = (ms: number): string => {
  if (ms < 1000) return `${ms}ms`;
  const seconds = (ms / 1000).toFixed(1);
  return `${seconds}s`;
};

/**
 * Format cost in dollars
 * @param cost Cost in dollars
 * @returns Formatted cost string
 */
export const formatCost = (cost: number | undefined): string => {
  if (cost === undefined || cost === null) return 'N/A';
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(3)}`;
};

/**
 * Format token count with commas
 * @param tokens Number of tokens
 * @returns Formatted token count
 */
export const formatTokens = (tokens: number | undefined): string => {
  if (tokens === undefined || tokens === null) return 'N/A';
  return tokens.toLocaleString();
};

/**
 * Truncate text to specified length
 * @param text Text to truncate
 * @param maxLength Maximum length
 * @returns Truncated text with ellipsis if needed
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Format category name for display
 * @param category Category string with underscores
 * @returns Human-readable category name
 */
export const formatCategory = (category: string): string => {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * Format improvement score with sign
 * @param improvement Improvement delta
 * @returns Formatted improvement string with + or -
 */
export const formatImprovement = (improvement: number): string => {
  const sign = improvement >= 0 ? '+' : '';
  return `${sign}${improvement.toFixed(1)}`;
};
