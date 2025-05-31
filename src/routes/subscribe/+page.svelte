<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation'; // For potential internal navigation if needed
  import { base } from '$app/paths';
  // Import public environment variables for Stripe Price IDs
  import { PUBLIC_STRIPE_PRICE_ID_MONTHLY, PUBLIC_STRIPE_PRICE_ID_YEARLY } from '$env/static/public';

  onMount(() => {
    // console.log("Subscribe page mounted");
    if (!PUBLIC_STRIPE_PRICE_ID_MONTHLY || !PUBLIC_STRIPE_PRICE_ID_YEARLY) {
        console.warn("Stripe Price IDs are not configured in public environment variables.");
        errorMessage = "Subscription options are currently unavailable. Please try again later.";
    }
  });

  let isLoadingMonthly = false;
  let isLoadingYearly = false;
  let errorMessage: string | null = null;

  // Base URL for API calls - assuming same origin or proxy
  const API_BASE_URL = '';

  async function redirectToCheckout(priceKey: 'monthly' | 'yearly') {
    errorMessage = null;
    let targetPriceId: string | undefined;

    if (priceKey === 'monthly') {
      isLoadingMonthly = true;
      targetPriceId = PUBLIC_STRIPE_PRICE_ID_MONTHLY;
    } else if (priceKey === 'yearly') {
      isLoadingYearly = true;
      targetPriceId = PUBLIC_STRIPE_PRICE_ID_YEARLY;
    }

    if (!targetPriceId) {
      errorMessage = `Configuration error: Price ID for ${priceKey} plan is not set.`;
      if (priceKey === 'monthly') isLoadingMonthly = false;
      if (priceKey === 'yearly') isLoadingYearly = false;
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // If using Bearer token auth, an Authorization header would be needed here.
          // For cookie-based auth (fastapi-users default), the browser handles it.
        },
        body: JSON.stringify({ price_id: targetPriceId }), // Backend expects price_id
      });

      if (response.ok) {
        const data = await response.json(); // Expects { checkout_url: "..." }
        if (data.checkout_url) {
          window.location.href = data.checkout_url; // Redirect to Stripe
        } else {
          errorMessage = 'Failed to retrieve checkout URL. Please try again.';
        }
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to create checkout session.' }));
        if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
        } else if (typeof errorData.detail === 'object' && errorData.detail.length > 0) { // FastAPI validation errors
            errorMessage = errorData.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join('; ');
        } else {
            errorMessage = `Error: ${response.status} - ${response.statusText || 'Could not create checkout session.'}`;
        }
      }
    } catch (error) {
      console.error('Checkout redirection error:', error);
      errorMessage = 'Failed to connect to the server for checkout. Please try again later.';
    } finally {
      if (priceKey === 'monthly') isLoadingMonthly = false;
      if (priceKey === 'yearly') isLoadingYearly = false;
    }
  }
</script>

<svelte:head>
  <title>Subscribe - AnimeMate</title>
</svelte:head>

<div class="subscribe-page-container">
  <h1>Choose Your Subscription Plan</h1>

  {#if errorMessage}
    <p class="error-message">{errorMessage}</p>
  {/if}

  <div class="plans-container">
    <div class="plan-card">
      <h2>Monthly Plan</h2>
      <p class="plan-price">$9.99<span class="price-period">/month</span></p>
      <ul class="plan-features">
        <li>Feature A</li>
        <li>Feature B</li>
        <li>Community Access</li>
      </ul>
      <button
        class="subscribe-button"
        on:click={() => redirectToCheckout('monthly')}
        disabled={isLoadingMonthly || isLoadingYearly}
      >
        {#if isLoadingMonthly}Processing...{:else}Choose Monthly{/if}
      </button>
    </div>

    <div class="plan-card recommended">
      <div class="recommended-badge">Recommended</div>
      <h2>Yearly Plan</h2>
      <p class="plan-price">$99.99<span class="price-period">/year</span></p>
      <p class="plan-savings">Save $19.89 compared to monthly!</p>
      <ul class="plan-features">
        <li>All Monthly Features</li>
        <li>Early Access to New Content</li>
        <li>Exclusive Badge</li>
      </ul>
      <button
        class="subscribe-button"
        on:click={() => redirectToCheckout('yearly')}
        disabled={isLoadingMonthly || isLoadingYearly}
      >
        {#if isLoadingYearly}Processing...{:else}Choose Yearly{/if}
      </button>
    </div>
  </div>
</div>

<style>
  /* Styles from previous step remain */
  .subscribe-page-container {
    padding: 2rem;
    text-align: center;
    max-width: 900px;
    margin: 2rem auto;
  }

  .subscribe-page-container h1 {
    margin-bottom: 2rem;
    color: #333;
  }

  .plans-container {
    display: flex;
    flex-wrap: wrap; /* Allow wrapping on smaller screens */
    justify-content: center;
    gap: 2rem;
  }

  .plan-card {
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 2rem;
    width: 300px; /* Fixed width for plan cards */
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    text-align: left;
    display: flex;
    flex-direction: column;
    position: relative; /* For recommended badge */
  }

  .plan-card.recommended {
    border-color: #007bff;
    border-width: 2px;
  }

  .recommended-badge {
    position: absolute;
    top: -15px; /* Position above the card */
    left: 50%;
    transform: translateX(-50%);
    background-color: #007bff;
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
  }

  .plan-card h2 {
    color: #007bff;
    margin-top: 0; /* Adjust if badge is present */
    margin-bottom: 1rem;
    text-align: center;
  }

  .plan-card.recommended h2 {
    margin-top: 1rem; /* Space for badge */
  }


  .plan-price {
    font-size: 2rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 0.5rem;
    text-align: center;
  }

  .price-period {
    font-size: 1rem;
    color: #777;
    font-weight: normal;
  }

  .plan-savings {
    text-align: center;
    color: #28a745; /* Green for savings */
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }

  .plan-features {
    list-style: none;
    padding: 0;
    margin-bottom: 1.5rem;
    flex-grow: 1; /* Push button to bottom */
  }

  .plan-features li {
    margin-bottom: 0.5rem;
    color: #555;
    position: relative;
    padding-left: 20px; /* Space for pseudo-element checkmark */
  }

  .plan-features li::before {
    content: '✔'; /* Checkmark */
    color: #28a745; /* Green checkmark */
    position: absolute;
    left: 0;
  }

  .subscribe-button {
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
    margin-top: auto; /* Stick to bottom if card flexes */
  }

  .subscribe-button:hover {
    background-color: #0056b3;
  }

  .subscribe-button:disabled {
    background-color: #aaa;
    cursor: not-allowed;
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
</style>
