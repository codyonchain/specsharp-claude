import React from 'react';

interface LoadingSkeletonProps {
  lines?: number;
  className?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  lines = 2, 
  className = '' 
}) => {
  return (
    <div className={`animate-pulse ${className}`}>
      {Array.from({ length: lines }, (_, index) => (
        <div key={index} className="mb-2">
          <div 
            className={`h-4 bg-gray-200 rounded ${
              index === lines - 1 ? 'w-1/2' : 'w-3/4'
            }`}
          />
        </div>
      ))}
    </div>
  );
};

export const LoadingSkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`bg-white p-6 rounded-lg shadow animate-pulse ${className}`}>
      <div className="h-6 bg-gray-200 rounded w-2/3 mb-4" />
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded w-full" />
        <div className="h-4 bg-gray-200 rounded w-5/6" />
        <div className="h-4 bg-gray-200 rounded w-3/4" />
      </div>
      <div className="mt-6 flex justify-between">
        <div className="h-8 bg-gray-200 rounded w-24" />
        <div className="h-8 bg-gray-200 rounded w-32" />
      </div>
    </div>
  );
};

export const LoadingSkeletonTable: React.FC<{ rows?: number; className?: string }> = ({ 
  rows = 5, 
  className = '' 
}) => {
  return (
    <div className={`animate-pulse ${className}`}>
      {/* Table Header */}
      <div className="bg-gray-100 p-4 rounded-t-lg">
        <div className="flex space-x-4">
          <div className="h-4 bg-gray-300 rounded w-1/4" />
          <div className="h-4 bg-gray-300 rounded w-1/4" />
          <div className="h-4 bg-gray-300 rounded w-1/4" />
          <div className="h-4 bg-gray-300 rounded w-1/4" />
        </div>
      </div>
      
      {/* Table Rows */}
      <div className="divide-y divide-gray-200">
        {Array.from({ length: rows }, (_, index) => (
          <div key={index} className="p-4">
            <div className="flex space-x-4">
              <div className="h-4 bg-gray-200 rounded w-1/4" />
              <div className="h-4 bg-gray-200 rounded w-1/4" />
              <div className="h-4 bg-gray-200 rounded w-1/4" />
              <div className="h-4 bg-gray-200 rounded w-1/4" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const LoadingSkeletonForm: React.FC<{ fields?: number; className?: string }> = ({ 
  fields = 4, 
  className = '' 
}) => {
  return (
    <div className={`animate-pulse space-y-6 ${className}`}>
      {Array.from({ length: fields }, (_, index) => (
        <div key={index}>
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-2" />
          <div className="h-10 bg-gray-200 rounded w-full" />
        </div>
      ))}
      <div className="pt-4">
        <div className="h-12 bg-gray-300 rounded w-full" />
      </div>
    </div>
  );
};