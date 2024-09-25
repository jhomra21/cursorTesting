export interface User {
    id: string;
    email: string;
    username?: string;
    // ... any other user properties
}

export interface Model {
    id: bigint;
    user_id: string | null; // UUID is represented as a string in TypeScript
    name: string | null;
    description: string | null;
    created_at: string | null; // Assuming you want to work with ISO date strings
    updated_at: string | null; // Assuming you want to work with ISO date strings
    model_version: string | null;
    status: string | null;
}