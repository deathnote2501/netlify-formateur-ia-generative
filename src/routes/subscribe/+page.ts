import type { PageLoad } from './$types';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { get } from 'svelte/store';
import { isAuthenticated, fetchCurrentUser, authLoading } from '$lib/stores/authStore';
import { base } from '$app/paths';

export const load: PageLoad = async ({ fetch: svelteKitFetch }) => {
  if (browser) { // Auth checks are client-side for cookie-based auth in SPAs
    // Wait for any ongoing auth check to complete (e.g., from layout load)
    while (get(authLoading)) {
      await new Promise(resolve => setTimeout(resolve, 50)); // Wait 50ms
    }

    if (!get(isAuthenticated)) {
      // Attempt to fetch current user status if not already authenticated
      // console.log('Subscribe page load: Not authenticated, attempting to fetch user.');
      await fetchCurrentUser();
    }

    // After attempting to fetch, check isAuthenticated again
    if (!get(isAuthenticated)) {
      // console.log('Subscribe page load: Still not authenticated, redirecting to login.');
      await goto(`${base}/auth/login`);
    }
  }
  return {}; // Return empty props, page will render if not redirected
};
