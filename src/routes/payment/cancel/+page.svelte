<script lang="ts">
  import { base } from '$app/paths';
</script>

<svelte:head>
  <title>Payment Cancelled - AnimeMate</title>
</svelte:head>

<div class="payment-status-container">
  <h1>Payment Cancelled</h1>
  <p>Your payment process was cancelled or encountered an issue.</p>
  <p>Your subscription has not been activated. You can try subscribing again if you wish.</p>
  <div class="actions">
    <a href="{base}/subscribe" class="button-primary">Try Again</a>
    <a href="{base}/" class="button-secondary">Back to Homepage</a>
  </div>
</div>

<style>
  /* Re-using styles from success page for consistency */
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
    color: #dc3545; /* Red for cancellation/error */
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
