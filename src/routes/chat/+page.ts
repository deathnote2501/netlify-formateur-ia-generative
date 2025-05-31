import type { PageLoad } from './$types';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { get } from 'svelte/store'; // To read the current value of a store
import { isAuthenticated, fetchCurrentUser, authLoading } from '$lib/stores/authStore';
import { base } from '$app/paths';

export const load: PageLoad = async ({ fetch: svelteKitFetch }) => {
  if (browser) { // Auth checks are client-side for cookie-based auth in SPAs
    // If auth state is currently being loaded, wait for it.
    // This requires authLoading to be reliably set by fetchCurrentUser.
    // A simple busy-wait loop (not ideal for production, but demonstrates concept):
    while (get(authLoading)) {
      await new Promise(resolve => setTimeout(resolve, 50)); // Wait 50ms
    }

    if (!get(isAuthenticated)) {
      // Attempt to fetch current user status if not already authenticated
      // This covers cases where the user directly navigates to /chat
      // or if the authStore wasn't initialized by +layout.svelte yet (less likely but possible)
      // console.log('Chat page load: Not authenticated, attempting to fetch user.');
      await fetchCurrentUser(); // fetchCurrentUser updates isAuthenticated internally
    }

    // After attempting to fetch, check isAuthenticated again
    if (!get(isAuthenticated)) {
      // console.log('Chat page load: Still not authenticated, redirecting to login.');
      await goto(`${base}/auth/login`);
      // While goto should navigate, returning a redirect is more robust for `load`
      // However, for client-side `load` with `goto`, an empty object might be fine
      // as `goto` handles the navigation. Let's stick to SvelteKit patterns for `load` if possible,
      // but client-side `goto` is often sufficient.
      // For SPA redirects after client-side checks, `goto` is the primary mechanism.
      // The `return { status: 302, redirect: ... }` is more for server-side `load`.
      // Let's ensure this runs and completes navigation before page attempts to render.
    }
  }
  return {}; // Return empty props, page will render if not redirected
};
