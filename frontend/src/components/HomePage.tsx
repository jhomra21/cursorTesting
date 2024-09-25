import React from 'react';
import { User } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface HomePageProps {
    user: User | null;
}

const HomePage: React.FC<HomePageProps> = ({ user }) => {
    return (
        <div>
            <Card>
                <CardHeader>
                    {/* style the title to be centered to have the same color as login button background */}
                    <CardTitle className="text-indigo-600">Welcome {user ? user.email : "!"}</CardTitle>
                </CardHeader>
                <CardContent>
                    <p>This is the home page content.</p>
                </CardContent>
            </Card>
            
        </div>
    );
};

export default HomePage;