import React from 'react';

interface Props {
  size?: 'small' | 'medium' | 'large';
  message?: string;
}

export const LoadingSpinner: React.FC<Props> = ({ size = 'medium', message }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <div className={`${sizeClasses[size]} animate-spin rounded-full border-b-2 border-blue-600`} />
      {message && <p className="mt-4 text-gray-600">{message}</p>}
    </div>
  );
};