# AnimeMate

AnimeMate is an innovative web application designed to provide users, especially anime enthusiasts, with an immersive conversational experience with an AI-powered virtual anime character. Users can engage in text-based conversations (with voice interactions planned for the future) and see the character react visually through animated video sequences corresponding to emotions and actions.

## Features

*   **Interactive Chat**: Users can type messages to the AI character.
*   **Visual Responses**: The AI character responds not only with text but also with animated video sequences displaying emotions (joy, sadness, anger, etc.) or actions (waving, nodding, jumping, etc.) relevant to the conversation.
*   **Diverse Personalities**: Users can choose to interact with characters possessing distinct personality archetypes (e.g., Tsundere, Kuudere, Yandere), influencing both text responses and video reactions.
*   **Subscription Model**: The application will feature a subscription system (managed by Stripe) to unlock full access or premium features.
*   **(Future) Customization**: Plans include allowing users to customize aspects of the interaction or character appearance.

## Technical Stack

*   **Frontend**: SvelteKit
    *   Manages the user interface: video display, chat interface, authentication, and subscription pages.
    *   Communicates with the backend via REST APIs.
    *   Dynamically handles playback of character video sequences.
*   **Backend**: Python with FastAPI
    *   Provides API endpoints for chat, authentication, Stripe subscription management, and character/video metadata.
    *   Handles the core AI interaction logic.
*   **Database**: PostgreSQL
    *   Uses SQLModel for ORM and Alembic for migrations.
    *   Stores user information, message history, persona definitions (including system prompts for AI), mapping between emotions/actions and video file paths, and Stripe subscription details.
*   **AI Interaction Logic**:
    *   Receives user messages and conversation history.
    *   Interfaces with a conversational AI (target: Google Gemini) using persona-based system prompts.
    *   The AI is expected to return a text response and a structured "action/emotion key" (e.g., `{"text_response": "...", "requested_emotion_action_key": "happy_smile"}`).
    *   The backend maps this key to a specific video file URL, which is then sent to the frontend.
*   **Authentication**: `fastapi-users` for user registration, login, and session management (JWT).
*   **Payments**: Stripe SDK (Python) for checkout sessions and webhook management.
*   **Video Assets**:
    *   Pre-generated short video sequences (WebM with alpha channel for transparency).
    *   Video generation (external to the main app) involves AI Image-to-Video (I2V) tools or interpolation between keyframes (e.g., Luma AI, DynamiCrafter).
    *   Videos are stored in an Object Storage service and served via a CDN (planned for production).

## Project Structure

```
.
├── alembic/              # Alembic migration scripts
├── app/                  # FastAPI backend application
│   ├── api/              # API endpoint definitions
│   ├── auth/             # Authentication logic (fastapi-users)
│   ├── core/             # Core settings and configurations (e.g., config.py)
│   ├── db/               # Database session management
│   ├── models/           # SQLModel database models
│   ├── schemas/          # Pydantic schemas for API requests/responses
│   └── services/         # Business logic services (e.g., chat, Stripe)
├── src/                  # SvelteKit frontend application
│   ├── lib/              # Svelte components, stores, utilities
│   │   └── stores/       # Svelte stores (e.g., authStore.ts)
│   ├── routes/           # SvelteKit page routes
│   └── app.html          # Main HTML shell
├── static/               # Static assets (currently videos, may change with CDN)
│   └── videos/
├── .env.example          # Example environment variables
├── alembic.ini           # Alembic configuration
├── Dockerfile            # (To be added for backend containerization if needed)
├── netlify.toml          # (To be added for Netlify deployment configuration)
├── Procfile              # (To be added for Railway deployment configuration)
├── package.json          # Frontend dependencies and scripts
├── requirements.txt      # Backend Python dependencies
├── svelte.config.js      # SvelteKit configuration
└── vite.config.js        # Vite configuration
```

## Local Development Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Backend Setup (Python FastAPI)**:
    *   Create and activate a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Copy `.env.example` to `.env` and fill in the required values (DATABASE_URL, SECRET_KEY, Stripe keys).
        ```bash
        cp .env.example .env
        ```
    *   Set up the PostgreSQL database. Ensure it's running.
    *   Run database migrations:
        ```bash
        alembic upgrade head
        ```
    *   Start the backend server:
        ```bash
        uvicorn app.main:app --reload --port 8000
        ```

3.  **Frontend Setup (SvelteKit)**:
    *   Navigate to the frontend directory (if your `package.json` is in the root, you might not need to change directories, but ensure your terminal is in the directory with `package.json`).
    *   Install dependencies:
        ```bash
        npm install
        ```
    *   (If not done already) Copy `.env.example` to `.env` or ensure your SvelteKit app can access `VITE_API_BASE_URL`. By default, SvelteKit apps run on port `5173` and the FastAPI backend on `8000`. The `VITE_API_BASE_URL` in the frontend's environment should point to the backend (e.g., `VITE_API_BASE_URL=http://localhost:8000`).
    *   Start the frontend development server:
        ```bash
        npm run dev
        ```
    The application should then be accessible at `http://localhost:5173`.

## Video Asset Generation

Character animation videos are a core component of AnimeMate. These are currently:
*   Pre-generated short sequences.
*   Ideally in WebM format with an alpha channel for transparent backgrounds.
*   The generation process involves using AI Image-to-Video (I2V) tools or frame interpolation techniques. This is done separately from the main application.
*   Key considerations during generation: character consistency, fixed camera perspective, and background preservation (or generation on a solid color for easy chroma keying).

For production, these video assets will be hosted on an Object Storage service (like AWS S3, Google Cloud Storage, or Cloudflare R2) and distributed via a CDN for optimal performance.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

Please ensure your code adheres to existing styling and that any new features are appropriately documented.

---

*This README was generated by Jules, an AI Software Engineering Agent.*

## Deployment

This section provides instructions on how to deploy the AnimeMate application to Railway (for the backend) and Netlify (for the frontend).

### Backend Deployment (Railway)

The backend is designed to be deployed on Railway using the provided `Procfile`.

1.  **Create a Railway Project**:
    *   Go to [railway.app](https://railway.app/) and create a new project.
    *   Choose "Deploy from GitHub repo" and select your repository.

2.  **Add PostgreSQL Database**:
    *   Within your Railway project, click "+ New" and add a "Database", selecting "PostgreSQL".
    *   Railway will provide you with connection details for this database.

3.  **Configure Environment Variables**:
    *   In your Railway project settings, navigate to the "Variables" tab for your service (the one built from your repo).
    *   Add the following environment variables:
        *   `DATABASE_URL`: Use the connection string provided by Railway's PostgreSQL service. It will look something like `postgresql://user:pass@host:port/db`.
        *   `SECRET_KEY`: Generate a strong secret key (e.g., using `openssl rand -hex 32`).
        *   `STRIPE_SECRET_KEY`: Your Stripe secret key (e.g., `sk_test_...` or `sk_live_...`).
        *   `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook signing secret (e.g., `whsec_...`).
        *   `STRIPE_PRICE_ID_MONTHLY`: (Optional) Your Stripe Price ID for monthly subscriptions.
        *   `STRIPE_PRICE_ID_YEARLY`: (Optional) Your Stripe Price ID for yearly subscriptions.
        *   `FRONTEND_DOMAIN`: Initially, you can set this to a placeholder like `http://localhost:5173`. **You will update this to your actual Netlify frontend URL after deploying the frontend.**

4.  **Deployment Process**:
    *   Railway uses the `Procfile` in your repository:
        *   The `web` command (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`) starts the FastAPI application. Railway automatically sets the `$PORT` variable.
        *   The `release` command (`alembic upgrade head`) runs database migrations before a new version is deployed. This ensures your database schema is up-to-date.
    *   Railway should automatically detect and use these commands. Monitor the deployment logs for any issues.

5.  **Accessing your API**:
    *   Once deployed, Railway will provide a public URL for your backend service (e.g., `my-backend-production.up.railway.app`). You will use this as the `VITE_API_BASE_URL` for your frontend.

### Frontend Deployment (Netlify)

The SvelteKit frontend is designed for deployment on Netlify.

1.  **Create a Netlify Site**:
    *   Go to [netlify.com](https://www.netlify.com/) and sign up or log in.
    *   Click "Add new site" -> "Import an existing project".
    *   Connect to your Git provider (e.g., GitHub) and select your repository.

2.  **Configure Build Settings**:
    *   Netlify should automatically detect SvelteKit projects and often pre-fills settings.
    *   The `netlify.toml` file in your repository specifies:
        *   **Build command**: `npm run build`
        *   **Publish directory**: `build/`
    *   Ensure these settings are correctly reflected in the Netlify UI, or rely on the `netlify.toml` file.

3.  **Configure Environment Variables**:
    *   In your Netlify site settings, go to "Site configuration" -> "Environment variables".
    *   Add the following environment variable:
        *   `VITE_API_BASE_URL`: The public URL of your deployed Railway backend service (e.g., `https://my-backend-production.up.railway.app`). **Make sure this URL does not end with a slash.**

4.  **Deploy**:
    *   Click "Deploy site". Netlify will build and deploy your frontend.

5.  **Accessing your Frontend**:
    *   Netlify will provide a public URL for your frontend (e.g., `https-my-awesome-app.netlify.app`).

### Post-Deployment Steps

1.  **Update `FRONTEND_DOMAIN` in Railway**:
    *   Once your Netlify frontend is live and you have its URL, go back to your Railway project's environment variables.
    *   Update the `FRONTEND_DOMAIN` variable to your actual Netlify frontend URL (e.g., `https://my-awesome-app.netlify.app`). This is important for CORS and for Stripe redirects.

2.  **Configure Stripe Webhooks**:
    *   In your Stripe dashboard, go to "Developers" -> "Webhooks".
    *   Add an endpoint:
        *   **Endpoint URL**: `YOUR_RAILWAY_BACKEND_URL/webhooks/stripe` (e.g., `https://my-backend-production.up.railway.app/webhooks/stripe`).
        *   **Events**: Select the events your application needs to listen to (e.g., `checkout.session.completed`, `invoice.paid`, `customer.subscription.deleted`, etc., based on your `app/api/endpoints/stripe_webhooks.py`).
    *   Make sure the `STRIPE_WEBHOOK_SECRET` in Railway matches the signing secret provided by Stripe for this endpoint.

3.  **(Recommended) Restrict CORS Origins**:
    *   Open `app/main.py` in your backend code.
    *   Change the `origins` list in the `CORSMiddleware` to include only your Netlify frontend URL and any other domains you need to allow (e.g., your local development URL).
        ```python
        origins = [
            "YOUR_NETLIFY_FRONTEND_URL", # e.g., "https://my-awesome-app.netlify.app"
            "http://localhost:5173",    # For local development
            "http://127.0.0.1:5173",   # For local development
        ]
        ```
    *   Commit and push this change. Railway will automatically redeploy your backend.

By following these steps, you should have a fully deployed AnimeMate application!
```
