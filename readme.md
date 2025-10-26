# Spotify Checker 🎵

A fun little Spotify "now playing" visualizer that displays album art with a rotating animation in a fullscreen window.

**Originally built for a round screen display on a Raspberry Pi or ESP32** - hence the circular album art and 640x640 resolution!

## ⚠️ Disclaimer

This is just a **proof of concept** made for fun! No energy went into making it perfectly optimized or production-ready. It does what it's supposed to do, and that's about it. 😄

*P.S. This README was written by AI because I couldn't be bothered to write it myself.* 🤖

## What It Does

- Monitors your Spotify playback in real-time
- Displays the current song's album art in a fullscreen window
- Rotates the album art when music is playing (perfect for round displays!)
- Shows song title and artist name
- Automatically refreshes when the track changes

## Hardware Target

This project was designed with a **round LCD screen** in mind, intended to run on:
- Raspberry Pi (any model with a display)
- ESP32 with display support
- Or just your regular computer if you want to try it out!

The circular cropping and 640x640 resolution were specifically chosen to match round display panels.

## Prerequisites

- Python 3.13+ (or whatever Python version your Raspberry Pi/ESP supports)
- A Spotify account
- Spotify API credentials (see setup below)

## Setting Up Spotify API

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **"Create app"**
4. Fill in the app details:
   - **App name**: Whatever you want (e.g., "Spotify Checker")
   - **App description**: Anything you like
   - **Redirect URI**: `http://google.com/callback/` (important!)
   - **APIs used**: Select "Web API"
5. Accept the terms and click **"Save"**
6. In your app's settings, you'll find:
   - **Client ID**
   - **Client Secret** (click "View client secret")
7. Copy both values for the next step

## Installation

1. Clone or download this repository

2. Create a `.env` file in the project root with the following content:
   ```
   API_CLIENT_ID=your_client_id_here
   API_SECRET=your_client_secret_here
   TOKEN=
   REFRESH=
   ```
   Replace `your_client_id_here` and `your_client_secret_here` with the values from your Spotify app.

3. Install dependencies (a virtual environment is already configured):
   ```bash
   pip install pillow requests python-dotenv
   ```

## Usage

1. Run the script:
   ```bash
   python main.py
   ```

2. On first run, you'll be prompted to authorize the app:
   - A URL will be printed in the console
   - Copy and paste it into your browser
   - Log in to Spotify and authorize the app
   - You'll be redirected to Google (which will show an error page - that's expected!)
   - Copy the **entire URL** from your browser's address bar
   - Paste it back into the console

3. The application will save your tokens in the `.env` file for future use

4. A fullscreen window will open showing your current Spotify playback

5. Press `Alt+F4` or close the window to exit

## Features

- **Token Management**: Automatically refreshes expired tokens
- **Real-time Updates**: Checks for song changes every 2 seconds
- **Smooth Animation**: Rotating album art with 360 pre-rendered frames
- **Circular Album Art**: Specifically designed for round displays!
- **Playback Detection**: Only rotates when music is actually playing

## Project Structure
