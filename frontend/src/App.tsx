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
import { AnimatedGroup } from './components/core/animatedGroup';
import { supabase } from './supabaseClient';

function App() {
    const { user, logout, isLoading } = useAuth();
    const [models, setModels] = useState<Model[] | null>(null);

    useEffect(() => {
        const fetchModels = async () => {
            if (user) {
                try {
                    // Convert UUID to string and use it in the query
                    const { data, error } = await supabase
                        .from('models')
                        .select('*')
                        .eq('user_id', user.id);

                    if (error) throw error;
                    setModels(data);
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
                    <Routes>
                        <Route path="/" element={
                            !user ? (
                                <Navigate to="/login" />
                            ) : (
                                <>
                                    <div className="flex justify-between items-center mb-4">
                                        <p>Welcome, {user.email}!</p>
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
                                        <AnimatedGroup preset="blur" className=" m-2 grid grid-flow-row grid-cols-1">
                                        <Button disabled>
                                            <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                                            Models are loading...
                                        </Button>
                                        </AnimatedGroup>
                                    ) : models.length > 0 ? (
                                        <Card className="m-2">
                                            <AnimatedGroup preset="blur-slide" className="space-y-4 m-4 grid grid-flow-row grid-cols-1">


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

                                            </AnimatedGroup>
                                        </Card>
                                    ) : (
                                        <AnimatedGroup preset="blur" className=" m-2 grid grid-flow-row grid-cols-1">
                                            <Button disabled>
                                                No Models Found
                                            </Button>
                                        </AnimatedGroup>
                                    )}
                                </>
                            )
                        } />
                        <Route path="/login" element={
                            !user ? (
                                <Login />
                            ) : (
                                <Navigate to="/" />
                            )
                        } />
                        <Route path="/generate/:modelId" element={
                            user ? (
                                <GenerateImage
                                    user={user}
                                    models={models || []}
                                    onLogout={logout}
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
