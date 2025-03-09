import React, { ReactNode } from "react";
import { AuthState, LoginCredentials, RegisterData } from "@/types";
/**
 * This is the AuthContext component that provides a central place to manage the authentication state and the user's session.
 * All components can access the authentication state and the user's session
 * 1. Check if the user is authenticated
 * 2. Get the current user's information
 * 3. Perform login and logout operations
 */
export interface AuthContextType {
    state: AuthState;
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (userData: RegisterData) => Promise<void>;
    logout: () => void;
}
export declare const AuthContext: React.Context<AuthContextType>;
export declare const AuthProvider: React.FC<{
    children: ReactNode;
}>;
