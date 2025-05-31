import { writable, type Writable } from 'svelte/store';
import { browser } from '$app/environment'; // To ensure fetch only runs client-side if needed for certain calls
import { goto } from '$app/navigation'; // For optional redirection on logout

// User interface based on fastapi-users UserRead schema (integer ID)
export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  // Add any other fields from your UserRead schema if customized
}

export const currentUser: Writable<User | null> = writable(null);
export const isAuthenticated: Writable<boolean> = writable(false);
// Optional: For more granular UI updates during auth operations
export const authLoading: Writable<boolean> = writable(false);

// Base URL for API calls - adjust if your setup is different
// If SvelteKit's dev server proxies, relative paths are fine.
// Otherwise, use full backend URL e.g., 'http://localhost:8000'
const API_BASE_URL = ''; // Assuming same origin or proxy

export async function fetchCurrentUser() {
  if (!browser) return; // fetchCurrentUser should primarily run on client

  authLoading.set(true);
  try {
    const response = await fetch(`${API_BASE_URL}/users/me`);
    if (response.ok) {
      const userData: User = await response.json();
      currentUser.set(userData);
      isAuthenticated.set(true);
    } else {
      currentUser.set(null);
      isAuthenticated.set(false);
      if (response.status === 401) {
        // Unauthorized, e.g. cookie expired or invalid
        console.log("Session expired or user not authenticated.");
      }
    }
  } catch (error) {
    console.error("Error fetching current user:", error);
    currentUser.set(null);
    isAuthenticated.set(false);
  } finally {
    authLoading.set(false);
  }
}

export async function logoutUser() {
  if (!browser) return;

  authLoading.set(true);
  try {
    const response = await fetch(`${API_BASE_URL}/auth/jwt/logout`, { method: 'POST' });
    // fastapi-users logout returns 200 OK on success, or 401 if not authenticated
    if (response.ok || response.status === 401) {
      currentUser.set(null);
      isAuthenticated.set(false);
      console.log("Logout successful or user was already logged out.");
      // Optional: Redirect to login page
      // await goto('/auth/login');
    } else {
      // Handle unexpected errors from logout endpoint
      console.error("Logout failed with status:", response.status, response.statusText);
      // Potentially still clear local state as a best effort
      currentUser.set(null);
      isAuthenticated.set(false);
    }
  } catch (error) {
    console.error("Error during logout:", error);
    // Potentially still clear local state
    currentUser.set(null);
    isAuthenticated.set(false);
  } finally {
    authLoading.set(false);
  }
}
