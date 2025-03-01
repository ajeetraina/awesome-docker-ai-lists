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
            entry = format_entry_for_readme(repo_info, category)
            
            print(f"  - Identified as Docker AI/ML content in category: {category}")
            print(f"  - Entry: {entry}")
            
            if not args.dry_run:
                success = create_pull_request(repo_info, category, entry, g)
                if success:
                    added_count += 1
                # Add some delay between PRs
                time.sleep(random.randint(5, 15))
        else:
            print(f"  - Not identified as Docker AI/ML content, skipping")
    
    # Optionally search blogs as well
    if args.days > 7:  # Only search blogs for longer timeframes
        print("\nSearching for blog posts...")
        blogs = search_blogs(args.days)
        for blog in blogs:
            category = determine_category(blog)
            entry = format_entry_for_readme(blog, category)
            
            print(f"  - Blog: {blog['name']}")
            print(f"  - Category: {category}")
            print(f"  - Entry: {entry}")
            
            if not args.dry_run:
                success = create_pull_request(blog, category, entry, g)
                if success:
                    added_count += 1
                time.sleep(random.randint(5, 15))
    
    print(f"\nDone! Created {added_count} pull requests.")

if __name__ == "__main__":
    main()