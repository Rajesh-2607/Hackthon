"""
Instagram Profile Scraper Integration with Apify API
Matches training data features (WITHOUT verification field).
"""

import os
import re
from typing import Dict, Tuple
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

class InstagramScraperService:
    """Service for scraping Instagram profiles using Apify."""

    def __init__(self):
        """Initialize Apify client with API token."""
        self.api_token = "apify_api_EdQkvCknO9BVJnsTW2qT0zJCQt3tHY2QixSL"
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN not found in .env file")

        self.client = ApifyClient(self.api_token)
        self.actor_id = "dSCLg0C3YEZ83HzYX"  # Instagram Profile Scraper

    def classify_input(self, user_input: str) -> Tuple[str, str]:
        """
        Classify if input is Instagram URL or username.

        Args:
            user_input: Raw input from frontend (URL or username)

        Returns:
            Tuple of (input_type, normalized_value)
            input_type: "url" or "username"
            normalized_value: Cleaned username without @ or extracted from URL
        """
        user_input = user_input.strip()

        # Check if it's a URL
        url_patterns = [
            r'(?:https?://)?(?:www\.)?instagram\.com/([^/?#&]+)',
            r'(?:https?://)?(?:www\.)?instagr\.am/([^/?#&]+)'
        ]

        for pattern in url_patterns:
            match = re.match(pattern, user_input)
            if match:
                username = match.group(1)
                # Remove any trailing slashes or query params
                username = username.rstrip('/').split('?')[0]
                return ("url", username)

        # If not URL, treat as username
        # Remove @ symbol if present
        username = user_input.lstrip('@')

        # Validate username format (Instagram allows letters, numbers, periods, underscores)
        if re.match(r'^[a-zA-Z0-9._]+$', username):
            return ("username", username)
        else:
            raise ValueError(f"Invalid Instagram username format: {username}")

    def scrape_profile(self, username: str) -> Dict:
        """
        Scrape Instagram profile data using Apify API.

        Args:
            username: Instagram username (without @)

        Returns:
            Dictionary with raw profile data from Apify
        """
        try:
            # Run the Apify actor
            run_input = {
                "usernames": [username],
                "resultsLimit": 1
            }

            print(f"[INFO] Starting Apify scrape for username: {username}")
            run = self.client.actor(self.actor_id).call(run_input=run_input)

            # Fetch results from dataset
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            if not items:
                raise ValueError(f"No data found for username: {username}")

            profile_data = items[0]
            
            # Check if account exists - if only username is returned, account doesn't exist
            # A valid account should have at least followers count, posts count, or profile pic
            has_followers = profile_data.get("followersCount") is not None
            has_posts = profile_data.get("postsCount") is not None
            has_profile_pic = profile_data.get("profilePicUrl") is not None and profile_data.get("profilePicUrl") != ""
            has_full_name = profile_data.get("fullName") is not None and profile_data.get("fullName") != ""
            
            # If only username exists and no other meaningful data, account doesn't exist
            if not has_followers and not has_posts and not has_profile_pic and not has_full_name:
                raise ValueError(f"Account does not exist: @{username}")
            
            # Additional check: if all counts are None or 0 and no bio/profile pic
            followers = profile_data.get("followersCount", 0) or 0
            following = profile_data.get("followsCount", 0) or 0
            posts = profile_data.get("postsCount", 0) or 0
            
            if followers == 0 and following == 0 and posts == 0 and not has_profile_pic and not has_full_name:
                raise ValueError(f"Account does not exist or is invalid: @{username}")
            
            print(f"[OK] Successfully scraped profile: {username}")
            return profile_data

        except ValueError as e:
            # Re-raise ValueError as-is (account doesn't exist)
            raise e
        except Exception as e:
            raise Exception(f"Apify scraping failed for {username}: {str(e)}")

    def extract_features(self, profile_data: Dict) -> Dict:
        """
        Extract features from Apify profile data matching training data columns.

        Training data columns (11 features):
        'profile pic', 'nums/length username', 'fullname words',
        'nums/length fullname', 'name==username', 'description length',
        'external URL', 'private', '#posts', '#followers', '#follows'

        Args:
            profile_data: Raw data from Apify

        Returns:
            Dictionary matching training data structure
        """
        # Extract basic fields
        username = profile_data.get("username", "")
        full_name = profile_data.get("fullName", "")
        biography = profile_data.get("biography", "")
        external_url = profile_data.get("externalUrl", "")
        profile_pic_url = profile_data.get("profilePicUrl", "")
        is_private = profile_data.get("private", False)

        # Follower metrics
        followers = profile_data.get("followersCount", 0)
        following = profile_data.get("followsCount", 0)
        posts = profile_data.get("postsCount", 0)

        # Feature engineering - 11 features total
        features = {
            # Match training column: 'profile pic'
            "profile_pic": 1 if profile_pic_url and len(profile_pic_url) > 0 else 0,

            # Match training column: 'nums/length username'
            "nums_length_username": self._calculate_digit_ratio(username),

            # Match training column: 'fullname words'
            "fullname_words": len(full_name.split()) if full_name else 0,

            # Match training column: 'nums/length fullname'
            "nums_length_fullname": self._calculate_digit_ratio(full_name),

            # Match training column: 'name==username'
            "name_eq_username": 1 if full_name.lower().replace(" ", "") == username.lower() else 0,

            # Match training column: 'description length'
            "description_length": len(biography) if biography else 0,

            # Match training column: 'external URL'
            "external_url": 1 if external_url else 0,

            # Match training column: 'private'
            "private": 1 if is_private else 0,

            # Match training column: '#posts'
            "posts": posts,

            # Match training column: '#followers'
            "followers": followers,

            # Match training column: '#follows'
            "following": following
        }

        return features

    def _calculate_digit_ratio(self, text: str) -> float:
        """
        Calculate ratio of digits to total characters in text.

        Args:
            text: Input string

        Returns:
            Float between 0 and 1
        """
        if not text or len(text) == 0:
            return 0.0

        digit_count = sum(c.isdigit() for c in text)
        return round(digit_count / len(text), 3)

    def process_instagram_input(self, user_input: str) -> Dict:
        """
        Main method: Process Instagram URL/username and return features.

        Args:
            user_input: Instagram URL or username from frontend

        Returns:
            Dictionary with features ready for ML model prediction
        """
        # Step 1: Classify input
        input_type, username = self.classify_input(user_input)
        print(f"[INFO] Detected input type: {input_type}, Username: {username}")

        # Step 2: Scrape profile
        profile_data = self.scrape_profile(username)

        # Step 3: Extract features
        features = self.extract_features(profile_data)

        # Add metadata for reference
        features["_metadata"] = {
            "input_type": input_type,
            "username": username,
            "full_name": profile_data.get("fullName", ""),
            "biography": profile_data.get("biography", ""),
            "is_verified": profile_data.get("verified", False),
            "profile_url": f"https://instagram.com/{username}"
        }

        return features


# Utility functions for use in main.py

def parse_instagram_input(user_input: str) -> Dict:
    """
    Convenience function to process Instagram input.
    Can be imported directly in main.py

    Usage:
        from instagram_scraper import parse_instagram_input
        features = parse_instagram_input("https://instagram.com/username")
    """
    scraper = InstagramScraperService()
    return scraper.process_instagram_input(user_input)


def validate_instagram_input(user_input: str) -> bool:
    """
    Validate if input is valid Instagram URL or username.

    Returns:
        True if valid, False otherwise
    """
    try:
        scraper = InstagramScraperService()
        scraper.classify_input(user_input)
        return True
    except ValueError:
        return False
