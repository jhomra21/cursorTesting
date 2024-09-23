import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { User, Model } from '../types';

interface GenerateImageProps {
    user: User | null;
    models: Model[];
    onLogout: () => void;
}

const GenerateImage: React.FC<GenerateImageProps> = ({ user, models, onLogout }) => {
    const [prompt, setPrompt] = useState('');
    const [imageUrl, setImageUrl] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { modelId } = useParams<{ modelId: string }>();
    const navigate = useNavigate();

    const model = models.find(m => m.id.toString() === modelId);

    useEffect(() => {
        if (!user) {
            navigate('/');
        }
    }, [user, navigate]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:5000/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ prompt, modelId }),
            });

            if (!response.ok) {
                throw new Error('Failed to generate image');
            }

            const data = await response.json();
            setImageUrl(data.image_url);
        } catch (error) {
            console.error('Error generating image:', error);
            // Set an error state or show an error message to the user
        } finally {
            setIsLoading(false);
        }
    };

    const handleBackToModels = () => {
        navigate('/');
    };

    return (
        <div className="max-w-md mx-auto mt-8">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Generate Image</h2>
                <div>
                    <button
                        onClick={handleBackToModels}
                        className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline mr-2"
                    >
                        Back to Models
                    </button>
                    <button
                        onClick={onLogout}
                        className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    >
                        Logout
                    </button>
                </div>
            </div>
            {model && <p className="mb-4">Model: {model.name}</p>}
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="prompt" className="block text-sm font-medium text-gray-700">
                        Prompt
                    </label>
                    <input
                        type="text"
                        id="prompt"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    disabled={isLoading}
                >
                    {isLoading ? 'Generating...' : 'Generate Image'}
                </button>
            </form>
            {imageUrl && (
                <div className="mt-8">
                    <h3 className="text-xl font-bold mb-2">Generated Image:</h3>
                    <img src={imageUrl} alt="Generated" className="w-full rounded-lg shadow-lg" />
                </div>
            )}
        </div>
    );
};

export default GenerateImage;