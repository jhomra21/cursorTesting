import React from 'react';
import { User } from '../types';
import { Link } from 'react-router-dom';

interface HomePageProps {
    user: User | null;
}

const HomePage: React.FC<HomePageProps> = ({ user }) => {
    return (
        <div>
            <h1>Welcome to Our App</h1>
            {user ? (
                <p>Hello, {user.username || user.email}!</p>
            ) : (
                <p>Please <Link to="/login">log in</Link> to access all features.</p>
            )}
            {/* Rest of your HomePage content */}
        </div>
    );
};

export default HomePage;