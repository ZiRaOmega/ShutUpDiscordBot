# ShutUpBot

**ShutUpBot** is a Discord bot that monitors users in voice channels, enforcing time limits on speaking. Users exceeding the limit are automatically muted and unmuted after a specified duration. The bot also gracefully unmutes all users on shutdown to ensure no one remains muted.

## Features

- Monitors users in voice channels and enforces speaking time limits.
- Automatically mutes users who exceed their allotted time.
- Incrementally increases mute duration for repeated offenses.
- Automatically unmuted after the mute period.
- Ensures all users are unmuted upon bot shutdown.

## Setup

### Prerequisites
- **Python 3.10+**
- **discord.py 2.x** (`pip install discord.py`)
- **.env file** with:
  - `BOT_TOKEN`: Discord bot token.
  - `CHANNEL_ID`: Voice channel ID to monitor.
  - `MAX_TALK_DURATION`: Maximum allowed talk time (seconds).
  - `mute_threshold`: Mute  duration threshold (seconds).
  - `base_mute_duration`:  Base mute duration (seconds).
### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ShutUpBot.git
   cd ShutUpBot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create .env file**:
   ```bash
   BOT_TOKEN=your_discord_bot_token
   CHANNEL_ID=your_voice_channel_id
   MAX_TALK_DURATION=300
   mute_threshold=60
   base_mute_duration=30
   ```

### Run the Bot
```bash
python3 main.py
```

### Commands

- `!monitor @user`: Start monitoring a user in the voice channel.
- `!unmonitor @user`: Stop monitoring a user.
- `!unmute @user`: Manually unmute a user.
- `!ping`: Check if the bot is online.

## Troubleshooting

### Common Issues

- **Timeout Errors During Voice Connection**:
  If you encounter `TimeoutError` while trying to connect to a voice channel, try increasing the timeout duration in the `connect_to_channel()` function or check the bot’s permissions in the server.

- **Permissions**:
  Ensure the bot has the following permissions in the voice channel:
  - `Connect`
  - `Speak`

- **Bot Fails to Start**:
  Ensure your `.env` file is correctly set up with the required `BOT_TOKEN`, `CHANNEL_ID`,`MAX_TALK_DURATION`,  `mute_threshold`, and `base_mute_duration` variables.

### Logs
If the bot crashes or doesn't work as expected, check the logs to identify the issue. Logs are printed directly in the console.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
