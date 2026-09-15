<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=00f2fe,4facfe,00f2fe&height=200&section=header&text=J.A.R.V.I.S%202.0&fontSize=65&fontColor=FFFFFF&fontAlignY=38&desc=Just%20A%20Rather%20Very%20Intelligent%20System&descAlignY=60&descSize=20" width="100%"/>

<p>
  <img src="https://img.shields.io/badge/JARVIS-v2.0-00f2fe?style=for-the-badge&logo=react&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/AI-Google%20Gemini%202.5-8E75B2?style=for-the-badge&logo=google&logoColor=white"/>
</p>
<p>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white"/>
  <img src="https://img.shields.io/badge/Voice-Speech%20Recognition-FF6B35?style=for-the-badge&logo=microphone&logoColor=white"/>
  <img src="https://img.shields.io/badge/IoT-Smart%20Home%20Control-22C55E?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

<br/>

> ### *"Just like having your own Tony Stark AI assistant right inside your PC."*

<br/>

**J.A.R.V.I.S 2.0** is a state-of-the-art AI-powered desktop assistant and full system automation suite for Windows.  
Powered by **Google Gemini 2.5 Flash** with a stunning **Iron Man ARC Reactor HUD** interface.

<br/>

</div>

---

## 📖 Table of Contents

- [✨ Features](#-features)
- [🖥️ Interface Preview](#%EF%B8%8F-interface-preview)
- [🧠 AI & Voice Commands](#-ai--voice-commands)
- [🏗️ Architecture](#%EF%B8%8F-architecture)
- [🛠️ Tech Stack](#%EF%B8%8F-tech-stack)
- [🚀 Installation & Setup](#-installation--setup)
- [🎤 Sample Commands](#-sample-commands)
- [⚙️ Configuration](#%EF%B8%8F-configuration)
- [🛡️ Privacy & Security](#%EF%B8%8F-privacy--security)
- [📜 License](#-license)

---

## ✨ Features

<table>
<tr>
<td width="50%">

### ⚛️ 3D ARC Reactor HUD
- Animated 3D spinning reactor rings
- Multi-state visual feedback — *Standby, Listening, Thinking, Speaking*
- Real-time **audio waveform canvas** visualizer
- Glassmorphism, CRT scanlines & neon glow aesthetics

</td>
<td width="50%">

### 🤖 Gemini AI Engine
- **Google Gemini 2.5 Flash** with native tool/function calling
- **OpenRouter fallback** for multi-LLM high availability
- Hands-free **voice control** via Speech-to-Text
- Natural **Text-to-Speech** audio responses

</td>
</tr>
<tr>
<td>

### 💻 System & App Automation
- Open, focus, or close any Windows app by voice
- **WhatsApp auto-message** sender
- Browser tab & window management
- Volume, media, and power control (Shutdown / Restart / Sleep)
- Screen capture & note logging

</td>
<td>

### 📊 System Health Monitor
- Live **CPU, RAM, Disk & Battery** metrics
- Top resource-hogging process identification
- Real-time hardware bottleneck detection

</td>
</tr>
<tr>
<td>

### 🏠 Smart Home / IoT Hub
- Bedroom Light & Study Lamp control
- Living Room AC temperature control
- Smart Plug power switching
- All controllable by **voice or HUD click**

</td>
<td>

### 📅 Productivity Suite
- Calendar scheduling, listing & deletion
- AI email summarizer & draft generator
- Multi-step **Workflow Automation** macros
- Auto file organizer for Downloads / Desktop

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
Jarvis 2.0/
├── app.py                 # Flask server & Gemini tool-calling API routes
├── system_tools.py        # Windows OS automation & PowerShell integrations
├── start_jarvis.bat       # One-click launcher (auto venv + dependency setup)
├── requirements.txt       # Python dependencies
├── .env                   # API key configuration (not committed to git)
├── jarvis_calendar.json   # Calendar event database
├── jarvis_workflows.json  # Saved multi-step automation macros
├── jarvis_iot.json        # Smart home device state persistence
└── templates/
    └── index.html         # 3D ARC Reactor HUD (HTML5, CSS3, JS)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|:---|:---|
| **Backend** | Python 3.9+, Flask 3.0, Flask-CORS, python-dotenv |
| **AI Engine** | Google Generative AI SDK, Gemini 2.5 Flash, OpenRouter |
| **System Tools** | psutil, pyautogui, PowerShell GDI+, WScript.Shell |
| **Frontend** | HTML5, Vanilla CSS3 (3D transforms, glassmorphism), JavaScript |
| **Browser APIs** | Web Audio API, Web Speech API, Canvas API |
| **Fonts** | Orbitron, Share Tech Mono, Outfit (Google Fonts) |

---

## 🚀 Installation & Setup

### ✅ Prerequisites

| Requirement | Details |
|:---|:---|
| Operating System | Windows 10 / Windows 11 |
| Python | 3.9 or higher (added to system PATH) |
| API Key | [Google Gemini API Key](https://aistudio.google.com/) — Free |
| Browser | Chrome / Edge (latest) |

---

### ⚡ Quick Start (Recommended)

**1. Clone the repository**
```bash
git clone https://github.com/jeetvaghela16/J.A.R.V.I.S.git
cd J.A.R.V.I.S
```

**2. Double-click `start_jarvis.bat`**

The launcher automatically:
- Creates a Python virtual environment
- Installs all dependencies from `requirements.txt`
- Starts the Flask server

**3. Open the HUD in your browser**
```
http://127.0.0.1:5000
```

**4. Enter your Gemini API Key** in the setup modal when prompted, or add it manually to `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

### 🔧 Manual Setup

```bash
# Step 1 — Create virtual environment
python -m venv venv

# Step 2 — Activate (Command Prompt)
venv\Scripts\activate

# Step 3 — Install dependencies
pip install -r requirements.txt

# Step 4 — Add API key to .env
echo GEMINI_API_KEY=your_actual_api_key > .env

# Step 5 — Run JARVIS
python app.py
```

---

## 🎤 Sample Commands

| Category | Example Command | What JARVIS Does |
|:---|:---|:---|
| **App Control** | *"Open Google Chrome"* | Launches Chrome |
| **App Control** | *"Close Spotify"* | Terminates Spotify process |
| **WhatsApp** | *"Send message to John saying I'll call you later"* | Auto-sends WhatsApp message |
| **Volume** | *"Set volume to 60%"* | Adjusts system audio |
| **Volume** | *"Mute audio"* | Instantly mutes sound |
| **Media** | *"Play next track"* | Sends media next key |
| **Screenshot** | *"Take a screenshot"* | Saves PNG, opens image |
| **System Info** | *"What is my CPU and RAM usage?"* | Reads hardware metrics aloud |
| **Web Search** | *"Search quantum computing on YouTube"* | Opens browser to results |
| **Power** | *"Shutdown the laptop"* | Executes Windows shutdown |
| **Calendar** | *"Add event Team Sync at 3 PM tomorrow"* | Schedules calendar event |
| **IoT** | *"Turn on bedroom light"* | Toggles smart device |
| **IoT** | *"Set AC temperature to 22"* | Adjusts smart thermostat |
| **Productivity** | *"Organise my Downloads folder"* | Auto-sorts files into folders |

---

## ⚙️ Configuration

### Windows Autostart on Boot
Enable or disable JARVIS launching on Windows startup directly from the HUD settings panel or via the API:
```
GET /api/settings/autostart
```

### OpenRouter Fallback
If your Gemini API credits are low, JARVIS automatically falls back to OpenRouter. Add your OpenRouter key to `.env`:
```env
GEMINI_API_KEY=your_gemini_key
OPENROUTER_API_KEY=your_openrouter_key
```

---

## 🛡️ Privacy & Security

- ✅ All automation tools run **100% locally** on your system
- ✅ Your `GEMINI_API_KEY` is stored in `.env` — **never committed** to Git (`.gitignore` protected)
- ✅ No user data is sent to any third-party server except the Gemini API for AI inference
- ✅ Voice processing uses the **browser's native Web Speech API** — no audio is recorded or stored

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=4facfe,00f2fe,4facfe&height=120&section=footer" width="100%"/>

**Built with ❤️ for AI Automation & Iron Man fans everywhere**

*Developed by **Jeet Vaghela***

<br/>

⭐ **If JARVIS impressed you, drop a star!** ⭐

</div>
