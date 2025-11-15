# PDFPixie 🤖📄

Chat with your PDFs using AI. Upload any document, ask questions, and get instant answers powered by semantic search and real-time AI responses.

**Live Demo:** https://pdfpixie.duckdns.org

## What's Inside

- **Smart PDF Processing** - Just drag and drop your files, we'll handle the rest
- **AI Conversations** - Ask questions and get answers based on your document's content
- **Lightning Fast Search** - Vector embeddings find exactly what you need
- **Real-time Chat** - WebSocket-powered instant responses
- **Memory** - Your chat history is saved automatically
- **Beautiful UI** - Clean, modern interface that's easy on the eyes
- **Production Ready** - Fully Dockerized and deployed on AWS

## Tech Stack

**Frontend:** React 18, TypeScript, Vite, Socket.IO  
**Backend:** FastAPI, Python 3.10+, LangChain  
**AI:** OpenRouter API, ChromaDB vectors  
**Database:** PostgreSQL, Redis  
**Deploy:** Docker, Nginx, AWS EC2

## Quick Start

### Using Docker (Easiest)

**You'll need:**
- Docker installed
- An OpenRouter API key (free at [openrouter.ai](https://openrouter.ai/))

**Let's go:**
```bash
git clone https://github.com/PikunMohanta/chatpdf.git
cd chatpdf

# Add your API key to .env
cp .env.example .env
nano .env  # Set OPENROUTER_API_KEY

# Fire it up
docker-compose up -d
```

Open http://localhost in your browser. That's it!

### Running Locally

**You'll need:** Node.js 18+ and Python 3.10+

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Mac/Linux
pip install -r requirements.txt
uvicorn main:socket_app --reload --port 8000
```

**Frontend (new terminal):**
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173 and you're good to go!

## Deploying to AWS
1. Spin up an AWS EC2 instance (t3.small recommended)
2. Get a free domain from DuckDNS
3. Clone the repo and run `docker-compose up -d`
4. You're live!

**Cost:** About $17-20/month for the infrastructure. Not bad for your own AI-powered PDF assistant!

## How to Use

1. **Upload** - Drop a PDF or click to upload
2. **Chat** - Ask anything about your document
3. **Get Answers** - AI reads through your PDF and responds with relevant info
4. **Save** - All your conversations are automatically saved

Simple as that.

## Project Structure

```
chatpdf/
├── frontend/          # React app
├── backend/           # FastAPI server
│   ├── app/          # Core logic (chat, PDF processing, auth)
│   └── data/         # Your PDFs and database
├── docs/             # Deployment guides
└── docker-compose.yml # One-command deploy
```

## Environment Setup

Create a `.env` file in the root:

```env
OPENROUTER_API_KEY=your_key_here
POSTGRES_PASSWORD=something_secure
DATABASE_URL=postgresql://pdfpixie_user:your_password@postgres:5432/pdfpixie
REDIS_URL=redis://redis:6379/0
```

That's all you really need to get started.

## Useful Commands

```bash
# Check what's happening
docker-compose logs -f app

# Restart everything
docker-compose restart

# Update to latest version
git pull && docker-compose build && docker-compose up -d

# Backup your data
docker-compose exec postgres pg_dump -U pdfpixie_user pdfpixie > backup.sql
```

## Troubleshooting

**Chat not working?**  
Make sure you're using `main:socket_app` when running the backend, not just `main:app`.

**Can't upload PDFs?**  
Check the logs with `docker-compose logs -f app` - usually it's a permissions thing.

**Container won't start?**  
Ports 80 and 8000 need to be free. Also make sure your `.env` file has the API key.

**Database errors?**  
Run `docker-compose ps` to check if PostgreSQL is running. If not, try `docker-compose restart`.

## Contributing

Found a bug? Have an idea? Pull requests are welcome! Just fork the repo, make your changes, and submit a PR.

## Links

- **Try it live:** https://pdfpixie.duckdns.org
- **GitHub:** https://github.com/PikunMohanta/chatpdf
- **Report issues:** https://github.com/PikunMohanta/chatpdf/issues

---

Built with ❤️ for anyone who's tired of manually searching through PDFs.
