import { InputHTMLAttributes } from 'react';
interface FormInputProps extends InputHTMLAttributes<HTMLInputElement> {
    label: string;
    name: string;
    error?: string;
    touched?: boolean;
}
export declare const FormInput: ({ label, name, error, touched, className, ...rest }: FormInputProps) => import("react/jsx-runtime").JSX.Element;
export {};
