import React from "react";
import { useFormik } from "formik";
import * as Yup from "yup";
import { FormInput } from "@/components/common/FormInput";
import { Button } from "@/components/common/Button";
import { JobSearchParams } from "@/types";

interface JobSearchFormProps {
  onSubmit: (values: JobSearchParams) => Promise<void>;
  isLoading: boolean;
  userId: string;
}

export const JobSearchForm: React.FC<JobSearchFormProps> = ({
  onSubmit,
  isLoading,
  userId,
}) => {
  const formik = useFormik<JobSearchParams>({
    initialValues: {
      keywords: "",
      location_name: "United States",
      experience_level: ["2", "3"], // Entry Level and Associate by default
      job_type: ["F", "C"], // Full-time and Contract by default
      remote: ["1", "2"], // On-site and Remote by default
      limit: 5,
      user_id: userId,
    },
    validationSchema: Yup.object({
      keywords: Yup.string().required("Keywords are required"),
      location_name: Yup.string().required("Location is required"),
    }),
    onSubmit: async (values) => {
      await onSubmit(values);
    },
  });

  // Experience level options
  const experienceLevels = [
    { value: "1", label: "Internship" },
    { value: "2", label: "Entry Level" },
    { value: "3", label: "Associate" },
    { value: "4", label: "Mid-Senior" },
    { value: "5", label: "Director" },
    { value: "6", label: "Executive" },
  ];

  // Job type options
  const jobTypes = [
    { value: "F", label: "Full-time" },
    { value: "P", label: "Part-time" },
    { value: "C", label: "Contract" },
    { value: "T", label: "Temporary" },
    { value: "I", label: "Internship" },
    { value: "V", label: "Volunteer" },
  ];

  // Remote options
  const remoteOptions = [
    { value: "1", label: "On-site" },
    { value: "2", label: "Remote" },
    { value: "3", label: "Hybrid" },
  ];

  // Handle checkbox changes for multi-select options
  const handleCheckboxChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    field: "experience_level" | "job_type" | "remote"
  ) => {
    const { checked, value } = e.target;
    const currentValues = [...formik.values[field]];

    if (checked) {
      if (!currentValues.includes(value)) {
        formik.setFieldValue(field, [...currentValues, value]);
      }
    } else {
      formik.setFieldValue(
        field,
        currentValues.filter((v) => v !== value)
      );
    }
  };

  return (
    <form onSubmit={formik.handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <FormInput
          label="Keywords"
          name="keywords"
          type="text"
          placeholder="e.g. Software Engineer, React, JavaScript"
          value={formik.values.keywords}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.errors.keywords}
          touched={formik.touched.keywords}
        />

        <FormInput
          label="Location"
          name="location_name"
          type="text"
          placeholder="e.g. United States, San Francisco, Remote"
          value={formik.values.location_name}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.errors.location_name}
          touched={formik.touched.location_name}
        />

        <div>
          <label className="form-label">Experience Level</label>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {experienceLevels.map((level) => (
              <div key={level.value} className="flex items-center">
                <input
                  id={`experience-${level.value}`}
                  name="experience"
                  type="checkbox"
                  value={level.value}
                  checked={formik.values.experience_level.includes(level.value)}
                  onChange={(e) => handleCheckboxChange(e, "experience_level")}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label
                  htmlFor={`experience-${level.value}`}
                  className="ml-2 block text-sm text-gray-700"
                >
                  {level.label}
                </label>
              </div>
            ))}
          </div>
        </div>

        <div>
          <label className="form-label">Job Type</label>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {jobTypes.map((type) => (
              <div key={type.value} className="flex items-center">
                <input
                  id={`job-type-${type.value}`}
                  name="jobType"
                  type="checkbox"
                  value={type.value}
                  checked={formik.values.job_type.includes(type.value)}
                  onChange={(e) => handleCheckboxChange(e, "job_type")}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label
                  htmlFor={`job-type-${type.value}`}
                  className="ml-2 block text-sm text-gray-700"
                >
                  {type.label}
                </label>
              </div>
            ))}
          </div>
        </div>

        <div>
          <label className="form-label">Work Environment</label>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {remoteOptions.map((option) => (
              <div key={option.value} className="flex items-center">
                <input
                  id={`remote-${option.value}`}
                  name="remote"
                  type="checkbox"
                  value={option.value}
                  checked={formik.values.remote.includes(option.value)}
                  onChange={(e) => handleCheckboxChange(e, "remote")}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label
                  htmlFor={`remote-${option.value}`}
                  className="ml-2 block text-sm text-gray-700"
                >
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        </div>

        <div>
          <label className="form-label">Number of Jobs</label>
          <input
            type="number"
            name="limit"
            min="1"
            max="100"
            value={formik.values.limit}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>
      </div>

      <Button
        type="submit"
        variant="primary"
        isLoading={isLoading}
        disabled={isLoading}
        fullWidth
      >
        Search Jobs
      </Button>
    </form>
  );
};
