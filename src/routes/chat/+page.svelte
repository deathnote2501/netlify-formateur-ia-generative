<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';

  type Message = {
    text: string;
    from: 'user' | 'ia' | 'system' | 'error';
    personaName?: string;
    timestamp: Date;
  };

  let messages: Message[] = [];
  let currentUserMessage: string = '';
  const currentPersonaId: number = 1;
  let isLoading: boolean = false;
  let messagesAreaElement: HTMLDivElement;

  afterUpdate(() => {
    if (messagesAreaElement) {
      messagesAreaElement.scrollTop = messagesAreaElement.scrollHeight;
    }
  });

  onMount(() => {
    messages = [
      { text: "Welcome to the chat! Type your message below and press Enter or click Send. You are chatting with Persona ID " + currentPersonaId , from: 'system', timestamp: new Date() }
    ];
  });

  async function sendMessage(): Promise<void> {
    const trimmedMessage = currentUserMessage.trim();
    if (!trimmedMessage) {
      return;
    }
    messages = [
      ...messages,
      { text: trimmedMessage, from: 'user', timestamp: new Date() },
    ];
    const messageToSend = trimmedMessage;
    currentUserMessage = '';
    isLoading = true;

    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: messageToSend,
          persona_id: currentPersonaId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown server error" }));
        throw new Error(`Server error: ${response.status} ${response.statusText}. ${errorData.detail || ''}`);
      }
      const data = await response.json();
      messages = [
        ...messages,
        { text: data.ia_response, from: 'ia', personaName: data.persona_name, timestamp: new Date() },
      ];
    } catch (error) {
      console.error('Failed to send message:', error);
      let errorMessage = 'Error communicating with the server.';
      if (error instanceof Error) {
          errorMessage = error.message;
      }
      messages = [
        ...messages,
        { text: `Failed to get response: ${errorMessage}`, from: 'error', timestamp: new Date() },
      ];
    } finally {
      isLoading = false;
    }
  }

  function handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }
</script>

<div class="chat-container">
  <header class="chat-header">
    <h1>AnimeMate Chat (Persona ID: {currentPersonaId})</h1>
  </header>

  <div class="messages-area" bind:this={messagesAreaElement}>
    {#each messages as message, i (message.timestamp.getTime() + i)}
      <div class="message {message.from}">
        {#if message.from === 'ia' && message.personaName}
          <span class="persona-name">{message.personaName}</span>
        {/if}
        <p>{message.text}</p>
        <span class="timestamp">{message.timestamp.toLocaleTimeString()}</span>
      </div>
    {:else}
      <p class="system-message">No messages yet. Send one to start the conversation!</p>
    {/each}
  </div>

  <div class="loading-indicator">
    {#if isLoading}
      <p>Thinking...</p>
    {/if}
  </div>

  <footer class="chat-input-area">
    <input
      type="text"
      class="message-input"
      placeholder="Type your message..."
      aria-label="Chat message input"
      bind:value={currentUserMessage}
      on:keydown={handleKeydown}
      disabled={isLoading}
    />
    <button class="send-button" on:click={sendMessage} disabled={isLoading}>
      {#if isLoading}Sending...{:else}Send{/if}
    </button>
  </footer>
</div>

<style>
  .chat-container {
    display: flex;
    flex-direction: column;
    height: 95vh; /* Make chat take most of the screen height */
    max-width: 700px;
    margin: 1rem auto;
    border: 1px solid #ccc;
    border-radius: 8px;
    overflow: hidden;
    font-family: sans-serif;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }

  .chat-header {
    background-color: #f1f1f1;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #ccc;
    text-align: center;
  }

  .chat-header h1 {
    margin: 0.5rem 0;
    font-size: 1.2rem;
  }

  .messages-area {
    flex-grow: 1;
    padding: 1rem;
    overflow-y: auto;
    background-color: #f9f9f9;
    display: flex;
    flex-direction: column;
    gap: 0.75rem; /* Space between messages */
  }

  .message {
    padding: 0.6rem 0.9rem;
    border-radius: 15px;
    max-width: 75%;
    word-wrap: break-word; /* Ensure long words don't overflow */
  }

  .message p {
    margin: 0 0 0.25rem 0; /* Space between text and timestamp */
  }

  .message .timestamp {
    font-size: 0.7rem;
    color: #666;
    display: block; /* Make timestamp appear on its own line or control alignment */
  }

  .message.user {
    background-color: #007bff;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 5px; /* Slightly different shape for user */
  }
  .message.user .timestamp {
    color: #e0e0e0;
    text-align: right;
  }

  .message.ia {
    background-color: #e9e9eb;
    color: black;
    align-self: flex-start;
    border-bottom-left-radius: 5px; /* Slightly different shape for IA */
  }
  .message.ia .timestamp {
    text-align: left;
  }
  .message.ia .persona-name {
    font-weight: bold;
    font-size: 0.8rem;
    color: #333;
    display: block;
    margin-bottom: 0.2rem;
  }

  .message.system, .message.error {
    background-color: #f0f0f0;
    color: #555;
    align-self: center;
    font-style: italic;
    font-size: 0.85rem;
    text-align: center;
    max-width: 90%;
  }
  .message.error {
    background-color: #ffdddd;
    color: #d8000c;
  }
  .message.system .timestamp, .message.error .timestamp {
    text-align: center;
  }


  .loading-indicator {
    text-align: center;
    padding: 0.5rem;
    font-style: italic;
    color: #777;
    height: 2em; /* Reserve space to prevent layout jump */
  }
  .loading-indicator p {
    margin: 0;
  }

  .chat-input-area {
    display: flex;
    padding: 0.75rem;
    border-top: 1px solid #ccc;
    background-color: #f1f1f1;
  }

  .message-input {
    flex-grow: 1;
    padding: 0.75rem;
    border: 1px solid #ccc;
    border-radius: 20px;
    margin-right: 0.5rem;
    font-size: 1rem;
  }

  .send-button {
    padding: 0.75rem 1.25rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.2s;
  }

  .send-button:hover {
    background-color: #0056b3;
  }
  .send-button:disabled {
    background-color: #aaa;
    cursor: not-allowed;
  }
</style>
