#!/bin/bash

# This script helps you copy the tweet scheduler to your kubetools repository

echo "This script will help you copy the tweet scheduler to your kubetools repository."
echo "Make sure you have cloned your kubetools repository locally."

# Ask for the path to the kubetools repository
read -p "Enter the path to your local kubetools repository: " KUBETOOLS_PATH

# Check if the path exists
if [ ! -d "$KUBETOOLS_PATH" ]; then
    echo "Error: The specified path does not exist."
    exit 1
fi

# Check if it's a Git repository
if [ ! -d "$KUBETOOLS_PATH/.git" ]; then
    echo "Error: The specified path is not a Git repository."
    exit 1
fi

# Create the tweet-scheduler directory in the kubetools repository
TARGET_DIR="$KUBETOOLS_PATH/tweet-scheduler"
mkdir -p "$TARGET_DIR"

# Copy all files from the tweet-scheduler directory
cp -r * "$TARGET_DIR"

echo "Files have been copied to $TARGET_DIR"
echo "Now navigate to your kubetools repository and commit the changes:"
echo "cd $KUBETOOLS_PATH"
echo "git add tweet-scheduler"
echo "git commit -m 'Add tweet scheduler for automatic tool tweeting'"
echo "git push origin main"
