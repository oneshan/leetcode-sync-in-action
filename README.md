# leetcode-sync-in-action

This project is inspired by [joshcai/leetcode-sync](https://github.com/joshcai/leetcode-sync)

Here is my repo to gather Leetcode submissions through the github action: [leetcode-python](https://github.com/oneshan/leetcode-python)

# Feature

 - Sync recent accepted submissions by checking `.leetcode_last_timestamp`
 - Add description of problems from Leetcode

# Usage

## How to get cookie value

The project requires the cookies `csrftoken` and `LEETCODE_SESSION` from the LeetCode website.

Follow these steps to obtain the values:

1. Login to the LeetCode website.
2. Right-click on the page and select `Inspect`.
3. Navigate to `Storage > Cookies` to find the values.


## Local use

Create a `.env` file with 
```
LEETCODE_SESSION=xxxxxxxx
LEETCODE_CSRF_TOKEN=xxxxx
```
Then run `python main.py`

## Setup Github Action

1. Create GitHub Secrets for LeetCode API access

    - Open `Settings > Secrets and variables > Actions` from the repository
    - Click `New repository secret`
    - Create new secrets `LEETCODE_SESSION` and `LEETCODE_CSRF_TOKEN` using cookie values

2. Give workflows write and read permissions for git commands

    - Open `Settings > Actions > General` from the repository
    - Select `Read and write permissions` and save

3. Create GithHub Action

    - Create a new yaml file (e.g. `leetcode_sync.yml`) in `.github/workflows` folder with the following content:
    ```yaml
    name: LeetcodeSync

    on:
      workflow_dispatch:
      schedule:
        # triggers the workflow every day at 0:00 UTC
        - cron: '0 0 * * *'
        
    jobs:
      leetcode-sync-in-action:
        runs-on: ubuntu-latest
        steps:
        
          - name: Sync me Leetcode
            uses: oneshan/leetcode-sync-in-action@v1.0
            with:
              GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
              LEETCODE_CSRF_TOKEN: ${{ secrets.LEETCODE_CSRF_TOKEN }}
              LEETCODE_SESSION: ${{ secrets.LEETCODE_SESSION }}
    ```

### Inputs

- `GITHUB_TOKEN` (required) - GitHub token used for pushing updates to the repository.
- `LEETCODE_SESSION` (required) - LeetCode session used for retrieving user data from Leetcode.
- `LEETCODE_CSRF_TOKEN` (required) - LeetCode CSRF token used for retrieving user data from Leetcode.
