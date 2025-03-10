// src/contexts/JobSearchContext.tsx
import React, {
  createContext,
  useContext,
  ReactNode,
  useState,
  useEffect,
} from "react";
import { JobMatch, JobSearchParams } from "@/types";
import { jobService } from "@/services/jobService";

// Define the context shape
interface JobSearchContextType {
  matches: JobMatch[];
  totalJobs: number;
  isLoading: boolean;
  error: string | null;
  lastSearchParams: JobSearchParams | null;
  searchJobs: (params: JobSearchParams) => Promise<JobMatch[]>;
  getMatchHistory: (
    userId: string,
    limit?: number,
    minScore?: number
  ) => Promise<JobMatch[]>;
  clearMatches: () => void;
}

// 1. Create the context: It is a container for the state and functions that are shared across the app, not the components
const JobSearchContext = createContext<JobSearchContextType | undefined>(
  undefined
);

// Props for the provider component
interface JobSearchProviderProps {
  children: ReactNode;
}

// 2. Create the Provider component
export const JobSearchProvider: React.FC<JobSearchProviderProps> = ({
  children,
}) => {
  // 3. Define the state
  const [matches, setMatches] = useState<JobMatch[]>(() => {
    // Initialize from localStorage
    const saved = localStorage.getItem("jobMatches");
    return saved ? JSON.parse(saved) : [];
  });
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [totalJobs, setTotalJobs] = useState<number>(0);
  const [lastSearchParams, setLastSearchParams] =
    useState<JobSearchParams | null>(() => {
      // Initialize from localStorage
      const saved = localStorage.getItem("lastSearchParams");
      return saved ? JSON.parse(saved) : null;
    });

  // Save to localStorage whenever matches or lastSearchParams change
  useEffect(() => {
    localStorage.setItem("jobMatches", JSON.stringify(matches));
  }, [matches]);

  useEffect(() => {
    if (lastSearchParams) {
      localStorage.setItem(
        "lastSearchParams",
        JSON.stringify(lastSearchParams)
      );
    }
  }, [lastSearchParams]);

  // 4. Define the functions
  const searchJobs = async (params: JobSearchParams) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await jobService.searchAndMatchJobs(params);

      setMatches(response.matches);
      setTotalJobs(response.matches.length);
      setLastSearchParams(params);

      return response.matches;
    } catch (err) {
      console.error("Error searching jobs:", err);
      setError("Failed to search jobs. Please try again.");
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  const getMatchHistory = async (
    userId: string,
    limit: number = 50,
    minScore: number = 50
  ) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await jobService.getMatchHistory(
        userId,
        limit,
        minScore
      );

      setMatches(response.matches);
      setTotalJobs(response.matches.length);

      return response.matches;
    } catch (err) {
      console.error("Error getting match history:", err);
      setError("Failed to get match history. Please try again.");
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  const clearMatches = () => {
    setMatches([]);
    setTotalJobs(0);
    setLastSearchParams(null);
  };

  const value = {
    matches,
    totalJobs,
    isLoading,
    error,
    lastSearchParams,
    searchJobs,
    getMatchHistory,
    clearMatches,
  };

  // 5. Return the Provider component
  // value: the state and functions that we want to share with the components
  return (
    <JobSearchContext.Provider value={value}>
      {children}
    </JobSearchContext.Provider>
  );
};

// Custom hook to use the context
export const useJobSearch = (): JobSearchContextType => {
  const context = useContext(JobSearchContext);
  if (context === undefined) {
    throw new Error("useJobSearch must be used within a JobSearchProvider");
  }
  return context;
};
