import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { authService, User } from '../lib/auth';

export default function Homepage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (!authService.isAuthenticated()) {
          router.push('/login');
          return;
        }

        const userProfile = await authService.getProfile();
        setUser(userProfile);
      } catch (error: any) {
        setError('Failed to load user profile');
        // If token is invalid, redirect to login
        if (error.message.includes('token')) {
          await authService.logout();
          router.push('/login');
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  const handleLogout = async () => {
    try {
      await authService.logout();
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="homepage-container">
        <div className="homepage-card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="loading-spinner" style={{ margin: '0 auto 20px' }}></div>
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="homepage-container">
        <div className="homepage-card">
          <div className="message error">{error}</div>
          <button onClick={handleLogout} className="logout-button">
            Sign Out
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="homepage-container">
      <div className="homepage-card">
        <h1 className="welcome-title">Welcome to Your Dashboard</h1>
        <p className="welcome-subtitle">
          You have successfully logged in to your account
        </p>

        {user && (
          <div className="user-info">
            <h3>Account Information</h3>
            <p><strong>User ID:</strong> {user.user_id}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Member Since:</strong> {new Date(user.created_at).toLocaleDateString()}</p>
          </div>
        )}

        <div style={{ textAlign: 'center' }}>
          <button onClick={handleLogout} className="logout-button">
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}