<script lang="ts">
  import { goto } from '$app/navigation';
  import { fetchCurrentUser, isAuthenticated } from '$lib/stores/authStore'; // Using isAuthenticated to check if login was needed
  import { base } from '$app/paths';
  import { onMount } from 'svelte';

  let email = ''; // Will be sent as 'username' in FormData
  let password = '';
  let errorMessage: string | null = null;
  let isLoading = false;

  // Base URL for API calls - adjust if your setup is different
  const API_BASE_URL = ''; // Assuming same origin or proxy

  // Redirect if already logged in
  onMount(() => {
    const unsubscribe = isAuthenticated.subscribe(value => {
      if (value === true) {
        // console.log('Already authenticated, redirecting from login.');
        // Check if this is an initial load or after a re-render
        // setTimeout(() => { // Timeout to prevent immediate redirect before potential initial auth check completes
        //    if ($isAuthenticated) goto(`${base}/chat`); // Or home
        // }, 0);
      }
    });
    // return unsubscribe; // Not strictly needed for a one-time check like this if not re-running onMount
  });


  async function handleLogin() {
    errorMessage = null;
    isLoading = true;

    const formData = new URLSearchParams();
    formData.append('username', email); // fastapi-users expects 'username' by default for login
    formData.append('password', password);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/jwt/login`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      if (response.ok) { // Typically 200 or 204 NO CONTENT for successful login with cookie transport
        await fetchCurrentUser(); // Update the auth state in the store
        // Check isAuthenticated from store, then redirect
        // This relies on fetchCurrentUser correctly setting isAuthenticated
        const unsubscribe = isAuthenticated.subscribe(authStatus => {
            if(authStatus) {
                goto(`${base}/chat`); // Redirect to chat page or dashboard
            } else {
                // This case should ideally not happen if fetchCurrentUser is correct after login
                errorMessage = "Login succeeded but failed to confirm session. Please try again.";
            }
        });
        unsubscribe(); // Unsubscribe immediately after checking

      } else {
        // Try to parse error from backend, default to generic message
        const errorData = await response.json().catch(() => ({ detail: 'Invalid email or password.' }));
         if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
        } else if (typeof errorData.detail === 'object' && errorData.detail.length > 0) {
             errorMessage = errorData.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join('; ');
        }
        else {
            errorMessage = 'Invalid email or password.';
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      errorMessage = 'Failed to connect to the server. Please try again later.';
    } finally {
      isLoading = false;
    }
  }
</script>

<svelte:head>
  <title>Login - AnimeMate</title>
</svelte:head>

<div class="auth-page-container">
  <div class="auth-form-card">
    <h1>Login to Your Account</h1>

    {#if errorMessage}
      <p class="error-message">{errorMessage}</p>
    {/if}

    <form on:submit|preventDefault={handleLogin}>
      <div class="form-group">
        <label for="email">Email (as Username):</label>
        <input type="email" id="email" bind:value={email} required disabled={isLoading} />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" id="password" bind:value={password} required disabled={isLoading} />
      </div>
      <button type="submit" class="submit-button" disabled={isLoading}>
        {#if isLoading}Logging in...{:else}Login{/if}
      </button>
    </form>
    <p class="auth-link">
      Don't have an account? <a href="{base}/auth/register">Register here</a>.
    </p>
  </div>
</div>

<!-- Using the same styles as register page for consistency -->
<style>
  .auth-page-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 70vh;
    padding: 2rem;
  }
  .auth-form-card {
    background-color: #fff;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    width: 100%;
    max-width: 400px;
  }
  .auth-form-card h1 {
    text-align: center;
    margin-bottom: 1.5rem;
    color: #333;
  }
  .form-group {
    margin-bottom: 1rem;
  }
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #555;
    font-weight: bold;
  }
  .form-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
    font-size: 1rem;
  }
  .submit-button {
    width: 100%;
    padding: 0.75rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: bold;
    transition: background-color 0.2s;
  }
  .submit-button:hover {
    background-color: #0056b3;
  }
  .submit-button:disabled {
    background-color: #aaa;
  }
  .error-message {
    color: #d8000c;
    background-color: #ffdddd;
    border: 1px solid #d8000c;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    text-align: center;
  }
  .auth-link {
    text-align: center;
    margin-top: 1rem;
  }
  .auth-link a {
    color: #007bff;
    text-decoration: none;
  }
  .auth-link a:hover {
    text-decoration: underline;
  }
</style>
