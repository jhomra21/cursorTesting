'use client'
import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button, buttonVariants } from './ui/button';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "./ui/form"
import { Input } from "./ui/input"
import { Slider } from "./ui/slider"
import { useToast } from "@/hooks/use-toast"
import { Card } from './ui/card';
import JSZip from 'jszip';

const formSchema = z.object({
  steps: z.number().min(100).max(1000),
  triggerWord: z.string().min(1, {
    message: "Trigger word is required.",
  }),
  inputImages: z.instanceof(FileList).refine((files) => files.length > 2, "At least 3 images are required."),
})

const CreateTraining: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      steps: 800,
      triggerWord: "user",
    },
  })

  const compressAndZipImages = async (files: FileList): Promise<Blob> => {
    const zip = new JSZip();
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      // You might want to add image compression here before adding to zip
      zip.file(file.name, file);
    }
    
    return await zip.generateAsync({type: "blob"});
  };

  const onSubmit = async (data: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    setError(null);

    try {
      const compressedZip = await compressAndZipImages(data.inputImages);

      const formData = new FormData();
      formData.append('steps', data.steps.toString());
      formData.append('triggerWord', data.triggerWord);
      formData.append('inputImages', compressedZip, 'images.zip');

      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch('http://localhost:5000/create-training', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const responseData = await response.json();
      console.log(responseData);
      toast({
        title: "Training started...",
        description: "Your training has been successfully started.",
      })
      // Handle successful response (e.g., redirect or update UI)
    } catch (error) {
      if (error instanceof Error) {
        setError('Error creating training: ' + error.message);
      } else {
        setError('An unknown error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className='items-center justify-center mx-auto max-w-xl'>
      <div className="flex flex-col items-center justify-center min-h-full p-4">
        <h2 className="text-2xl font-bold mb-4">Create Training</h2>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 w-full max-w-md">
            <FormField
              control={form.control}
              name="steps"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Steps: </FormLabel> <span className="text-sm text-gray-700 font-bold">{field.value}</span>
                  <FormControl>
                    <Slider
                      min={100}
                      max={1000}
                      step={1}
                      value={[field.value]}
                      onValueChange={(value) => field.onChange(value[0])}
                    />
                  </FormControl>
                  <FormDescription>
                    Number of training steps (100-1000). 
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="triggerWord"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Trigger Word</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter trigger word" {...field} />
                  </FormControl>
                  <FormDescription>
                    Enter a unique word to trigger this style.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="inputImages"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Input Images</FormLabel>
                  <FormControl>
                    <Input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={(e) => field.onChange(e.target.files)}
                    />
                  </FormControl>
                  <FormDescription>
                    Upload one or more input images for training.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Creating...' : 'Create Training'}
            </Button>
          </form>
        </Form>
        {error && <p className="text-red-500 mt-4">{error}</p>}
        <Link to="/" className={buttonVariants({ variant: "outline" }) + " mt-4 hover:bg-gray-900 hover:text-white"}>Back</Link>
      </div>
    </Card>
  )
}

export default CreateTraining;