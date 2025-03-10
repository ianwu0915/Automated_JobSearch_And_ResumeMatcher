import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';  
import { Button } from '@/components/common/Button';
import { JobCard } from '@/components/jobs/JobCard';
import { Spinner } from '@/components/common/Spinner';
import { useAuth } from '@/hooks/useAuth';
import { useJobSearch } from '@/contexts/JobSearchContext';
import { JobMatch} from '@/types';

// Sorting options
type SortOption = 'match' | 'date' | 'company';

export const JobResultsPage: React.FC = () => {
  const navigate = useNavigate();
  const { state: authState } = useAuth();
  const { matches, isLoading, error: searchError, lastSearchParams, searchJobs } = useJobSearch();
  
  const [sortedMatches, setSortedMatches] = useState<JobMatch[]>([]);
  const [sortBy, setSortBy] = useState<SortOption>('match');
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    if (searchError) {
      setError(searchError);
    }
  }, [searchError]);
  
  useEffect(() => {
    // Redirect if not authenticated
    if (!authState.isAuthenticated) {
      navigate('/login');
      return;
    }
    
    // If no matches and not loading, redirect to search
    if (matches.length === 0 && !isLoading) {
      navigate('/search');
      return;
    }
    
    // Set matches from context
    setSortedMatches(matches);
  }, [authState.isAuthenticated, matches, isLoading, navigate]);
  
  // Effect for sorting matches
  useEffect(() => {
    if (sortedMatches.length === 0) return;
    
    let sorted = [...sortedMatches];
    
    switch (sortBy) {
      case 'match':
        sorted = sorted.sort((a, b) => b.match_score - a.match_score);
        break;
      case 'date':
        sorted = sorted.sort((a, b) => 
          new Date(b.job.listed_time).getTime() - new Date(a.job.listed_time).getTime()
        );
        break;
      case 'company':
        sorted = sorted.sort((a, b) => 
          a.job.company.localeCompare(b.job.company)
        );
        break;
    }
    
    setSortedMatches(sorted);
  }, [sortBy]);
  
  const handleNewSearch = () => {
    navigate('/search');
  };
  
  // Handle rerunning the same search
  const handleRefreshSearch = async () => {
    if (!lastSearchParams) {
      navigate('/search');
      return;
    }
    
    try {
      await searchJobs(lastSearchParams);
    } catch (err) {
      console.error('Error refreshing search:', err);
      setError('Failed to refresh search results. Please try again.');
    }
  };
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }
  
  return (
    <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Job Matches</h1>
          <p className="mt-1 text-sm text-gray-500">
            Found {sortedMatches.length} jobs matching your skills and criteria
          </p>
        </div>
        <Button onClick={handleNewSearch}>New Search</Button>
      </div>
      
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          {error}
        </div>
      )}
      
      <div className="flex justify-between items-center mb-4 bg-white p-4 rounded-lg shadow-sm">
        <div className="flex space-x-2">
          <span className="text-sm font-medium text-gray-700">Sort by:</span>
          <button
            className={`text-sm ${sortBy === 'match' ? 'font-medium text-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setSortBy('match')}
          >
            Match Score
          </button>
          <button
            className={`text-sm ${sortBy === 'date' ? 'font-medium text-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setSortBy('date')}
          >
            Date Posted
          </button>
          <button
            className={`text-sm ${sortBy === 'company' ? 'font-medium text-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setSortBy('company')}
          >
            Company
          </button>
        </div>
        
        <button
          className="text-sm text-primary-600 hover:text-primary-500"
          onClick={handleRefreshSearch}
          disabled={isLoading}
        >
          Refresh Results
        </button>
      </div>
      
      {sortedMatches.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <h2 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h2>
          <p className="text-gray-500 mb-6">
            We couldn't find any jobs matching your criteria. Try adjusting your search parameters.
          </p>
          <Button onClick={handleNewSearch}>Back to Search</Button>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedMatches.map((jobMatch) => (
            <JobCard key={jobMatch.job_id} jobMatch={jobMatch} />
          ))}
        </div>
      )}
    </div>
  );
};