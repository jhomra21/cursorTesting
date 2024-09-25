import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Login from './components/Login';
import GenerateImage from './components/GenerateImage';
import Register from './components/Register';
import { useAuth } from './hooks/useAuth';
import { Button, buttonVariants } from './components/ui/button';
import { ReloadIcon } from "@radix-ui/react-icons"
import CreateTraining from './components/CreateTraining';
import HomePage from './components/HomePage'; // New component
import ModelsPage from './components/ModelsPage'; // New component
import { Model } from './types';
import { supabase } from './supabaseClient';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
    const { user, logout, isLoading } = useAuth();
    const [models, setModels] = useState<Model[]>([]);

    useEffect(() => {
        const fetchModels = async () => {
            if (user) {
                try {
                    const { data, error } = await supabase
                        .from('models')
                        .select('*')
                        .eq('user_id', user.id);

                    if (error) throw error;
                    setModels(data || []);
                } catch (error) {
                    console.error('Error fetching models:', error);
                    setModels([]);
                }
            }
        };

        fetchModels();
    }, [user]);

    if (isLoading) {
        return <Button disabled>
            <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
            Loading...
        </Button>;
    }

    return (
        <Router>
            <div className="App">
                <header className="App-header">
                    <h1 className="flex justify-center text-3xl font-bold mb-4">Flask-Replicate Image Generation</h1>
                    <h2 className="flex justify-center text-xl mb-4">Generate images with AI</h2>
                    {user && (
                        <nav className="flex justify-between items-center mb-4 mx-4">
                            <div>
                                <Link to="/" className={buttonVariants({ variant: "outline" }) + " m-2"}>Home</Link>
                                <Link to="/models" className={buttonVariants({ variant: "outline" }) + " m-2"}>My Models</Link>
                                <Link to="/create-training" className={buttonVariants({ variant: "outline" }) + " m-2"}>Train Model</Link>
                            </div>
                            <div className="flex items-center">
                                <span className="mr-4 px-3 py-2 bg-gray-100 text-gray-800 rounded-md font-medium">
                                    {user.email}
                                </span>
                                <Button onClick={logout} variant="destructive">Logout</Button>
                            </div>
                        </nav>
                    )}
                    <Routes>
                        <Route path="/" element={<HomePage user={user} />} />
                        <Route path="/models" element={
                            <ProtectedRoute>
                                <ModelsPage user={user!} />
                            </ProtectedRoute>
                        } />
                        <Route path="/login" element={<Login />} />
                        <Route path="/generate/:modelId" element={
                            <ProtectedRoute>
                                <GenerateImage
                                    user={user!}
                                    models={models}
                                    onLogout={logout}
                                />
                            </ProtectedRoute>
                        } />
                        <Route path="/register" element={<Register />} />
                        <Route path="/create-training" element={
                            <ProtectedRoute>
                                <CreateTraining />
                            </ProtectedRoute>
                        } />
                    </Routes>
                </header>
            </div>
        </Router>
    );
}

export default App;
