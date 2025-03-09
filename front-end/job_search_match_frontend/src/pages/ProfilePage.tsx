import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { resumeService } from "@/services/resumeService";
import { ResumeUploader } from "@/components/resume/ResumeUploader";
import { Button } from "@/components/common/Button";
import { Resume } from "@/types";
import { Spinner } from "@/components/common/Spinner";

export const ProfilePage: React.FC = () => {
  const { state } = useAuth();
  const navigate = useNavigate();
  const [resume, setResume] = useState<Resume | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Redirect if not authenticated
    if (!state.isAuthenticated) {
      navigate("/login");
      return;
    }

    // Fetch user's resume
    const fetchResume = async () => {
      try {
        setIsLoading(true);
        if (state.user) {
          const userResume = await resumeService.getResumeByUserId(
            state.user.user_id
          );
          setResume(userResume);
        }
      } catch (err) {
        console.error("Error fetching resume:", err);
        // It's okay if the user doesn't have a resume yet
      } finally {
        setIsLoading(false);
      }
    };

    fetchResume();
  }, [state.isAuthenticated, state.user, navigate]);

  const handleResumeUpload = async (file: File, userId: string) => {
    try {
      console.log("handleResumeUpload", file, userId);
      const result = await resumeService.uploadResume(file, userId);

      console.log("result", result);
      // Refetch the resume to get the full object
      const userResume = await resumeService.getResumeByUserId(userId);
      setResume(userResume);
      console.log("userResume", userResume);
      console.log("userResume.resume_id", userResume.resume_id);
      return {
        resumeId: userResume.resume_id,
        features: userResume.features,
      };
    } catch (err) {
      console.error("Error uploading resume:", err);
      setError("Failed to upload resume. Please try again.");
      throw err;
    }
  };

  const handleContinueToSearch = () => {
    navigate("/search");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  console.log("state.user", state.user);
  return (
    // <div className="max-w-3xl mx-auto py-10 px-4 sm:px-6 lg:px-8">
    <div className="w-full mx-auto py-10 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h1 className="text-2xl font-semibold text-gray-900">Profile</h1>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Upload your resume to start matching with jobs
          </p>
        </div>

        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <h2 className="text-lg font-medium text-gray-900">
            Your Information
          </h2>

          <div className="mt-4 grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Full Name</h3>
              <p className="mt-1 text-sm text-gray-900">
                {state.user?.full_name}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">
                Email Address
              </h3>
              <p className="mt-1 text-sm text-gray-900">{state.user?.email}</p>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Resume</h2>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {state.user && (
            <ResumeUploader
              userId={state.user.user_id}
              onUpload={handleResumeUpload}
              currentResume={
                resume
                  ? {
                      resumeId: resume.resume_id,
                      fileName: "Your uploaded resume",
                    }
                  : undefined
              }
            />
          )}

          {resume && (
            <div className="mt-6 flex justify-end">
              <Button onClick={handleContinueToSearch}>
                Continue to Job Search
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
