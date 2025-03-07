import React from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { FormInput } from '@/components/common/FormInput';
import { Button } from '@/components/common/Button';
import { JobSearchParams } from '@/types';

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
      keywords: '',
      location: 'United States',
      experienceLevel: ['2', '3'], // Mid-level and Senior by default
      jobType: ['F', 'C'], // Full-time and Contract by default
      remote: ['2'], // Remote by default
      limit: 50,
      userId: userId,
    },
    validationSchema: Yup.object({
      keywords: Yup.string().required('Keywords are required'),
      location: Yup.string().required('Location is required'),
    }),
    onSubmit: async (values) => {
      await onSubmit(values);
    },
  });

  // Experience level options
  const experienceLevels = [
    { value: '1', label: 'Entry Level' },
    { value: '2', label: 'Mid Level' },
    { value: '3', label: 'Senior Level' },
    { value: '4', label: 'Director' },
    { value: '5', label: 'Executive' },
  ];

  // Job type options
  const jobTypes = [
    { value: 'F', label: 'Full-time' },
    { value: 'C', label: 'Contract' },
    { value: 'P', label: 'Part-time' },
    { value: 'T', label: 'Temporary' },
    { value: 'I', label: 'Internship' },
  ];

  // Remote options
  const remoteOptions = [
    { value: '1', label: 'On-site' },
    { value: '2', label: 'Remote' },
    { value: '3', label: 'Hybrid' },
  ];

  // Handle checkbox changes for multi-select options
  const handleCheckboxChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    field: 'experienceLevel' | 'jobType' | 'remote'
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
          name="location"
          type="text"
          placeholder="e.g. United States, San Francisco, Remote"
          value={formik.values.location}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          error={formik.errors.location}
          touched={formik.touched.location}
        />

        <div>
          <label className="form-label">Experience Level</label>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {experienceLevels.map((level) => (
              <div key={level.value} className="flex items-center">
                <input
                  id={`experience-${level.value}`}
                  name="experienceLevel"
                  type="checkbox"
                  value={level.value}
                  checked={formik.values.experienceLevel.includes(level.value)}
                  onChange={(e) => handleCheckboxChange(e, 'experienceLevel')}
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
                  checked={formik.values.jobType.includes(type.value)}
                  onChange={(e) => handleCheckboxChange(e, 'jobType')}
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
                  onChange={(e) => handleCheckboxChange(e, 'remote')}
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