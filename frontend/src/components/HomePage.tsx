import React from 'react';
import { buttonVariants } from './ui/button';
import { Link } from 'react-router-dom';
import { User } from '../types';

interface HomePageProps {
    user: User | null;
}

const HomePage: React.FC<HomePageProps> = ({ user }) => {
    return (
        <div className="max-w-4xl mx-auto px-4 py-8 bg-white text-gray-800">
            {user ? (
                <div className="text-center">
                    <p className="text-xl mb-4">You're logged in.</p>
                </div>
            ) : (
                <div className="text-center">
                    <p className="text-xl mb-4">Login to get started</p>
                    <Link to="/login" className={buttonVariants({ variant: "outline" }) + " m-2 text-lg"}>Login</Link>
                    <Link to="/register" className={buttonVariants({ variant: "outline" }) + " m-2 text-lg"}>Register</Link>
                </div>
            )}
        </div>
    );
};

export default HomePage;