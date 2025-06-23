# Anor Dating Bot

Anor Dating is a Telegram bot that lets users chat anonymously in a dating app experience, all inside Telegram. Users can try the bot at [https://t.me/anormatchbot](https://t.me/anormatchbot).

## Features

- Anonymous chat and matching inside Telegram
- Web app interface for enhanced experience
- Easy local and production deployment with Docker

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd anordating
```

### 2. Set up environment variables

- Copy the example environment files and fill in the required values:

```bash
cp example.env .env
cp frontend/example.env frontend/.env
```

Edit `.env` and `frontend/.env` to provide your Telegram bot token and other required secrets.

#### Hashing the ADMIN_PASSWORD

For the admin panel, you need to provide a hashed password. You can generate it with:

```sh
echo $(htpasswd -nb admin yourpassword) | cut -d: -f2 | xargs
```

This command will output only the password hash (the part after the `$` sign). Copy the output and set it as the value for `TRAEFIK_PASSWORD` in your `.env` file.

### 3. Running in Development

- Make sure you have [Docker](https://www.docker.com/) installed.
- Start the services in watch mode:

```bash
docker compose watch
```

- **Important:** Telegram does not accept `localhost` as a web app URL. Use a service like [nip.io](https://nip.io/) to point to your local IP address. For example, if your local IP is `192.168.1.16`, use `192.168.1.16.nip.io` as your domain in the `.env` files.
- Use [Telegram Beta](https://desktop.telegram.org/changelog#beta-versions) and "test backend" when adding an account to run the bot in development environment.

### 4. Running in Production

- Build and start the services in detached mode:

```bash
docker compose -f compose.yaml up -d --build
```

- Set your production domain in the `.env` files.

## Project Structure

- `backend/` — FastAPI backend, bot logic, database, and API
- `frontend/` — SvelteKit frontend for the web app

## Dependencies

- Docker & Docker Compose
- Telegram Bot API
- nip.io (or similar) for local development
- Python (FastAPI, SQLAlchemy, etc.)
- Node.js (SvelteKit, Vite, etc.)

All dependencies are managed by Docker; you do not need to install them manually.

## Support

For questions or issues, please open an issue in this repository.

---

Enjoy chatting anonymously with Anor Dating!
