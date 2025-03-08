import React, { createContext, useReducer, useEffect, ReactNode } from "react";
import { AuthState, LoginCredentials, RegisterData, User } from "@/types";
import { authService } from "@/services/authService";

/**
 * This is the AuthContext component that provides a central place to manage the authentication state and the user's session.
 * All components can access the authentication state and the user's session
 * 1. Check if the user is authenticated
 * 2. Get the current user's information
 * 3. Perform login and logout operations
 */

// Define the shape of our context
export interface AuthContextType {
  state: AuthState;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
}

// Initial state: information about the user's session
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem("token"),
  isAuthenticated: !!localStorage.getItem("token"),
  isLoading: false, // if an authentication request is in progress
  error: null,
};

// Create context
export const AuthContext = createContext<AuthContextType>({
  state: initialState,
  login: async () => {},
  register: async () => {},
  logout: () => {},
});

// Reducer pattern: function that takes the current state and an action, and returns the new state
// Action types
type AuthAction =
  | { type: "AUTH_START" }
  | { type: "AUTH_SUCCESS"; payload: { user: User; token: string } }
  | { type: "AUTH_FAILURE"; payload: string }
  | { type: "AUTH_LOGOUT" };

// Reducer function
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case "AUTH_START":
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case "AUTH_SUCCESS":
      return {
        ...state,
        isLoading: false,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token,
        error: null,
      };
    case "AUTH_FAILURE":
      return {
        ...state,
        isLoading: false,
        isAuthenticated: false,
        user: null,
        error: action.payload,
      };
    case "AUTH_LOGOUT":
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        token: null,
        error: null,
      };
    default:
      return state;
  }
};

// Provider component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  // useReducer: hook that is used to manage the state of the component
  // takes in reducer function and initial state
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check if user is authenticated on mount
  // If the user is authenticated, load the user's information
  // If the user is not authenticated, remove the token and refresh token from local storage
  useEffect(() => {
    const loadUser = async () => {
      if (state.token) {
        try {
          dispatch({ type: "AUTH_START" });
          const user = await authService.getCurrentUser();
          dispatch({
            type: "AUTH_SUCCESS",
            payload: { user, token: state.token as string },
          });
        } catch (error) {
          console.error("Failed to load user:", error);
          localStorage.removeItem("token");
          localStorage.removeItem("refreshToken");
          dispatch({
            type: "AUTH_FAILURE",
            payload: "Session expired. Please login again.",
          });
        }
      }
    };

    loadUser();
  }, [state.token]);

  // Login function
  const login = async (credentials: LoginCredentials) => {
    try {
      dispatch({ type: "AUTH_START" });
      const authResponse = await authService.login(credentials);
      const user = await authService.getCurrentUser();
      dispatch({
        type: "AUTH_SUCCESS",
        payload: { user, token: authResponse.access_token },
      });
    } catch (error) {
      console.error("Login error:", error);
      dispatch({
        type: "AUTH_FAILURE",
        payload: "Invalid email or password",
      });
    }
  };

  // Register function
  const register = async (userData: RegisterData) => {
    try {
      dispatch({ type: "AUTH_START" });
      await authService.register(userData);

      const authResponse = await authService.login({
        email: userData.email,
        password: userData.password,
      });
      const user = await authService.getCurrentUser();
      dispatch({
        type: "AUTH_SUCCESS",
        payload: { user, token: authResponse.access_token },
      });
    } catch (error) {
      console.error("Register error:", error);
      dispatch({
        type: "AUTH_FAILURE",
        payload: "Registration failed. Please try again.",
      });
    }
  };

  // Logout function
  const logout = () => {
    authService.logout();
    dispatch({ type: "AUTH_LOGOUT" });
  };

  return (
    <AuthContext.Provider value={{ state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
