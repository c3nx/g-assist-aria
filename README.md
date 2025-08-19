# 🌸 Aria Avatar Companion for NVIDIA G-Assist

<p align="center">
  <img src="https://github.com/user-attachments/assets/15e7e074-ee79-48e6-810c-8c504642491d" alt="Aria Avatar Companion" width="600">
</p>

<p align="center">
  <strong>An AI-powered anime companion that lives on your screen</strong><br>
  Powered by Google Gemini and NVIDIA G-Assist
</p>

<p align="center">
  <a href="https://github.com/c3nx/g-assist-aria/releases"><img src="https://img.shields.io/github/v/release/c3nx/g-assist-aria" alt="Release"></a>
  <a href="https://github.com/c3nx/g-assist-aria/blob/main/LICENSE"><img src="https://img.shields.io/github/license/c3nx/g-assist-aria" alt="License"></a>
  <a href="https://github.com/c3nx/g-assist-aria/issues"><img src="https://img.shields.io/github/issues/c3nx/g-assist-aria" alt="Issues"></a>
</p>

---

## 🎯 What is Aria?

Aria is your personal anime gaming companion - a cute, interactive avatar that responds to your chat with emotions, personality, and helpful gaming advice. She appears as a draggable overlay on your screen and uses AI to have natural conversations with you while you game.

## ✨ Features

- 🤖 **AI-Powered Conversations** - Natural chat using Google Gemini
- 🎭 **Emotion System** - Responsive animations based on conversation context
- 💬 **Speech Bubbles** - Manga-style chat bubbles with personality
- 🌍 **Multi-Language** - Auto-detects and responds in your language (English/Turkish)
- 🎮 **Gaming Companion** - Get tips, strategies, and encouragement
- 📍 **Draggable Overlay** - Position Aria anywhere on your screen
- 🔧 **Enhanced Error Handling** - User-friendly setup with helpful error messages
- 📦 **Easy Installation** - One-click setup with pre-built releases

## 📋 Requirements

- **Windows 10/11**
- **NVIDIA G-Assist** (installed and running)
- **Google Gemini API Key** (free from Google AI Studio)

## 📦 Installation

### Option 1: Pre-built Release (Recommended)

1. **Download** the latest release:
   ```
   📥 Download aria_avatar_companion_v1.1.0.zip from:
   https://github.com/c3nx/g-assist-aria/releases
   ```

2. **Extract** to G-Assist plugins directory:
   ```
   Extract to: %PROGRAMDATA%\NVIDIA Corporation\nvtopps\rise\plugins\
   ```
   
   ✅ **Correct folder structure:**
   ```
   📁 %PROGRAMDATA%\NVIDIA Corporation\nvtopps\rise\plugins\
   └── 📁 aria\
       ├── aria_companion.exe
       ├── manifest.json
       ├── sprites\
       └── gemini.key.example
   ```

3. **Get your API key:**
   - Visit: https://aistudio.google.com/app/apikey
   - Create a new API key (free)
   - Copy the key

4. **Create gemini.key file:**
   ```
   📁 In the aria folder, create a new file named exactly: gemini.key
   ⚠️ NOT gemini.key.txt - just gemini.key
   📝 Paste your API key inside this file
   ```

5. **Restart G-Assist**

### Option 2: Build from Source

```bash
git clone https://github.com/c3nx/g-assist-aria.git
cd g-assist-aria
pip install -r requirements.txt
python build.py
```

## 🎮 Usage

Once installed, chat with Aria using G-Assist:

```
/aria hi there!
/aria how are you feeling today?
/aria show yourself
/aria give me some gaming tips
```

### Special Commands

- **Show Avatar:** `/aria show` or `/aria show yourself`
- **Hide Avatar:** `/aria hide` or `/aria go away`
- **Language Settings:**
  - `/aria speak turkish` - Switch to Turkish
  - `/aria speak english` - Switch to English
  - `/aria auto language` - Auto-detect language

## 🔧 Troubleshooting

### ❌ "Gemini API not configured" Error

**Problem:** Plugin can't find or read your API key

**Solutions:**
- ✅ Check if `gemini.key` file exists (NOT `gemini.key.txt`)
- ✅ Verify API key is valid and has no extra spaces
- ✅ Get a new key from: https://aistudio.google.com/app/apikey

### ❌ "No message provided" Error

**Problem:** Plugin recognizes commands but can't read messages

**Solution:** 
- ✅ Update to v1.1.0+ (this was a compatibility bug)

### ❌ Avatar Not Showing

**Causes & Solutions:**
- 🎮 **Game mode:** Run games in Windowed or Borderless Windowed mode
- 🛡️ **Windows Defender:** Check if overlay was blocked, add exception
- 📁 **Missing sprites:** Verify `sprites/aria.png` exists

### ❌ Turkish Characters Look Broken

**Status:** Known issue, fix coming in next update
**Temporary fix:** Use English mode with `/aria speak english`

### ❌ Found gemini.key.txt instead of gemini.key

**Problem:** File extension is wrong
**Solution:** Rename file to remove `.txt` extension

## 🎨 Customization

### Using Your Own Avatar Sprite

1. Create a **5x2 grid** sprite sheet (PNG format)
2. Each frame should be the same size (recommended: 64x64px)
3. Save as `sprites/aria.png`

**Frame Layout:**
```
[0: Idle]    [1: Happy]   [2: Angry]   [3: Greeting] [4: Sad]
[5: Extra 1] [6: Extra 2] [7: Extra 3] [8: Extra 4]  [9: Speaking]
```

### Configuration

Edit `config.json` to customize:
- Avatar size and position
- Speech bubble duration
- Emotion mappings
- Animation timing

## 📁 Project Structure

```
g-assist-aria/
├── 📄 plugin.py              # Main plugin logic
├── 📄 canvas_overlay.py      # Avatar overlay window
├── 📄 manifest.json          # G-Assist plugin metadata
├── 📄 config.json           # Configuration settings
├── 📄 build.py             # Build script
├── 📄 requirements.txt     # Python dependencies
├── 📁 sprites/
│   └── 📄 aria.png         # Default avatar sprite sheet
└── 📁 assets/              # Additional assets
```

## 📝 Changelog

### v1.1.0 (2024-01-20) - Enhanced Compatibility Update
- ✅ **FIXED:** G-Assist parameter passing compatibility
- ✅ **FIXED:** "No message provided" error
- ✅ **ADDED:** Intelligent API key detection (handles .txt mistakes)
- ✅ **ADDED:** User-friendly error messages with help links
- ✅ **IMPROVED:** Build system and folder structure
- ✅ **UPDATED:** Documentation and troubleshooting

### v1.0.0 - Initial Release
- 🎉 Initial release with basic functionality

## 🤝 Contributing

Contributions are welcome! Please check the [Issues](https://github.com/c3nx/g-assist-aria/issues) page for ways to help.

### Development Setup
```bash
git clone https://github.com/c3nx/g-assist-aria.git
cd g-assist-aria
pip install -r requirements.txt
python plugin.py  # Run from source
```

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NVIDIA** for the G-Assist platform
- **Google** for Gemini AI API
- **The anime and gaming community** for inspiration

## 📞 Support & Community

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/c3nx/g-assist-aria/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/c3nx/g-assist-aria/discussions)
- 🎮 **G-Assist Community:** [NVIDIA Developer Forums](https://forums.developer.nvidia.com/)

---

<p align="center">
  Made with ❤️ for the gaming community
</p>