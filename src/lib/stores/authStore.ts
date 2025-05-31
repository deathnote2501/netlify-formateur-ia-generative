import { writable, type Writable } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation'; // Kept for logout redirect if re-enabled

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  // Add any other fields from your UserRead schema if customized
}

// Existing stores
export const currentUser: Writable<User | null> = writable(null);
export const isAuthenticated: Writable<boolean> = writable(false);
export const authLoading: Writable<boolean> = writable(false);

// New stores for subscription status
export interface SubscriptionDetails {
    status: string;
    current_period_end: string | null; // ISO date string from backend
    // Add other fields from your SubscriptionStatusResponse if needed
}
export const subscription: Writable<SubscriptionDetails | null> = writable(null);
export const isSubscribedActive: Writable<boolean> = writable(false); // Derived store for easy checking of active status

const API_BASE_URL = '';

export async function fetchCurrentUser() {
  if (!browser) return;
  authLoading.set(true);
  currentUser.set(null); // Reset before fetching
  isAuthenticated.set(false);
  subscription.set(null); // Reset subscription state too
  isSubscribedActive.set(false);

  try {
    const userResponse = await fetch(`${API_BASE_URL}/users/me`);
    if (userResponse.ok) {
      const userData: User = await userResponse.json();
      currentUser.set(userData);
      isAuthenticated.set(true);

      // If authenticated, try to fetch subscription status
      try {
        const subResponse = await fetch(`${API_BASE_URL}/api/v1/subscriptions/subscription-status`);
        if (subResponse.ok) {
          const subData: SubscriptionDetails = await subResponse.json();
          subscription.set(subData);
          // Assuming 'active' is the status for a currently valid subscription
          if (subData.status === 'active') {
            isSubscribedActive.set(true);
          } else {
            isSubscribedActive.set(false);
          }
        } else {
          console.warn("Could not fetch subscription status:", subResponse.statusText);
          subscription.set(null); // Clear if fetch fails or no subscription
          isSubscribedActive.set(false);
        }
      } catch (subError) {
        console.error("Error fetching subscription status:", subError);
        subscription.set(null);
        isSubscribedActive.set(false);
      }

    } else {
      // Handled: currentUser, isAuthenticated, subscription, isSubscribedActive already reset or false
      if (userResponse.status === 401) {
        console.log("Session expired or user not authenticated (fetchCurrentUser).");
      }
    }
  } catch (error) {
    console.error("Error fetching current user:", error);
    // Ensure all states are reset on major error
    currentUser.set(null);
    isAuthenticated.set(false);
    subscription.set(null);
    isSubscribedActive.set(false);
  } finally {
    authLoading.set(false);
  }
}

export async function logoutUser() {
  if (!browser) return;
  authLoading.set(true);
  try {
    await fetch(`${API_BASE_URL}/auth/jwt/logout`, { method: 'POST' });
    // Regardless of response for logout (as cookie is HttpOnly), clear local state
  } catch (error) {
    console.error("Error during logout fetch:", error);
  } finally {
    currentUser.set(null);
    isAuthenticated.set(false);
    subscription.set(null); // Clear subscription state on logout
    isSubscribedActive.set(false);
    authLoading.set(false);
    // Optional: await goto('/auth/login');
  }
}
