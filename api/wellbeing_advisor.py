import os
import json
import re

try:
    import google.generativeai as genai
except ImportError:
    genai = None

class WellbeingAdvisor:
    """AI-powered wellness advisor service for students"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

    def analyze_wellbeing(self, mood, exam, triggers, hobbies, journal):
        """
        Analyze student mood, stressors, and hobbies, and generate custom well-being guidance.
        """
        prompt = self._build_prompt(mood, exam, triggers, hobbies, journal)
        try:
            if self.model:
                response = self.model.generate_content(prompt)
                return self._parse_response(response.text, mood, exam, triggers, hobbies)
            else:
                return self._generate_fallback_response(mood, exam, triggers, hobbies)
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return self._generate_fallback_response(mood, exam, triggers, hobbies)

    def _build_prompt(self, mood, exam, triggers, hobbies, journal):
        triggers_str = ", ".join(triggers) if triggers else "None specified"
        hobbies_str = ", ".join(hobbies) if hobbies else "None specified"
        journal_str = journal if journal else "No journal entry provided."
        
        prompt = f"""You are a compassionate, warm, and professional student wellness coach specializing in helping students cope with stress during high-stakes competitive examinations and board results seasons.

Analyze this student profile:
- Current Mood/State: {mood}
- Preparing for Exam: {exam}
- Key Stress Triggers: {triggers_str}
- Hobbies/Relaxation Activities: {hobbies_str}
- Personal Reflection/Journal: {journal_str}

Please generate a personalized, deeply encouraging support guide in the following JSON format:
{{
    "empathy_statement": "A warm, comforting, and validating response directly acknowledging their current emotional state, their specific exam, and their triggers.",
    "insights": "2-3 short, compassionate insights into why their specific triggers (e.g., test scores, fear of failure) affect them, written in an encouraging and demystifying tone.",
    "coping_strategies": [
        "Strategy 1: A specific, actionable mental or physical strategy tailored to their exam and triggers.",
        "Strategy 2: Another actionable, study-routine stress-relief strategy."
    ],
    "hobby_integration": "A personalized recommendation on how they can actively use their specific hobbies ({hobbies_str}) to construct healthy, guilt-free study breaks to combat burnout.",
    "custom_affirmation": "A powerful, personalized positive affirmation tailored to their current challenge.",
    "suggested_actions": [
        "Action 1: A brief relaxation action (e.g., take a 10-minute walk).",
        "Action 2: A concrete scheduling or study-break action."
    ]
}}

Provide ONLY the raw JSON response, no markdown blocks, no extra text, and ensure it is valid, parseable JSON. Do not put markdown codes (like ```json) in the response.
"""
        return prompt

    def _parse_response(self, response_text, mood, exam, triggers, hobbies):
        try:
            # Clean up potential markdown formatting code blocks
            clean_text = response_text.strip()
            if clean_text.startswith("```"):
                # strip out opening and closing ticks
                json_match = re.search(r'\{[\s\S]*\}', clean_text)
                if json_match:
                    clean_text = json_match.group()
            return json.loads(clean_text)
        except Exception as e:
            print(f"Failed to parse response: {e}")
            return self._generate_fallback_response(mood, exam, triggers, hobbies)

    def _generate_fallback_response(self, mood, exam, triggers, hobbies):
        # Default fallback recommendations if AI fails or key is missing
        trigger_detail = ", ".join(triggers) if triggers else "general academic pressure"
        hobby_detail = ", ".join(hobbies) if hobbies else "your favorite break activities"
        
        return {
            "empathy_statement": f"Preparing for {exam} is an intense journey, and feeling {mood.lower()} due to {trigger_detail} is a completely natural response. You are carrying a heavy load right now, and it's okay to feel overwhelmed.",
            "insights": "Stress is not a sign of weakness; it's a sign that you care deeply about your future. In high-pressure environments like exam preparation, triggers like syllabus volume or mock scores can create a false sense of urgency, triggering self-doubt.",
            "coping_strategies": [
                "Practice the 5-minute rule: If you feel overwhelmed, study for just 5 minutes. Often, the resistance melts once you start. If it doesn't, take a structured break.",
                "Separate self-worth from performance: Mock test scores are feedback loops, not final judgments. Use them to analyze gaps, not define your potential."
            ],
            "hobby_integration": f"Integrating {hobby_detail} into a structured study schedule is not wasted time—it is critical cognitive recovery. Try scheduled 15-minute breaks doing these activities to naturally recharge your focus.",
            "custom_affirmation": "I am more than my exam scores. My worth is constant, and my effort is progress.",
            "suggested_actions": [
                "Engage in 5 minutes of box breathing now.",
                "Plan a study block that ends with a guilt-free break to enjoy your hobby."
            ]
        }

    def translate_wellbeing(self, plan_json):
        """
        Translate the dynamically generated wellbeing plan into comforting Hindi using Gemini.
        """
        prompt = f"""You are a helpful and compassionate translator. Please translate the following JSON wellbeing plan into natural, warm, comforting, and highly grammatically correct Hindi (Devanagari script).

For technical or examination terms (like syllabus backlog, mock test scores, peer pressure, box breathing, Pomodoro technique), please provide standard, intuitive translations or common Devanagari transliteration of these English words (e.g. 'मॉक टेस्ट स्कोर', 'सिलेबस बैकलाग') so it is natural for an Indian student. Do not translate the keys of the JSON, only translate the text values.

JSON to translate:
{json.dumps(plan_json, ensure_ascii=False)}

Provide ONLY the raw translated JSON response, no markdown blocks, no extra text, and ensure it is valid, parseable JSON. Do not put markdown codes (like ```json) in the response.
"""
        try:
            if self.model:
                response = self.model.generate_content(prompt)
                return self._parse_response(response.text, "", "", [], [])
            else:
                return self._generate_fallback_translation(plan_json)
        except Exception as e:
            print(f"Error calling Gemini API for translation: {e}")
            return self._generate_fallback_translation(plan_json)

    def _generate_fallback_translation(self, plan):
        """Standard fallback Hindi response if the AI translator fails"""
        return {
            "empathy_statement": "परीक्षा की तैयारी एक कठिन यात्रा है, और तनाव महसूस करना पूरी तरह से स्वाभाविक है। आप अभी एक भारी बोझ उठा रहे हैं, और अभिभूत महसूस करना बिल्कुल ठीक है।",
            "insights": "तनाव कमजोरी का संकेत नहीं है; यह एक संकेत है कि आप अपने भविष्य की परवाह करते हैं। परीक्षा के माहौल में, दबाव आत्म-संदेह पैदा कर सकता है।",
            "coping_strategies": [
                "5-मिनट का नियम अपनाएं: यदि आप अभिभूत महसूस करते हैं, तो केवल 5 मिनट के लिए अध्ययन करें। अक्सर काम शुरू करने के बाद प्रतिरोध कम हो जाता है।",
                "आत्म-मूल्य को प्रदर्शन से अलग करें: मॉक टेस्ट के अंक प्रतिक्रिया हैं, अंतिम निर्णय नहीं। अंतराल का विश्लेषण करने के लिए उनका उपयोग करें।"
            ],
            "hobby_integration": "अध्ययन के बीच में अपनी पसंद की गतिविधियों को शामिल करना समय की बर्बादी नहीं है, बल्कि मस्तिष्क की रिकवरी के लिए महत्वपूर्ण है।",
            "custom_affirmation": "मैं अपने परीक्षा अंकों से कहीं बढ़कर हूँ। मेरी योग्यता स्थिर है, और मेरा प्रयास ही मेरी प्रगति है।",
            "suggested_actions": [
                "अभी 5 मिनट के लिए बॉक्स ब्रीदिंग (गहरी सांस लेने का व्यायाम) करें।",
                "एक अध्ययन ब्लॉक की योजना बनाएं जो आपकी पसंद की गतिविधि के साथ समाप्त हो।"
            ]
        }
