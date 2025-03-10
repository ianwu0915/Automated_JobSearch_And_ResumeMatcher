import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { jobService } from "@/services/jobService";
import { JobMatchCardType } from "@/types";
import { JobMatchCard } from "@/components/jobs/JobMatchCard";

export const JobMatchedPage: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useAuth();
  const [matches, setMatches] = useState<JobMatchCardType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!state.isAuthenticated || !state.user?.user_id) {
      navigate("/login");
      return;
    }

    const fetchMatches = async () => {
      try {
        setIsLoading(true);
        const response = await jobService.getMatchHistory(state.user!.user_id, 20, 50);
        console.log("response", response.matches);
        console.log("response.matches[0]", response.matches[0]);
        setMatches(response.matches);
      } catch (err) {
        console.error("Error fetching matches:", err);
        setError("Failed to fetch job matches");
      } finally {
        setIsLoading(false);
      }
    };

    fetchMatches();
  }, [state.isAuthenticated, state.user?.user_id, navigate]);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <div className="flex-grow container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold mb-6">Your Job Match History</h1>
          {matches.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600">
                No matches found. Try searching for jobs!
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {matches.length > 0 && matches.map((match) => (
                <JobMatchCard key={match.job_id} jobMatchCardType={{...match}} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
