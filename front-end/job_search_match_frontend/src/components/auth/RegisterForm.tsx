import { useFormik } from 'formik';
import * as Yup from 'yup';
import { FormInput } from '@/components/common/FormInput';
import { Button } from '@/components/common/Button';
import { RegisterData } from '@/types';

interface RegisterFormProps {
  onSubmit: (values: RegisterData) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export const RegisterForm = ({ 
  onSubmit, 
  isLoading, 
  error 
}: RegisterFormProps) => {
  const formik = useFormik({
    initialValues: {
      full_name: '',
      email: '',
      password: '',
      confirm_password: '',
    },
    validationSchema: Yup.object({
      full_name: Yup.string()
        .required('Full name is required'),
      email: Yup.string()
        .email('Invalid email address')
        .required('Email is required'),
      password: Yup.string()
        .min(8, 'Password must be at least 8 characters')
        .required('Password is required'),
      confirm_password: Yup.string()
        .oneOf([Yup.ref('password')], 'Passwords must match')
        .required('Please confirm your password'),
    }),
    onSubmit: async (values) => {
      const { confirm_password, ...registerData } = values;
      await onSubmit(registerData);
    },
  });

  return (
    <form onSubmit={formik.handleSubmit} className="space-y-4">
      <FormInput
        label="Full Name"
        name="full_name"
        type="text"
        placeholder="John Doe"
        value={formik.values.full_name}
        onChange={formik.handleChange}  
        onBlur={formik.handleBlur}
        error={formik.errors.full_name}
        touched={formik.touched.full_name}
      />

      <FormInput
        label="Email"
        name="email"
        type="email"
        placeholder="your.email@example.com"
        value={formik.values.email}
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        error={formik.errors.email}
        touched={formik.touched.email}
      />

      <FormInput
        label="Password"
        name="password"
        type="password"
        placeholder="********"
        value={formik.values.password}
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        error={formik.errors.password}
        touched={formik.touched.password}
      />

      <FormInput
        label="Confirm Password"
        name="confirm_password"
        type="password"
        placeholder="********"
        value={formik.values.confirm_password}
        onChange={formik.handleChange}
        onBlur={formik.handleBlur}
        error={formik.errors.confirm_password}
        touched={formik.touched.confirm_password}
      />

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <Button
        type="submit"
        variant="primary"
        fullWidth
        isLoading={isLoading}
        disabled={isLoading}
      >
        Create Account
      </Button>
    </form>
  );
};