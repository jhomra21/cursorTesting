import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://cnmuuxtrfzytjdlwtjxz.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNubXV1eHRyZnp5dGpkbHd0anh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjcxODkzOTIsImV4cCI6MjA0Mjc2NTM5Mn0.olWyzckGbgHarNviGXdjiGtMe9p0g_qXQJ18tk6MMYw'

export const supabase = createClient(supabaseUrl, supabaseKey)