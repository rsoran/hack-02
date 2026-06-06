// Configuration
const API_BASE_URL = '';

// DOM Elements
const wellbeingForm = document.getElementById('wellbeingForm');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const formSection = document.getElementById('formSection');

// Results elements
const empathyText = document.getElementById('empathyText');
const insightsText = document.getElementById('insightsText');
const copingList = document.getElementById('copingList');
const hobbyText = document.getElementById('hobbyText');
const affirmationText = document.getElementById('affirmationText');
const actionList = document.getElementById('actionList');

// Breathing Helper Elements
const btnBreathe = document.getElementById('btnBreathe');
const btnResetBreathe = document.getElementById('btnResetBreathe');
const breathingCircle = document.getElementById('breathingCircle');
const breathingText = document.getElementById('breathingText');

// Breathing Timer State
let breathingInterval = null;
let breathingTick = 0; // 0 to 15 seconds box cycle

// Global storage for translation and download
let currentEnglishPlan = null;
let currentHindiPlan = null;
let currentLanguage = 'en'; // 'en' or 'hi'
let isTranslating = false;

window.currentAdvicePlan = null;

// Anime Quotes Database
const CHARACTER_QUOTES = [
    {
        name: "Naruto Uzumaki",
        anime: "Naruto",
        avatar: "assets/naruto.png",
        quote: "If you don't like your destiny, don't accept it. Instead, have the courage to change it the way you want it to be!"
    },
    {
        name: "Naruto Uzumaki",
        anime: "Naruto",
        avatar: "assets/naruto.png",
        quote: "Failing doesn't give you a reason to give up, as long as you believe."
    },
    {
        name: "Monkey D. Luffy",
        anime: "One Piece",
        avatar: "assets/luffy.png",
        quote: "If you don't take risks, you can't create a future!"
    },
    {
        name: "Monkey D. Luffy",
        anime: "One Piece",
        avatar: "assets/luffy.png",
        quote: "No matter how hard or how impossible it is, never lose sight of your goal!"
    },
    {
        name: "Son Goku",
        anime: "Dragon Ball",
        avatar: "assets/goku.png",
        quote: "Power comes in response to a need, not a desire. You have to create that need!"
    },
    {
        name: "Son Goku",
        anime: "Dragon Ball",
        avatar: "assets/goku.png",
        quote: "Limit-break! Every obstacle is just a chance to push past your previous self."
    },
    {
        name: "Izuku Midoriya (Deku)",
        anime: "My Hero Academia",
        avatar: "assets/deku.png",
        quote: "Sometimes I do feel like a failure... but even so, I'll keep going!"
    },
    {
        name: "Izuku Midoriya (Deku)",
        anime: "My Hero Academia",
        avatar: "assets/deku.png",
        quote: "A hero is someone who overcomes every obstacle and keeps moving forward, no matter what!"
    },
    {
        name: "Tanjiro Kamado",
        anime: "Demon Slayer",
        avatar: "assets/tanjiro.png",
        quote: "No matter how many people you may lose, you have no choice but to go on living. No matter how devastating the blows may be."
    },
    {
        name: "Tanjiro Kamado",
        anime: "Demon Slayer",
        avatar: "assets/tanjiro.png",
        quote: "I can do it. I know I can do it. I'm the guy who gets it done, broken bones or not! I will keep moving!"
    },
    {
        name: "Nezuko Kamado",
        anime: "Demon Slayer",
        avatar: "assets/nezuko.png",
        quote: "Breathe in, stay strong. Protecting those we love gives us the power to overcome any challenge!"
    },
    {
        name: "Zenitsu Agatsuma",
        anime: "Demon Slayer",
        avatar: "assets/zenitsu.png",
        quote: "If you can only do one thing, hone it to perfection! Hone it to the utmost limit!"
    },
    {
        name: "Zenitsu Agatsuma",
        anime: "Demon Slayer",
        avatar: "assets/zenitsu.png",
        quote: "Don't give up! Even if it's painful, even if it's tough, don't try to take the easy way out!"
    }
];

const DEMON_SLAYER_CHARACTERS = [
    { name: "Tanjiro Kamado", avatar: "assets/tanjiro.png" },
    { name: "Nezuko Kamado", avatar: "assets/nezuko.png" },
    { name: "Zenitsu Agatsuma", avatar: "assets/zenitsu.png" }
];

const SHONEN_CHARACTERS = [
    { name: "Naruto Uzumaki", avatar: "assets/naruto.png" },
    { name: "Monkey D. Luffy", avatar: "assets/luffy.png" },
    { name: "Son Goku", avatar: "assets/goku.png" },
    { name: "Izuku Midoriya (Deku)", avatar: "assets/deku.png" }
];

function selectRandomCharacters() {
    const randomItem = CHARACTER_QUOTES[Math.floor(Math.random() * CHARACTER_QUOTES.length)];
    
    const quoteEl = document.getElementById('motivationQuote');
    const authorEl = document.getElementById('quoteAuthor');
    const avatarEl = document.getElementById('characterAvatar');
    const bgCharEl = document.getElementById('floatingCharacter');
    const bgCharLeftEl = document.getElementById('floatingCharacterLeft');
    
    if (quoteEl) quoteEl.textContent = randomItem.quote;
    if (authorEl) authorEl.textContent = `- ${randomItem.name} (${randomItem.anime})`;
    if (avatarEl) {
        avatarEl.src = randomItem.avatar;
        avatarEl.alt = randomItem.name;
    }
    
    // Choose Left Character (Demon Slayer) avoiding duplication with banner
    const leftChoices = DEMON_SLAYER_CHARACTERS.filter(c => c.name !== randomItem.name);
    const leftChar = leftChoices[Math.floor(Math.random() * leftChoices.length)];
    
    // Choose Right Character (Shonen) avoiding duplication with banner
    const rightChoices = SHONEN_CHARACTERS.filter(c => c.name !== randomItem.name);
    const rightChar = rightChoices[Math.floor(Math.random() * rightChoices.length)];
    
    if (bgCharEl) {
        bgCharEl.style.backgroundImage = `url('${rightChar.avatar}')`;
    }
    if (bgCharLeftEl) {
        bgCharLeftEl.style.backgroundImage = `url('${leftChar.avatar}')`;
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Select random anime characters for banner, left float, and right float
    selectRandomCharacters();

    // Load self-care checklist states
    const habitChecks = document.querySelectorAll('.habit-check');
    habitChecks.forEach(check => {
        const savedState = localStorage.getItem(`habit_${check.id}`);
        if (savedState !== null) {
            check.checked = savedState === 'true';
        }
        check.addEventListener('change', () => {
            localStorage.setItem(`habit_${check.id}`, check.checked);
        });
    });

    // Render mood history log
    renderHistory();

    wellbeingForm.addEventListener('submit', handleFormSubmit);
    btnBreathe.addEventListener('click', toggleBreathing);
    btnResetBreathe.addEventListener('click', resetBreathing);
});

/**
 * Handle Wellbeing form submit
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    // Get input values
    const moodEl = document.querySelector('input[name="mood"]:checked');
    const mood = moodEl ? moodEl.value : null;
    const exam = document.getElementById('examSelect').value;
    const triggers = Array.from(document.querySelectorAll('input[name="triggers"]:checked'))
        .map(el => el.value);
    const hobbies = Array.from(document.querySelectorAll('input[name="hobbies"]:checked'))
        .map(el => el.value);
    const journal = document.getElementById('journalInput').value.trim();

    // Basic Validation
    if (!mood || !exam) {
        alert('Please select your mood and the exam you are preparing for.');
        return;
    }

    showLoading();

    try {
        // Send request to Vercel Serverless Function
        const response = await fetch(`${API_BASE_URL}/api/analyze-wellbeing`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mood, exam, triggers, hobbies, journal })
        });

        if (!response.ok) {
            throw new Error(`Server returned code ${response.status}`);
        }

        const advicePlan = await response.json();
        
        // Cache the English plan
        currentEnglishPlan = advicePlan;
        currentHindiPlan = null;
        currentLanguage = 'en';
        
        const btnTrans = document.getElementById('btnTranslate');
        if (btnTrans) {
            btnTrans.textContent = "🌐 Translate to Hindi (हिंदी)";
        }
        
        // Cache for download
        window.currentAdvicePlan = advicePlan;

        // Reset display card animations
        triggerCardAnimations();

        // Populate and display results
        displayAdvicePlan(advicePlan);
        updateStressGauge(mood);
        showResults();

        // Save check-in to history
        saveCheckin(mood, exam);
    } catch (error) {
        console.error('Error fetching wellness plan:', error);
        showError('Could not retrieve your wellbeing plan right now. Please try again.');
    }
}

/**
 * Display the AI advice details in the UI
 */
function displayAdvicePlan(plan) {
    // 1. Empathy Statement
    empathyText.textContent = plan.empathy_statement || '';

    // 2. Insights
    insightsText.innerHTML = '';
    const insights = plan.insights || '';
    if (Array.isArray(insights)) {
        insights.forEach(insight => {
            const p = document.createElement('p');
            p.style.marginBottom = '10px';
            p.textContent = insight;
            insightsText.appendChild(p);
        });
    } else {
        insightsText.textContent = insights;
    }

    // 3. Coping Strategies
    copingList.innerHTML = '';
    const strategies = plan.coping_strategies || [];
    strategies.forEach(strategy => {
        const li = document.createElement('li');
        li.textContent = strategy;
        copingList.appendChild(li);
    });

    // 4. Hobby Integration
    hobbyText.textContent = plan.hobby_integration || 'Remember to take breaks to do things you love.';

    // 5. Custom Affirmation
    affirmationText.textContent = plan.custom_affirmation ? `“ ${plan.custom_affirmation} ”` : '';

    // 6. Action Items
    actionList.innerHTML = '';
    const actions = plan.suggested_actions || ['Practice breathing exercises', 'Take a 10 min break'];
    actions.forEach(action => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'action-item';
        itemDiv.textContent = action;
        actionList.appendChild(itemDiv);
    });
}

/**
 * Toggle language of the displayed plan between English and Hindi
 */
async function toggleLanguage() {
    if (isTranslating || !currentEnglishPlan) return;
    
    const btnTrans = document.getElementById('btnTranslate');
    
    if (currentLanguage === 'en') {
        // Switch to Hindi
        if (!currentHindiPlan) {
            isTranslating = true;
            if (btnTrans) btnTrans.textContent = "⌛ Translating... कृपया प्रतीक्षा करें...";
            
            try {
                currentHindiPlan = await translatePlanOnServer(currentEnglishPlan);
            } catch (err) {
                console.error("Translation failed:", err);
                alert("Translation failed. Please try again in a moment.");
                if (btnTrans) btnTrans.textContent = "🌐 Translate to Hindi (हिंदी)";
                isTranslating = false;
                return;
            }
            isTranslating = false;
        }
        
        // Display Hindi
        displayAdvicePlan(currentHindiPlan);
        currentLanguage = 'hi';
        window.currentAdvicePlan = currentHindiPlan;
        if (btnTrans) btnTrans.textContent = "🌐 View in English (अंग्रेजी)";
    } else {
        // Switch to English
        displayAdvicePlan(currentEnglishPlan);
        currentLanguage = 'en';
        window.currentAdvicePlan = currentEnglishPlan;
        if (btnTrans) btnTrans.textContent = "🌐 Translate to Hindi (हिंदी)";
    }
    
    // Trigger animations when toggle occurs
    triggerCardAnimations();
}

/**
 * Send English plan to server for Gemini-powered Hindi translation
 */
async function translatePlanOnServer(plan) {
    const response = await fetch(`${API_BASE_URL}/api/translate-wellbeing`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(plan)
    });
    
    if (!response.ok) {
        throw new Error("Failed to translate layout");
    }
    
    return await response.json();
}

/**
 * Update the visual Stress Level and Resilience Gauge
 */
function updateStressGauge(mood) {
    const gaugeBar = document.getElementById('gaugeBar');
    const gaugeValue = document.getElementById('gaugeValue');
    if (!gaugeBar || !gaugeValue) return;

    let width = '50%';
    let text = 'Moderate Stress';
    let color = '#d97706'; // Dark amber

    if (mood === 'Happy & Confident') {
        width = '20%';
        text = 'Low Stress / Stable';
        color = '#065f46'; // Dark green
    } else if (mood === 'Neutral & Calm') {
        width = '40%';
        text = 'Balanced / Stable';
        color = '#0e7490'; // Dark cyan
    } else if (mood === 'Anxious & Stressed') {
        width = '75%';
        text = 'High Stress';
        color = '#b45309'; // Warm amber
    } else if (mood === 'Sad & Doubting Myself') {
        width = '80%';
        text = 'High Self-Doubt / Low Resilience';
        color = '#be123c'; // Dark rose
    } else if (mood === 'Burned Out & Exhausted') {
        width = '95%';
        text = 'Extreme Burnout / Exhaustion';
        color = '#b91c1c'; // Dark red
    }

    // Apply animation properties
    gaugeBar.style.width = width;
    gaugeBar.style.backgroundColor = color;
    gaugeValue.textContent = text;
    gaugeValue.style.backgroundColor = color;
    gaugeValue.style.color = '#ffffff';
}

/**
 * Utility to restart css staggered entrance animations
 */
function triggerCardAnimations() {
    const cards = document.querySelectorAll('.card-animate');
    cards.forEach(card => {
        // Strip element and add back animation class to force browser to repaint keyframes
        card.style.animation = 'none';
        card.offsetHeight; /* Trigger reflow */
        card.style.animation = '';
    });
}

/**
 * Box Breathing logic (16s cycle: 4s inhale, 4s hold, 4s exhale, 4s hold)
 */
function toggleBreathing() {
    if (breathingInterval) {
        pauseBreathing();
    } else {
        startBreathing();
    }
}

function startBreathing() {
    btnBreathe.textContent = 'Pause Cycle';
    btnResetBreathe.classList.remove('hidden');
    
    // Immediate execution of first tick
    runBreathingTick();
    
    breathingInterval = setInterval(() => {
        breathingTick = (breathingTick + 1) % 16;
        runBreathingTick();
    }, 1000);
}

function runBreathingTick() {
    // Reset classes
    breathingCircle.className = 'breathing-circle';
    
    if (breathingTick < 4) {
        // Inhale phase
        breathingCircle.classList.add('inhale');
        breathingText.textContent = `Inhale... ${4 - breathingTick}s`;
    } else if (breathingTick < 8) {
        // Hold phase (inhaled)
        breathingCircle.classList.add('hold-inhale');
        breathingText.textContent = `Hold... ${8 - breathingTick}s`;
    } else if (breathingTick < 12) {
        // Exhale phase
        breathingCircle.classList.add('exhale');
        breathingText.textContent = `Exhale... ${12 - breathingTick}s`;
    } else {
        // Hold phase (exhaled)
        breathingCircle.classList.add('hold-exhale');
        breathingText.textContent = `Hold... ${16 - breathingTick}s`;
    }
}

function pauseBreathing() {
    clearInterval(breathingInterval);
    breathingInterval = null;
    btnBreathe.textContent = 'Resume Breathing';
}

function resetBreathing() {
    clearInterval(breathingInterval);
    breathingInterval = null;
    breathingTick = 0;
    
    breathingCircle.className = 'breathing-circle';
    breathingText.textContent = 'Ready';
    btnBreathe.textContent = 'Start Breathing';
    btnResetBreathe.classList.add('hidden');
}

/**
 * UI visual states management
 */
function showLoading() {
    formSection.classList.add('hidden');
    loadingSpinner.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
}

function showResults() {
    loadingSpinner.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    errorSection.classList.add('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function showError(msg) {
    loadingSpinner.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.remove('hidden');
    document.getElementById('errorMessage').textContent = msg;
}

function resetForm() {
    wellbeingForm.reset();
    
    // Choose a new random anime quote & characters on start over
    selectRandomCharacters();

    formSection.classList.remove('hidden');
    loadingSpinner.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    window.currentAdvicePlan = null;
    formSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Export advice plan as a formatted text file
 */
function downloadAdvice() {
    if (!window.currentAdvicePlan) {
        alert('No wellness plan found to download.');
        return;
    }

    const plan = window.currentAdvicePlan;
    let text = `=========================================\n`;
    text += `🌱 MINDEASE WELL-BEING ACTION PLAN\n`;
    text += `=========================================\n\n`;
    text += `MESSAGE FOR YOU:\n${plan.empathy_statement}\n\n`;
    text += `INSIGHT:\n${plan.insights}\n\n`;
    text += `COPING STRATEGIES:\n`;
    (plan.coping_strategies || []).forEach((s, idx) => {
        text += `${idx + 1}. ${s}\n`;
    });
    text += `\nHOBBY-BASED RECOVERY:\n${plan.hobby_integration}\n\n`;
    text += `YOUR DAILY AFFIRMATION:\n"${plan.custom_affirmation}"\n\n`;
    text += `RECOMMENDED SELF-CARE ACTIONS:\n`;
    (plan.suggested_actions || []).forEach(a => {
        text += `- ${a}\n`;
    });
    text += `\n=========================================\n`;
    text += `Take it one breath at a time. You can do this!\n`;

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `mindease-wellness-plan-${new Date().toISOString().split('T')[0]}.txt`;
    link.click();
}

/**
 * Save wellbeing check-in to localStorage history log
 */
function saveCheckin(mood, exam) {
    const timestamp = new Date().toLocaleString();
    const history = JSON.parse(localStorage.getItem('mindease_history') || '[]');
    
    // Add new check-in to the front of history
    history.unshift({ mood, exam, timestamp });
    
    // Cap history at 10 items
    if (history.length > 10) {
        history.pop();
    }
    
    localStorage.setItem('mindease_history', JSON.stringify(history));
    renderHistory();
}

/**
 * Render historical check-ins to UI
 */
function renderHistory() {
    const historyLogList = document.getElementById('historyLogList');
    if (!historyLogList) return;
    
    const history = JSON.parse(localStorage.getItem('mindease_history') || '[]');
    
    if (history.length === 0) {
        historyLogList.innerHTML = `
            <div class="history-empty">No check-ins logged yet. Complete the form above to log your first check-in!</div>
        `;
        return;
    }
    
    historyLogList.innerHTML = '';
    history.forEach(item => {
        const card = document.createElement('div');
        card.className = 'history-item-card';
        
        let emoji = '🧘';
        let moodClass = 'mood-calm';
        
        if (item.mood.includes('Confident')) {
            emoji = '🚀';
            moodClass = 'mood-confident';
        } else if (item.mood.includes('Anxious')) {
            emoji = '😰';
            moodClass = 'mood-anxious';
        } else if (item.mood.includes('Calm')) {
            emoji = '🧘';
            moodClass = 'mood-calm';
        } else if (item.mood.includes('Exhausted') || item.mood.includes('Burned Out')) {
            emoji = '🔋';
            moodClass = 'mood-exhausted';
        } else if (item.mood.includes('Sad') || item.mood.includes('Doubt')) {
            emoji = '🥺';
            moodClass = 'mood-doubt';
        }
        
        card.innerHTML = `
            <div class="history-item-header">
                <span class="history-item-mood ${moodClass}">${emoji} ${escapeHTML(item.mood)}</span>
                <span class="history-item-time">${escapeHTML(item.timestamp)}</span>
            </div>
            <div class="history-item-body">
                <span class="history-item-label">Exam:</span>
                <span class="history-item-value">${escapeHTML(item.exam)}</span>
            </div>
        `;
        historyLogList.appendChild(card);
    });
}

/**
 * Clear all history entries
 */
function clearHistory() {
    if (confirm('Are you sure you want to clear all your saved check-in history?')) {
        localStorage.removeItem('mindease_history');
        renderHistory();
    }
}

/**
 * Escape string utility for safe rendering
 */
function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

// Expose clearHistory globally so HTML button onclick attribute works
window.clearHistory = clearHistory;
