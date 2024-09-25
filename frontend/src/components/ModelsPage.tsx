import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { User, Model } from '../types';
import { supabase } from '../supabaseClient';
import { Button, buttonVariants } from './ui/button';
import { ReloadIcon } from "@radix-ui/react-icons";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./ui/card";
import { AnimatedGroup } from './core/animatedGroup';

interface ModelsPageProps {
    user: User; // Changed from User | null to User
}

const ModelsPage: React.FC<ModelsPageProps> = ({ user }) => {
    const [models, setModels] = useState<Model[] | null>(null);

    useEffect(() => {
        const fetchModels = async () => {
            try {
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
        };

        fetchModels();
    }, [user]);

    return (
        <div className='text-center'>
            <Card className='pb-4'>
                <CardHeader>
                    <CardTitle>{user.email} Models</CardTitle>
                </CardHeader>
            
            {models === null ? (
                <AnimatedGroup preset="blur" className="m-2 grid grid-flow-row grid-cols-1">
                    <Button disabled>
                        <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                        Models are loading...
                    </Button>
                </AnimatedGroup>
            ) : models.length > 0 ? (
                
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
                
            ) : (
                <AnimatedGroup preset="blur" className="m-2 grid grid-flow-row grid-cols-1">
                    <Button disabled>
                        No Models Found
                    </Button>
                </AnimatedGroup>
            )}
            </Card>
        </div>
    );
};

export default ModelsPage;