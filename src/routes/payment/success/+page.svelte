<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores'; // To access URL query parameters
  import { fetchCurrentUser } from '$lib/stores/authStore'; // To refresh user state
  import { base } from '$app/paths';

  let sessionId: string | null = null;
  let message = "Processing your subscription... please wait.";

  onMount(async () => {
    sessionId = $page.url.searchParams.get('session_id');

    // Refresh user/subscription status.
    // The backend webhook should ideally handle subscription updates,
    // but refreshing client-side state is good practice.
    await fetchCurrentUser(); // This might now also fetch subscription status if authStore was updated

    if (sessionId) {
      message = `Payment successful! Your subscription is being activated. (Session ID: ${sessionId})`;
      // Optionally, you could make another call to your backend here to verify
      // the session_id and get more concrete status if webhooks are delayed.
      // For example:
      // const response = await fetch(`${base}/api/v1/subscriptions/verify-session?session_id=${sessionId}`);
      // const data = await response.json();
      // message = data.message; // Update message based on verification
    } else {
      message = "Payment successful! Your subscription is being activated.";
    }
  });
</script>

<svelte:head>
  <title>Payment Successful - AnimeMate</title>
</svelte:head>

<div class="payment-status-container">
  <h1>Payment Successful!</h1>
  <p>{message}</p>
  <p>Thank you for subscribing to AnimeMate.</p>
  <div class="actions">
    <a href="{base}/chat" class="button-primary">Go to Chat</a>
    <a href="{base}/" class="button-secondary">Back to Homepage</a>
  </div>
</div>

<style>
  .payment-status-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
    min-height: 70vh;
  }
  .payment-status-container h1 {
    color: #28a745; /* Green for success */
    margin-bottom: 1rem;
  }
  .payment-status-container p {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    max-width: 600px;
  }
  .actions {
    margin-top: 2rem;
  }
  .actions a {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    text-decoration: none;
    font-weight: bold;
    margin: 0 0.5rem;
    transition: background-color 0.2s, color 0.2s;
  }
  .button-primary {
    background-color: #007bff;
    color: white;
  }
  .button-primary:hover {
    background-color: #0056b3;
  }
  .button-secondary {
    background-color: #6c757d;
    color: white;
  }
  .button-secondary:hover {
    background-color: #545b62;
  }
</style>
