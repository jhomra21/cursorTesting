import React, { useState, useEffect } from 'react';
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

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { login, user } = useAuth();

    useEffect(() => {
        if (user) {
            navigate('/');
        }
    }, [user, navigate]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            await login(email, password);
            // No need to navigate here, the useEffect will handle it
        } catch (error) {
            console.error('Error during login:', error);
            setError('Invalid email or password');
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
                            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
                                Email
                            </label>
                            <Input
                                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                                id="email"
                                type="email"
                                placeholder="Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
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
                        {error && <p className="text-red-500 text-xs italic mb-4">{error}</p>}
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