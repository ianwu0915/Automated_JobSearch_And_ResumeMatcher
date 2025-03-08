import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { useAuth } from '@/hooks/useAuth';
import { RegisterData } from '@/types';

export const RegisterPage: React.FC = () => {
  const { state, register } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (state.isAuthenticated) {
      navigate('/profile');
    }
  }, [state.isAuthenticated, navigate]);

  const handleRegister = async (userData: RegisterData) => {
    await register(userData);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create a new account
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Or{' '}
          <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
            sign in to your existing account
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <RegisterForm
            onSubmit={handleRegister}
            isLoading={state.isLoading}
            error={state.error}
          />
        </div>
      </div>
    </div>
  );
};