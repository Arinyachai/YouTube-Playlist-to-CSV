import csv
import re
from tqdm import tqdm
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def extract_playlist_id(link):
    """Extracts the playlist ID from a YouTube playlist link."""
    pattern = r"(?<=list=)[\w-]+"
    match = re.search(pattern, link)
    if match:
        return match.group(0)
    else:
        return None

try:
    # Set up the YouTube Data API client
    api_key = 'YOUR_API_KEY_HERE'
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Prompt user for playlist URL
    print("Enter the URL of the YouTube playlist you want to retrieve data for:")
    link = input("URL: ")

    # Extract playlist ID from the URL
    playlist_id = extract_playlist_id(link)
    if not playlist_id:
        print("Invalid playlist URL. Please provide a valid YouTube playlist URL.")
        exit()

    print("Retrieving playlist data...")

    # Call the YouTube Data API to retrieve the playlist data
    playlist_request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )

    # Write the video data to a CSV file
    with open('youtube_playlist.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Video Title', 'Video Description', 'Published At', 'Duration', 'Video URL'])

        try:
            # Retrieve video data for each video in the playlist
            for item in tqdm(playlist_request.execute()['items'], desc='Videos processed'):
                video_id = item['snippet']['resourceId']['videoId']
                video_title = item['snippet']['title']
                video_description = item['snippet']['description']
                video_published = item['snippet']['publishedAt']

                # Get the video duration
                video_response = youtube.videos().list(part='contentDetails', id=video_id).execute()
                video_duration = video_response['items'][0]['contentDetails']['duration'] if video_response['items'] else ''

                # Create video URL
                video_url = f'https://www.youtube.com/watch?v={video_id}'

                # Write the video data to the CSV file
                writer.writerow([video_title, video_description, video_published, video_duration, video_url])

            print("Data retrieved successfully. Output saved to youtube_playlist.csv")

        except HttpError as e:
            print(f"An HTTP error occurred: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
