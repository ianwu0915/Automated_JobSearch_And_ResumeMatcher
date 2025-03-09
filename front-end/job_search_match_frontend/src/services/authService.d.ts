import { AuthResponse, LoginCredentials, RegisterData, User } from "@/types";
export declare const authService: {
    login(credentials: LoginCredentials): Promise<AuthResponse>;
    register(userData: RegisterData): Promise<{
        userId: string;
        message: string;
    }>;
    refreshToken(refreshToken: string): Promise<AuthResponse>;
    getCurrentUser(): Promise<User>;
    logout(): void;
    isAuthenticated(): boolean;
};
