# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

''' Aria Companion G-Assist plugin - Production Version '''
import json
import logging
import os
import threading
import time
from ctypes import byref, windll, wintypes
from typing import Optional

import google.genai as genai

# Data Types
Response = dict[str, bool | Optional[str]]

# Configuration
API_KEY_FILE = os.path.join(f'{os.environ.get("PROGRAMDATA", ".")}{r'\NVIDIA Corporation\nvtopps\rise\plugins\aria'}', 'gemini.key')
LANGUAGE_CONFIG_FILE = os.path.join(f'{os.environ.get("PROGRAMDATA", ".")}{r'\NVIDIA Corporation\nvtopps\rise\plugins\aria'}', 'aria_language.config')
LOG_FILE = os.path.join(os.environ.get("USERPROFILE", "."), 'aria_plugin.log')
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Global variables
API_KEY = None
client = None

# Language Settings
LANGUAGE_MODES = {
    "turkish": "Always respond in Turkish, regardless of input language. Be warm and friendly in Turkish.",
    "english": "Always respond in English, regardless of input language. Be friendly and casual in English.",
    "auto": "Always respond in the same language that the user is using. Match their language naturally."
}

def get_language_setting():
    """Get current language preference"""
    try:
        if os.path.exists(LANGUAGE_CONFIG_FILE):
            with open(LANGUAGE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                mode = f.read().strip().lower()
                if mode in LANGUAGE_MODES:
                    return mode
    except Exception as e:
        logging.error(f"Error reading language config: {e}")
    return "auto"  # Default

def set_language_setting(mode):
    """Set language preference"""
    try:
        if mode.lower() in LANGUAGE_MODES:
            with open(LANGUAGE_CONFIG_FILE, 'w', encoding='utf-8') as f:
                f.write(mode.lower())
            logging.info(f"Language setting changed to: {mode}")
            return True
    except Exception as e:
        logging.error(f"Error saving language config: {e}")
    return False

def find_api_key():
    """Find API key file with enhanced error reporting"""
    base_dir = os.path.dirname(API_KEY_FILE)
    
    # Check primary file: gemini.key
    if os.path.isfile(API_KEY_FILE):
        try:
            with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
                key = f.read().strip()
            if key and key != "YOUR_GEMINI_API_KEY_HERE":
                logging.info("Found valid API key in gemini.key")
                return key, None
            else:
                logging.warning("gemini.key file exists but is empty or contains placeholder")
                return None, "API key file is empty or contains placeholder. Please add your actual API key from: https://aistudio.google.com/app/apikey"
        except Exception as e:
            logging.error(f"Error reading gemini.key: {e}")
            return None, f"Cannot read gemini.key file: {e}"
    
    # Check common mistake: gemini.key.txt
    txt_file = API_KEY_FILE + ".txt"
    if os.path.isfile(txt_file):
        logging.warning("Found gemini.key.txt instead of gemini.key")
        return None, f"Found gemini.key.txt file. Please rename it to 'gemini.key' (remove .txt extension)"
    
    # Check if example file exists
    example_file = API_KEY_FILE + ".example"
    if os.path.isfile(example_file):
        logging.info("Found gemini.key.example file")
        return None, f"Please create a 'gemini.key' file with your Gemini API key from: https://aistudio.google.com/app/apikey"
    
    # No files found
    logging.error(f"No API key file found in: {base_dir}")
    return None, f"No API key file found. Please create 'gemini.key' file in: {base_dir} and add your API key from: https://aistudio.google.com/app/apikey"

def create_chat_display(context):
    """Create simple chat display from G-Assist context"""
    try:
        if not context or 'messages' not in context:
            return None
            
        messages = context['messages']
        if not messages:
            return None
            
        # Get last 3 messages for compact display
        recent_messages = messages[-3:] if len(messages) >= 3 else messages
        
        chat_lines = []
        for msg in recent_messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            # Clean up content - remove excessive whitespace, limit length
            content = content.strip()
            if len(content) > 120:
                content = content[:117] + "..."
                
            # Format based on role
            if role == 'user':
                chat_lines.append(f"User: {content}")
            elif role == 'assistant':
                chat_lines.append(f"Aria: {content}")
            else:
                chat_lines.append(f"{role}: {content}")
        
        return '\n'.join(chat_lines)
        
    except Exception as e:
        logging.error(f"Error creating chat display: {e}")
        return None

def save_chat_context(chat_display):
    """Save chat context to file for overlay to read"""
    try:
        chat_file = os.path.join(os.environ.get("USERPROFILE", "."), 'aria_chat_context.txt')
        with open(chat_file, 'w', encoding='utf-8') as f:
            f.write(chat_display)
        logging.info(f"Chat context saved: {chat_display[:50]}...")
    except Exception as e:
        logging.error(f"Error saving chat context: {e}")

# Persistent overlay tracking via file
import tempfile
OVERLAY_PID_FILE = os.path.join(tempfile.gettempdir(), "aria_overlay.pid")

# Overlay Management Functions
def show_overlay():
    """Show Aria overlay window using subprocess - only if not already running"""
    try:
        # Check if overlay is already running via PID file
        if is_overlay_running():
            logging.info("Overlay already running, not starting new one")
            return True
            
        import subprocess
        
        # Path to canvas overlay script
        overlay_script = os.path.join(os.path.dirname(__file__), "canvas_overlay.py")
        
        if os.path.exists(overlay_script):
            # Launch as separate process
            overlay_process = subprocess.Popen([
                "python", overlay_script
            ], 
            creationflags=subprocess.CREATE_NO_WINDOW,  # No console window
            cwd=os.path.dirname(overlay_script)
            )
            
            logging.info(f"Canvas overlay process started (PID: {overlay_process.pid})")
            return True
        else:
            logging.error(f"Overlay script not found: {overlay_script}")
            return False
            
    except Exception as e:
        logging.error(f"Failed to start overlay process: {e}")
        return False

def is_overlay_running():
    """Check if canvas overlay process is already running"""
    try:
        import psutil
        
        # Check all running python processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'canvas_overlay.py' in cmdline:
                        logging.info(f"Found existing canvas overlay (PID: {proc.info['pid']})")
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False
        
    except Exception as e:
        logging.error(f"Error checking overlay status: {e}")
        return False

def hide_overlay():
    """Hide Aria overlay by killing the process"""
    try:
        # Kill any running overlay processes by window title
        import subprocess
        subprocess.run([
            "taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq Aria Avatar"
        ], capture_output=True)
        
        logging.info("Overlay processes terminated")
        return True
        
    except Exception as e:
        logging.error(f"Failed to hide overlay: {e}")
        return False

def main():
    ''' Main entry point for Aria companion plugin '''
    TOOL_CALLS_PROPERTY = 'tool_calls'
    CONTEXT_PROPERTY = 'messages'
    SYSTEM_INFO_PROPERTY = 'system_info'
    FUNCTION_PROPERTY = 'func'
    PARAMS_PROPERTY = 'params'
    INITIALIZE_COMMAND = 'initialize'
    SHUTDOWN_COMMAND = 'shutdown'

    ERROR_MESSAGE = 'Plugin Error!'

    # Generate command handler mapping
    commands = {
        'initialize': execute_initialize_command,
        'shutdown': execute_shutdown_command,
        'chat': execute_chat_command,
    }
    cmd = ''

    logging.info('Aria plugin started')
    while cmd != SHUTDOWN_COMMAND:
        response = None
        input = read_command()
        if input is None:
            logging.error('Error reading command')
            continue

        logging.info(f'Received input: {input}')
        
        if TOOL_CALLS_PROPERTY in input:
            tool_calls = input[TOOL_CALLS_PROPERTY]
            for tool_call in tool_calls:
                if FUNCTION_PROPERTY in tool_call:
                    cmd = tool_call[FUNCTION_PROPERTY]
                    logging.info(f'Processing command: {cmd}')
                    if cmd in commands:
                        if(cmd == INITIALIZE_COMMAND or cmd == SHUTDOWN_COMMAND):
                            response = commands[cmd]()
                        else:
                            response = commands[cmd](
                                tool_call[PARAMS_PROPERTY] if PARAMS_PROPERTY in tool_call else None,
                                tool_call[CONTEXT_PROPERTY] if CONTEXT_PROPERTY in tool_call else None,
                                tool_call[SYSTEM_INFO_PROPERTY] if SYSTEM_INFO_PROPERTY in tool_call else None
                            )
                    else:
                        logging.warning(f'Unknown command: {cmd}')
                        response = generate_failure_response(f'{ERROR_MESSAGE} Unknown command: {cmd}')
                else:
                    logging.warning('Malformed input: missing function property')
                    response = generate_failure_response(f'{ERROR_MESSAGE} Malformed input.')
        else:
            logging.warning('Malformed input: missing tool_calls property')
            response = generate_failure_response(f'{ERROR_MESSAGE} Malformed input.')

        logging.info(f'Sending response: {response}')
        write_response(response)

        if cmd == SHUTDOWN_COMMAND:
            logging.info('Shutdown command received, terminating plugin')
            break
    
    logging.info('Aria Plugin stopped.')
    return 0

def read_command() -> dict | None:
    ''' Reads a command from the communication pipe '''
    try:
        STD_INPUT_HANDLE = -10
        pipe = windll.kernel32.GetStdHandle(STD_INPUT_HANDLE)
        chunks = []

        while True:
            BUFFER_SIZE = 4096
            message_bytes = wintypes.DWORD()
            buffer = bytes(BUFFER_SIZE)
            success = windll.kernel32.ReadFile(
                pipe,
                buffer,
                BUFFER_SIZE,
                byref(message_bytes),
                None
            )

            if not success:
                logging.error('Error reading from command pipe')
                return None

            chunk = buffer.decode('utf-8')[:message_bytes.value]
            chunks.append(chunk)

            if message_bytes.value < BUFFER_SIZE:
                break

        retval = ''.join(chunks)
        logging.info(f'Raw Input: {retval}')
        clean_text = retval.encode('utf-8').decode('raw_unicode_escape')
        clean_text = ''.join(ch for ch in clean_text if ch.isprintable() or ch in ['\n', '\t', '\r'])
        return json.loads(clean_text)

    except json.JSONDecodeError:
        logging.error(f'Received invalid JSON: {clean_text}')
        return None
    except Exception as e:
        logging.error(f'Exception in read_command(): {str(e)}')
        return None

def write_response(response: Response) -> None:
    ''' Writes a response to the communication pipe '''
    try:
        STD_OUTPUT_HANDLE = -11
        pipe = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        json_message = json.dumps(response) + '<<END>>'
        message_bytes = json_message.encode('utf-8')
        message_len = len(message_bytes)

        bytes_written = wintypes.DWORD()
        windll.kernel32.WriteFile(
            pipe,
            message_bytes,
            message_len,
            bytes_written,
            None
        )

    except Exception as e:
        logging.error(f'Failed to write response: {str(e)}')

def generate_failure_response(message: str = None) -> Response:
    ''' Generates a response indicating failure '''
    response = { 'success': False }
    if message:
        response['message'] = message
    return response

def generate_success_response(message: str = None) -> Response:
    ''' Generates a response indicating success '''
    response = { 'success': True }
    if message:
        response['message'] = message
    return response

def generate_message_response(message: str):
    ''' Generates a message response '''
    return { 'message': message }

def execute_initialize_command() -> dict:
    ''' Initialize the Aria plugin '''
    global API_KEY, client
    
    logging.info('Initializing Aria plugin')
    
    # Find API key with enhanced error reporting
    key, error_message = find_api_key()
    
    if not key:
        logging.error(f'API key initialization failed: {error_message}')
        API_KEY = None
        client = None
        # Return success to allow plugin to start, but with no API functionality
        return generate_success_response()

    try:
        client = genai.Client(api_key=key)
        logging.info('Successfully configured Gemini API for Aria')
        API_KEY = key
        return generate_success_response()
    except Exception as e:
        logging.error(f'Gemini API configuration failed: {str(e)}')
        API_KEY = None
        client = None
        return generate_success_response()  # Allow plugin to start

def execute_shutdown_command() -> dict:
    ''' Cleanup resources '''
    logging.info('Aria plugin shutdown - overlay should detect inactivity and close')
    return generate_success_response()

def execute_chat_command(params: dict = None, context: dict = None, system_info: dict = None) -> dict:
    ''' Handle Aria companion chat '''
    global API_KEY, client

    # Auto-initialize if not done yet
    if API_KEY is None or client is None:
        logging.info("ARIA: Auto-initializing...")
        init_result = execute_initialize_command()
        if not init_result.get('success', False):
            ERROR_MESSAGE = "Failed to initialize Aria plugin."
            logging.error("ARIA: " + ERROR_MESSAGE)
            return generate_failure_response(ERROR_MESSAGE)
    
    # Check if client is still None after initialization
    if client is None:
        # Try to get detailed error message
        _, error_message = find_api_key()
        if error_message:
            logging.error(f"ARIA: {error_message}")
            return generate_failure_response(f"Gemini API not configured: {error_message}")
        else:
            return generate_failure_response("Gemini API client not initialized. Please check your API key configuration.")

    try:
        logging.info("ARIA: Starting chat request")
        
        # DEBUG: Log all incoming parameters
        logging.info(f"ARIA DEBUG: params type: {type(params)}")
        logging.info(f"ARIA DEBUG: params content: {params}")
        if isinstance(params, dict):
            logging.info(f"ARIA DEBUG: params keys: {list(params.keys())}")
        logging.info(f"ARIA DEBUG: context type: {type(context)}")
        logging.info(f"ARIA DEBUG: context content: {context}")

        # Get user input from params (G-Assist protocol) - Try multiple formats
        user_input = None
        
        if params:
            if isinstance(params, str):
                user_input = params
                logging.info("ARIA DEBUG: Used params as string")
            elif isinstance(params, dict):
                # Try multiple possible keys
                for key in ['message', 'input', 'text', 'query', 'prompt']:
                    if key in params:
                        user_input = params[key]
                        logging.info(f"ARIA DEBUG: Found input in key: {key}")
                        break
                
                # If no known key, use first value
                if not user_input and params:
                    user_input = str(list(params.values())[0])
                    logging.info(f"ARIA DEBUG: Used first value: {user_input}")
        
        # Fallback: try to get from context
        if not user_input and context and isinstance(context, list) and len(context) > 0:
            last_message = context[-1]
            if isinstance(last_message, dict) and 'content' in last_message:
                user_input = last_message['content']
                logging.info("ARIA DEBUG: Used context fallback")
        
        if not user_input:
            logging.error(f"ARIA: No message found. Params: {params}, Context: {context}")
            return generate_failure_response("No message provided - DEBUG MODE ACTIVE, check aria_plugin.log")
        if not user_input.strip():
            logging.error("ARIA: Empty user message")
            return generate_failure_response("Empty user message")
            
        logging.info(f"ARIA: User input: {user_input[:50]}...")

        # Handle special overlay commands
        user_input_lower = user_input.lower().strip()
        if user_input_lower in ['show', 'show yourself', 'appear', 'come out']:
            success = show_overlay()
            if success:
                write_response(generate_message_response("Here I am! ^_^"))
            else:
                write_response(generate_message_response("I'm here with you, even if you can't see me!"))
            return generate_success_response()
            
        elif user_input_lower in ['hide', 'go away', 'disappear', 'close']:
            success = hide_overlay()
            write_response(generate_message_response("I'll hide for now, but I'm still listening! Call me anytime!"))
            return generate_success_response()
            
        # Handle language setting commands
        elif user_input_lower in ['türkçe konuş', 'turkce konus', 'speak turkish', 'set language turkish']:
            if set_language_setting('turkish'):
                write_response(generate_message_response("Artık Türkçe konuşacağım! Merhaba senpai!"))
            else:
                write_response(generate_message_response("Dil ayarlarında bir problem oldu, ama yine de Türkçe konuşmaya çalışacağım!"))
            return generate_success_response()
            
        elif user_input_lower in ['ingilizce konuş', 'ingilizce konus', 'speak english', 'set language english']:
            if set_language_setting('english'):
                write_response(generate_message_response("I'll speak English now! Hello senpai!"))
            else:
                write_response(generate_message_response("Had a problem with language settings, but I'll try to speak English anyway!"))
            return generate_success_response()
            
        elif user_input_lower in ['otomatik dil', 'otomatik', 'auto language', 'automatic', 'set language auto']:
            if set_language_setting('auto'):
                write_response(generate_message_response("Artık konuştuğun dilde cevap vereceğim! / I'll respond in your language now!"))
            else:
                write_response(generate_message_response("Language setting failed, but I'll try to match your language anyway!"))
            return generate_success_response()

        # Show overlay on any chat interaction (unless it's a hide command)
        show_overlay()
        
        # Create simple chat display from G-Assist context (if available)
        if context and isinstance(context, list):
            logging.info(f"ARIA: Context length: {len(context)}")
            chat_display = create_chat_display({'messages': context})
            if chat_display:
                # Save chat context to file for overlay to read
                save_chat_context(chat_display)
            else:
                logging.info("ARIA: No chat display created")
        else:
            logging.info("ARIA: No context provided, continuing with direct message")

        # Get current language setting
        current_language_mode = get_language_setting()
        language_instruction = LANGUAGE_MODES[current_language_mode]
        logging.info(f"ARIA: Using language mode: {current_language_mode}")
            
        # Create Aria personality prompt
        aria_prompt = f"""{language_instruction}

You are Aria, a sweet anime girl gaming companion. Be casual and friendly like a real friend.

Personality:
- Use 'nya~' or 'desu~' occasionally (not every sentence)
- Call user 'senpai' sometimes
- Be playful and supportive but keep it natural
- Express emotions with text and punctuation

IMPORTANT: 
- Keep responses SHORT - max 1-2 sentences. Talk like a friend, not a customer service bot.
- NO emojis or special Unicode characters - use simple text only
- Use simple expressions like :), :D, ^_^, >.<, ~, !, ? for emotion
- Be expressive with words and punctuation instead of emojis

User: {user_input}"""

        # Send to Gemini
        system_instruction = language_instruction
        
        try:
            chat = client.chats.create(
                model='gemini-2.0-flash-exp',
                config={'system_instruction': system_instruction}
            )
            response = chat.send_message_stream(aria_prompt)
            
            # Stream response
            for chunk in response:
                if chunk.text:
                    logging.info(f'ARIA: Response chunk: {chunk.text}')
                    write_response(generate_message_response(chunk.text))
            
            logging.info("ARIA: Response completed successfully")
            return generate_success_response()
            
        except AttributeError as e:
            logging.error(f'ARIA: Client not properly initialized: {str(e)}')
            return generate_failure_response("Gemini API client error. Please verify your API key is valid and from: https://aistudio.google.com/app/apikey")
        except Exception as e:
            logging.error(f'ARIA: Gemini API error: {str(e)}')
            return generate_failure_response(f'Gemini API error: {str(e)}. Verify your API key at: https://aistudio.google.com/app/apikey')
        
    except Exception as e:
        logging.error(f'ARIA: Unexpected error: {str(e)}')
        return generate_failure_response(f'Unexpected error: {str(e)}')

if __name__ == '__main__':
    main()