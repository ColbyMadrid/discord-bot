Zyrix Music Bot 🎶


Zyrix is a powerful and versatile Discord bot built for playing music directly in your server’s voice channels. With features like queue management, playback controls, volume adjustment, and more, Zyrix makes it easy to bring music to your Discord community.

  ## Features

  - 🎶 Play Music from YouTube links.

  - 📜 Queue Management for viewing, adding, and organizing songs.

  - ⏸️ Playback Controls including play, pause, resume, and skip.

  - 🔊 Volume Control to adjust the bot's volume.

  - 🔁 Replay and Shuffle options to replay the last song or shuffle the queue.

  - ❌ Queue Clearing and Song Removal commands.

  - ✅ Easy to set up and fully customizable.

## Commands
| Command          | Description                                              |
|------------------|----------------------------------------------------------|
| `!join`          | Make the bot join your current voice channel             |
| `!leave`         | Disconnect the bot from the voice channel                |
| `!play <url>`    | Play audio from a YouTube link                           |
| `!pause`         | Pause the current song                                   |
| `!resume`        | Resume the paused song                                   |
| `!skip`          | Skip to the next song in the queue                       |
| `!volume <0-100>`| Set the volume level (default is 50%)                    |
| `!queue`         | View the current song queue                              |
| `!replay`        | Replay the last played song                              |
| `!shuffle`       | Shuffle the current queue                                |
| `!clear`         | Clear all songs from the queue                           |
| `!remove <index>`| Remove a specific song from the queue by its position    |
| `!commands`      | Display the list of available commands                   |


## Installation

Follow these steps to set up and run the Zyrix Music Bot on your local machine:

### Prerequisites
- [Python 3.8+](https://www.python.org/downloads/) must be installed on your system.
- [FFmpeg](https://ffmpeg.org/download.html) is required for audio processing. Make sure it is added to your system's PATH.

### Steps
1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/zyrix-music-bot.git
    cd zyrix-music-bot
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**:
   - For **Windows**:
      ```bash
      source venv\Scripts\activate
      ```
   - For **MacOS/Linux**:
      ```bash
      source venv/bin/activate
      ```

4. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Set up environment variables**:
    - Create a `.env` file in the root directory of the project.
    - Inside `.env`, set your bot token:
      ```plaintext
      DISCORD_TOKEN=your_discord_bot_token_here
      ```

6. **Run the bot**:
    ```bash
    python bot.py
    ```

### Notes
- Ensure the bot has permission to join and play audio in your Discord server.
- You can invite the bot to your server with the appropriate permissions via the Discord Developer Portal.

After completing these steps, Zyrix Music Bot should be up and running in your Discord server!

## Contributing

Feel free to fork the repository and submit pull requests if you'd like to contribute new features, improvements, or bug fixes.

## License

Zyrix Music Bot is open source under the MIT License.

## Support

For questions, suggestions, or troubleshooting, please open an issue or reach out in the discussions section on GitHub.

Enjoy using Zyrix Music Bot to bring music to your Discord server! 🎉