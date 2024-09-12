# Stigmata Protocol

Welcome to the Stigmata Protocol repository! Stigmata Protocol is a Discord bot integrated with OpenAI's Meta-Llama model, designed to create engaging and personalized interactions within Discord servers. The bot offers functionalities for channel-specific interactions, personalized responses, and automatic status updates. 

## Features

- **Channel-Specific Interaction**: Configure the bot to respond only in designated channels.
- **Personalized Responses**: The bot adapts its responses based on user information and preferences.
- **Status Updates**: Regularly updates its status to keep interactions engaging.
- **Error Handling**: Robust error handling ensures smooth operation and user feedback.

## Prerequisites

Before running the bot, make sure you have the following installed:

- Python 3.8 or later
- Required Python packages (listed in `requirements.txt`)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/instax-dutta/Stigmata-Protocol
   cd Stigmata-Protocol
   ```

2. **Install Dependencies**

   Create a virtual environment and install the required packages:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**

   Create a `.env` file in the root directory of the project and add your Discord bot token and OpenAI API key:

   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Run the Bot**

   ```bash
   python app.py
   ```

## Commands

- `!setchannel <channel>`: Set the channel where the bot will respond. Requires admin permissions.
- `!addchannel <channel>`: Add a channel to the allowed list. Requires admin permissions.
- `!removechannel <channel>`: Remove a channel from the allowed list. Requires admin permissions.

## Configuration

The bot maintains two configuration files:

- `allowed_channels.json`: Stores the allowed channel IDs for each guild.
- `memory.json`: Stores user-specific information for personalized responses.

## Code Overview

- **`app.py`**: Main bot script that handles command processing, message handling, and status updates.
- **`requirements.txt`**: Lists the Python packages required to run the bot.
- **`config.json`**: Contains configuration data (e.g., allowed channels).

## Error Handling

In case of errors, the bot will log the error details. Common issues include:

- Incorrect or missing environment variables.
- Network issues when accessing OpenAI's API.

## Contributing

If you'd like to contribute to the Stigmata Protocol project, please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or support, please reach out to [contact@sdad.pro].
