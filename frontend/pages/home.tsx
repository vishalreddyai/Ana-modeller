import { AppLayout } from '../components/AppLayout';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

export default function HomePage() {
  const [username, setUsername] = useState('User');
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // This effect runs only on the client side
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user');
      
      if (!userData) {
        // If no user data, redirect to login
        router.push('/');
        return;
      }

      try {
        const user = JSON.parse(userData);
        setUsername(user.name || user.email?.split('@')[0] || 'User');
        setUserId(user.id ?? null);
      } catch (error) {
        console.error('Error parsing user data:', error);
        router.push('/');
      } finally {
        setIsLoading(false);
      }
    }
  }, [router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f9fafb',
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <AppLayout username={username} userId={userId} />
  );
}

