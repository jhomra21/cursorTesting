import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { User, Model } from '../types';
import { Button, buttonVariants } from './ui/button';
import { Input } from './ui/input';
import { Slider } from './ui/slider';
import { DownloadIcon, ReloadIcon } from '@radix-ui/react-icons';
import { Link } from 'react-router-dom';


export default function CreateTraining() {
    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-2xl font-bold">Create Training</h1>
            <Link to="/" className={buttonVariants({ variant: "outline" }) + " m-2 hover:bg-gray-900 hover:text-white"}>Back</Link>
        </div>
    )
}