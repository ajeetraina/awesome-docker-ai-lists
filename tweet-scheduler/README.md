# Kubetools Tweet Scheduler

This tool automatically tweets about Kubernetes tools from the [kubetools](https://github.com/ajeetraina/kubetools) repository at a specified interval (default: 1 hour).

## Features

- Extracts tools and their details from the kubetools repository README
- Tweets one tool at a time at a configurable interval
- Keeps track of tweeted tools to ensure variety
- Includes tool name, category, description, and URL in tweets
- Adds relevant hashtags for visibility (#Kubetools #Kubernetes #K8s #CloudNative)

## Requirements

- Python 3.6 or higher
- Twitter Developer account with API keys
- Required Python packages (see requirements.txt)

## Setup

### Twitter Developer Account

1. Create a Twitter Developer account at [developer.twitter.com](https://developer.twitter.com/)
2. Create a project and app
3. Generate API keys and access tokens

### Configuration

Create a `.env` file based on the provided `.env.example` file:

```
# Twitter API Credentials
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_token_secret

# GitHub Token (optional, for higher API rate limits)
GITHUB_TOKEN=your_github_token

# Tweet interval in hours (default: 1)
TWEET_INTERVAL=1
```

## Usage

### Running Locally

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Run the script:

```bash
python tweet_scheduler.py
```

You can specify a custom interval with:

```bash
python tweet_scheduler.py --interval 2  # Tweet every 2 hours
```

### Running with Docker

1. Build and run using Docker Compose:

```bash
docker-compose up -d
```

2. View logs:

```bash
docker-compose logs -f
```

3. Stop the service:

```bash
docker-compose down
```

## Tweet Format

Each tweet includes:

```
🔧 #Kubernetes Tool: [Tool Name] - Category: [Category]

[Tool Description]

[Tool URL]

#Kubetools #Kubernetes #K8s #CloudNative
```

## Deployment

### Server Deployment

For a production environment, you can deploy this as a Docker container on any server with Docker installed.

### Cloud Deployment

This can be deployed on cloud platforms:

- **AWS**: Use ECS (Elastic Container Service) or Fargate
- **GCP**: Use Cloud Run or GKE (Google Kubernetes Engine)
- **Azure**: Use Container Instances or AKS (Azure Kubernetes Service)

## Log and History

The script maintains:

- A log file `tweet_scheduler.log` for debugging and monitoring
- A history file `tweet_history.json` that keeps track of tweeted tools

When using Docker, these files are persisted in the `./data` directory through a volume mount.

## Customization

You can customize the tweet format by modifying the `create_tweet_text` function in the script.

## License

MIT
