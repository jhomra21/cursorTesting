import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User } from '../types';  // Make sure to import the User type
import { useAuth } from '../hooks/useAuth';
import { Button, buttonVariants } from './ui/button';
import { Input } from './ui/input';
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Link } from 'react-router-dom';

interface LoginProps {
    setIsAuthenticated: (isAuthenticated: boolean, userData: User) => void;
}

const Login: React.FC<LoginProps> = ({ setIsAuthenticated }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                login({ id: data.user_id, username: data.username }); // Use the login function from useAuth
                navigate('/');
            } else {
                setError('Invalid username or password');
            }
        } catch (error) {
            console.error('Error during login:', error);
            setError('An error occurred during login');
        }
    };

    const handleLogin = async (username: string, password: string) => {
        try {
            const response = await fetch('http://localhost:5000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            // Handle successful login (e.g., redirect, update state, etc.)
        } catch (error) {
            console.error('Login error:', error);
        }
    };

    return (
        <div className="max-w-md mx-auto mt-8">
            <Card>
                <CardHeader>
                    <CardTitle>Login</CardTitle>
                    <CardDescription>Please enter your details.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} >
                        <div className="mb-4">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                                Username
                            </label>
                            <Input
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                id="username"
                                type="text"
                                placeholder="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>
                        <div className="mb-6">
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
                                Password
                            </label>
                            <Input
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                                id="password"
                                type="password"
                                placeholder="******************"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                        
                        <div className="flex justify-end">
                            <Button type="submit" variant="outline" className="hover:bg-gray-900 hover:text-white">Sign In</Button>

                        </div>
                    </form>
                </CardContent>
                <CardFooter>
                    <p className="text-sm text-gray-500">Don't have an account? <Link className={buttonVariants({ variant: "outline" }) + " hover:bg-gray-900 hover:text-white"} to="/register">Register</Link></p>
                </CardFooter>
            </Card>
        </div>
    );
}

export default Login;