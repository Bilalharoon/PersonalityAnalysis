import os
from openai import OpenAI
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv('SECRETS.env')
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)
print(os.getenv("SPOTIPY_CLIENT_ID"))
# Spotify Auth
scope = "user-top-read"
auth_manager = auth_manager=SpotifyOAuth(
    scope=scope,
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    cache_path='./.cache'
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Fetch top tracks and audio features
def get_top_tracks_with_features(limit=20, time_range="short_term"):
    results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
    songs_info = []
    track_ids = []
    for item in results['items']:
        name = item['name']
        artists = ", ".join([artist['name'] for artist in item['artists']])
        track_ids.append(item['id'])
        songs_info.append({'name': name, 'artists': artists})
    # audio_features = sp.audio_features(track_ids)

    # for song in songs_info:
        # detailed_songs.append(f'{song['name']} by {song['artist']}\n')
        # if features:
            # detailed_songs.append({
            #     'title': f"{song['name']} by {song['artists']}",
            #     'valence': features['valence'],
            #     'energy': features['energy'],
            #     'danceability': features['danceability'],
            #     'acousticness': features['acousticness'],
            #     'instrumentalness': features['instrumentalness'],
            #     'tempo': features['tempo'],
            # })

    return songs_info

# Format data for GPT
def format_features_for_prompt(songs_info):
    prompt_lines = ["Given the following list of songs, analyze the personality of the listener. "
        "Use psychological insight and musical trends to infer emotional traits, energy level, social tendencies, etc. In addition, try to guess the users likely hobbies, career, kinds of pets, etc.\n\n"
        "Songs:\n"]
    for song in songs_info:
        prompt_lines.append(f'{song['name']} by {song['artists']}\n')
    prompt_lines.append("\nPersonality analysis:")
    return "".join(prompt_lines)

# Analyze with GPT
def analyze_personality(detailed_songs):
    prompt = format_features_for_prompt(detailed_songs)
    print(prompt)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{'role':'developer', 'content':'Keept it fun, make assumptions'},{"role": "user", "content": prompt}],
        temperature=0.8,
        max_completion_tokens=700
    )
    return response.choices[0].message.content
    

# Main
if __name__ == "__main__":
    print("Fetching your top Spotify tracks and audio features...")
    songs = get_top_tracks_with_features(limit=10)
    print(f'your top 20 songs are: {[i['name'] for i in songs]}')
    print("\nAnalyzing your musical taste with audio features...\n")
    analysis = analyze_personality(songs)
    print(analysis)
    with open('responses.md', 'a') as response_file:
        response_file.write(analysis + '\n\n\n')
