import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/common/Button";
import { Spinner } from "@/components/common/Spinner";
import { ResumeFeatures } from "@/types";

interface ResumeUploaderProps {
  userId: string;
  onUpload: (
    file: File,
    userId: string
  ) => Promise<{ resumeId: string; features: ResumeFeatures }>;
  currentResume?: { resumeId: string; fileName: string };
}

export const ResumeUploader = ({
  userId,
  onUpload,
  currentResume,
}: ResumeUploaderProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resumeId, setResumeId] = useState<string | null>(
    currentResume?.resumeId || null
  );
  const [features, setFeatures] = useState<ResumeFeatures | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Only accept PDF, DOCX, or TXT files
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      const fileType = selectedFile.type;
      if (
        fileType === "application/pdf" ||
        fileType ===
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
        fileType === "text/plain"
      ) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError("Please upload a PDF, DOCX, or TXT file.");
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "text/plain": [".txt"],
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file || !userId) return;

    try {
      setIsUploading(true);
      setError(null);
      const result = await onUpload(file, userId);
      setResumeId(result.resumeId);
      setFeatures(result.features);
      setIsUploading(false);
    } catch (err) {
      console.error("Upload failed:", err);
      setError("Failed to upload resume. Please try again.");
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-primary-500 bg-primary-50"
            : "border-gray-300 hover:border-primary-400"
        }`}
      >
        <input
          {...(getInputProps() as React.InputHTMLAttributes<HTMLInputElement>)}
        />
        <div className="space-y-2">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <div className="text-sm text-gray-600">
            <p className="font-medium">
              {isDragActive
                ? "Drop your resume here"
                : "Drag and drop your resume, or click to browse"}
            </p>
            <p className="mt-1">PDF, DOCX, or TXT up to 5MB</p>
          </div>
        </div>
      </div>

      {file && (
        <div className="flex items-center justify-between bg-gray-50 px-4 py-3 rounded-md">
          <div className="flex items-center">
            <svg
              className="h-5 w-5 text-gray-400 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="text-sm font-medium text-gray-700 truncate">
              {file.name}
            </span>
          </div>
          <Button
            onClick={handleUpload}
            disabled={isUploading}
            isLoading={isUploading}
            size="sm"
          >
            Upload
          </Button>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {isUploading && (
        <div className="flex justify-center py-4">
          <Spinner size="lg" color="primary" />
        </div>
      )}

      {features && resumeId && (
        <div className="mt-6 bg-green-50 border border-green-200 p-4 rounded-md">
          <h3 className="text-lg font-medium text-green-800">
            Resume Processed Successfully!
          </h3>
          <div className="mt-3">
            <h4 className="font-medium text-sm text-green-800">
              Skills Detected:
            </h4>
            <div className="mt-1 flex flex-wrap gap-1">
              {features.skills.map((skill, index) => (
                <span
                  key={index}
                  className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
          <div className="mt-3">
            <h4 className="font-medium text-sm text-green-800">Experience:</h4>
            <p className="text-sm text-green-800">
              {features.workExperienceYears} years
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
