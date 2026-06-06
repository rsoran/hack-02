# 🌱 MindEase - Student Mental Well-being Companion

MindEase is a lightweight, responsive, and visually soothing web companion built to support students preparing for high-stakes competitive entrance exams (**JEE, NEET, UPSC, CAT, GATE, CUET**) and board results seasons. It combines interactive, stress-reducing tools with AI-powered coping strategies and features popular anime themes to keep students motivated and focused on their well-being.

---

## ✨ Features

- **🧠 AI Wellness Coach**: Personalized wellness recommendations powered by the Google Gemini API (`gemini-2.5-flash`). Analyzes user mood, exam type, specific triggers, and current hobbies to build a custom wellbeing roadmap.
- **🧘 Interactive Box Breathing Guide**: A visual, interactive 16-second box breathing assistant (Inhale, Hold, Exhale, Hold) that dynamically animates to help students regulate cortisol levels and reduce exam anxiety instantly.
- **💧 Daily Self-Care Goals Checklist**: A micro-habit tracker to encourage healthy student routines (hydration, stretch breaks, sleep, and hobbies).
- **🏮 Dynamic Anime Motivation Banner**: Displays random, context-aware motivational quotes from iconic anime characters (Naruto, Luffy, Goku, Deku) accompanied by floating background artwork and banner avatars.
- **💾 Advice Plan Exporter**: Direct local export of the AI-curated wellbeing action plan as a clean text file to keep as a handy self-care reference.
- **♿ Highly Accessible (WCAG 2.1)**: Built with semantic HTML, correct labeling structures, ARIA landmark identifiers, and high-contrast color systems suitable for long study hours.

---

## 🛠️ Tech Stack

- **Frontend**: 
  - Semantic HTML5 & CSS3 variables for maximum theme flexibility.
  - Modern pastel glassmorphism UI designed to soothe eye strain.
  - Vanilla JS for breathing controls, checklist logic, and visual transitions.
- **Backend**: 
  - **Flask (Python)**: Light API server serving static assets and proxying AI queries.
  - **Python Dotenv**: Standard local configuration loader.
  - **Google Generative AI SDK**: High-performance interface to the Gemini model.
- **Security & Efficiency**:
  - **Security Headers**: Strict CSP, X-Frame-Options, MIME-sniffing protection, and Referrer-Policy configured on all API responses.
  - **CORS Hardening**: Strict cross-origin specifications with disabled credential sharing.
  - **Asset Caching**: Cache-Control headers implemented for static resources to optimize loading speeds.

---

## 📁 Repository Structure

```tree
├── api/
│   ├── config.py             # Flask configuration classes
│   ├── index.py              # Main Flask server & route endpoints
│   └── wellbeing_advisor.py  # Gemini API advisor class & fallback generator
├── frontend/
│   ├── assets/               # Anime character transparent PNGs
│   ├── index.html            # Core frontend document
│   ├── script.js             # Client-side form routing and breathing logic
│   └── styles.css            # Pastel light glassmorphic styles
├── tests/
│   ├── test_api.py           # Unit tests for HTTP routes and caching
│   └── test_wellbeing_advisor.py # Unit tests for prompt logic and fallbacks
├── requirements.txt          # Python dependencies
├── vercel.json               # Serverless rewrites and routes configuration
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- A Google AI Studio Gemini API Key (get one from [Google AI Studio](https://aistudio.google.com/))

### Installation & Local Run

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rsoran/hack-02.git
   cd hack-02
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask Server**:
   ```bash
   python api/index.py
   ```
   Open your browser and navigate to `http://localhost:5005`.

---

## 🧪 Running Automated Tests

A comprehensive unit testing suite using the standard Python `unittest` library is provided under the `tests/` folder. It mocks API calls to ensure zero external dependency.

To execute tests:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 🌐 Production Deployment

The project is pre-configured for deployment on **Vercel** as a serverless Flask backend combined with static assets:

1. Import your repository into Vercel.
2. In **Project Settings > Environment Variables**, add your `GOOGLE_API_KEY`.
3. Vercel will build the `api/index.py` serverless functions and host the static files under the frontend directory seamlessly as per the `vercel.json` rewrites.
