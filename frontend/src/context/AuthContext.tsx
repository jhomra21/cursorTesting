import React, { createContext, useState, useEffect } from 'react';
import { User } from '../types';
import { createClient, SupabaseClient, Session, User as SupabaseUser } from '@supabase/supabase-js';

// Initialize Supabase client
const supabase: SupabaseClient = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (email: string, password: string) => Promise<{ user: User | null; error: Error | null }>;
    logout: () => Promise<void>;
    isLoading: boolean;
    models: any[]; // Add proper type if available
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [models, setModels] = useState<any[]>([]);

    useEffect(() => {
        const initializeAuth = async () => {
            // Check for existing session
            const { data: { session } } = await supabase.auth.getSession();
            updateSessionState(session);

            // Listen for auth changes
            const { data: { subscription } } = supabase.auth.onAuthStateChange(
                async (event, session) => {
                    updateSessionState(session);
                }
            );

            return () => {
                subscription.unsubscribe();
            };
        };

        initializeAuth();
    }, []);

    const updateSessionState = (session: Session | null) => {
        setUser(convertSupabaseUser(session?.user ?? null));
        setToken(session?.access_token ?? null);
        setIsLoading(false);
    };

    const convertSupabaseUser = (supabaseUser: SupabaseUser | null): User | null => {
        if (!supabaseUser) return null;
        return {
            id: supabaseUser.id,
            email: supabaseUser.email ?? '',
            // Add other necessary fields from your User type
        };
    };

    const login = async (email: string, password: string) => {
        try {
            const { data, error } = await supabase.auth.signInWithPassword({ email, password });
            if (error) throw error;
            return { user: convertSupabaseUser(data.user), error: null };
        } catch (error) {
            console.error('Login error:', error);
            return { user: null, error: error as Error };
        }
    };

    const logout = async () => {
        await supabase.auth.signOut();
        setUser(null);
        setToken(null);
        setModels([]);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isLoading, models }}>
            {children}
        </AuthContext.Provider>
    );
};