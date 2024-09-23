import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import GenerateImage from './components/GenerateImage';
import { Model, User } from './types';
import { useAuth } from './hooks/useAuth';
import { Button } from './components/ui/button';

function App() {
    const { user, logout, isLoading } = useAuth();
    const [models, setModels] = useState<Model[]>([]);

    useEffect(() => {
        const fetchModels = async () => {
            if (user) {
                try {
                    const token = localStorage.getItem('token');
                    const response = await fetch('http://localhost:5000/api/data', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    if (response.ok) {
                        const data = await response.json();
                        setModels(data);
                    } else if (response.status === 401) {
                        console.error('Unauthorized access when fetching models');
                        // Don't logout here, just log the error
                    }
                } catch (error) {
                    console.error('Error fetching models:', error);
                }
            }
        };

        fetchModels();
    }, [user]);

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <Router>
            <div className="App">
                <header className="App-header">
                    <h1 className="text-3xl font-bold mb-4">Flask and React Integration</h1>
                    <Routes>
                        <Route path="/" element={
                            !user ? (
                                <Navigate to="/login" />
                            ) : (
                                <>
                                    <div className="flex justify-between items-center mb-4">
                                        <p>Welcome, {user.username}!</p>
                                        <Button 
                                            onClick={logout}
                                            variant="destructive"
                                        >
                                            Logout
                                        </Button>
                                        
                                    </div>
                                    {models.length > 0 ? (
                                        <ul className="space-y-4">
                                            {models.map(model => (
                                                <li key={model.id} className="bg-white shadow rounded p-4">
                                                    <h2 className="text-xl font-semibold">{model.name}</h2>
                                                    <p className="text-gray-600">{model.description}</p>
                                                    <p className="text-sm">Version: {model.model_version}</p>
                                                    <p className="text-sm">Status: {model.status}</p>
                                                    {model.model_version && (
                                                        <Link 
                                                            to={`/generate/${model.id}`}
                                                            className="mt-2 inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                                                        >
                                                            Generate Image
                                                        </Link>
                                                    )}
                                                </li>
                                            ))}
                                        </ul>
                                    ) : (
                                        <p>No models available.</p>
                                    )}
                                </>
                            )
                        } />
                        <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />
                        <Route path="/generate/:modelId" element={
                            user ? (
                                <GenerateImage 
                                    user={user} 
                                    models={models} 
                                    onLogout={logout}  // Add this line
                                />
                            ) : (
                                <Navigate to="/login" />
                            )
                        } />
                    </Routes>
                </header>
            </div>
        </Router>
    );
}

export default App;
