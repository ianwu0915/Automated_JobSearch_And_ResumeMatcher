import { RegisterData } from '@/types';
interface RegisterFormProps {
    onSubmit: (values: RegisterData) => Promise<void>;
    isLoading: boolean;
    error: string | null;
}
export declare const RegisterForm: ({ onSubmit, isLoading, error }: RegisterFormProps) => import("react/jsx-runtime").JSX.Element;
export {};
