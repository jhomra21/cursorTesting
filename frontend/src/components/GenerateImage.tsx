import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { User, Model } from '../types';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Slider } from './ui/slider';
import { DownloadIcon, ReloadIcon } from '@radix-ui/react-icons';
import { AnimatedGroup } from './core/animatedGroup';
import { AuthContext } from '../context/AuthContext';
import { supabase } from '../supabaseClient';

interface GenerateImageProps {
    user: User;
    onLogout: () => void;
}

const GenerateImage: React.FC<GenerateImageProps> = ({ user, onLogout }) => {
    const auth = useContext(AuthContext);
    const [prompt, setPrompt] = useState('');
    const [imageUrl, setImageUrl] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [loraScale, setLoraScale] = useState(0.8);
    const [guidanceScale, setGuidanceScale] = useState(3.5);
    const [inferenceSteps, setInferenceSteps] = useState(22);
    const [model, setModel] = useState<Model | null>(null);
    const { modelId } = useParams<{ modelId: string }>();
    const navigate = useNavigate();

    useEffect(() => {
        if (!user) {
            navigate('/');
        }
    }, [user, navigate]);

    useEffect(() => {
        const fetchModel = async () => {
            if (!modelId) return;

            try {
                const { data, error } = await supabase
                    .from('models')
                    .select('*')
                    .eq('id', modelId)
                    .single();

                if (error) throw error;
                setModel(data);
            } catch (error) {
                console.error('Error fetching model:', error);
                navigate('/models');
            }
        };

        fetchModel();
    }, [modelId, navigate]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        if (!model) {
            console.error('Model not found');
            setIsLoading(false);
            return;
        }

        try {
            const response = await fetch('http://localhost:5000/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${auth?.token}`
                },
                body: JSON.stringify({ 
                    model_id: model.id, // Ensure this is correct
                    prompt: prompt,
                    lora_scale: loraScale,
                    guidance_scale: guidanceScale,
                    num_inference_steps: inferenceSteps
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Server response:', errorData);
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
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
        navigate('/models');
    };

    const handleDownload = async () => {
        try {
            const response = await fetch(imageUrl);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'generated-image.png';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error downloading image:', error);
        }
    };

    return (
        <div className="max-w-md mx-auto mt-8 relative">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Generate Image</h2>
                <div>
                    <Button
                        onClick={handleBackToModels}
                        variant="outline"
                        className="mr-2 hover:bg-gray-900 hover:text-white"
                    >
                        Back to Models
                    </Button>
                    <Button
                        onClick={onLogout}
                        variant="outline"
                        className="hover:bg-red-500 hover:text-white"
                    >
                        Logout
                    </Button>
                </div>
            </div>
            {model && <p className="mb-4">Model: {model.name}</p>}
            <form onSubmit={handleSubmit} className={`space-y-4 ${isLoading ? 'opacity-50 pointer-events-none' : ''}`}>
                <div>
                    <label htmlFor="prompt" className="block text-sm font-medium text-gray-700">
                        Prompt
                    </label>
                    <Input
                        type="text"
                        id="prompt"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        className="mt-1 block w-full"
                        required
                    />
                </div>
                <div>
                    <label htmlFor="loraScale" className="block text-sm font-medium text-gray-700">
                        Lora Scale: {loraScale}
                    </label>
                    <Slider
                        id="loraScale"
                        min={0}
                        max={1}
                        step={0.1}
                        value={[loraScale]}
                        onValueChange={(value) => setLoraScale(value[0])}
                    />
                </div>
                <div>
                    <label htmlFor="guidanceScale" className="block text-sm font-medium text-gray-700">
                        Guidance Scale: {guidanceScale}
                    </label>
                    <Slider
                        id="guidanceScale"
                        min={1}
                        max={10}
                        step={0.1}
                        value={[guidanceScale]}
                        onValueChange={(value) => setGuidanceScale(value[0])}
                    />
                </div>
                <div>
                    <label htmlFor="inferenceSteps" className="block text-sm font-medium text-gray-700">
                        Inference Steps: {inferenceSteps}
                    </label>
                    <Slider
                        id="inferenceSteps"
                        min={10}
                        max={38}
                        step={1}
                        value={[inferenceSteps]}
                        onValueChange={(value) => setInferenceSteps(value[0])}
                    />
                </div>
                <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full"
                >
                    Generate Image
                </Button>
            </form>
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
                    <ReloadIcon className="h-8 w-8 animate-spin text-gray-700" />
                    <span className="ml-2 text-lg font-semibold text-gray-700">Generating...</span>
                </div>
            )}
            {imageUrl && (
                <AnimatedGroup preset="blur">
                <div className="mt-8 relative group">
                    <h3 className="text-xl font-bold mb-2">Generated Image:</h3>
                    <div className="relative">
                        <img src={imageUrl} alt="Generated" className="w-full rounded-lg shadow-lg" />
                        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            <Button
                                onClick={handleDownload}
                                variant="secondary"
                                className="bg-white bg-opacity-75 hover:bg-opacity-100"
                            >
                                <DownloadIcon className="mr-2 h-4 w-4" />
                                Download
                            </Button>
                        </div>
                    </div>
                </div></AnimatedGroup>
            )}
        </div>
    );
};

export default GenerateImage;