import { LoginCredentials } from '@/types';
interface LoginFormProps {
    onSubmit: (values: LoginCredentials) => Promise<void>;
    isLoading: boolean;
    error: string | null;
}
export declare const LoginForm: ({ onSubmit, isLoading, error }: LoginFormProps) => import("react/jsx-runtime").JSX.Element;
export {};
