<script lang="ts">
  import { onMount } from 'svelte';
  import { currentUser, isAuthenticated, fetchCurrentUser, logoutUser, authLoading } from '$lib/stores/authStore';
  import { navigating } from '$app/stores'; // To potentially re-fetch user on navigation if needed
  import { base } from '$app/paths'; // For base path prefixing if deployed to a subpath

  onMount(async () => {
    // Initial fetch of current user state when the layout mounts
    await fetchCurrentUser();
  });

  // Optional: Re-check user status on navigation end if not currently navigating and not authenticated.
  // This can be useful if a cookie might have changed status in another tab, or expired.
  // However, it can also lead to many requests. Use with caution or a more sophisticated strategy.
  // $: if ($navigating === null && !$isAuthenticated && !$authLoading) {
  //   // console.log("Checking auth status after navigation...");
  //   // fetchCurrentUser(); // Be careful with this, might cause excessive calls.
  // }

  function handleLogout() {
    logoutUser().then(() => {
      // Optional: force a page reload or navigation to ensure UI updates correctly if needed
      // window.location.href = `${base}/auth/login`; // Or use goto
    });
  }
</script>

<div class="app-container">
  <nav class="main-nav">
    <a href="{base}/">Accueil</a> |
    <a href="{base}/chat">Chat</a> |
    {#if $authLoading}
      <span>Loading auth...</span>
    {:else if $isAuthenticated && $currentUser}
      <span class="user-greeting">Bienvenue, {$currentUser.email}!</span> |
      <button on:click={handleLogout} class="logout-button">Déconnexion</button>
    {:else}
      <a href="{base}/auth/login">Connexion</a> |
      <a href="{base}/auth/register">Inscription</a>
    {/if}
  </nav>

  <main class="main-content">
    <slot />
  </main>

  <footer class="app-footer">
    <p>&copy; {new Date().getFullYear()} AnimeMate</p>
  </footer>
</div>

<style>
  .app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    font-family: Arial, sans-serif;
  }

  .main-nav {
    padding: 1rem;
    background-color: #333;
    color: white;
    text-align: center;
  }

  .main-nav a, .main-nav span, .main-nav button {
    color: white;
    margin: 0 0.75rem;
    text-decoration: none;
  }

  .main-nav a:hover {
    text-decoration: underline;
  }

  .main-nav .logout-button {
    background: none;
    border: none;
    color: #ffdddd; /* Light red for logout, stands out a bit */
    cursor: pointer;
    padding: 0;
    font-size: inherit; /* Match link font size */
  }
  .main-nav .logout-button:hover {
    color: #ff8888;
    text-decoration: underline;
  }

  .user-greeting {
    font-weight: bold;
  }

  .main-content {
    flex-grow: 1;
    padding: 1rem;
    max-width: 1200px; /* Max width for content area */
    width: 100%;
    margin: 0 auto; /* Center content */
    box-sizing: border-box;
  }

  .app-footer {
    text-align: center;
    padding: 1rem;
    background-color: #f0f0f0;
    color: #333;
    font-size: 0.9rem;
    border-top: 1px solid #ddd;
  }
</style>
