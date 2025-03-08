import React from 'react';
import { Button } from '@/components/common/Button';
import { MatchScore } from '@/components/common/MatchScore';
import { JobMatch } from '@/types';

interface JobDetailProps {
  jobMatch: JobMatch;
}

export const JobDetail: React.FC<JobDetailProps> = ({ jobMatch }) => {
  const { job, matchScore, matchedSkills, missingSkills, requiredExperienceYears, resumeExperienceYears } = jobMatch;

  // Format the listed time to a readable format
  const formatListedTime = (listedTime: string) => {
    const date = new Date(listedTime);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  // Calculate experience match percentage
  const calculateExperienceMatch = () => {
    if (requiredExperienceYears === 0) return 100; // No experience required = perfect match
    if (resumeExperienceYears >= requiredExperienceYears) return 100; // Exceeding requirement = perfect match
    return Math.min(100, Math.round((resumeExperienceYears / requiredExperienceYears) * 100));
  };

  // Calculate skill match percentage
  const calculateSkillMatch = () => {
    const totalRequiredSkills = matchedSkills.length + missingSkills.length;
    if (totalRequiredSkills === 0) return 0;
    return Math.round((matchedSkills.length / totalRequiredSkills) * 100);
  };

  const experienceMatch = calculateExperienceMatch();
  const skillMatch = calculateSkillMatch();

  const handleApply = () => {
    window.open(job.applyUrl, '_blank');
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200">
      {/* Job Header */}
      <div className="bg-gray-50 p-6 border-b border-gray-200">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
            <p className="text-lg text-gray-600">{job.company}</p>
            <div className="flex items-center mt-2 text-sm text-gray-500">
              <svg
                className="mr-1 h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span>{job.location}</span>
              <span className="mx-2">•</span>
              <span>{job.workplaceType}</span>
              <span className="mx-2">•</span>
              <span>Posted: {formatListedTime(job.listedTime)}</span>
            </div>
          </div>
          <div className="flex flex-col items-end">
            <div className="mb-1 font-medium">Overall Match</div>
            <MatchScore score={matchScore} size="lg" />
          </div>
        </div>
        <div className="mt-4">
          <Button onClick={handleApply} fullWidth>
            Apply Now
          </Button>
        </div>
      </div>

      {/* Match Details */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Match Analysis</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Overall Match */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700">Overall Match</h3>
            <div className="mt-2 flex items-center">
              <MatchScore score={matchScore} size="md" />
              <span className="ml-2 text-sm text-gray-600">
                {matchScore >= 80 ? 'Excellent' : matchScore >= 60 ? 'Good' : matchScore >= 40 ? 'Fair' : 'Low'}
              </span>
            </div>
          </div>
          
          {/* Skills Match */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700">Skills Match</h3>
            <div className="mt-2 flex items-center">
              <MatchScore score={skillMatch} size="md" />
              <span className="ml-2 text-sm text-gray-600">
                {matchedSkills.length} of {matchedSkills.length + missingSkills.length} skills
              </span>
            </div>
          </div>
          
          {/* Experience Match */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700">Experience Match</h3>
            <div className="mt-2 flex items-center">
              <MatchScore score={experienceMatch} size="md" />
              <span className="ml-2 text-sm text-gray-600">
                {resumeExperienceYears} yrs / {requiredExperienceYears} yrs required
              </span>
            </div>
          </div>
        </div>
        
        {/* Matched Skills */}
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700">Matched Skills ({matchedSkills.length})</h3>
          <div className="mt-2 flex flex-wrap gap-1">
            {matchedSkills.map((skill, index) => (
              <span
                key={index}
                className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800"
              >
                {skill}
              </span>
            ))}
            {matchedSkills.length === 0 && (
              <span className="text-sm text-gray-500">No matched skills found</span>
            )}
          </div>
        </div>
        
        {/* Missing Skills */}
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700">Missing Skills ({missingSkills.length})</h3>
          <div className="mt-2 flex flex-wrap gap-1">
            {missingSkills.map((skill, index) => (
              <span
                key={index}
                className="px-2 py-1 rounded-full text-xs bg-red-100 text-red-800"
              >
                {skill}
              </span>
            ))}
            {missingSkills.length === 0 && (
              <span className="text-sm text-gray-500">No missing skills</span>
            )}
          </div>
        </div>
      </div>

      {/* Job Description */}
      <div className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Job Description</h2>
        <div className="prose prose-sm max-w-none">
          {/* Render job description - might need to sanitize HTML */}
          <div dangerouslySetInnerHTML={{ __html: job.description }} />
        </div>
      </div>
    </div>
  );
};