import React, { useContext } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import { AuthContext, AuthProvider } from './context/AuthContext';
import Login from './components/Login';
import HomePage from './components/HomePage';
import ModelsPage from './components/ModelsPage';
import CreateTraining from './components/CreateTraining';
import { Toaster } from './components/ui/toaster';
import { User } from './types';
import GenerateImage from './components/GenerateImage';

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

    return (
        <div className="min-h-screen flex flex-col">
            <header className="bg-white border-b border-gray-200">
                <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex">
                            <Link to="/" className="flex-shrink-0 flex items-center">
                                {/* update this img to use svg in src/assets/react.svg */}

                                <img className="h-8 w-auto" src="/assets/react.svg" alt="Flux.make" />
                            </Link>
                            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
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
                    </div>
                </nav>
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
            {/* Add any other routes here */}
        </Routes>
    );
};

export default App;
