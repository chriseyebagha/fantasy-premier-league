# Deployment Setup Guide

The FPL Predictor uses a GitHub Action to automatically deploy changes to your personal website. For this to work, the FPL repository needs permission to push code to your `personal-website` repository. This is granted via a **Personal Access Token (PAT)**.

## Step 1: Generate a Personal Access Token (PAT)

1.  Log in to your GitHub account.
2.  Navigate to **Settings** (click your profile picture in the top right > Settings).
3.  In the left sidebar, scroll down and click **Developer settings**.
4.  Click **Personal access tokens** > **Tokens (classic)**.
5.  Click the **Generate new token** button (select **Generate new token (classic)**).
6.  **Note**: Give it a descriptive name like "FPL Predictor Deployment".
7.  **Expiration**: Set this to "No expiration" (or set a reminder to rotate it if you prefer security best practices).
8.  **Select Scopes**:
    *   check the box for **`repo`** (Full control of private repositories).
    *   *This is required to push files to your other repository.*
9.  Click **Generate token**.
10. **COPY THIS TOKEN NOW**. You will not be able to see it again.

## Step 2: Add the Secret to the FPL Project

1.  Navigate to your **Fantasy Premier League Project** repository on GitHub.
2.  Click on the **Settings** tab (usually the rightmost tab in the top bar).
3.  In the left sidebar, click **Secrets and variables** > **Actions**.
4.  Click the green **New repository secret** button.
5.  **Name**: Enter `PERSONAL_WEBSITE_PAT` (must match exactly).
6.  **Secret**: Paste the token you copied in Step 1.
7.  Click **Add secret**.

## Step 3: Trigger a Deploy

1.  Make a small change to the project (or just an empty commit) and push to `main`.
2.  Go to the **Actions** tab in your FPL repository to watch the `Deploy FPL Predictor` workflow run.
3.  Once green, check your `personal-website` repository or live site to verify the update.
