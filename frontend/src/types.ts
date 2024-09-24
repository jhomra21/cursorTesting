export interface User {
    id: number;
    username: string;
}

export interface Model {
    id: number;
    user_id: number;
    name: string;
    description: string;
    created_at: string;
    updated_at: string;
    model_version: string;
    status: string;
}