<script lang="ts">
  import { onMount } from 'svelte';
  import {
    currentUser, isAuthenticated, fetchCurrentUser, logoutUser, authLoading,
    subscription, isSubscribedActive // Import new subscription stores
  } from '$lib/stores/authStore';
  import { navigating } from '$app/stores';
  import { base } from '$app/paths';

  onMount(async () => {
    await fetchCurrentUser();
  });

  function handleLogout() {
    logoutUser().then(() => {
      // window.location.href = `${base}/auth/login`;
    });
  }

  function formatSubscriptionDate(isoDateString: string | null): string {
    if (!isoDateString) return 'N/A';
    try {
      return new Date(isoDateString).toLocaleDateString();
    } catch (e) {
      return 'Invalid Date';
    }
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
      {#if $isSubscribedActive && $subscription?.current_period_end}
        <span class="subscription-status active">
          Abonné jusqu'au {formatSubscriptionDate($subscription.current_period_end)}
        </span> |
      {:else if $subscription && $subscription.status !== 'active'}
        <span class="subscription-status inactive">
          Abonnement: {$subscription.status}
        </span> |
        <a href="{base}/subscribe">S'abonner</a> |
      {:else}
        <a href="{base}/subscribe">S'abonner</a> |
      {/if}
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
  /* Existing styles from previous step remain */
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

  /* New styles for subscription status */
  .subscription-status {
    font-size: 0.9em;
    padding: 0.2em 0.5em;
    border-radius: 4px;
    margin-right: 0.75rem; /* Consistent with other nav items */
  }
  .subscription-status.active {
    background-color: #28a745; /* Green for active */
    color: white;
  }
  .subscription-status.inactive {
    background-color: #ffc107; /* Yellow for inactive/other statuses */
    color: #333;
  }
</style>
