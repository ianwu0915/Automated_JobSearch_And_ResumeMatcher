import React from "react";
import { Link } from "react-router-dom";
import { MatchScore } from "@/components/common/MatchScore";
import { JobMatchCardType } from "@/types";

interface JobMatchCardProps {
  jobMatchCardType: JobMatchCardType;
}

export const JobMatchCard: React.FC<JobMatchCardProps> = ({ jobMatchCardType }) => {
  const {
    job_id,
    match_score,
    matched_skills,
    missing_skills,
    title,
    company,
    location,
    apply_url,
    listed_time,
    workplace_type,
  } = jobMatchCardType;

  // Format the listed time to a readable format
  const formatListedTime = (listedTime: string) => {
    const date = new Date(listedTime);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  // Limit the number of skills to display
  const displayedMatchedSkills = matched_skills.slice(0, 5);
  const displayedMissingSkills = missing_skills.slice(0, 3);
  const hasMoreMatchedSkills = matched_skills.length > 5;
  const hasMoreMissingSkills = missing_skills.length > 3;

  return (
    <div className="card hover:shadow-lg transition-shadow duration-300 border border-gray-200">
      <div className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              <Link to={`/jobs/${job_id}`} className="hover:text-primary-600">
                {title}
              </Link>
            </h3>
            <p className="text-sm text-gray-600">{company}</p>
            <div className="flex items-center mt-1 text-sm text-gray-500">
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
              <span>{location}</span>
              <span className="mx-2">•</span>
              <span>{workplace_type}</span>
            </div>
          </div>
          <div className="flex flex-col items-end">
            <div className="mb-1 font-medium text-sm">Match Score</div>
            <MatchScore score={match_score} size="md" />
          </div>
        </div>

        <div className="mt-4">
          <div className="text-sm font-medium text-gray-700">
            Matched Skills:
          </div>
          <div className="mt-1 flex flex-wrap gap-1">
            {displayedMatchedSkills.map((skill: any, index: any) => (
              <span
                key={index}
                className="px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-800"
              >
                {skill}
              </span>
            ))}
            {hasMoreMatchedSkills && (
              <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-800">
                +{matched_skills.length - 5} more
              </span>
            )}
          </div>
        </div>

        {displayedMissingSkills.length > 0 && (
          <div className="mt-3">
            <div className="text-sm font-medium text-gray-700">
              Missing Skills:
            </div>
            <div className="mt-1 flex flex-wrap gap-1">
              {displayedMissingSkills.map((skill, index) => (
                <span
                  key={index}
                  className="px-2 py-0.5 rounded-full text-xs bg-red-100 text-red-800"
                >
                  {skill}
                </span>
              ))}
              {hasMoreMissingSkills && (
                <span className="px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-800">
                  +{missing_skills.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        <div className="mt-5 pt-4 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-500">
            Posted: {formatListedTime(listed_time)}
          </div>
          <div className="flex gap-2">
            <a
              href={apply_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Quick Apply
              <svg
                className="ml-1 -mr-0.5 h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            </a>
            <Link
              to={`/jobs/${job_id}`}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-primary-700 bg-primary-50 hover:bg-primary-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              View Details
              <svg
                className="ml-1 -mr-0.5 h-4 w-4"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
