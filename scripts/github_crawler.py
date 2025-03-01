#!/usr/bin/env python3
"""
GitHub Crawler for Docker AI/ML Blogs and Projects

This script searches GitHub for Docker AI/ML related blogs and projects 
and automatically creates PRs to add them to the awesome-docker-ai-lists repository.
"""

import os
import re
import sys
import time
import random
import argparse
import requests
from datetime import datetime
from github import Github, GithubException

# Configuration
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_OWNER = "ajeetraina"
REPO_NAME = "awesome-docker-ai-lists"
CATEGORIES = {
    "model-context-protocol": ["mcp", "model context protocol", "claude"],
    "generative-ai": ["genai", "generative ai", "llm", "gpt", "language model"],
    "hugging-face": ["huggingface", "hugging face", "hf"],
    "ai-ml-use-cases": ["ai use case", "ml use case", "ai implementation"],
    "ai-ml-deployment": ["ai deployment", "ml deployment", "model serving"],
    "developer-tools": ["developer tool", "ai tool", "ml tool"],
    "assistants-automation": ["ai assistant", "automation", "ai agent", "chatbot"],
    "healthcare": ["health", "medical", "doctor", "patient", "wellness"],
    "education": ["education", "learning", "teaching", "course", "student"],
    "nlp-communication": ["nlp", "natural language", "communication", "text analysis"],
    "security-monitoring": ["security", "monitoring", "surveillance", "protection"],
    "documentation": ["documentation", "knowledge", "information", "content management"]
}

def setup_argument_parser():
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(description="GitHub crawler for Docker AI/ML content")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back")
    parser.add_argument("--limit", type=int, default=20, help="Max number of repositories to process")
    parser.add_argument("--dry-run", action="store_true", help="Don't create PRs, just print findings")
    return parser.parse_args()

def search_github_repositories(query, days_ago, limit=20):
    """Search GitHub for repositories matching the query criteria"""
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    g = Github(GITHUB_TOKEN)
    date_filter = datetime.now() - datetime.timedelta(days=days_ago)
    date_str = date_filter.strftime("%Y-%m-%d")
    
    query = f"{query} pushed:>{date_str} language:python language:javascript"
    print(f"Searching GitHub with query: {query}")
    
    try:
        repos = g.search_repositories(query, sort="updated", order="desc")
        return list(repos)[:limit]
    except GithubException as e:
        print(f"GitHub API error: {e}")
        return []

def get_repository_info(repo):
    """Extract relevant information from a repository"""
    return {
        "name": repo.name,
        "full_name": repo.full_name,
        "owner": repo.owner.login,
        "description": repo.description or "",
        "url": repo.html_url,
        "stars": repo.stargazers_count,
        "updated_at": repo.updated_at,
        "topics": repo.get_topics()
    }

def has_docker_and_ai_ml(repo_info):
    """Check if repository is related to both Docker and AI/ML"""
    docker_terms = ["docker", "container", "containerization", "dockerfile"]
    ai_ml_terms = ["ai", "ml", "machine learning", "artificial intelligence", 
                  "deep learning", "neural network", "tensorflow", "pytorch",
                  "model", "prediction", "analysis", "analytics"]
    
    # Check name, description and topics
    content = (repo_info["name"] + " " + 
              repo_info["description"] + " " + 
              " ".join(repo_info["topics"])).lower()
    
    has_docker = any(term in content for term in docker_terms)
    has_ai_ml = any(term in content for term in ai_ml_terms)
    
    return has_docker and has_ai_ml

def determine_category(repo_info):
    """Determine best category for the repository"""
    content = (repo_info["name"] + " " + 
              repo_info["description"] + " " + 
              " ".join(repo_info["topics"])).lower()
    
    scores = {}
    for category, keywords in CATEGORIES.items():
        score = sum(1 for keyword in keywords if keyword in content)
        scores[category] = score
    
    if max(scores.values(), default=0) > 0:
        return max(scores.items(), key=lambda x: x[1])[0]
    return "ai-ml-use-cases"  # Default category

def format_entry_for_readme(repo_info, category):
    """Format repository information for README entry"""
    type_label = "Project"
    if "blog" in repo_info["name"].lower() or "article" in repo_info["name"].lower():
        type_label = "Blog"
    
    name = repo_info["name"].replace("-", " ").title()
    description = repo_info["description"]
    if len(description) > 100:
        description = description[:97] + "..."
    
    return f"| {name} | {description} | {type_label} | [View]({repo_info['url']}) |"

def create_pull_request(repo_info, category_name, entry_markdown, g):
    """Create a pull request to add new repository to the README"""
    try:
        repo = g.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
        main_branch = repo.get_branch("main")
        
        # Create a new branch
        branch_name = f"add-{repo_info['name'].lower()}-{int(time.time())}"
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
        
        # Get the current README
        readme_content = repo.get_contents("README.md", ref=branch_name).decoded_content.decode("utf-8")
        
        # Find the section to update
        section_pattern = f"## {category_name}\n\n"
        table_start = readme_content.find(section_pattern)
        if table_start == -1:
            print(f"Warning: Could not find section {category_name} in README")
            return False
        
        table_start = readme_content.find("|", table_start)
        table_end = readme_content.find("\n\n", table_start)
        if table_end == -1:
            table_end = len(readme_content)
        
        # Insert new entry at the end of the table
        updated_content = (
            readme_content[:table_end] + 
            "\n" + entry_markdown + 
            readme_content[table_end:]
        )
        
        # Commit the change
        repo.update_file(
            path="README.md",
            message=f"Add {repo_info['name']} to {category_name}",
            content=updated_content,
            sha=repo.get_contents("README.md", ref=branch_name).sha,
            branch=branch_name
        )
        
        # Create a pull request
        pr = repo.create_pull(
            title=f"Add {repo_info['name']} to {category_name}",
            body=f"This PR adds {repo_info['full_name']} to the {category_name} section.\n\n"
                 f"Stars: {repo_info['stars']}\n"
                 f"Description: {repo_info['description']}\n"
                 f"URL: {repo_info['url']}",
            head=branch_name,
            base="main"
        )
        
        print(f"Created PR #{pr.number}: {pr.html_url}")
        return True
    
    except Exception as e:
        print(f"Error creating PR: {e}")
        return False

def main():
    args = setup_argument_parser()
    
    # Docker AI/ML related search queries
    search_queries = [
        "docker ai",
        "docker machine learning",
        "docker ml",
        "docker neural network",
        "docker deep learning",
        "containerized ai",
        "containerized machine learning",
        "docker llm"
    ]
    
    g = Github(GITHUB_TOKEN)
    all_repos = []
    
    for query in search_queries:
        repos = search_github_repositories(query, args.days, args.limit // len(search_queries))
        all_repos.extend(repos)
        # Avoid rate limiting
        time.sleep(2)
    
    # Remove duplicates
    unique_repos = {repo.full_name: repo for repo in all_repos}
    print(f"Found {len(unique_repos)} unique repositories")
    
    added_count = 0
    for repo_name, repo in unique_repos.items():
        print(f"Processing {repo_name}...")
        repo_info = get_repository_info(repo)
        
        if has_docker_and_ai_ml(repo_info):
            category = determine_category(repo_info)
            category_name = category.replace("-", " ").title()
            entry = format_entry_for_readme(repo_info, category)
            
            print(f"  - Identified as Docker AI/ML content in category: {category_name}")
            print(f"  - Entry: {entry}")
            
            if not args.dry_run:
                success = create_pull_request(repo_info, category_name, entry, g)
                if success:
                    added_count += 1
                # Add some delay between PRs
                time.sleep(random.randint(5, 15))
        else:
            print(f"  - Not identified as Docker AI/ML content, skipping")
    
    print(f"Done! Created {added_count} pull requests.")

if __name__ == "__main__":
    main()
