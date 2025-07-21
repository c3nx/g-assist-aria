# Aria Avatar Companion for NVIDIA G-Assist

<p align="center">
  <img src="assets/aria_banner.png" alt="Aria Avatar Companion" width="600">
</p>

An anime-style avatar companion plugin for NVIDIA G-Assist that brings your gaming experience to life with an interactive AI friend powered by Google Gemini.

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
- Python 3.10+ (if running from source)
- Google Gemini API key

## 🚀 Quick Start

### Installation

1. **Download the Plugin**
   - Download the latest release from [Releases](https://github.com/yourusername/aria-avatar-companion/releases)
   - Extract the ZIP file

2. **Install to G-Assist**
   ```
   Copy all files to: %PROGRAMDATA%\NVIDIA Corporation\nvtopps\rise\plugins\aria
   ```

3. **Add Your API Key**
   - Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a file named `gemini.key` in the plugin directory
   - Paste your API key into this file

4. **Restart G-Assist**

### Usage

Simply chat with Aria using the G-Assist command:
```
/aria chat Hello! How are you today?
```

### Special Commands

- **Show Avatar**: `/aria chat show`
- **Hide Avatar**: `/aria chat hide`
- **Set Language Turkish**: `/aria chat türkçe konuş`
- **Set Language English**: `/aria chat speak english`
- **Auto Language Mode**: `/aria chat auto language`

## 🎨 Customization

### Using Your Own Sprite

1. Create a 5x2 grid sprite sheet (PNG format)
2. Each frame should be the same size
3. Place it in the `sprites` folder as `aria.png`

Frame Layout:
```
[0: Idle]    [1: Happy]   [2: Angry]   [3: Greeting] [4: Sad]
[5: Extra 1] [6: Extra 2] [7: Extra 3] [8: Extra 4]  [9: Speaking]
```

### Configuration

Edit `config.json` to customize:
- Avatar position and size
- Speech bubble duration
- Emotion mappings
- Language preferences
- And more!

## 🛠️ Building from Source

### Prerequisites

```bash
pip install -r requirements.txt
```

### Running from Source

```bash
python plugin.py
```

### Building Executable

```bash
python build.py
```

This creates a distributable package with all necessary files.

## 📁 Project Structure

```
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
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines

1. Follow the existing code style
2. Test your changes thoroughly
3. Update documentation as needed
4. Submit PR with clear description

## 🐛 Troubleshooting

### Avatar Not Appearing
- Check if PyQt5 is installed: `pip install PyQt5`
- Verify sprite file exists in correct location
- Check `aria_plugin.log` for errors
- Try windowed or fullscreen windowed options in game menu.

### API Errors
- Verify your Gemini API key is valid
- Check internet connection
- Ensure API key file has no extra spaces or newlines

### Text Truncation
- Update to the latest version
- Check log file for chunk processing errors

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NVIDIA for G-Assist platform
- Google for Gemini AI API
- The anime and gaming community for inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/aria-avatar-companion/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/aria-avatar-companion/discussions)
- **G-Assist Forums**: [NVIDIA Forums](https://forums.developer.nvidia.com/)

---

<p align="center">
  Made with ❤️ for the gaming community
</p>
