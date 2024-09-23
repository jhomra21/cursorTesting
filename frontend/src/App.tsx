import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import Login from './components/Login';
import GenerateImage from './components/GenerateImage';
import { User, Model } from './types';

function App() {
    const [models, setModels] = useState<Model[]>([]);
    const [user, setUser] = useState<User | null>(null);

    const login = async (username: string, password: string) => {
        try {
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json();
            if (response.ok) {
                setUser({
                    user_id: data.user_id,
                    username: data.username,
                    models: data.models
                });
                setModels(data.models);
            } else {
                console.error(data.error);
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    };

    const logout = () => {
        setUser(null);
        setModels([]);
        localStorage.removeItem('token');
        // You might want to call your backend to invalidate the session
        fetch('http://localhost:5000/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
    };

    useEffect(() => {
        const fetchModels = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/data', {
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        // Include any other headers you might need
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    setModels(data);
                } else if (response.status === 401) {
                    // User is not authenticated, clear the user state
                    setUser(null);
                }
            } catch (error) {
                console.error('Error fetching models:', error);
            }
        };

        if (user) {
            fetchModels();
        }
    }, [user]);

    return (
        <Router>
            <div className="App">
                <header className="App-header">
                    <h1 className="text-3xl font-bold mb-4">Flask and React Integration</h1>
                    <Routes>
                        <Route path="/" element={
                            !user ? (
                                <Login onLogin={login} />
                            ) : (
                                <>
                                    <div className="flex justify-between items-center mb-4">
                                        <p>Welcome, {user.username}!</p>
                                        <button
                                            onClick={logout}
                                            className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                                        >
                                            Logout
                                        </button>
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
                        <Route path="/generate/:modelId" element={
                            user ? <GenerateImage user={user} models={models} onLogout={logout} /> : <Navigate to="/" />
                        } />
                    </Routes>
                </header>
            </div>
        </Router>
    );
}

export default App;
