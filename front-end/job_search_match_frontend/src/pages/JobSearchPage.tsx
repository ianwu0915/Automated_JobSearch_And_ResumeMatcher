import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useJobSearch } from '@/contexts/JobSearchContext';
import { resumeService } from '@/services/resumeService';
import { JobSearchForm } from '@/components/jobs/JobSearchForm';
import { Button } from '@/components/common/Button';
import { Resume, JobSearchParams } from '@/types';
import { Spinner } from '@/components/common/Spinner';

export const JobSearchPage: React.FC = () => {
  const { state } = useAuth();
  const { searchJobs, isLoading: isSearching, error: searchError } = useJobSearch();
  const navigate = useNavigate();
  
  const [resume, setResume] = useState<Resume | null>(null);
  const [isLoadingResume, setIsLoadingResume] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Set error if there's a search error
    if (searchError) {
      setError(searchError);
    }
  }, [searchError]);

  useEffect(() => {
    // Redirect if not authenticated
    if (!state.isAuthenticated) {
      navigate('/login');
      return;
    }

    // Fetch user's resume
    const fetchResume = async () => {
      try {
        setIsLoadingResume(true);
        if (state.user) {
          const userResume = await resumeService.getResumeByUserId(state.user.user_id);
          setResume(userResume);
        }
      } catch (err) {
        console.error('Error fetching resume:', err);
        setError('Please upload your resume before searching for jobs.');
      } finally {
        setIsLoadingResume(false);
      }
    };

    fetchResume();
  }, [state.isAuthenticated, state.user, navigate]);

  const handleSearch = async (searchParams: JobSearchParams) => {
    try {
      if (!state.user) {
        setError('You must be logged in to search for jobs.');
        return;
      }
      
      // Update userId in search params
      const params = {
        ...searchParams,
        user_id: state.user.user_id,
      };

      console.log(params);
      
      const matches = await searchJobs(params);
      
      if (matches && matches.length > 0) {
        console.log("Navigating to results page");
        navigate('/matches');
      } else {
        setError('No matching jobs found. Try adjusting your search criteria.');
      }
    } catch (err) {
      console.error('Error searching jobs:', err);
      setError('Failed to search jobs. Please try again.');
    }
  };

  if (isLoadingResume) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  // If no resume is found, prompt user to upload one
  if (!resume) {
    return (
      <div className="max-w-3xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h1 className="text-2xl font-semibold text-gray-900">Job Search</h1>
          </div>
          
          <div className="px-4 py-5 sm:px-6">
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    Resume Required
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>
                      You need to upload your resume before searching for jobs. This helps us match you with the most relevant positions.
                    </p>
                  </div>
                  <div className="mt-4">
                    <Button
                      size="sm"
                      onClick={() => navigate('/profile')}
                    >
                      Upload Resume
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h1 className="text-2xl font-semibold text-gray-900">Job Search</h1>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Find jobs that match your skills and experience
          </p>
        </div>
        
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div className="bg-gray-50 p-4 rounded-md mb-6">
            <h2 className="text-sm font-medium text-gray-700">Your Resume Skills:</h2>
            <div className="mt-2 flex flex-wrap gap-1">
              {resume?.features.skills.map((skill, index) => (
                <span
                  key={index}
                  className="px-2 py-1 rounded-full text-xs bg-primary-100 text-primary-800"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
          
          <JobSearchForm
            onSubmit={handleSearch}
            isLoading={isSearching}
            userId={state.user?.user_id || ''}
          />
        </div>
      </div>
    </div>  
  );
};