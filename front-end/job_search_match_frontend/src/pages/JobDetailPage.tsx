import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { JobDetail } from '@/components/jobs/JobDetail';
import { Spinner } from '@/components/common/Spinner';
import { useAuth } from '@/hooks/useAuth';
import { jobService } from '@/services/jobService';
import { resumeService } from '@/services/resumeService';
import { JobMatch } from '@/types';

export const JobDetailPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { state } = useAuth();
  
  const [jobMatch, setJobMatch] = useState<JobMatch | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Redirect if not authenticated
    if (!state.isAuthenticated) {
      navigate('/login');
      return;
    }
    
    if (!jobId) {
      navigate('/search');
      return;
    }
    
    const fetchJobDetails = async () => {
      try {
        setIsLoading(true);
        
        // Get the user's resume
        if (!state.user) {
          throw new Error('User not found');
        }
        
        const resume = await resumeService.getResumeByUserId(state.user.user_id);
        if (!resume) {
          navigate('/profile');
          return;
        }
        
        // Get job details
        console.log("Getting job detailsby ID:", jobId);
        const job = await jobService.getJobById(jobId);
        console.log("Job details:", job);
        // Get match history to find this job's match score
        console.log("Getting match history for user:", state.user.user_id);
        const matchHistory = await jobService.getMatchHistory(state.user.user_id);
        console.log("Match history:", matchHistory);
        // Find this job in match history
        const match = matchHistory.matches.find(m => m.job_id === jobId);
        
        if (match) {
          // Use existing match data
          setJobMatch(match);
        } else {
          // If job not found in match history, create a temporary match object
          // This is not ideal but allows viewing job details
          setJobMatch({
            resume_id: resume.resume_id,
            job_id: job.job_id,
            match_score: 0, 
            matched_skills: [],
            missing_skills: job.features.skills,
            required_experience_years: job.features.required_experience_years,
            resume_experience_years: resume.features.work_experience_years, 
            job: job,
            title: job.title,
            company: job.company,
            location: job.location,
            created_at: new Date().toISOString(),
            apply_url: job.apply_url,
            id: 0,
          });
          
          setError('This job was not in your match results. Match score may not be accurate.');
        }
      } catch (err) {
        console.error('Error fetching job details:', err);
        setError('Failed to load job details. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchJobDetails();
  }, [jobId, state.isAuthenticated, state.user, navigate]);
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }
  
  if (!jobMatch) {
    return (
      <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <h2 className="text-lg font-medium text-gray-900 mb-2">Job not found</h2>
          <p className="text-gray-500 mb-6">
            We couldn't find the job you're looking for.
          </p>
          <Link
            to="/search"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            Back to Search
          </Link>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center justify-between">
        <Link
          to="/matches"
          className="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-500"
        >
          <svg
            className="mr-1 -ml-1 h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
              clipRule="evenodd"
            />
          </svg>
          Back to Results
        </Link>
      </div>
      
      {error && (
        <div className="mb-6 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
          {error}
        </div>
      )}
      
      <JobDetail jobMatch={jobMatch} />
    </div>
  );
};
