# Aria Avatar Companion for NVIDIA G-Assist

  <p align="center">
    <img src="https://github.com/user-attachments/assets/15e7e074-ee79-48e6-810c-8c504642491d" alt="Aria Avatar
  Companion" width="600">
  </p>

  An anime-style avatar companion plugin for NVIDIA G-Assist that brings your gaming experience to life with an
  interactive AI friend powered by Google Gemini.

  ## ✨ Features

  - **Interactive Avatar**: Cute anime-style character with emotion-responsive animations
  - **AI-Powered Chat**: Natural conversations powered by Google Gemini AI
  - **Visual Speech Bubbles**: Manga-style chat bubbles above the avatar
  - **Multi-Language Support**: Automatic language detection (English/Turkish)
  - **Draggable Overlay**: Position Aria anywhere on your screen
  - **Emotion System**: Dynamic expressions based on conversation context
  - **Gaming Companion**: Get gaming tips, strategies, and friendly support

  ## 📋 Requirements

  - Windows 10/11
  - NVIDIA G-Assist
  - Python 3.10+
  - Google Gemini API key

  ## 🚀 Quick Start

  ### Installation

  1. **Clone the Repository**
     ```bash
     git clone https://github.com/c3nx/g-assist-aria.git
     cd g-assist-aria

  2. Install Dependencies
  pip install -r requirements.txt
  3. Build the Plugin
  python build.py
  4. Install to G-Assist
  Copy all files from the dist folder to: %PROGRAMDATA%\NVIDIA Corporation\nvtopps\rise\plugins\aria
  5. Add Your API Key
    - Get a free API key from https://makersuite.google.com/app/apikey
    - Create a file named gemini.key in the plugin directory
    - Paste your API key into this file
  6. Restart G-Assist

  Note: Building from source avoids Windows Defender false positive warnings that may occur with pre-compiled
  releases.

  Usage

  Simply chat with Aria using the G-Assist command:
  /aria chat Hello! How are you today?

  Special Commands

  - Show Avatar: /aria chat show
  - Hide Avatar: /aria chat hide

  🎨 Customization

  Using Your Own Sprite

  1. Create a 5x2 grid sprite sheet (PNG format)
  2. Each frame should be the same size
  3. Place it in the sprites folder as aria.png

  Frame Layout:
  [0: Idle]    [1: Happy]   [2: Angry]   [3: Greeting] [4: Sad]
  [5: Extra 1] [6: Extra 2] [7: Extra 3] [8: Extra 4]  [9: Speaking]

  Configuration

  Edit config.json to customize:
  - Avatar position and size
  - Speech bubble duration
  - Emotion mappings
  - Language preferences
  - And more!

  🛠️ Building from Source

  Prerequisites

  pip install -r requirements.txt

  Running from Source

  python plugin.py

  Building Executable

  python build.py

  This creates a distributable package with all necessary files.

  📁 Project Structure

  aria-avatar-companion/
  ├── plugin.py              # Main plugin file
  ├── canvas_overlay.py      # Avatar overlay window
  ├── manifest.json          # Plugin metadata
  ├── config.json           # Configuration file
  ├── requirements.txt      # Python dependencies
  ├── build.py             # Build script
  ├── sprites/
  │   └── aria.png         # Default sprite sheet
  └── assets/
      └── aria_icon.png    # Plugin icon

  🤝 Contributing

  Contributions are welcome! Please feel free to submit a Pull Request.

  Development Guidelines

  1. Follow the existing code style
  2. Test your changes thoroughly
  3. Update documentation as needed
  4. Submit PR with a clear description

  🐛 Troubleshooting

  Avatar Not Appearing

  - Check if PyQt5 is installed: pip install PyQt5
  - Verify the sprite file exists in the correct location
  - Check aria_plugin.log for errors
  - Try windowed or fullscreen windowed options in the game menu.

  API Errors

  - Verify your Gemini API key is valid
  - Check internet connection
  - Ensure the API key file has no extra spaces or newlines

  Text Truncation

  - Update to the latest version
  - Check the log file for chunk processing errors

  📜 License

  This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

  🙏 Acknowledgments

  - NVIDIA for the G-Assist platform
  - Google for Gemini AI API
  - The anime and gaming community for inspiration

  📞 Support

  - Issues: https://github.com/c3nx/g-assist-aria/issues
  - Discussions: https://github.com/c3nx/g-assist-aria/discussions
  - G-Assist Forums: https://forums.developer.nvidia.com/
