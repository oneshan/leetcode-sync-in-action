import os

from dotenv import load_dotenv

from leetcode_sync import LeetcodeSync

load_dotenv()


def main() -> None:

    # Load configs
    leetcode_session: str = os.getenv('LEETCODE_SESSION')
    leetcode_csrf_token: str = os.getenv('LEETCODE_CSRF_TOKEN')
    if not leetcode_session or not leetcode_csrf_token:
        raise ValueError('Session is not set')

    # Export recent submissions
    leetcode_sync = LeetcodeSync(leetcode_csrf_token, leetcode_session)
    leetcode_sync.sync_recent_submissions()


if __name__ == '__main__':
    main()
