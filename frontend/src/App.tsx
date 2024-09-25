import React, { useContext, useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import { AuthContext, AuthProvider } from './context/AuthContext';
import Login from './components/Login';
import HomePage from './components/HomePage';
import ModelsPage from './components/ModelsPage';
import CreateTraining from './components/CreateTraining';
import { Toaster } from './components/ui/toaster';
import { User } from './types';
import GenerateImage from './components/GenerateImage';
import Pennies from './components/Pennies';

const App: React.FC = () => {
    return (
        <AuthProvider>
            <Router>
                <Layout>
                    <AppContent />
                </Layout>
            </Router>
            <Toaster />
        </AuthProvider>
    );
};

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const auth = useContext(AuthContext);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsMenuOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    return (
        <div className="min-h-screen flex flex-col">
            <header className="bg-white border-b border-gray-200">
                <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex">
                            <Link to="/" className="flex-shrink-0 flex items-center">
                                <img className="h-8 w-auto" src="/assets/react.svg" alt="Flux.make" />
                            </Link>
                            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                                {/* Desktop menu items */}
                                <Link to="/" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                                    Home
                                </Link>
                                {auth?.user && (
                                    <>
                                        <Link to="/models" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                                            Models
                                        </Link>
                                        <Link to="/create-training" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                                            Create Training
                                        </Link>
                                        <Link to="/pennies" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                                            Pennies
                                        </Link>
                                    </>
                                )}
                            </div>
                        </div>
                        <div className="hidden sm:ml-6 sm:flex sm:items-center">
                            {auth?.user ? (
                                <button onClick={auth.logout} className="ml-8 inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    Logout
                                </button>
                            ) : (
                                <Link to="/login" className="ml-8 inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                    Login
                                </Link>
                            )}
                        </div>
                        <div className="flex items-center sm:hidden">
                            <button
                                onClick={() => setIsMenuOpen(!isMenuOpen)}
                                className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
                            >
                                <span className="sr-only">Open main menu</span>
                                {/* Icon for menu button */}
                                <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </nav>
                {/* Mobile menu */}
                {isMenuOpen && (
                    <div ref={menuRef} className="sm:hidden">
                        <div className="pt-2 pb-3 space-y-1">
                            <Link to="/" className="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
                                Home
                            </Link>
                            {auth?.user && (
                                <>
                                    <Link to="/models" className="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
                                        Models
                                    </Link>
                                    <Link to="/create-training" className="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
                                        Create Training
                                    </Link>
                                    <Link to="/pennies" className="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
                                        Pennies
                                    </Link>
                                </>
                            )}
                            {auth?.user ? (
                                <button onClick={auth.logout} className="block w-full text-left pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-gray-600 hover:bg-gray-50 hover:border-red-600 hover:text-red-600">
                                    Logout
                                </button>
                            ) : (
                                <Link to="/login" className="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
                                    Login
                                </Link>
                            )}
                        </div>
                    </div>
                )}
            </header>
            <main className="flex-grow">
                <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                    {children}
                </div>
            </main>
            <footer className="bg-white border-t border-gray-200">
                <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                    <p className="text-center text-sm text-gray-500">© 2024 juan-testing. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

const AppContent: React.FC = () => {
    const auth = useContext(AuthContext);

    if (!auth) {
        throw new Error("AuthContext is undefined");
    }

    if (auth?.isLoading) {
        return <div>Loading...</div>; // Or a more sophisticated loading component
    }

    return (
        <Routes>
            <Route path="/" element={<HomePage user={auth.user} />} />
            <Route path="/login" element={auth.user ? <Navigate to="/" /> : <Login />} />
            <Route 
                path="/models" 
                element={auth.user ? <ModelsPage user={auth.user} /> : <Navigate to="/login" />}
            />
            <Route 
                path="/create-training" 
                element={auth.user ? <CreateTraining /> : <Navigate to="/login" />}
            />
            <Route 
                path="/generate/:modelId" 
                element={auth.user ? <GenerateImage user={auth.user} onLogout={auth.logout} /> : <Navigate to="/login" />}
            />
            {/* Add the new Pennies route */}
            <Route 
                path="/pennies" 
                element={auth.user ? <Pennies /> : <Navigate to="/login" />}
            />
            {/* Add any other routes here */}
        </Routes>
    );
};

export default App;
