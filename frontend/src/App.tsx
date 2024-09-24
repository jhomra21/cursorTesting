import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import GenerateImage from './components/GenerateImage';
import Register from './components/Register';
import { Model, User } from './types';
import { useAuth } from './hooks/useAuth';
import { Button, buttonVariants } from './components/ui/button';
import { ReloadIcon } from "@radix-ui/react-icons"
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import CreateTraining from './components/CreateTraining';

function App() {
    const { user, logout, isLoading } = useAuth();
    const [models, setModels] = useState<Model[] | null>(null);

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
                    }
                } catch (error) {
                    console.error('Error fetching models:', error);
                    setModels([]); // Set to empty array if there's an error
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
                                    <div className="flex justify-start">
                                        <Link to="/create-training" className={buttonVariants({ variant: "outline" }) + " m-2 hover:bg-green-800 hover:text-white"}>Train Model</Link>
                                    </div>

                                    {models === null ? (
                                        <Button disabled>
                                            <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                                            Modules are loading...
                                        </Button>
                                    ) : models.length > 0 ? (
                                        <Card className="space-y-4 m-2 p-4">

                                            {models.map(model => (
                                                <Card key={model.id} className="bg-white shadow rounded p-4">
                                                    <CardHeader>
                                                        <CardTitle>{model.name}</CardTitle>
                                                        <CardDescription>{model.description}</CardDescription>
                                                    </CardHeader>
                                                    <CardContent>
                                                        <p>Version: {model.model_version}</p>
                                                        <p>Status: {model.status}</p>
                                                    </CardContent>
                                                    {model.model_version && (
                                                        <CardFooter>
                                                            <Link
                                                                to={`/generate/${model.id}`}
                                                                className={buttonVariants({ variant: "outline" }) + " hover:bg-blue-700 hover:text-white font-bold py-2 px-4 rounded"}
                                                            >
                                                                Generate Image
                                                            </Link>
                                                        </CardFooter>
                                                    )}
                                                </Card>
                                            ))}

                                        </Card>
                                    ) : (
                                        <Button disabled>
                                            No Modules Found
                                        </Button>
                                    )}
                                </>
                            )
                        } />
                        <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />
                        <Route path="/generate/:modelId" element={
                            user ? (
                                <GenerateImage
                                    user={user}
                                    models={models || []}
                                    onLogout={logout}  // Add this line
                                />
                            ) : (
                                <Navigate to="/login" />
                            )
                        } />
                        <Route path="/register" element={!user ? <Register /> : <Navigate to="/" />} />
                        <Route path="/create-training" element={user ? <CreateTraining /> : <Navigate to="/login" />} />
                    </Routes>
                </header>
            </div>
        </Router>
    );
}

export default App;
