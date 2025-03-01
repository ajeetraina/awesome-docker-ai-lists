# Docker AI/ML Resource Crawler Scripts

These scripts help maintain the awesome-docker-ai-lists repository by automatically finding and adding new Docker AI/ML resources.

## GitHub Crawler

The `github_crawler.py` script searches GitHub for repositories related to Docker and AI/ML, and creates pull requests to add them to the appropriate sections of the README.

### Usage

```bash
# Set your GitHub token
export GITHUB_TOKEN=your_github_token

# Run with default settings (search last 7 days, limit to 20 repos)
python github_crawler.py

# Custom search parameters
python github_crawler.py --days 30 --limit 50

# Dry run (don't create PRs, just print findings)
python github_crawler.py --dry-run
```

### Features

- Searches for Docker AI/ML repositories by multiple queries
- Automatically categorizes content based on repository description and topics
- Creates pull requests with properly formatted entries
- Rate-limit aware to avoid GitHub API restrictions
- Optionally searches blog sources for Docker AI/ML content

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Adding to CI/CD

This script can be integrated into a GitHub Action workflow to automatically run on a schedule. 
See the example workflow in `.github/workflows/crawler.yml`.
