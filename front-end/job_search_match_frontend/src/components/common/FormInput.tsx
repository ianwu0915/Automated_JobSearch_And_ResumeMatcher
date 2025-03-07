import { InputHTMLAttributes } from 'react';
interface FormInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  name: string;
  error?: string;
  touched?: boolean;
}

export const FormInput = ({
  label,
  name,
  error,
  touched,
  className = '',
  ...rest
}: FormInputProps) => {
  const showError = touched && error;
  
  return (
    <div className="mb-4">
      <label htmlFor={name} className="form-label">
        {label}
      </label>
      <input
        id={name}
        name={name}
        className={`form-input ${showError ? 'border-red-500' : ''} ${className}`}
        {...rest}
      />
      {showError && <p className="form-error">{error}</p>}
    </div>
  );
};