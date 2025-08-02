from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os
import uuid
import re
import json
from datetime import datetime, date, timedelta
from gtts import gTTS
import tempfile
import subprocess
import socket
import speech_recognition as sr

app = Flask(__name__)
CORS(app)

# Function to get local IP address
def get_local_ip():
    try:
        # Create a socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        # Fallback to localhost if network detection fails
        return "localhost"

# Get the base URL dynamically
def get_base_url(port=5000):
    # For Railway deployment, use the PORT environment variable
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # In Railway, we don't need to construct the base URL as it will be provided
        return ""
    else:
        # For local development
        return f"http://{get_local_ip()}:{port}"

# Initialize BASE_URL
BASE_URL = get_base_url(5000)

# Database setup
def init_db():
    conn = sqlite3.connect('eco_whisper_demo.db')
    cursor = conn.cursor()
    
    # Check if conversations table exists and has the old structure
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [column[1] for column in cursor.fetchall()]
    
    # If conversations table exists but doesn't have user_id column, add it
    if len(columns) > 0 and 'user_id' not in columns:
        print("Upgrading conversations table...")
        try:
            cursor.execute('ALTER TABLE conversations ADD COLUMN user_id TEXT')
            cursor.execute('ALTER TABLE conversations ADD COLUMN intent_matched TEXT')
        except sqlite3.OperationalError:
            pass  # Columns might already exist
    
    # Check if Intent table exists and add question_patterns column if needed
    cursor.execute("PRAGMA table_info(Intent)")
    intent_columns = [column[1] for column in cursor.fetchall()]
    
    if len(intent_columns) > 0 and 'question_patterns' not in intent_columns:
        print("Upgrading Intent table...")
        try:
            cursor.execute('ALTER TABLE Intent ADD COLUMN question_patterns TEXT')
        except sqlite3.OperationalError:
            pass  # Column might already exist
    
    # Create new tables if they don't exist
    try:
        # Read and execute schema
        with open('schema.sql', 'r') as f:
            schema = f.read()
            cursor.executescript(schema)
    except sqlite3.OperationalError as e:
        print(f"Schema execution error (some tables may already exist): {e}")
    
    # Read and execute sample data
    try:
        with open('sample_data.sql', 'r') as f:
            sample_data = f.read()
            cursor.executescript(sample_data)
    except sqlite3.OperationalError as e:
        print(f"Sample data execution error (some data may already exist): {e}")
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'message': 'Eco Whisper Backend is running',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """Alternative health check endpoint"""
    return jsonify({'status': 'ok'})

def match_intent(user_input):
    """Match user input to database intents using pattern matching"""
    user_input_lower = user_input.lower()
    
    conn = sqlite3.connect('eco_whisper_demo.db')
    cursor = conn.cursor()
    
    # Get all intents with their question patterns
    cursor.execute('SELECT intent_id, name, question_patterns FROM Intent')
    intents = cursor.fetchall()
    
    best_match = None
    best_score = 0
    
    for intent_id, intent_name, patterns_json in intents:
        if patterns_json:
            try:
                patterns = json.loads(patterns_json)
                for pattern in patterns:
                    pattern_lower = pattern.lower()
                    # Improved matching logic
                    if pattern_lower in user_input_lower:
                        score = len(pattern_lower.split())  # Longer patterns get higher scores
                        if score > best_score:
                            best_score = score
                            best_match = intent_id
            except json.JSONDecodeError:
                # Fallback to simple keyword matching
                if intent_name.lower() in user_input_lower:
                    if len(intent_name) > best_score:
                        best_score = len(intent_name)
                        best_match = intent_id
    
    conn.close()
    
    # If no database match found, try enhanced legacy matching
    if not best_match:
        return match_intent_enhanced(user_input)
    
    return best_match

def match_intent_enhanced(user_input):
    """Enhanced intent matching for better accuracy"""
    user_input_lower = user_input.lower()
    
    # Community usage patterns - more specific matching
    if any(phrase in user_input_lower for phrase in ['community use', 'community usage', 'neighborhood use', 'neighborhood usage']):
        if any(word in user_input_lower for word in ['today', 'did', 'how much']):
            return "intent2"  # query_community_usage
    
    # Sustainability tip patterns - more specific matching
    if any(phrase in user_input_lower for phrase in ['sustainability tip', 'eco tip', 'green tip', 'sustainable tip', 'give me a tip']):
        return "intent6"  # random_tip
    
    # Community comparison patterns - more specific matching
    if any(phrase in user_input_lower for phrase in ['green compared', 'greener than', 'compared to others', 'community comparison', 'how green am i']):
        return "intent9"  # compare_community
    
    # Specific patterns for the problematic questions
    if any(phrase in user_input_lower for phrase in ['greenest time', 'best time to use power', 'greenest time to use power']):
        return "intent4"  # greenest_time
    
    if any(phrase in user_input_lower for phrase in ['carbon dioxide', 'co2', 'co₂', 'carbon']):
        if any(word in user_input_lower for word in ['save', 'saved', 'reduced']):
            return "intent5"  # query_co2_saved
    
    if any(phrase in user_input_lower for phrase in ['summarize', 'summary', 'green behavior', 'eco behavior']):
        if any(word in user_input_lower for word in ['today', 'daily']):
            return "intent10"  # summary_today
    
    # Electricity usage patterns
    if any(word in user_input_lower for word in ['electricity', 'power', 'energy', 'kwh', 'kilowatt']):
        if any(word in user_input_lower for word in ['today', 'used', 'consumption', 'usage']):
            return "intent1"  # query_electricity_today
        elif any(word in user_input_lower for word in ['save', 'reduce', 'lower', 'cut']):
            return "electricity_save"
        elif any(word in user_input_lower for word in ['cost', 'bill', 'money', 'dollars', 'euros']):
            return "electricity_cost"
    
    # Appliance-specific patterns
    if any(word in user_input_lower for word in ['dishwasher', 'dish washer']):
        if any(word in user_input_lower for word in ['time', 'when', 'best']):
            return "dishwasher_time"
        elif any(word in user_input_lower for word in ['save', 'efficient', 'eco']):
            return "dishwasher_save"
    
    if any(word in user_input_lower for word in ['laundry', 'washer', 'washing machine']):
        if any(word in user_input_lower for word in ['time', 'when', 'best', 'greenest']):
            return "laundry_time"
        elif any(word in user_input_lower for word in ['save', 'efficient', 'eco']):
            return "laundry_save"
    
    # Food and diet patterns
    if any(word in user_input_lower for word in ['milk', 'oat', 'almond', 'dairy']):
        if any(word in user_input_lower for word in ['eco', 'friendly', 'sustainable', 'better']):
            return "milk_comparison"
    
    # General sustainability
    if any(word in user_input_lower for word in ['tip', 'advice', 'sustainable', 'eco']):
        if any(word in user_input_lower for word in ['today', 'daily', 'everyday']):
            return "intent6"  # random_tip
    
    return "general_eco"

def match_intent_legacy(user_input):
    """Legacy intent matching for backward compatibility"""
    user_input_lower = user_input.lower()
    
    # Electricity usage patterns
    if any(word in user_input_lower for word in ['electricity', 'power', 'energy', 'kwh', 'kilowatt']):
        if any(word in user_input_lower for word in ['today', 'used', 'consumption', 'usage']):
            return "electricity_today"
        elif any(word in user_input_lower for word in ['save', 'reduce', 'lower', 'cut']):
            return "electricity_save"
        elif any(word in user_input_lower for word in ['cost', 'bill', 'money', 'dollars']):
            return "electricity_cost"
    
    # Appliance-specific patterns
    if any(word in user_input_lower for word in ['dishwasher', 'dish washer']):
        if any(word in user_input_lower for word in ['time', 'when', 'best']):
            return "dishwasher_time"
        elif any(word in user_input_lower for word in ['save', 'efficient', 'eco']):
            return "dishwasher_save"
    
    if any(word in user_input_lower for word in ['laundry', 'washer', 'washing machine']):
        if any(word in user_input_lower for word in ['time', 'when', 'best', 'greenest']):
            return "laundry_time"
        elif any(word in user_input_lower for word in ['save', 'efficient', 'eco']):
            return "laundry_save"
    
    # Food and diet patterns
    if any(word in user_input_lower for word in ['milk', 'oat', 'almond', 'dairy']):
        if any(word in user_input_lower for word in ['eco', 'friendly', 'sustainable', 'better']):
            return "milk_comparison"
    
    # General sustainability
    if any(word in user_input_lower for word in ['tip', 'advice', 'sustainable', 'eco']):
        if any(word in user_input_lower for word in ['today', 'daily', 'everyday']):
            return "daily_tip"
    
    return "general_eco"

def get_response(intent_id, user_id=None):
    """Get dynamic response based on intent and database data"""
    conn = sqlite3.connect('eco_whisper_demo.db')
    cursor = conn.cursor()
    
    # Get intent information
    cursor.execute('SELECT name, response_template, requires_data_access FROM Intent WHERE intent_id = ?', (intent_id,))
    intent_data = cursor.fetchone()
    
    if not intent_data:
        conn.close()
        return get_response_legacy(intent_id)
    
    intent_name, response_template, requires_data_access = intent_data
    
    if not requires_data_access:
        # For intents that don't need data, return template as-is or with static values
        if intent_name == 'greenest_time':
            return response_template.format(green_time="during off-peak hours (10 PM - 6 AM) when renewable energy is more prevalent on the grid")
        return response_template
    
    # For data-driven intents, query the database and format the response
    today = date.today().isoformat()
    
    try:
        if intent_name == 'query_electricity_today':
            if user_id:
                cursor.execute('''
                    SELECT kwh_used, estimated_cost FROM Electricity_Usage 
                    WHERE user_id = ? AND date = ?
                ''', (user_id, today))
                usage_data = cursor.fetchone()
                if usage_data:
                    kwh, cost = usage_data
                    return response_template.format(kwh=kwh, cost=cost)
            
            # Fallback to sample data
            return response_template.format(kwh=5.6, cost=2.08)
        
        elif intent_name == 'query_community_usage':
            cursor.execute('''
                SELECT avg_kwh_per_user FROM Community_Stats 
                WHERE date = ? ORDER BY created_at DESC LIMIT 1
            ''', (today,))
            community_data = cursor.fetchone()
            if community_data:
                avg_kwh = community_data[0]
                return response_template.format(avg_kwh=avg_kwh)
            
            # Fallback to sample data
            return response_template.format(avg_kwh=5.2)
        
        elif intent_name == 'compare_yesterday':
            if user_id:
                cursor.execute('''
                    SELECT kwh_used FROM Electricity_Usage 
                    WHERE user_id = ? AND date IN (?, ?)
                    ORDER BY date DESC
                ''', (user_id, today, (date.today() - timedelta(days=1)).isoformat()))
                usage_data = cursor.fetchall()
                if len(usage_data) >= 2:
                    today_kwh, yesterday_kwh = usage_data[0][0], usage_data[1][0]
                    diff = abs(today_kwh - yesterday_kwh)
                    compare = "more" if today_kwh > yesterday_kwh else "less"
                    compare_text = "more than yesterday" if today_kwh > yesterday_kwh else "less than yesterday"
                    return response_template.format(compare=compare, diff=diff, compare_text=compare_text)
            
            # Fallback
            return response_template.format(compare="less", diff=0.6, compare_text="less than yesterday")
        
        elif intent_name == 'query_co2_saved':
            if user_id:
                cursor.execute('''
                    SELECT impact_value FROM Impact_Record 
                    WHERE user_id = ? AND date = ? AND impact_type = 'CO2_saved'
                ''', (user_id, today))
                co2_data = cursor.fetchone()
                if co2_data:
                    co2 = co2_data[0]
                    return response_template.format(co2=co2)
            
            # Fallback
            return response_template.format(co2=2.1)
        
        elif intent_name == 'random_tip':
            cursor.execute('''
                SELECT content FROM Tip 
                WHERE is_active = 1 
                ORDER BY RANDOM() LIMIT 1
            ''')
            tip_data = cursor.fetchone()
            if tip_data:
                tip = tip_data[0]
                return response_template.format(tip=tip)
            
            # Fallback
            return response_template.format(tip="Turn off lights when leaving a room to save energy")
        
        elif intent_name == 'query_water_saved':
            if user_id:
                cursor.execute('''
                    SELECT impact_value FROM Impact_Record 
                    WHERE user_id = ? AND date = ? AND impact_type = 'water_saved'
                ''', (user_id, today))
                water_data = cursor.fetchone()
                if water_data:
                    water = water_data[0]
                    return response_template.format(water=water)
            
            # Fallback
            return response_template.format(water=15.0)
        
        elif intent_name == 'query_money_saved_week':
            if user_id:
                # Calculate weekly savings (simplified)
                cursor.execute('''
                    SELECT SUM(estimated_cost) FROM Electricity_Usage 
                    WHERE user_id = ? AND date >= date(?, '-7 days')
                ''', (user_id, today))
                cost_data = cursor.fetchone()
                if cost_data and cost_data[0]:
                    # Assume baseline cost and calculate savings
                    total_cost = cost_data[0]
                    baseline_cost = 17.0  # Weekly baseline in euros
                    savings = max(0, baseline_cost - total_cost)
                    return response_template.format(money=savings)
            
            # Fallback
            return response_template.format(money=2.98)
        
        elif intent_name == 'compare_community':
            if user_id:
                # Get user's today usage
                cursor.execute('''
                    SELECT kwh_used FROM Electricity_Usage 
                    WHERE user_id = ? AND date = ?
                ''', (user_id, today))
                user_usage = cursor.fetchone()
                
                # Get community average
                cursor.execute('''
                    SELECT avg_kwh_per_user FROM Community_Stats 
                    WHERE date = ? ORDER BY created_at DESC LIMIT 1
                ''', (today,))
                community_avg = cursor.fetchone()
                
                if user_usage and community_avg:
                    user_kwh = user_usage[0]
                    avg_kwh = community_avg[0]
                    diff = abs(user_kwh - avg_kwh)
                    compare = "less" if user_kwh < avg_kwh else "more"
                    compare_text = "than your community average"
                    return response_template.format(compare=compare, diff=diff, compare_text=compare_text)
            
            # Fallback
            return response_template.format(compare="less", diff=0.4, compare_text="than your community average")
        
        elif intent_name == 'summary_today':
            if user_id:
                cursor.execute('''
                    SELECT kwh_used FROM Electricity_Usage 
                    WHERE user_id = ? AND date = ?
                ''', (user_id, today))
                usage_data = cursor.fetchone()
                
                cursor.execute('''
                    SELECT impact_value FROM Impact_Record 
                    WHERE user_id = ? AND date = ? AND impact_type = 'CO2_saved'
                ''', (user_id, today))
                co2_data = cursor.fetchone()
                
                kwh = usage_data[0] if usage_data else 5.6
                co2 = co2_data[0] if co2_data else 2.1
                return response_template.format(kwh=kwh, co2=co2)
            
            # Fallback
            return response_template.format(kwh=5.6, co2=2.1)
        
    except Exception as e:
        print(f"Error getting response for intent {intent_id}: {e}")
    
    conn.close()
    
    # Fallback to legacy response
    return get_response_legacy(intent_id)

def get_response_legacy(intent):
    """Legacy response system for backward compatibility"""
    responses = {
        "electricity_today": "You used 5.6 kilowatt-hours today, which cost about 2.45 dollars.",
        "electricity_save": "To save electricity, try using LED bulbs, unplug devices when not in use, and run appliances during off-peak hours.",
        "electricity_cost": "Your current electricity rate is about 44 cents per kilowatt-hour. Consider switching to renewable energy providers.",
        "dishwasher_time": "The best time to run your dishwasher is during off-peak hours (10 PM - 6 AM) when renewable energy is more prevalent on the grid. Also, only run it when full and use the eco-mode if available!",
        "dishwasher_save": "To save energy with your dishwasher, only run full loads, use eco-mode, and skip the heated dry cycle.",
        "laundry_time": "The greenest time to wash laundry is during off-peak hours (10 PM - 6 AM) when the grid uses more renewable energy. Also, wash with cold water to save 90% of the energy!",
        "laundry_save": "To save energy with laundry, use cold water, wash full loads, and air dry when possible.",
        "milk_comparison": "Oat milk is generally more eco-friendly than almond milk. It uses less water and produces fewer greenhouse gases. However, both are better than dairy milk for the environment.",
        "daily_tip": "Here's a sustainable tip for today: Try using a reusable water bottle instead of disposable plastic bottles. This simple change can save hundreds of plastic bottles per year!",
        "general_eco": "I'm here to help you live more sustainably! Ask me about electricity usage, appliance efficiency, or eco-friendly choices."
    }
    return responses.get(intent, "I'm here to help you live more sustainably! Ask me about electricity usage, appliance efficiency, or eco-friendly choices.")

def text_to_speech(text, filename):
    """Convert text to speech and save as MP3"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        return True
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        return False

@app.route('/api/text_ask', methods=['POST'])
def text_ask():
    try:
        text = request.form.get('text', '').strip()
        user_id = request.form.get('user_id', None)  # Optional user ID
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Match intent and get response
        intent = match_intent(text)
        answer = get_response(intent, user_id)
        
        # Generate audio file
        audio_filename = f"answer_{uuid.uuid4()}.mp3"
        audio_path = os.path.join(os.getcwd(), audio_filename)
        
        if text_to_speech(answer, audio_path):
            if os.environ.get('RAILWAY_ENVIRONMENT'):
                # For Railway, construct URL using request
                audio_url = f"{request.url_root.rstrip('/')}/{audio_filename}"
            else:
                audio_url = f"{BASE_URL}/{audio_filename}"
        else:
            audio_url = None
        
        # Save to database
        conversation_id = str(uuid.uuid4())
        conn = sqlite3.connect('eco_whisper_demo.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (conversation_id, user_id, user_message, assistant_message, intent_matched)
            VALUES (?, ?, ?, ?, ?)
        ''', (conversation_id, user_id, text, answer, intent))
        conn.commit()
        conn.close()
        
        return jsonify({
            'answer': answer,
            'audio_url': audio_url,
            'conversation_id': conversation_id,
            'intent_matched': intent
        })
        
    except Exception as e:
        print(f"Error in text_ask: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    """Handle voice transcription"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        user_id = request.form.get('user_id', None)  # Optional user ID
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save audio file temporarily with original extension
        file_extension = os.path.splitext(audio_file.filename)[1] if audio_file.filename else '.wav'
        temp_audio_path = f"temp_audio_{uuid.uuid4()}{file_extension}"
        audio_file.save(temp_audio_path)
        
        # Convert to WAV if needed for speech recognition
        wav_audio_path = temp_audio_path
        if file_extension.lower() not in ['.wav', '.wave']:
            wav_audio_path = f"temp_audio_{uuid.uuid4()}.wav"
            try:
                # Use ffmpeg to convert audio to WAV format
                subprocess.run([
                    'ffmpeg', '-i', temp_audio_path, 
                    '-acodec', 'pcm_s16le', 
                    '-ar', '16000', 
                    '-ac', '1', 
                    wav_audio_path,
                    '-y'  # Overwrite output file
                ], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # If ffmpeg is not available, try to use the original file
                wav_audio_path = temp_audio_path
                print("Warning: ffmpeg not available, using original audio file")
        
        # Transcribe audio using speech recognition
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(wav_audio_path) as source:
                audio_data = recognizer.record(source)
                try:
                    transcript = recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    transcript = "I didn't catch that. Can you try again?"
                except sr.RequestError:
                    transcript = "Sorry, there was an error with the speech recognition service"
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            transcript = "I didn't catch that. Can you try again?"
        
        # Clean up temporary files
        try:
            os.remove(temp_audio_path)
            if wav_audio_path != temp_audio_path:
                os.remove(wav_audio_path)
        except:
            pass
        
        # Match intent and get response
        intent = match_intent(transcript)
        answer = get_response(intent, user_id)
        
        # Generate audio file
        audio_filename = f"answer_{uuid.uuid4()}.mp3"
        audio_path = os.path.join(os.getcwd(), audio_filename)
        
        if text_to_speech(answer, audio_path):
            if os.environ.get('RAILWAY_ENVIRONMENT'):
                # For Railway, construct URL using request
                audio_url = f"{request.url_root.rstrip('/')}/{audio_filename}"
            else:
                audio_url = f"{BASE_URL}/{audio_filename}"
        else:
            audio_url = None
        
        # Save to database
        conversation_id = str(uuid.uuid4())
        conn = sqlite3.connect('eco_whisper_demo.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (conversation_id, user_id, user_message, assistant_message, intent_matched)
            VALUES (?, ?, ?, ?, ?)
        ''', (conversation_id, user_id, transcript, answer, intent))
        conn.commit()
        conn.close()
        
        return jsonify({
            'transcript': transcript,
            'answer': answer,
            'audio_url': audio_url,
            'conversation_id': conversation_id,
            'intent_matched': intent
        })
        
    except Exception as e:
        print(f"Error in transcribe: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/usage/community/today', methods=['GET'])
def community_usage_today():
    """Get community usage for today"""
    try:
        today = date.today().isoformat()
        
        conn = sqlite3.connect('eco_whisper_demo.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT avg_kwh_per_user, total_co2_saved 
            FROM Community_Stats 
            WHERE date = ? 
            ORDER BY created_at DESC LIMIT 1
        ''', (today,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            avg_kwh, co2_saved = result
            return jsonify({
                'date': today,
                'avg_kwh_per_user': avg_kwh,
                'total_co2_saved': co2_saved
            })
        else:
            # Return sample data if no real data exists
            return jsonify({
                'date': today,
                'avg_kwh_per_user': 5.2,
                'total_co2_saved': 1.8
            })
            
    except Exception as e:
        print(f"Error getting community usage: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/usage/user/<user_id>/today', methods=['GET'])
def user_usage_today(user_id):
    """Get user's electricity usage for today"""
    try:
        today = date.today().isoformat()
        
        conn = sqlite3.connect('eco_whisper_demo.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT kwh_used, estimated_cost, is_peak_time 
            FROM Electricity_Usage 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            kwh_used, estimated_cost, is_peak_time = result
            return jsonify({
                'user_id': user_id,
                'date': today,
                'kwh_used': kwh_used,
                'estimated_cost': estimated_cost,
                'is_peak_time': bool(is_peak_time)
            })
        else:
            return jsonify({'error': 'No usage data found for today'}), 404
            
    except Exception as e:
        print(f"Error getting user usage: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/<filename>')
def serve_audio(filename):
    """Serve audio files"""
    try:
        return send_file(filename, mimetype='audio/mpeg')
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    # Get port from environment variable (Railway) or use default
    port = int(os.environ.get('PORT', 5000))
    
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # For Railway deployment
        print(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port)
    else:
        # For local development
        base_url = get_base_url(5000)
        print(f"Starting server on {base_url}")
        app.run(host='0.0.0.0', port=5000, debug=True) 