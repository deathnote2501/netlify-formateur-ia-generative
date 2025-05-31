<script lang="ts">
  import { goto } from '$app/navigation';
  import { fetchCurrentUser } from '$lib/stores/authStore'; // To potentially update auth state after registration
  import { base } from '$app/paths';

  let email = '';
  let password = '';
  let passwordConfirm = ''; // For password confirmation field
  let errorMessage: string | null = null;
  let successMessage: string | null = null;
  let isLoading = false;

  // Base URL for API calls - adjust if your setup is different
  const API_BASE_URL = ''; // Assuming same origin or proxy

  async function handleRegister() {
    errorMessage = null;
    successMessage = null;

    if (password !== passwordConfirm) {
      errorMessage = 'Passwords do not match.';
      return;
    }
    if (!email || !password) {
      errorMessage = 'Email and password are required.';
      return;
    }

    isLoading = true;
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (response.status === 201) { // Created
        successMessage = 'Registration successful! You can now log in.';
        // Optionally, clear form or redirect
        email = '';
        password = '';
        passwordConfirm = '';
        // await fetchCurrentUser(); // If registration also logs in or to refresh state
        // await goto(`${base}/auth/login`); // Redirect to login
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Registration failed. Please try again.' }));
        errorMessage = errorData.detail || 'An unknown error occurred during registration.';
        if (typeof errorData.detail === 'object' && errorData.detail.length > 0) {
            // Handle FastAPI validation errors which might be an array of objects
            errorMessage = errorData.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join('; ');
        } else if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
      errorMessage = 'Failed to connect to the server. Please try again later.';
    } finally {
      isLoading = false;
    }
  }
</script>

<svelte:head>
  <title>Register - AnimeMate</title>
</svelte:head>

<div class="auth-page-container">
  <div class="auth-form-card">
    <h1>Create Account</h1>

    {#if successMessage}
      <p class="success-message">{successMessage} <a href="{base}/auth/login">Login here</a>.</p>
    {/if}

    {#if errorMessage}
      <p class="error-message">{errorMessage}</p>
    {/if}

    <form on:submit|preventDefault={handleRegister}>
      <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" id="email" bind:value={email} required disabled={isLoading} />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" id="password" bind:value={password} required disabled={isLoading} />
      </div>
      <div class="form-group">
        <label for="passwordConfirm">Confirm Password:</label>
        <input type="password" id="passwordConfirm" bind:value={passwordConfirm} required disabled={isLoading} />
      </div>
      <button type="submit" class="submit-button" disabled={isLoading}>
        {#if isLoading}Registering...{:else}Register{/if}
      </button>
    </form>
    <p class="auth-link">
      Already have an account? <a href="{base}/auth/login">Login here</a>.
    </p>
  </div>
</div>

<style>
  .auth-page-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 70vh; /* Adjust as needed within the layout */
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
    color: #d8000c; /* Red for errors */
    background-color: #ffdddd;
    border: 1px solid #d8000c;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    text-align: center;
  }
  .success-message {
    color: #006400; /* Dark green for success */
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
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
