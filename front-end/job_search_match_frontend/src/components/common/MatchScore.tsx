interface MatchScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

export const MatchScore = ({ 
  score, 
  size = 'md', 
  showText = true 
}: MatchScoreProps) => {
  // Determine color based on score
  const getColor = () => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-green-400';
    if (score >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  // Size classes
  const sizeClasses = {
    sm: 'h-2 w-20',
    md: 'h-3 w-24',
    lg: 'h-4 w-32',
  };
  
  // Text size classes
  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };
  
  const barColor = getColor();
  
  return (
    <div className="flex flex-col">
      <div className="flex items-center space-x-2">
        <div className={`bg-gray-200 rounded-full overflow-hidden ${sizeClasses[size]}`}>
          <div
            className={`${barColor} h-full rounded-full`}
            style={{ width: `${score}%` }}
          ></div>
        </div>
        {showText && (
          <span className={`font-semibold ${textSizeClasses[size]}`}>
            {score}%
          </span>
        )}
      </div>
    </div>
  );
};