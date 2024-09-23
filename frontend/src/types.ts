export interface User {
    user_id: number;
    username: string;
    models: any[]
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