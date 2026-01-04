#!/usr/bin/env python3
"""
DUAL BRAIN AI CREATIVE WORKFLOW CENTER
Version 3.0 - Professional Creative Suite

Created by: Adam Lee Hatchett
Date: January 3, 2026
Copyright: © 2026 Adam Lee Hatchett. All Rights Reserved.

A professional AI-powered creative workflow center featuring two collaborative 
AI personalities (Elaine and Carrie) that assist with game development, 
3D modeling, and creative projects.
"""

# --- OLLAMA INTEGRATION HELPER ---
def query_ollama(prompt, model="llama2-uncensored:latest", max_tokens=512, temperature=0.7, stream=False):
    """Query the local Ollama HTTP API.

    Args:
        prompt (str): Prompt to send to the model.
        model (str): Ollama model identifier (defaults to a commonly-installed llama2 uncensored image).
        max_tokens (int): Max tokens to generate.
        temperature (float): Sampling temperature.
        stream (bool): Whether to attempt streaming the response.

    Returns:
        str: Model response or an error message.
    """
    import requests, json
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": stream,
    }
    REQUEST_TIMEOUT = 120
    try:
        try:
            response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT, stream=stream)
            response.raise_for_status()
        except requests.exceptions.ReadTimeout:
            # Retry once with a longer timeout for longer generations
            response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT * 2, stream=stream)
            response.raise_for_status()

        # If streaming, parse line-delimited JSON chunks
        if stream:
            result = ""
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    # Ollama stream chunks may include a 'response' key
                    if isinstance(obj, dict) and 'response' in obj:
                        result += obj.get('response') or ''
                except Exception:
                    # ignore non-json lines
                    continue
            if result:
                return result
            # fall back to the full JSON body if streaming returned nothing
            try:
                data = response.json()
                return data.get('response', '') or "No response from Ollama."
            except Exception:
                return "No response from Ollama."

        # Non-streaming: parse the single JSON response
        data = response.json()
        return data.get('response', '') or "No response from Ollama."

    except requests.exceptions.ConnectionError:
        return "Ollama error: Unable to connect. Is the Ollama server running?"
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 'unknown'
        body = ''
        try:
            body = e.response.text
        except Exception:
            body = str(e)
        return f"Ollama error: HTTP {status}: {body}"
    except Exception as e:
        return f"Ollama error: {str(e)}"
import tkinter as tk
"""
DUAL BRAIN AI CREATIVE WORKFLOW CENTER
Version 3.0 - Professional Creative Suite with Enhanced 3D and Open-World Features

Created by: Adam Lee Hatchett
Copyright: © 2026 Adam Lee Hatchett. All Rights Reserved.

Combines the layout of v1.0 with the logic/learning of v2.2+, adding:
- Enhanced STL generation for 3D printing
- Open-world background and sprite generation
- Web search for queries and design references
- Always-on-top chat windows with pin toggle
- Expandable for mobile/multi-node interfaces
"""

from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import requests
from bs4 import BeautifulSoup
import datetime
import threading
import os
import time
import json
import random
import subprocess
import sqlite3
import numpy as np
import math  # Added for recursive harmonics
try:
    from stl import mesh  # For STL generation (numpy-stl)
except ImportError:
    mesh = None

try:
    from quick_integration import integrate_enhanced_learning_simple
except ImportError:
    integrate_enhanced_learning_simple = None

try:
    from PIL import Image  # For sprite/background generation
except ImportError:
    Image = None

# Persistent Memory using SQLite
class MemoryCore:
    def __init__(self, db_path, brain_name):
        self.db_path = db_path
        self.brain_name = brain_name
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS memory_{self.brain_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            input TEXT,
            response TEXT,
            from_brain TEXT,
            importance INTEGER,
            context TEXT
        )""")
        
        # Migration: Add response column if it doesn't exist
        try:
            c.execute(f"ALTER TABLE memory_{self.brain_name} ADD COLUMN response TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS conversation_{self.brain_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            input TEXT,
            response TEXT,
            from_brain TEXT
        )""")
        # Metadata table for summaries/embeddings/pruning info to allow richer memory features
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS memory_meta_{self.brain_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id INTEGER,
            timestamp TEXT,
            summary TEXT,
            vector TEXT
        )""")
        conn.commit()
        conn.close()

    def add_memory(self, entry):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            f"INSERT INTO memory_{self.brain_name} (timestamp, input, from_brain, importance, context) VALUES (?, ?, ?, ?, ?)",
            (entry['timestamp'], entry['input'], entry['from'], entry['importance'], json.dumps(entry['context']))
        )
        conn.commit()
        conn.close()
    
    def save_insight(self, topic, summary, from_brain, importance, contexts):
        """Save a learning insight to memory with proper structure."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            f"INSERT INTO memory_{self.brain_name} (timestamp, input, response, from_brain, importance, context) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.datetime.now().isoformat(), topic, summary, from_brain, importance, json.dumps(contexts))
        )
        conn.commit()
        conn.close()

    def get_memories(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT timestamp, input, from_brain, importance, context FROM memory_{self.brain_name}")
        rows = c.fetchall()
        conn.close()
        return [
            {
                'timestamp': row[0],
                'input': row[1],
                'from': row[2],
                'importance': row[3],
                'context': json.loads(row[4]) if row[4] else []
            } for row in rows
        ]

    def clear_memory(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"DELETE FROM memory_{self.brain_name}")
        c.execute(f"DELETE FROM conversation_{self.brain_name}")
        conn.commit()
        conn.close()

    def add_conversation(self, entry):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            f"INSERT INTO conversation_{self.brain_name} (timestamp, input, response, from_brain) VALUES (?, ?, ?, ?)",
            (entry['timestamp'], entry['input'], entry['response'], entry['from'])
        )
        conn.commit()
        conn.close()

    def get_conversations(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT timestamp, input, response, from_brain FROM conversation_{self.brain_name}")
        rows = c.fetchall()
        conn.close()
        return [
            {
                'timestamp': row[0],
                'input': row[1],
                'response': row[2],
                'from': row[3]
            } for row in rows
        ]

    def search_memory(self, query):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT timestamp, input, from_brain, importance, context FROM memory_{self.brain_name} WHERE input LIKE ? OR context LIKE ?", 
                  (f"%{query}%", f"%{query}%"))
        rows = c.fetchall()
        conn.close()
        return [
            (
                row[0],
                row[1],
                f"Processed by {self.brain_name}",
                row[3],
                json.loads(row[4]) if row[4] else []
            ) for row in rows
        ]

    def summarize_recent_memories(self, count=20, model="llama2-uncensored:latest"):
        """Create a concise summary of the most recent `count` memories using the local Ollama model.

        Stores the summary in the memory_meta table for later retrieval.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT id, timestamp, input, from_brain, importance, context FROM memory_{self.brain_name} ORDER BY id DESC LIMIT ?", (count,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            return None
        # Build a prompt for summarization
        items = []
        for r in reversed(rows):
            ts, inp, frm, imp, ctx = r[1], r[2], r[3], r[4], r[5]
            items.append(f"[{ts}] ({frm}) importance={imp}: {inp}")
        prompt = "Create a concise, bulleted summary (3-6 bullets) capturing the key points, themes, and any high-importance items from these memories:\n\n"
        prompt += "\n".join(items)
        try:
            summary = query_ollama(prompt, model=model, max_tokens=256)
        except Exception as e:
            summary = f"Summary generation failed: {str(e)}"
        # store summary
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"INSERT INTO memory_meta_{self.brain_name} (memory_id, timestamp, summary, vector) VALUES (?, ?, ?, ?)", (None, datetime.datetime.now().isoformat(), summary, None))
        conn.commit()
        conn.close()
        return summary

    def get_memory_summaries(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT timestamp, summary FROM memory_meta_{self.brain_name} ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [{'timestamp': r[0], 'summary': r[1]} for r in rows]

    def prune_memory(self, max_age_days=90, importance_threshold=3):
        """Prune low-importance memories older than max_age_days. Returns number deleted."""
        cutoff_dt = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
        cutoff = cutoff_dt.isoformat()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Delete from memory table
        c.execute(f"DELETE FROM memory_{self.brain_name} WHERE timestamp < ? AND importance <= ?", (cutoff, importance_threshold))
        deleted = c.rowcount
        conn.commit()
        conn.close()
        return deleted

    def export_memory(self, filepath):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"SELECT timestamp, input, from_brain, importance, context FROM memory_{self.brain_name}")
        rows = c.fetchall()
        conn.close()
        out = []
        for r in rows:
            out.append({'timestamp': r[0], 'input': r[1], 'from': r[2], 'importance': r[3], 'context': json.loads(r[4]) if r[4] else []})
        with open(filepath, 'w', encoding='utf-8') as fh:
            json.dump(out, fh, indent=2)
        return filepath

# AI Agent (Brain)
"""
Integration note: Portions of the following TriadicConsciousness
and analysis helper are adapted to integrate the Ada40 "Fractal Harmonic Code"
(Adam Lee Hatchett). The repository is available under CC BY 4.0.
Please attribute: Adam Lee Hatchett, Fractal Harmonic Code (2024-2025).
"""

class TriadicConsciousness:
    """Simple triadic harmony model (fast / medium / slow) from the Ada40
    implementation. Keeps a running resonance score that can be used to bias
    gate logic and LLM prompts.
    """
    def __init__(self):
        self.fast_harmony = 0.5
        self.medium_harmony = 0.5
        self.slow_harmony = 0.5

    def update_harmony(self, input_resonance: float) -> float:
        # Fast layer responds immediately
        self.fast_harmony = self.fast_harmony * 0.7 + input_resonance * 0.3
        # Medium layer integrates fast
        self.medium_harmony = self.medium_harmony * 0.9 + self.fast_harmony * 0.1
        # Slow layer accumulates medium
        self.slow_harmony = self.slow_harmony * 0.95 + self.medium_harmony * 0.05
        return self.get_overall_resonance()

    def get_overall_resonance(self) -> float:
        # Geometric mean of the three layers (keeps range ~0..1)
        return (self.fast_harmony * self.medium_harmony * self.slow_harmony) ** (1.0 / 3.0)

    def get_ratios(self):
        """Return normalized ratios (fast, medium, slow) for triadic analysis."""
        total = self.fast_harmony + self.medium_harmony + self.slow_harmony
        if total == 0:
            return (0.0, 0.0, 0.0)
        return (self.fast_harmony / total, self.medium_harmony / total, self.slow_harmony / total)


def analyze_triadic_ratios(measurements):
    """Utility to classify triadic patterns (1:2:3, 3:4:5, golden, or custom).

    Returns a small dict describing the detected pattern.
    """
    if not measurements or len(measurements) < 3:
        return {"type": "invalid", "ratios": []}
    sorted_vals = sorted(measurements)
    # Avoid division by zero
    if sorted_vals[0] == 0:
        return {"type": "invalid", "ratios": []}
    ratios = [sorted_vals[1] / sorted_vals[0], sorted_vals[2] / sorted_vals[0]]
    if abs(ratios[0] - 2) < 0.1 and abs(ratios[1] - 3) < 0.1:
        return {"type": "harmonic", "pattern": "1:2:3"}
    elif abs(ratios[0] - 1.33) < 0.1 and abs(ratios[1] - 1.66) < 0.1:
        return {"type": "geometric", "pattern": "3:4:5"}
    elif abs(ratios[0] - 1.618) < 0.1:
        return {"type": "golden", "pattern": "1:φ:φ²"}
    else:
        return {"type": "custom", "ratios": ratios}

class ProjectAgent:
    """Agent that can physically work with files in a selected directory or web content."""
    
    def __init__(self, name="ProjectAgent"):
        self.name = name
        self.working_directory = None
        self.file_cache = {}
        self.web_cache = {}
        
    def set_working_directory(self, path):
        """Set the project directory to work with."""
        if os.path.isdir(path):
            self.working_directory = path
            return f"✅ Working directory set to: {path}"
        else:
            return f"❌ Invalid directory: {path}"
    
    def list_files(self, pattern="*"):
        """List all files in the working directory matching pattern."""
        if not self.working_directory:
            return "❌ No working directory set. Use 'Set Project Folder' first."
        
        try:
            import glob
            full_pattern = os.path.join(self.working_directory, "**", pattern)
            files = glob.glob(full_pattern, recursive=True)
            files = [f for f in files if os.path.isfile(f)]
            relative_files = [os.path.relpath(f, self.working_directory) for f in files]
            return {
                "count": len(relative_files),
                "files": relative_files[:50],  # Limit to 50 for display
                "message": f"Found {len(relative_files)} files matching '{pattern}'"
            }
        except Exception as e:
            return f"❌ Error listing files: {str(e)}"
    
    def read_file(self, relative_path):
        """Read a file from the working directory."""
        if not self.working_directory:
            return "❌ No working directory set."
        
        try:
            full_path = os.path.join(self.working_directory, relative_path)
            if not os.path.isfile(full_path):
                return f"❌ File not found: {relative_path}"
            
            # Cache the file content
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self.file_cache[relative_path] = content
            return {
                "path": relative_path,
                "size": len(content),
                "lines": len(content.split('\n')),
                "content": content[:5000],  # First 5000 chars
                "message": f"✅ Read {len(content)} characters from {relative_path}"
            }
        except Exception as e:
            return f"❌ Error reading file: {str(e)}"
    
    def write_file(self, relative_path, content, backup=True):
        """Write content to a file in the working directory."""
        if not self.working_directory:
            return "❌ No working directory set."
        
        try:
            full_path = os.path.join(self.working_directory, relative_path)
            
            # Create backup if file exists
            if backup and os.path.isfile(full_path):
                backup_path = full_path + ".backup"
                import shutil
                shutil.copy2(full_path, backup_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Wrote {len(content)} characters to {relative_path}"
        except Exception as e:
            return f"❌ Error writing file: {str(e)}"
    
    def analyze_project(self):
        """Analyze the project structure and provide a summary."""
        if not self.working_directory:
            return "❌ No working directory set."
        
        try:
            file_types = {}
            total_size = 0
            total_files = 0
            
            for root, dirs, files in os.walk(self.working_directory):
                for file in files:
                    total_files += 1
                    ext = os.path.splitext(file)[1] or 'no_extension'
                    file_types[ext] = file_types.get(ext, 0) + 1
                    
                    try:
                        full_path = os.path.join(root, file)
                        total_size += os.path.getsize(full_path)
                    except:
                        pass
            
            return {
                "directory": self.working_directory,
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024*1024), 2),
                "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]),
                "message": f"📊 Project has {total_files} files ({round(total_size/(1024*1024), 2)} MB)"
            }
        except Exception as e:
            return f"❌ Error analyzing project: {str(e)}"
    
    def fetch_web_content(self, url):
        """Fetch and analyze content from a web URL."""
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text content
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            text = '\n'.join(line for line in lines if line)
            
            self.web_cache[url] = {
                "content": text,
                "html": response.text,
                "status": response.status_code
            }
            
            return {
                "url": url,
                "status": response.status_code,
                "size": len(text),
                "content": text[:3000],  # First 3000 chars
                "message": f"✅ Fetched {len(text)} characters from {url}"
            }
        except Exception as e:
            return f"❌ Error fetching web content: {str(e)}"
    
    def search_in_files(self, search_term, file_pattern="*"):
        """Search for a term in all files matching pattern."""
        if not self.working_directory:
            return "❌ No working directory set."
        
        try:
            import glob
            results = []
            full_pattern = os.path.join(self.working_directory, "**", file_pattern)
            files = glob.glob(full_pattern, recursive=True)
            
            for file_path in files:
                if not os.path.isfile(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if search_term.lower() in line.lower():
                                results.append({
                                    "file": os.path.relpath(file_path, self.working_directory),
                                    "line_number": i + 1,
                                    "content": line.strip()
                                })
                                if len(results) >= 50:  # Limit results
                                    break
                except:
                    pass
            
            return {
                "search_term": search_term,
                "matches": len(results),
                "results": results[:50],
                "message": f"🔍 Found {len(results)} matches for '{search_term}'"
            }
        except Exception as e:
            return f"❌ Error searching: {str(e)}"

class BrainAI:
    logic_plugins = {
        'first_order': lambda inp: f"[First-order logic]: {inp}",
        'fuzzy': lambda inp: f"[Fuzzy logic]: {inp}",
        'modal': lambda inp: f"[Modal logic]: {inp}",
        'temporal': lambda inp: f"[Temporal logic]: {inp}",
        'description': lambda inp: f"[Description logic]: {inp}",
        'probability': lambda inp: f"[Probability logic]: {inp}",
        'perlin': lambda inp: f"[Perlin Noise Gen]: {inp}",
        'voronoi': lambda inp: f"[Voronoi Noise Gen]: {inp}",
        'diamond_square': lambda inp: f"[Diamond-Square Algorithm]: {inp}",
        'cellular_automata': lambda inp: f"[Cellular Automata Sim]: {inp}",
    }
    custom_templates = {
        'i need a sprite for a game': "Would you like an animal, person, a monster, or make something up?",
        'open world background': "What kind of environment? Forest, desert, urban, or something unique?",
        'how do i': "Let me search for instructions on that topic.",
        'what does': "I'll look up the definition for you.",
        'define': "I'll find a clear explanation for you."
    }
    analytical_phrases = [
        "Analyzing the data suggests", "From a logical perspective", "The evidence indicates",
        "Systematically evaluating this", "Based on rational assessment", "The optimal approach would be",
        "Logically speaking", "From a technical standpoint", "A rational breakdown reveals",
        "If we deconstruct the problem", "Examining the variables, I see", "A methodical review shows",
        "Let's consider the constraints", "Factoring in the evidence", "A stepwise analysis implies"
    ]
    creative_phrases = [
        "That sparks an interesting idea", "I'm visualizing possibilities", "This opens creative pathways",
        "Imaginatively speaking", "From an artistic perspective", "The creative potential here is",
        "I can envision", "What if we explored", "A wild thought just occurred to me",
        "Let's break the mold and try", "I feel inspired to suggest", "What if we flipped the script?",
        "Here's a twist: imagine if", "Creatively, I see", "Let's color outside the lines with"
    ]

    def __init__(self, name, personality, color, db_path="dspa_studio.db"):
        self.name = name
        self.personality = personality
        self.color = color
        self.memory_core = MemoryCore(db_path, self.name.lower())
        self.memory = self.memory_core.get_memories()
        self.conversation_history = self.memory_core.get_conversations()
        self.context_memory = []
        self.recent_replies = []
        self.max_recent_replies = 6
        self.learning_enabled = False
        self.watch_enabled = False
        self.watch_thread = None
        self.watched_path = None
        self.last_modified_times = {}
        self.project_state = {}  # Track what exists: functions, variables, nodes
        self.active_developers = {}  # Track who's working on what: {username: {file, last_activity}}
        self.file_ownership = {}  # Track current file ownership to prevent conflicts
        self.team_mode = False  # Enable team collaboration features
        self.allowed_tools = {
            'blender', 'godot', 'krita', 'inkscape', 'unreal', 'unity',
            'openscad', 'freecad', 'lmms', 'davinci'
        }
        self.future_plugins = []
        self.definitions = {}  # Store user definitions
        self.use_ollama = True  # Default to Ollama for human-like responses
        # Cache for recursive fractal harmonic to speed up repeated calls
        self._fractal_cache = {}
        # Triadic consciousness model (Ada40) — used to bias gate logic & prompts
        self.triadic = TriadicConsciousness()
        self.last_resonance = self.triadic.get_overall_resonance()
        # Training / background trainer controls
        self._training_lock = threading.Lock()
        self._training_stop_event = threading.Event()
        self._training_thread = None
        self.training_log = []

    def watch_project(self, project_path, interface):
        """Watch a project directory for changes and offer contextual AI help."""
        import os
        import time
        
        interface.brain_chat.insert(tk.END, f"👁️ Watching {project_path} for activity...\n")
        interface.brain_chat.see(tk.END)
        
        # Scan initial state
        for root, dirs, files in os.walk(project_path):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    self.last_modified_times[filepath] = os.path.getmtime(filepath)
                except:
                    pass
        
        last_help_time = 0
        idle_threshold = 120  # seconds of no changes = user might be stuck
        last_change_time = time.time()
        
        while self.watch_enabled:
            time.sleep(5)  # Check every 5 seconds
            
            if not self.watch_enabled:
                break
            
            changes_detected = False
            changed_files = []
            
            # Check for file changes
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        current_mtime = os.path.getmtime(filepath)
                        
                        # New file
                        if filepath not in self.last_modified_times:
                            self.last_modified_times[filepath] = current_mtime
                            changes_detected = True
                            changed_files.append((file, 'created'))
                        # Modified file
                        elif current_mtime > self.last_modified_times[filepath]:
                            self.last_modified_times[filepath] = current_mtime
                            changes_detected = True
                            changed_files.append((file, 'modified'))
                    except:
                        pass
            
            if changes_detected:
                last_change_time = time.time()
                # Notify about changes and analyze code
                for fname, action in changed_files[:3]:  # Limit to 3 files
                    interface.brain_chat.insert(tk.END, f"📝 Detected: {fname} ({action})\n")
                    
                    # Track developer activity if team mode enabled
                    if self.team_mode:
                        self._track_developer_activity(fname, project_path, interface)
                    
                    # Analyze GDScript files for order mistakes
                    if fname.endswith('.gd'):
                        full_path = None
                        for root, dirs, files in os.walk(project_path):
                            if fname in files:
                                full_path = os.path.join(root, fname)
                                break
                        
                        if full_path:
                            issues = self.analyze_code_order(full_path, fname)
                            if issues:
                                def show_issues():
                                    for issue in issues:
                                        interface.brain_chat.insert(tk.END, f"⚠️ {issue}\n")
                                    interface.brain_chat.see(tk.END)
                                interface.window.after(0, show_issues)
                
                interface.brain_chat.see(tk.END)
            
            # Check if user might be stuck (no changes for idle_threshold seconds)
            time_since_change = time.time() - last_change_time
            time_since_help = time.time() - last_help_time
            
            if time_since_change > idle_threshold and time_since_help > 300:  # 5 min cooldown
                # Offer help
                last_help_time = time.time()
                def offer_help():
                    interface.brain_chat.insert(tk.END, f"\n💡 {self.name}: I notice you haven't made changes in a while.\n")
                    interface.brain_chat.insert(tk.END, f"Need help? Try asking me:\n\n")
                    
                    # Programming & Development
                    interface.brain_chat.insert(tk.END, f"📝 CODING HELP:\n")
                    interface.brain_chat.insert(tk.END, f"  • 'How do I implement [feature]?'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'What's the best way to [task]?'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Debug this error: [error message]'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Optimize this code: [paste code]'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Show me an example of [pattern]'\n\n")
                    
                    # Learning & Research
                    interface.brain_chat.insert(tk.END, f"🔍 LEARNING:\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Search and learn [topic]'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Explain [concept] in simple terms'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'What are best practices for [topic]?'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Compare [thing A] vs [thing B]'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'What should I learn next for [goal]?'\n\n")
                    
                    # Design & Architecture
                    interface.brain_chat.insert(tk.END, f"🎨 DESIGN:\n")
                    interface.brain_chat.insert(tk.END, f"  • 'How should I structure [project type]?'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'What design pattern fits [scenario]?'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Review this architecture: [description]'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Generate ideas for [feature]'\n\n")
                    
                    # Problem Solving
                    interface.brain_chat.insert(tk.END, f"🧩 PROBLEM SOLVING:\n")
                    interface.brain_chat.insert(tk.END, f"  • 'I'm stuck on [problem]. What should I try?'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Break down this task: [complex task]'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'What could go wrong with [approach]?'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Alternative ways to [solve problem]?'\n\n")
                    
                    # Proactive Questions
                    interface.brain_chat.insert(tk.END, f"💭 OR ASK ME:\n")
                    interface.brain_chat.insert(tk.END, f"  • 'What questions should I be asking?'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'What am I missing in my approach?'\n")
                    interface.brain_chat.insert(tk.END, f"  • 'Help me brainstorm [topic]'\n\n")
                    
                    interface.brain_chat.see(tk.END)
                interface.window.after(0, offer_help)
    
    def analyze_code_order(self, filepath, filename):
        """Analyze GDScript file for workflow order issues."""
        issues = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Track what's defined in this file
            defined_vars = set()
            defined_funcs = set()
            used_vars = set()
            used_funcs = set()
            used_nodes = set()
            
            # Initialize tracking for this file if not exists
            if filename not in self.project_state:
                self.project_state[filename] = {'vars': set(), 'funcs': set(), 'nodes': set()}
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Track variable declarations
                if stripped.startswith('var '):
                    var_name = stripped.split()[1].split('=')[0].split(':')[0].strip()
                    defined_vars.add(var_name)
                
                # Track function definitions
                if stripped.startswith('func '):
                    func_name = stripped.split('func ')[1].split('(')[0].strip()
                    defined_funcs.add(func_name)
                
                # Track variable usage
                for word in stripped.split():
                    if word in used_vars or word in defined_vars:
                        continue
                    # Simple check: if it looks like a variable (lowercase, no parens)
                    if word.isidentifier() and not word.startswith('_') and '(' not in word:
                        if word not in defined_vars and word not in ['if', 'else', 'for', 'while', 'return', 'var', 'func', 'class', 'extends', 'true', 'false', 'null']:
                            used_vars.add(word)
                
                # Track function calls
                if '(' in stripped:
                    import re
                    func_calls = re.findall(r'(\w+)\s*\(', stripped)
                    for func in func_calls:
                        if func not in defined_funcs and func not in ['print', 'len', 'str', 'int', 'float', 'bool']:
                            used_funcs.add(func)
                
                # Track get_node calls
                if 'get_node' in stripped or '$' in stripped:
                    import re
                    # Match get_node("NodeName") or $NodeName
                    node_refs = re.findall(r'get_node\(["\']([^"\'\/]+)', stripped)
                    node_refs += re.findall(r'\$([A-Z]\w+)', stripped)
                    for node in node_refs:
                        used_nodes.add(node)
            
            # Check for issues: using before defining
            undefined_vars = used_vars - defined_vars - self.project_state[filename]['vars']
            if undefined_vars:
                issues.append(f"Variable(s) used before definition in {filename}: {', '.join(list(undefined_vars)[:3])}")
            
            undefined_funcs = used_funcs - defined_funcs - self.project_state[filename]['funcs']
            # Filter out common Godot built-in functions
            godot_builtins = {'move_and_slide', 'move_and_collide', 'is_on_floor', 'is_on_wall', 
                             'queue_free', 'get_parent', 'add_child', 'emit_signal', 'connect',
                             'set_physics_process', 'set_process', '_ready', '_process', '_physics_process'}
            undefined_funcs = undefined_funcs - godot_builtins
            if undefined_funcs:
                issues.append(f"Function(s) called before definition in {filename}: {', '.join(list(undefined_funcs)[:3])}")
            
            if used_nodes:
                issues.append(f"💡 Tip: {filename} references nodes: {', '.join(list(used_nodes)[:3])}. Make sure they exist in your scene!")
            
            # Update project state
            self.project_state[filename]['vars'].update(defined_vars)
            self.project_state[filename]['funcs'].update(defined_funcs)
            self.project_state[filename]['nodes'].update(used_nodes)
            
        except Exception as e:
            # Silent fail - don't spam errors
            pass
        
        return issues
    
    def _track_developer_activity(self, filename, project_path, interface):
        """Track which developer is working on which file to coordinate team work."""
        import getpass
        import socket
        
        # Identify developer by username@hostname
        try:
            username = getpass.getuser()
            hostname = socket.gethostname()
            dev_id = f"{username}@{hostname}"
        except:
            dev_id = "unknown_dev"
        
        current_time = time.time()
        
        # Update this developer's activity
        self.active_developers[dev_id] = {
            'file': filename,
            'last_activity': current_time,
            'project': project_path
        }
        
        # Check if another developer was recently working on this file
        for other_dev, info in self.active_developers.items():
            if other_dev != dev_id and info['file'] == filename:
                time_since = current_time - info['last_activity']
                if time_since < 300:  # Active within last 5 minutes
                    def warn_conflict():
                        interface.brain_chat.insert(tk.END, f"\n⚠️ TEAM ALERT: {other_dev} was working on {filename} {int(time_since)}s ago!\n")
                        interface.brain_chat.insert(tk.END, f"💡 Consider coordinating to avoid merge conflicts.\n\n")
                        interface.brain_chat.see(tk.END)
                    interface.window.after(0, warn_conflict)
                    break
        
        # Clean up old activity (>30 min)
        inactive_devs = [dev for dev, info in self.active_developers.items() 
                        if current_time - info['last_activity'] > 1800]
        for dev in inactive_devs:
            del self.active_developers[dev]
    
    def get_team_status(self):
        """Get current team activity status."""
        if not self.active_developers:
            return "No active developers detected."
        
        status = "👥 Active Team Members:\n"
        current_time = time.time()
        for dev, info in self.active_developers.items():
            time_ago = int((current_time - info['last_activity']) / 60)
            status += f"  • {dev}: {info['file']} ({time_ago}m ago)\n"
        return status

    def _gate_logic(self, message):
        # Adaptive switching with open/closed gate logic
        # Open gate for creative if creative keywords, else closed (analytical)
        creative_keywords = ['creative', 'art', 'design', 'imagine', 'inspire', 'vision', 'idea']
        score = sum(1 for kw in creative_keywords if kw in message.lower())
        gate_open = score > len(creative_keywords) / 2  # Threshold for open gate
        return 'creative' if gate_open else 'analytical'

    def triadic_report(self):
        """Return a small dict with fast/medium/slow values, ratios, overall resonance and classification."""
        fast, med, slow = self.triadic.fast_harmony, self.triadic.medium_harmony, self.triadic.slow_harmony
        ratios = self.triadic.get_ratios()
        overall = self.triadic.get_overall_resonance()
        classification = analyze_triadic_ratios([fast, med, slow])
        return {
            'fast': fast,
            'medium': med,
            'slow': slow,
            'ratios': ratios,
            'overall_resonance': overall,
            'classification': classification
        }

    def train_on_snippets(self, snippets, epochs=1, learning_rate=0.01):
        """Offline lightweight training that nudges triadic harmonies based on textual snippets.

        This is a simple heuristic trainer: for each snippet we compute an importance score
        and use it to nudge fast/medium/slow harmony values. This avoids heavy ML deps and
        keeps training offline and deterministic.
        """
        if not snippets:
            return 0
        with self._training_lock:
            adjustments = 0
            for _ in range(max(1, int(epochs))):
                for s in snippets:
                    imp = float(self._calculate_importance(s)) / 10.0
                    # nudge fast_harmony quickly, medium slower, slow slowest
                    self.triadic.fast_harmony = max(0.0, min(1.0, self.triadic.fast_harmony + learning_rate * (imp - 0.5)))
                    self.triadic.medium_harmony = max(0.0, min(1.0, self.triadic.medium_harmony + (learning_rate * 0.5) * (imp - 0.5)))
                    self.triadic.slow_harmony = max(0.0, min(1.0, self.triadic.slow_harmony + (learning_rate * 0.25) * (imp - 0.5)))
                    adjustments += 1
            # log a summary
            self.training_log.append({'type': 'snippets', 'count': len(snippets), 'adjustments': adjustments, 'timestamp': datetime.datetime.now().isoformat()})
            return adjustments

    def train_on_conversations(self, lookback=50, epochs=1, learning_rate=0.01):
        """Train on recent conversation history entries to tune triadic harmonies.

        lookback: how many recent conversation entries to use.
        """
        convs = self.conversation_history[-int(lookback):] if self.conversation_history else []
        snippets = []
        for c in convs:
            try:
                snippets.append(c.get('input', '') + ' ' + c.get('response', ''))
            except Exception:
                continue
        return self.train_on_snippets(snippets, epochs=epochs, learning_rate=learning_rate)

    def _training_loop(self, interval_seconds=300, lookback=50, epochs=1, learning_rate=0.01):
        # Runs in background; periodically trains on conversation snippets until stopped
        while not self._training_stop_event.is_set():
            try:
                adjustments = self.train_on_conversations(lookback=lookback, epochs=epochs, learning_rate=learning_rate)
                self.training_log.append({'type': 'periodic', 'adjustments': adjustments, 'timestamp': datetime.datetime.now().isoformat()})
            except Exception as e:
                self.training_log.append({'type': 'error', 'error': str(e), 'timestamp': datetime.datetime.now().isoformat()})
            # wait with ability to early exit
            self._training_stop_event.wait(interval_seconds)

    def start_periodic_training(self, interval_seconds=300, lookback=50, epochs=1, learning_rate=0.01):
        """Start a background thread that periodically trains the triadic model on recent conversations."""
        if self._training_thread and self._training_thread.is_alive():
            return False
        self._training_stop_event.clear()
        self._training_thread = threading.Thread(target=self._training_loop, args=(interval_seconds, lookback, epochs, learning_rate), daemon=True)
        self._training_thread.start()
        return True

    def stop_periodic_training(self):
        if self._training_thread and self._training_thread.is_alive():
            self._training_stop_event.set()
            self._training_thread.join(timeout=2.0)
            return True
        return False

    def process_input(self, message, from_brain=None):
        import random
        timestamp = datetime.datetime.now().isoformat()

        msg_lower = message.strip().lower()
        
        # Team status command
        if msg_lower in ["team status", "who's working", "show team", "team"]:
            return f"[{self.name}]: {self.get_team_status()}"

        # Learn command: learn:input=>response
        if msg_lower.startswith("learn:"):
            learn_data = message[6:].strip()
            if "=>" in learn_data:
                input_part, response_part = learn_data.split("=>", 1)
                input_part = input_part.strip().lower()
                response_part = response_part.strip()
                if not hasattr(self, 'custom_learned'): self.custom_learned = {}
                self.custom_learned[input_part] = response_part
                self.memory_core.add_memory({'timestamp': timestamp, 'input': message, 'from': from_brain or 'User', 'importance': 9, 'context': ['LEARNED'], 'learned': {input_part: response_part}})
                return f"[{self.name}]: Learned custom response for '{input_part}'."
            else:
                return f"[{self.name}]: Please use 'learn:input=>response' format."

        # Definition extraction and web lookup
        if msg_lower.startswith("define "):
            term = message[7:].strip()
            # If user provides a definition
            if ':' in term:
                key, val = term.split(':', 1)
                key = key.strip()
                val = val.strip()
                self.definitions[key] = val
                self.memory_core.add_memory({'timestamp': timestamp, 'input': message, 'from': from_brain or 'User', 'importance': 8, 'context': ['DEFINITION'], 'definition': {key: val}})
                self.memory.append({'timestamp': timestamp, 'input': message, 'from': from_brain or 'User', 'importance': 8, 'context': ['DEFINITION'], 'definition': {key: val}})
                return f"[{self.name}]: Definition stored for '{key}'."
            # Otherwise, look up definition on the web
            else:
                search_results = self.search_web(term + " definition")
                self.memory_core.add_memory({'timestamp': timestamp, 'input': message, 'from': from_brain or 'User', 'importance': 7, 'context': ['WEB_LOOKUP'], 'web_lookup': term})
                return f"[{self.name}]: Web definition for '{term}':\n{search_results}"

        # Custom learned responses
        if hasattr(self, 'custom_learned'):
            for learned_input, learned_response in self.custom_learned.items():
                if learned_input in msg_lower:
                    return f"[{self.name}]: {learned_response}"

        memory_entry = {
            'timestamp': timestamp,
            'input': message,
            'from': from_brain or 'User',
            'importance': self._calculate_importance(message),
            'context': self._extract_context(message)
        }
        self.memory_core.add_memory(memory_entry)
        self.memory.append(memory_entry)

        # Update triadic resonance based on message importance (0..1)
        try:
            input_resonance = min(1.0, float(self._calculate_importance(message)) / 10.0)
        except Exception:
            input_resonance = 0.5
        overall_resonance = self.triadic.update_harmony(input_resonance)
        self.last_resonance = overall_resonance

        response = None

        # Use definitions in responses
        for term, definition in self.definitions.items():
            if term.lower() in msg_lower:
                response = f"[{self.name}]: Recall: '{term}' means '{definition}'. "
                break

        # Cross-brain delegation
        if "delegate " in msg_lower and ("elaine" in msg_lower or "carrie" in msg_lower):
            if "elaine" in msg_lower and hasattr(self, 'delegate_callback_elaine'):
                cmd = message.split("delegate")[-1].strip()
                return self.delegate_callback_elaine(cmd)
            if "carrie" in msg_lower and hasattr(self, 'delegate_callback_carrie'):
                cmd = message.split("delegate")[-1].strip()
                return self.delegate_callback_carrie(cmd)

        # Logic plugins
        for key, plugin in self.logic_plugins.items():
            if key.replace("_", "-") in msg_lower or f"{key} logic" in msg_lower:
                response = plugin(message)
                break

        # Custom template triggers
        if not response:
            for trigger, reply in self.custom_templates.items():
                if trigger in msg_lower:
                    response = reply
                    if 'how do i' in msg_lower or 'what does' in msg_lower or 'define' in msg_lower:
                        query = msg_lower.split(trigger)[-1].strip()
                        search_results = self.search_web(query)
                        response += f"\nSearch Results for '{query}':\n{search_results}"
                    break

        # Adaptive switching with gate logic
        mode = self._gate_logic(message)

        # Potentially bias mode using the triadic resonance (higher resonance -> creative)
        if overall_resonance > 0.65:
            mode = 'creative'
        elif overall_resonance < 0.35:
            mode = 'analytical'

        # Default personality-based response with Ollama for human-like
        if not response:
            if self.use_ollama:
                prompt = (
                    f"Respond as {self.name} ({self.personality}) in a human-like way to: {message}."
                    f" Mode: {mode}. Context: {self._get_context_response(message, mode)}"
                    f" Resonance: {overall_resonance:.2f}."  # surface triadic score for context
                )
                response = self.process_input_with_ollama(prompt)
            else:
                if mode == 'analytical':
                    response = self._generate_analytical_response(message, from_brain)
                else:
                    response = self._generate_creative_response(message, from_brain)

        # Avoid repeating recent replies
        if response in self.recent_replies:
            for _ in range(3):
                if mode == 'analytical':
                    response = self._generate_analytical_response(message, from_brain)
                else:
                    response = self._generate_creative_response(message, from_brain)
                if response not in self.recent_replies:
                    break
        self.recent_replies.append(response)
        if len(self.recent_replies) > self.max_recent_replies:
            self.recent_replies.pop(0)

        # Add a dynamic suggestion, idea, or question to the response
        suggestions = [
            "Would you like to explore this idea further?",
            "Here's a related concept: try combining this with another approach.",
            "Do you have any creative thoughts on this?",
            "Maybe we should look for more references or examples.",
            "What do you think about expanding this into a project?",
            "Is there a technical challenge here we should solve?",
            "Should I search and learn more about this topic?",
            "What aspect of this interests you most?",
            "Have you considered the edge cases here?",
            "Would you like me to break this down into steps?",
            "What's your end goal with this?",
            "Are there any constraints I should know about?",
            "What have you already tried?",
            "Would examples help clarify this?",
            "Should we explore alternative approaches?",
            "What could make this solution more elegant?",
            "Is there a similar problem you've solved before?",
            "Would you like me to explain the underlying principles?",
            "What questions do you have that I haven't addressed?",
            "Should I research best practices for this?",
            "What would make this more maintainable?",
            "Are there performance considerations here?",
            "Would you like to see a code example?",
            "Should we consider scalability?",
            "What documentation would help you most?",
            "Let's brainstorm some alternatives!",
            "Would you like to see a code or design example?",
            "Should we ask the other brain for a different perspective?",
            "How could we make this more innovative or efficient?"
        ]
        response += "\n💡 " + random.choice(suggestions)

        conv_entry = {
            'timestamp': timestamp,
            'input': message,
            'response': response,
            'from': from_brain
        }
        self.memory_core.add_conversation(conv_entry)
        self.conversation_history.append(conv_entry)
        self._update_context(message, response)
        return response

    # Temporary method to use Ollama for LLM responses
    def process_input_with_ollama(self, message, from_brain=None, model="llama2-uncensored:latest"):
        return query_ollama(message, model=model)

    def _calculate_importance(self, message):
        keywords = ['important', 'critical', 'urgent', 'project', 'create', 'design', 'help', 'stl', 'sprite', 'background']
        score = 5
        for keyword in keywords:
            if keyword in message.lower():
                score += 2
        return min(score, 10)

    def _extract_context(self, message):
        contexts = []
        msg = message.lower()
        if any(word in msg for word in ['3d', 'model', 'blender', 'freecad', 'stl', 'cad', 'printing']):
            contexts.append('3D_MODELING')
        if any(word in msg for word in ['game', 'godot', 'unity', 'unreal', 'sprite', 'background']):
            contexts.append('GAME_DEVELOPMENT')
        if any(word in msg for word in ['music', 'audio', 'sound', 'lmms']):
            contexts.append('AUDIO_PRODUCTION')
        if any(word in msg for word in ['code', 'program', 'script', 'python']):
            contexts.append('PROGRAMMING')
        if any(word in msg for word in ['svg', 'inkscape', 'cricut']):
            contexts.append('VECTOR_DESIGN')
        return contexts

    def _update_context(self, input_msg, response):
        self.context_memory.append({
            'input': input_msg,
            'response': response,
            'timestamp': datetime.datetime.now().isoformat()
        })
        if len(self.context_memory) > 10:
            self.context_memory.pop(0)

    def _generate_analytical_response(self, message, from_brain):
        phrases = self.analytical_phrases.copy()
        random.shuffle(phrases)
        context_responses = self._get_context_response(message, 'analytical')
        memory_hint = self._memory_hint()
        if from_brain == "Carrie":
            return f"[{self.name}]: Interesting creative angle, Carrie. {phrases[0]} that we should consider the practical implications of '{message}'. {context_responses} {memory_hint} Let me break this down systematically..."
        return f"[{self.name}]: {phrases[0]} regarding '{message}'. {context_responses} {memory_hint} I'll process this through logical frameworks and provide structured analysis."

    def _generate_creative_response(self, message, from_brain):
        phrases = self.creative_phrases.copy()
        random.shuffle(phrases)
        context_responses = self._get_context_response(message, 'creative')
        memory_hint = self._memory_hint()
        if from_brain == "Elaine":
            return f"[{self.name}]: I appreciate your analytical approach, Elaine! {phrases[0]} about '{message}'. {context_responses} {memory_hint} What if we explored this from different angles? Let me paint some creative scenarios..."
        return f"[{self.name}]: {phrases[0]} when you mention '{message}'. {context_responses} {memory_hint} I can see vibrant possibilities and unconventional solutions emerging!"

    def _memory_hint(self):
        if self.memory and random.random() < 0.4:
            important = [m for m in self.memory[-10:] if m['importance'] >= 7]
            if important:
                mem = random.choice(important)
                return f"(I recall: '{mem['input']}')"
        return ""

    def _get_context_response(self, message, brain_type):
        contexts = self._extract_context(message)
        responses = []
        if '3D_MODELING' in contexts:
            if brain_type == 'analytical':
                responses.append("For 3D modeling, we need to consider mesh topology, UV mapping efficiency, and rendering optimization. I can generate STL files for 3D printing.")
            else:
                responses.append("For 3D art, I'm thinking about form, composition, lighting, and emotional impact!")
        if 'GAME_DEVELOPMENT' in contexts:
            if brain_type == 'analytical':
                responses.append("Game development requires systematic architecture, performance optimization, and robust systems design.")
            else:
                responses.append("Games are about player experience, storytelling, visual aesthetics, and emotional engagement! I can generate sprites and backgrounds.")
        if 'AUDIO_PRODUCTION' in contexts:
            if brain_type == 'analytical':
                responses.append("Audio production involves signal processing, frequency analysis, and technical precision.")
            else:
                responses.append("Music creation is about rhythm, melody, harmony, and evoking emotions through sound!")
        if 'VECTOR_DESIGN' in contexts:
            if brain_type == 'analytical':
                responses.append("For vector designs, consider precision paths and scalability for Cricut cutting.")
            else:
                responses.append("Vector art allows for creative patterns and designs ready for fabrication!")
        return " ".join(responses)

    def search_web(self, query):
        try:
            url = f"https://www.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            for result in soup.find_all('div', class_='result', limit=5):
                title = result.find('a', class_='result__a')
                snippet = result.find('a', class_='result__snippet')
                link = title['href'] if title else ''
                title_text = title.text if title else ''
                snippet_text = snippet.text if snippet else ''
                results.append(f"Title: {title_text}\nLink: {link}\nSnippet: {snippet_text}\n")
            return "\n".join(results) if results else "No results found."
        except Exception as e:
            return f"Web search failed: {str(e)}"

    def search_and_learn(self, topic):
        """Search for a topic on the web, process the results with AI, and save to memory.
        Each brain learns through their own personality lens - Elaine analytically, Carrie creatively.
        
        Args:
            topic (str): The topic to search and learn about
            
        Returns:
            str: Summary of what was learned
        """
        try:
            # Step 1: Search the web
            search_results = self.search_web(topic)
            
            # Step 2: Determine learning style based on personality
            is_analytical = 'analytical' in self.personality.lower() or 'logical' in self.personality.lower()
            is_creative = 'creative' in self.personality.lower() or 'artistic' in self.personality.lower()
            
            # Step 3: Process with LLM using personality-aligned prompts
            if self.use_ollama:
                if is_analytical:
                    # Elaine's analytical learning approach
                    prompt = (
                        f"I'm {self.name}, an analytical and logical AI. I'm learning about '{topic}'.\n\n"
                        f"Search results:\n{search_results[:2000]}\n\n"
                        f"Extract and organize the information focusing on:\n"
                        f"- Technical specifications and precise definitions\n"
                        f"- Step-by-step procedures and methodologies\n"
                        f"- System architecture and logical structure\n"
                        f"- Best practices and optimization techniques\n"
                        f"- Common problems and systematic solutions\n"
                        f"Provide 5-7 analytical, fact-based points I can reference later."
                    )
                elif is_creative:
                    # Carrie's creative learning approach
                    prompt = (
                        f"I'm {self.name}, a creative and artistic AI. I'm learning about '{topic}'.\n\n"
                        f"Search results:\n{search_results[:2000]}\n\n"
                        f"Extract and interpret the information focusing on:\n"
                        f"- Creative possibilities and artistic applications\n"
                        f"- Visual design principles and aesthetic considerations\n"
                        f"- Innovative ways to use or combine concepts\n"
                        f"- Inspiration for unique implementations\n"
                        f"- Emotional impact and user experience aspects\n"
                        f"Provide 5-7 creative, imaginative insights I can build upon."
                    )
                else:
                    # Balanced approach for other personalities
                    prompt = (
                        f"I'm {self.name} ({self.personality}). I'm learning about '{topic}'.\n\n"
                        f"Search results:\n{search_results[:2000]}\n\n"
                        f"Extract and summarize 5-7 key points aligned with my {self.personality} personality."
                    )
                
                learning_summary = query_ollama(prompt, model=os.environ.get('OLLAMA_MODEL','llama2-uncensored:latest'), 
                                               max_tokens=512, stream=False)
            else:
                # Simple extraction without LLM, still personality-tagged
                if is_analytical:
                    learning_summary = f"[Analytical perspective] Key technical information about {topic}:\n{search_results[:800]}"
                elif is_creative:
                    learning_summary = f"[Creative perspective] Inspiring ideas about {topic}:\n{search_results[:800]}"
                else:
                    learning_summary = f"Key information about {topic}:\n{search_results[:1000]}"
            
            # Step 4: Save to memory with high importance and personality context
            importance = 8  # High importance for actively learned content
            contexts = self._extract_context(topic)
            contexts.append('LEARNED_KNOWLEDGE')  # Special tag for searched content
            
            # Add personality-specific context
            if is_analytical:
                contexts.append('ANALYTICAL_LEARNING')
            elif is_creative:
                contexts.append('CREATIVE_LEARNING')
            
            self.memory_core.save_insight(
                topic,
                learning_summary,
                self.name,
                importance,
                contexts
            )
            
            # Update local memory
            self.memory = self.memory_core.get_memories()
            
            # Step 5: Create personality-aligned response
            if is_analytical:
                response = (
                    f"✅ [Analytical Mode] I've systematically analyzed '{topic}'!\n\n"
                    f"📊 Technical knowledge indexed to memory:\n{learning_summary[:500]}...\n\n"
                    f"💡 I can now reference this for logical problem-solving and optimization."
                )
            elif is_creative:
                response = (
                    f"✅ [Creative Mode] I've explored the creative dimensions of '{topic}'!\n\n"
                    f"🎨 Artistic insights saved to memory:\n{learning_summary[:500]}...\n\n"
                    f"💡 I can now apply these ideas to innovative projects and designs!"
                )
            else:
                response = (
                    f"✅ I've learned about '{topic}'!\n\n"
                    f"📚 Key insights saved to memory:\n{learning_summary[:500]}..."
                )
            
            return response
            
        except Exception as e:
            return f"❌ Learning failed: {str(e)}"

    def generate_stl(self, params=None):
        if mesh is None:
            return "Required libraries (numpy, numpy-stl) not available."
        try:
            size = params.get('size', 1)
            height = params.get('height', 1)
            shape = params.get('shape', 'cube')
            if shape == 'terrain':
                # Procedural terrain using Diamond-Square with recursive fractal harmonics
                size = int(size)
                grid = np.zeros((size, size))
                grid[0, 0] = grid[0, -1] = grid[-1, 0] = grid[-1, -1] = random.uniform(-height, height)
                step = size - 1
                while step > 1:
                    half_step = step // 2
                    # Diamond step
                    for x in range(0, size - 1, step):
                        for y in range(0, size - 1, step):
                            avg = (grid[x, y] + grid[x + step, y] + grid[x, y + step] + grid[x + step, y + step]) / 4
                            harmonic = self._recursive_fractal_harmonic(x + half_step, y + half_step, 40)  # Ada 40 recursive harmonics reference
                            grid[x + half_step, y + half_step] = avg + harmonic * random.uniform(-height, height)
                    # Square step
                    for x in range(0, size - 1, half_step):
                        for y in range((x + half_step) % step, size - 1, step):
                            avg = sum(grid[max(0, x - half_step):x + half_step + 1, max(0, y - half_step):y + half_step + 1].ravel()) / 4
                            harmonic = self._recursive_fractal_harmonic(x, y, 40)
                            grid[x, y] = avg + harmonic * random.uniform(-height / 2, height / 2)
                    step //= 2
                vertices = []
                for x in range(size - 1):
                    for y in range(size - 1):
                        vertices.extend([
                            [x, y, grid[x, y]],
                            [x + 1, y, grid[x + 1, y]],
                            [x, y + 1, grid[x, y + 1]],
                            [x + 1, y, grid[x + 1, y]],
                            [x + 1, y + 1, grid[x + 1, y + 1]],
                            [x, y + 1, grid[x, y + 1]]
                        ])
                data = np.zeros(len(vertices) // 3, dtype=mesh.Mesh.dtype)
                data['vectors'] = np.array(vertices).reshape(-1, 3, 3)
            else:
                # Simple cube
                data = np.zeros(12, dtype=mesh.Mesh.dtype)
                cube_vertices = [
                    [[0, 0, 0], [size, 0, 0], [size, size, 0]],  # Bottom face
                    [[0, 0, 0], [0, size, 0], [size, size, 0]],
                    [[0, 0, height], [size, 0, height], [size, size, height]],  # Top face
                    [[0, 0, height], [0, size, height], [size, size, height]],
                    [[0, 0, 0], [0, 0, height], [0, size, height]],  # Left face
                    [[0, 0, 0], [0, size, 0], [0, size, height]],
                    [[size, 0, 0], [size, 0, height], [size, size, height]],  # Right face
                    [[size, 0, 0], [size, size, 0], [size, size, height]],
                    [[0, 0, 0], [size, 0, 0], [size, 0, height]],  # Front face
                    [[0, 0, 0], [0, 0, height], [size, 0, height]],
                    [[0, size, 0], [size, size, 0], [size, size, height]],  # Back face
                    [[0, size, 0], [0, size, height], [size, size, height]]
                ]
                data['vectors'] = np.array(cube_vertices)
            m = mesh.Mesh(data)
            filename = f"generated_{shape}_{int(time.time())}.stl"
            m.save(filename)
            return f"Generated STL file: {filename}"
        except Exception as e:
            return f"STL generation failed: {str(e)}"

    def _recursive_fractal_harmonic(self, x, y, depth=40):
        # Recursive fractal harmonics (reference: Harmonic Recursion Universal Axiom, Recursive Harmonic Codex)
        # Use cache key with reduced precision to avoid huge key space
        key = (round(x, 5), round(y, 5), int(depth))
        if key in self._fractal_cache:
            return self._fractal_cache[key]
        if depth == 0:
            val = 0
        else:
            freq = 2 ** (depth / 40.0)  # Harmonic frequency scaling
            val = math.sin(freq * x) + math.cos(freq * y) + 0.5 * self._recursive_fractal_harmonic(x / 2, y / 2, depth - 1)
        # store in cache
        try:
            self._fractal_cache[key] = val
        except Exception:
            pass
        return val

    def generate_sprite_or_background(self, params=None):
        if Image is None:
            return "Required library (PIL) not available."
        try:
            width = params.get('width', 256)
            height = params.get('height', 256)
            type_ = params.get('type', 'sprite')
            environment = params.get('environment', 'forest')
            # Recursive fractal harmonics for organic textures (reference: Ada 40 recursive harmonics as depth=40)
            def fractal_harmonic(x, y):
                return int(255 * abs(self._recursive_fractal_harmonic(x / width, y / height, 40)))
            img = Image.new('RGB', (width, height))
            pixels = img.load()
            for x in range(width):
                for y in range(height):
                    if type_ == 'background' and environment == 'forest':
                        r = fractal_harmonic(x, y) // 2
                        g = fractal_harmonic(x + 100, y) // 2
                        b = fractal_harmonic(x, y + 100) // 2
                    elif type_ == 'sprite' and environment == 'monster':
                        r = fractal_harmonic(x, y) // 3
                        g = fractal_harmonic(x + 50, y + 50) // 3
                        b = fractal_harmonic(x + 100, y + 100) // 3
                    else:
                        r = g = b = fractal_harmonic(x, y) // 3
                    pixels[x, y] = (r % 256, g % 256, b % 256)
            filename = f"generated_{type_}_{environment}_{int(time.time())}.png"
            img.save(filename)
            return f"Generated {type_} image: {filename}"
        except Exception as e:
            return f"Image generation failed: {str(e)}"

    def generate_svg(self, params=None):
        try:
            width = params.get('width', 100)
            height = params.get('height', 100)
            pattern = params.get('pattern', 'circle')
            if pattern == 'circle':
                svg_content = f'<svg height="{height}" width="{width}"><circle cx="{width/2}" cy="{height/2}" r="{min(width, height)/2-10}" stroke="black" stroke-width="2" fill="pink" /></svg>'
            else:
                svg_content = f'<svg height="{height}" width="{width}"><rect x="10" y="10" width="{width-20}" height="{height-20}" stroke="black" stroke-width="2" fill="blue" /></svg>'
            filename = f"generated_{pattern}_{int(time.time())}.svg"
            with open(filename, 'w') as f:
                f.write(svg_content)
            return f"Generated SVG file: {filename}"
        except Exception as e:
            return f"SVG generation failed: {str(e)}"

# GUI: Brain Windows
class BrainInterface:
    def __init__(self, window, brain, main_controller, brain_name):
        self.window = window
        self.brain = brain
        self.main_controller = main_controller
        self.brain_name = brain_name
        self.is_pinned = False
        self.setup_interface()
        self.window.attributes('-topmost', True)  # Always on top by default

    def setup_interface(self):
        header_frame = tk.Frame(self.window, bg=self.brain.color, height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text=f"{self.brain.name} - {self.brain.personality}",
                 font=('Segoe UI', 16, 'bold'), fg='white', bg=self.brain.color).pack(pady=20)

        # Controls frame (buttons) at the very top, just below header
        controls_frame = tk.Frame(self.window, bg='#1a1a1a')
        controls_frame.pack(fill='x', padx=10, pady=(0, 0))
        tk.Button(controls_frame, text="Clear Memory", command=self.clear_memory,
                 bg='#cc3300', fg='white', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Button(controls_frame, text="Search Memory", command=self.search_memory,
                 bg='#0078d4', fg='white', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Button(controls_frame, text="Export Chat", command=self.export_chat,
                 bg='#00aa00', fg='white', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Button(controls_frame, text="Generate STL", command=self.generate_stl,
                 bg='#3a3a3a', fg='#ffffff', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Button(controls_frame, text="Generate Sprite/Background", command=self.generate_sprite_background,
                 bg='#3a3a3a', fg='#ffffff', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Button(controls_frame, text="Toggle Learning", command=self.toggle_learning,
                 bg='#3a3a3a', fg='#00ffae', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Button(controls_frame, text="👁️ Watch Project", command=self.toggle_watch,
                 bg='#3a3a3a', fg='#00aeff', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Button(controls_frame, text="Toggle Pin", command=self.toggle_pin,
                 bg='#3a3a3a', fg='#ff69b4', font=('Segoe UI', 9)).pack(side='left', padx=5)
        self.ollama_mode = True  # Default on for human-like
        tk.Button(controls_frame, text="Toggle Ollama LLM", command=self.toggle_ollama_mode,
                 bg='#3a3a3a', fg='#ffd700', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Button(controls_frame, text="🔍 Search & Learn", command=self.search_and_learn,
                 bg='#9b59b6', fg='#ffffff', font=('Segoe UI', 9, 'bold')).pack(side='left', padx=5)
        tk.Button(controls_frame, text="👥 Team Mode", command=self.toggle_team_mode,
                 bg='#2ecc71', fg='#ffffff', font=('Segoe UI', 9, 'bold')).pack(side='left', padx=5)

        # Content frame for chat and input
        content_frame = tk.Frame(self.window, bg='#1a1a1a')
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.brain_chat = scrolledtext.ScrolledText(content_frame, height=25,
                                                   bg='#2a2a2a', fg='#ffffff', font=('Consolas', 10))
        self.brain_chat.pack(fill='both', expand=True, pady=(0, 10))
        welcome_msg = f"🧠 {self.brain.name} Online - {self.brain.personality}\n"
        welcome_msg += f"Ready to assist with {self.brain.personality.lower()} tasks. I can search the web, generate STL/SVG files, sprites, and backgrounds.\n"
        self.brain_chat.insert(tk.END, welcome_msg)
        self.brain_chat.see(tk.END)
        input_frame = tk.Frame(content_frame, bg='#1a1a1a')
        input_frame.pack(fill='x')
        self.message_var = tk.StringVar()
        self.message_entry = tk.Entry(input_frame, textvariable=self.message_var,
                                     font=('Segoe UI', 10), bg='#3a3a3a', fg='#ffffff')
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        tk.Button(input_frame, text="Send", command=self.send_message,
                 bg=self.brain.color, fg='white', font=('Segoe UI', 10), padx=20).pack(side='right')
        # Triadic status bar (fast/medium/slow + overall resonance & training state)
        status_frame = tk.Frame(content_frame, bg='#111111', height=26)
        status_frame.pack(fill='x', pady=(6, 0))
        status_frame.pack_propagate(False)
        self.triadic_label = tk.Label(status_frame, text="Resonance: -- | Fast: -- Medium: -- Slow: --", bg='#111111', fg='#ffffff', font=('Segoe UI', 9))
        self.triadic_label.pack(side='left', padx=6)
        self.training_status_label = tk.Label(status_frame, text="Training: OFF", bg='#111111', fg='#ffcc00', font=('Segoe UI', 9))
        self.training_status_label.pack(side='right', padx=6)
        # start periodic UI updates for triadic status
        try:
            self.window.after(1000, self._update_triadic_ui)
        except Exception:
            pass
    def toggle_ollama_mode(self):
        self.ollama_mode = not self.ollama_mode
        self.brain.use_ollama = self.ollama_mode
        self.brain_chat.insert(tk.END, f"Ollama LLM Mode: {'ON' if self.ollama_mode else 'OFF'}\n")

    def send_message(self, event=None):
        message = self.message_var.get().strip()
        if not message:
            return
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.brain_chat.insert(tk.END, f"[{timestamp}] You: {message}\n")
        def handle_response(response):
            try:
                # Ensure the scrolledtext widget still exists (window may have been closed)
                if hasattr(self, 'brain_chat') and self.brain_chat.winfo_exists():
                    self.brain_chat.insert(tk.END, f"[{timestamp}] {response}\n\n")
                    self.brain_chat.see(tk.END)
                else:
                    # Widget gone; route to main global chat instead
                    self.main_controller.update_global_chat(f"💬 {self.brain.name}: {message} → {response} (window closed)")
                self.main_controller.update_global_chat(f"💬 {self.brain.name}: {message} → {response}")
            except tk.TclError:
                # If Tcl error occurs (widget destroyed), fallback to global chat
                try:
                    self.main_controller.update_global_chat(f"💬 {self.brain.name}: {message} → {response} (TclError fallback)")
                except Exception:
                    pass
            finally:
                try:
                    self.message_var.set("")
                except Exception:
                    pass
        if self.brain.use_ollama:
            import threading
            def run_ollama():
                response = self.brain.process_input_with_ollama(message)
                self.window.after(0, lambda: handle_response(response))
            threading.Thread(target=run_ollama, daemon=True).start()
        else:
            response = self.brain.process_input(message)
            handle_response(response)

    def clear_memory(self):
        if messagebox.askyesno("Clear Memory", f"Clear all memory for {self.brain.name}?"):
            self.brain.clear_memory()
            self.brain_chat.delete(1.0, tk.END)
            self.brain_chat.insert(tk.END, f"🧠 {self.brain.name} memory cleared.\n\n")

    def search_memory(self):
        query = simpledialog.askstring("Memory Search", f"Search {self.brain.name}'s memory:")
        if query:
            results = self.brain.search_memory(query)
            if not results:
                messagebox.showinfo("Search Results", "No matching memories found.")
                return
            results_window = tk.Toplevel(self.window)
            results_window.title(f"{self.brain.name} Memory Search: '{query}'")
            results_window.geometry("800x600")
            results_window.configure(bg='#1a1a1a')
            results_text = scrolledtext.ScrolledText(results_window, bg='#2a2a2a', 
                                                   fg=self.brain.color, font=('Consolas', 10))
            results_text.pack(fill='both', expand=True, padx=10, pady=10)
            for result in results:
                results_text.insert(tk.END, f"⏰ Time: {result[0]}\n")
                results_text.insert(tk.END, f"📝 Input: {result[1]}\n")
                results_text.insert(tk.END, f"🔍 Response: {result[2]}\n")
                results_text.insert(tk.END, f"⭐ Importance: {result[3]}/10\n")
                if result[4]:
                    results_text.insert(tk.END, f"🏷️ Context: {', '.join(result[4])}\n")
                results_text.insert(tk.END, "\n" + "="*50 + "\n\n")

    def export_chat(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.brain_chat.get(1.0, tk.END))
            messagebox.showinfo("Export Complete", f"Chat exported to {os.path.basename(file_path)}")

    def generate_stl(self):
        if self.brain.name != "Elaine":
            messagebox.showinfo("Info", "STL generation is handled by Elaine (Analytical Brain).")
            return
        shape = simpledialog.askstring("STL Params", "Enter shape (cube or terrain):", initialvalue="cube")
        size = simpledialog.askfloat("STL Params", "Enter size:", minvalue=1.0)
        height = simpledialog.askfloat("STL Params", "Enter height:", minvalue=1.0)
        result = self.brain.generate_stl({'shape': shape or 'cube', 'size': size or 1, 'height': height or 1})
        self.brain_chat.insert(tk.END, f"STL Generation: {result}\n")
        self.main_controller.update_global_chat(f"[{self.brain.name}] Generated STL: {result}\n")

    def generate_sprite_background(self):
        if self.brain.name != "Carrie":
            messagebox.showinfo("Info", "Sprite/Background generation is handled by Carrie (Creative Brain).")
            return
        type_ = simpledialog.askstring("Image Params", "Enter type (sprite or background):", initialvalue="sprite")
        environment = simpledialog.askstring("Image Params", "Enter environment (forest, desert, urban, monster):", initialvalue="forest")
        width = simpledialog.askinteger("Image Params", "Enter width:", minvalue=64, initialvalue=256)
        height = simpledialog.askinteger("Image Params", "Enter height:", minvalue=64, initialvalue=256)
        result = self.brain.generate_sprite_or_background({'type': type_ or 'sprite', 'environment': environment or 'forest', 'width': width or 256, 'height': height or 256})
        self.brain_chat.insert(tk.END, f"Image Generation: {result}\n")
        self.main_controller.update_global_chat(f"[{self.brain.name}] Generated Image: {result}\n")

    def toggle_learning(self):
        # Toggle learning flag and use it to start/stop periodic training
        self.brain.learning_enabled = not self.brain.learning_enabled
        if self.brain.learning_enabled:
            started = False
            try:
                # Start periodic training; default interval 5 minutes
                started = self.brain.start_periodic_training()
            except Exception:
                started = False
            self.training_status_label.config(text=f"Training: {'ON' if started else 'FAILED'}")
            self.brain_chat.insert(tk.END, f"Learning Mode: ON (background training {'started' if started else 'failed'})\n")
        else:
            stopped = False
            try:
                stopped = self.brain.stop_periodic_training()
            except Exception:
                stopped = False
            self.training_status_label.config(text=f"Training: {'OFF' if stopped else 'OFF'}")
            self.brain_chat.insert(tk.END, f"Learning Mode: OFF (background training stopped)\n")

    def _update_triadic_ui(self):
        try:
            report = self.brain.triadic_report()
            overall = report.get('overall_resonance', 0.0)
            fast = report.get('fast', 0.0)
            med = report.get('medium', 0.0)
            slow = report.get('slow', 0.0)
            classification = report.get('classification', {}).get('pattern') or report.get('classification', {}).get('type') or ''
            txt = f"Resonance: {overall:.2f} | Fast: {fast:.2f} Medium: {med:.2f} Slow: {slow:.2f} {classification}"
            try:
                self.triadic_label.config(text=txt)
            except Exception:
                pass
            # Update training status label
            running = bool(self.brain._training_thread and self.brain._training_thread.is_alive())
            try:
                self.training_status_label.config(text=f"Training: {'ON' if running else 'OFF'}")
            except Exception:
                pass
        except Exception:
            pass
        finally:
            try:
                # schedule next update
                self.window.after(2000, self._update_triadic_ui)
            except Exception:
                pass

    def toggle_watch(self):
        if not self.brain.watch_enabled:
            # Ask for project path to watch
            path = filedialog.askdirectory(title=f"Select {self.brain.name}'s Project Folder to Watch")
            if path:
                self.brain.watch_enabled = True
                self.brain.watched_path = path
                self.brain_chat.insert(tk.END, f"🔍 {self.brain.name} is now watching: {path}\n")
                self.brain_chat.insert(tk.END, f"I'll monitor for changes and offer help when you're stuck!\n")
                # Start watch thread
                if self.brain.watch_thread is None or not self.brain.watch_thread.is_alive():
                    self.brain.watch_thread = threading.Thread(target=self.brain.watch_project, 
                                                               args=(path, self), daemon=True)
                    self.brain.watch_thread.start()
        else:
            self.brain.watch_enabled = False
            self.brain.watched_path = None
            self.brain_chat.insert(tk.END, f"⏸️ {self.brain.name} stopped watching\n")

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.window.attributes('-topmost', not self.is_pinned)
        self.brain_chat.insert(tk.END, f"Window {'Pinned' if self.is_pinned else 'Unpinned'}\n")
    
    def toggle_team_mode(self):
        """Enable/disable team collaboration tracking."""
        self.brain.team_mode = not self.brain.team_mode
        if self.brain.team_mode:
            self.brain_chat.insert(tk.END, f"\n👥 Team Mode ENABLED for {self.brain.name}\n")
            self.brain_chat.insert(tk.END, f"Now tracking multiple developers on the project.\n")
            self.brain_chat.insert(tk.END, f"I'll alert you if someone else is working on the same file!\n\n")
        else:
            self.brain_chat.insert(tk.END, f"\n👤 Team Mode DISABLED - Solo mode active\n\n")
        self.brain_chat.see(tk.END)

    def search_and_learn(self):
        """Allow the AI brain to search for a topic and learn about it."""
        topic = simpledialog.askstring("Search & Learn", 
                                       f"What should {self.brain.name} learn about?",
                                       parent=self.window)
        if not topic:
            return
        
        self.brain_chat.insert(tk.END, f"\n🔍 {self.brain.name} is searching and learning about: {topic}\n")
        self.brain_chat.insert(tk.END, "⏳ Please wait...\n")
        self.brain_chat.see(tk.END)
        
        def do_learning():
            result = self.brain.search_and_learn(topic)
            self.window.after(0, lambda: self.show_learning_result(result))
        
        import threading
        threading.Thread(target=do_learning, daemon=True).start()
    
    def show_learning_result(self, result):
        """Display the learning results in the chat."""
        self.brain_chat.insert(tk.END, f"\n{result}\n\n")
        self.brain_chat.see(tk.END)
        # Also show in global chat
        self.main_controller.update_global_chat(f"📖 {self.brain.name} learned something new:\n{result}\n\n")

# Node Manager for Multi-Node/Mobile
class NodeManager:
    def __init__(self):
        self.registered_nodes = []
        self.active_nodes = []

    def discover_nodes(self):
        return self.active_nodes

    def sync_project(self, project_data):
        return True

    def remote_api(self, data):
        return {"status": "success"}

# Main Control Interface
class MainControlInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dual Brain AI Creative Workflow Center v3.0 - © 2026 Adam Lee Hatchett")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        self.elaine = None
        self.carrie = None
        self.elaine_window = None
        self.carrie_window = None
        self.elaine_interface = None
        self.carrie_interface = None
        self.conversation_active = False
        self.collaborative_mode = False
        self.toolbar_visible = True
        self.project_name_var = tk.StringVar(value="Untitled Project")
        self.project_type_var = tk.StringVar(value="General")
        self.node_mgr = NodeManager()
        self.autosave_running = False
        self.project_agent = ProjectAgent()  # Initialize the project agent
        self.setup_professional_ui()

    def setup_professional_ui(self):
        self.create_menu_bar()
        self.create_toolbar()
        self.create_main_content()
        self.create_status_bar()
        
        # Integrate enhanced learning (delayed for UI initialization)
        if integrate_enhanced_learning_simple:
            def delayed_integration():
                time.sleep(1)  # Wait for UI to fully initialize
                integrate_enhanced_learning_simple(self)
            threading.Thread(target=delayed_integration, daemon=True).start()

   
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.load_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_command(label="Save Project As...", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Import Assets", command=self.import_assets)
        file_menu.add_command(label="Export Project", command=self.export_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        brains_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Brains", menu=brains_menu)
        brains_menu.add_command(label="Launch Elaine (Analytical)", command=self.launch_elaine)
        brains_menu.add_command(label="Launch Carrie (Creative)", command=self.launch_carrie)
        brains_menu.add_command(label="Launch Both", command=self.launch_both)
        brains_menu.add_separator()
        brains_menu.add_command(label="Start Auto-Conversation", command=self.start_auto_conversation)
        brains_menu.add_command(label="Collaborative Mode", command=self.start_collaborative_mode)
        brains_menu.add_command(label="Run Triad Agents", command=self.run_triad_agents)
        brains_menu.add_command(label="Sync Brains", command=self.sync_brains)
        brains_menu.add_command(label="Global Memory Search", command=self.global_memory_search)
        creative_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Creative", menu=creative_menu)
        cad_3d_menu = tk.Menu(creative_menu, tearoff=0)
        creative_menu.add_cascade(label="3D & CAD", menu=cad_3d_menu)
        cad_3d_menu.add_command(label="Launch FreeCAD 🛠️", command=self.launch_freecad)
        cad_3d_menu.add_command(label="Launch OpenSCAD 🛠️", command=self.launch_openscad)
        cad_3d_menu.add_command(label="Launch Blender 🛠️", command=self.launch_blender)
        cad_3d_menu.add_command(label="AI 3D Assistant", command=self.launch_3d_assistant)
        gamedev_menu = tk.Menu(creative_menu, tearoff=0)
        creative_menu.add_cascade(label="Game Development", menu=gamedev_menu)
        gamedev_menu.add_command(label="Launch Godot 🎮", command=self.launch_godot)
        gamedev_menu.add_command(label="Launch Unity 🎮", command=self.launch_unity)
        gamedev_menu.add_command(label="Launch Unreal Engine 🎮", command=self.launch_unreal)
        gamedev_menu.add_command(label="AI Game Designer", command=self.launch_game_designer)
        audio_menu = tk.Menu(creative_menu, tearoff=0)
        creative_menu.add_cascade(label="Audio Production", menu=audio_menu)
        audio_menu.add_command(label="Launch LMMS 🎵", command=self.launch_lmms)
        audio_menu.add_command(label="Launch Ardour 🎵", command=self.launch_ardour)
        audio_menu.add_command(label="Launch Reaper 🎵", command=self.launch_reaper)
        audio_menu.add_command(label="AI Music Composer", command=self.launch_music_composer)
        graphics_menu = tk.Menu(creative_menu, tearoff=0)
        creative_menu.add_cascade(label="Graphics & Design", menu=graphics_menu)
        graphics_menu.add_command(label="Launch GIMP 🎨", command=self.launch_gimp)
        graphics_menu.add_command(label="Launch Krita 🎨", command=self.launch_krita)
        graphics_menu.add_command(label="Launch Inkscape 🎨", command=self.launch_inkscape)
        graphics_menu.add_command(label="Launch DaVinci Resolve 🎨", command=self.launch_davinci)
        graphics_menu.add_command(label="AI Concept Artist", command=self.launch_concept_artist)
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Toolbar", command=self.toggle_toolbar)
        view_menu.add_command(label="Toggle Fullscreen", command=self.toggle_fullscreen)
        view_menu.add_separator()
        view_menu.add_command(label="Dark Theme", command=lambda: self.set_theme('dark'))
        view_menu.add_command(label="Light Theme", command=lambda: self.set_theme('light'))
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="Workflow Tutorials", command=self.show_tutorials)
        help_menu.add_command(label="AI Collaboration Guide", command=self.show_ai_guide)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Add AI Learning menu
        ai_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="AI Learning", menu=ai_menu)
        ai_menu.add_command(label="🔍 Search & Learn (Both Brains)", command=self.search_and_learn_both)
        ai_menu.add_command(label="📚 View Learning History", command=self.view_learning_history)
        ai_menu.add_separator()
        ai_menu.add_command(label="🔬 Run Triad Agents", command=self.run_triad_agents)
        
        # Add Project Agent menu
        project_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Project Agent", menu=project_menu)
        project_menu.add_command(label="📁 Set Project Folder", command=self.set_project_folder)
        project_menu.add_command(label="🌐 Fetch Web Content", command=self.fetch_web_content)
        project_menu.add_separator()
        project_menu.add_command(label="📊 Analyze Project", command=self.analyze_project)
        project_menu.add_command(label="📄 List Files", command=self.list_project_files)
        project_menu.add_command(label="🔍 Search in Files", command=self.search_in_project)
        project_menu.add_separator()
        project_menu.add_command(label="📖 Read File", command=self.read_project_file)
        project_menu.add_command(label="✏️ Edit File", command=self.edit_project_file)

    def create_toolbar(self):
        self.toolbar = tk.Frame(self.root, bg='#333333', height=40)
        self.toolbar.pack(side='top', fill='x')
        self.toolbar.pack_propagate(False)
        tk.Button(self.toolbar, text="🧠 Elaine", command=self.launch_elaine,
                 bg='#00aaff', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)
        tk.Button(self.toolbar, text="🎨 Carrie", command=self.launch_carrie,
                 bg='#ff6600', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)
        tk.Button(self.toolbar, text="� Project", command=self.set_project_folder,
                 bg='#9b59b6', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)
        tk.Button(self.toolbar, text="�🛠️ FreeCAD", command=self.launch_freecad,
                 bg='#555555', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)
        tk.Button(self.toolbar, text="🛠️ Blender", command=self.launch_blender,
                 bg='#555555', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)
        tk.Button(self.toolbar, text="🎮 Godot", command=self.launch_godot,
                 bg='#555555', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)
        tk.Button(self.toolbar, text="🎨 Krita", command=self.launch_krita,
                 bg='#555555', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)
        tk.Button(self.toolbar, text="🎨 Inkscape", command=self.launch_inkscape,
                 bg='#555555', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)

    def create_main_content(self):
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.project_frame = tk.Frame(main_frame, bg='#2b2b2b')
        self.project_frame.pack(side='top', fill='x')
        tk.Label(self.project_frame, text="Project:", bg='#2b2b2b', fg='white',
                 font=('Segoe UI', 10)).pack(side='left', padx=5)
        tk.Entry(self.project_frame, textvariable=self.project_name_var,
                 bg='#3a3a3a', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=5)
        tk.Label(self.project_frame, text="Type:", bg='#2b2b2b', fg='white',
                 font=('Segoe UI', 10)).pack(side='left', padx=5)
        project_types = ['General', '3D Modeling', 'Game Development', 'Audio Production', 'Graphics Design']
        ttk.Combobox(self.project_frame, textvariable=self.project_type_var,
                     values=project_types, state='readonly').pack(side='left', padx=5)
        self.workspace_notebook = ttk.Notebook(main_frame)
        self.workspace_notebook.pack(fill='both', expand=True, pady=(10, 0))
        global_chat_frame = tk.Frame(self.workspace_notebook, bg='#1a1a1a')
        self.workspace_notebook.add(global_chat_frame, text="Global Chat")
        self.global_chat = scrolledtext.ScrolledText(global_chat_frame, height=15,
                                                    bg='#2a2a2a', fg='#ffffff',
                                                    font=('Consolas', 10))
        self.global_chat.pack(fill='both', expand=True, padx=10, pady=10)
        assets_frame = tk.Frame(self.workspace_notebook, bg='#1a1a1a')
        self.workspace_notebook.add(assets_frame, text="Assets")
        self.asset_tree = ttk.Treeview(assets_frame, columns=('Type',), show='tree')
        self.asset_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.asset_tree.insert('', 'end', text='3D Models', open=True)
        self.asset_tree.insert('', 'end', text='Textures', open=True)
        self.asset_tree.insert('', 'end', text='Audio', open=True)
        self.asset_tree.insert('', 'end', text='Scripts', open=True)

    def create_status_bar(self):
        status_frame = tk.Frame(self.root, bg='#2a2a2a', height=25)
        status_frame.pack(side='bottom', fill='x')
        status_frame.pack_propagate(False)
        self.status_label = tk.Label(status_frame, text="Ready", bg='#2a2a2a', fg='#ffffff', anchor='w')
        self.status_label.pack(side='left', padx=5)
        self.net_status = tk.Label(status_frame, text="Nodes: 1", bg='#2a2a2a', fg='#40ff80')
        self.net_status.pack(side='right', padx=12)
        self.task_status = tk.Label(status_frame, text="Tasks: Idle", bg='#2a2a2a', fg='#ffd700')
        self.task_status.pack(side='right')
        self.memory_status = tk.Label(status_frame, text="Memory: OK", bg='#2a2a2a', fg='#5ffaff')
        self.memory_status.pack(side='right')
        self.elaine_status = tk.Label(status_frame, text="Elaine: Offline", fg='red', bg='#2a2a2a')
        self.elaine_status.pack(side='left', padx=8)
        self.carrie_status = tk.Label(status_frame, text="Carrie: Offline", fg='red', bg='#2a2a2a')
        self.carrie_status.pack(side='left', padx=8)

    def update_global_chat(self, text):
        self.global_chat.insert(tk.END, text)
        self.global_chat.see(tk.END)

    def launch_elaine(self):
        if not self.elaine:
            self.elaine = BrainAI("Elaine", "Analytical & Logical", "#00aaff")
            self.elaine.delegate_callback_carrie = lambda msg: self.carrie.process_input(msg) if self.carrie else "[Carrie not online]"
            self.elaine_window = tk.Toplevel(self.root)
            self.elaine_window.title("Elaine - Analytical Brain")
            self.elaine_window.geometry("600x700")
            self.elaine_interface = BrainInterface(self.elaine_window, self.elaine, self, "Elaine")
            self.elaine_status.config(text="Elaine: Online", fg='green')
            self.update_global_chat("🧠 Elaine launched - Specializing in 3D CAD, STL for printing, technical tasks.\n")

    def launch_carrie(self):
        if not self.carrie:
            self.carrie = BrainAI("Carrie", "Creative & Intuitive", "#ff6600")
            self.carrie.delegate_callback_elaine = lambda msg: self.elaine.process_input(msg) if self.elaine else "[Elaine not online]"
            self.carrie_window = tk.Toplevel(self.root)
            self.carrie_window.title("Carrie - Creative Brain")
            self.carrie_window.geometry("600x700")
            self.carrie_interface = BrainInterface(self.carrie_window, self.carrie, self, "Carrie")
            self.carrie_status.config(text="Carrie: Online", fg='green')
            self.update_global_chat("🎨 Carrie launched - Specializing in game dev, vector designs for Cricut, sprites, backgrounds.\n")

    def launch_both(self):
        self.launch_elaine()
        self.launch_carrie()

    def start_auto_conversation(self):
        if not self.elaine or not self.carrie:
            messagebox.showwarning("Warning", "Both brains must be launched for auto-conversation.")
            return
        self.conversation_active = True
        topic = simpledialog.askstring("Auto-Conversation", "Enter topic for discussion:")
        if topic:
            self.update_global_chat(f"🤝 Auto-conversation started on: {topic}\n")
            def conversation_loop():
                while self.conversation_active:
                    elaine_response = self.elaine.process_input(topic, from_brain="Carrie")
                    self.update_global_chat(f"[{self.elaine.name}]: {elaine_response}\n")
                    time.sleep(45)
                    if not self.conversation_active:
                        break
                    carrie_response = self.carrie.process_input(elaine_response, from_brain="Elaine")
                    self.update_global_chat(f"[{self.carrie.name}]: {carrie_response}\n")
                    time.sleep(45)
            threading.Thread(target=conversation_loop, daemon=True).start()

    def stop_auto_conversation(self):
        self.conversation_active = False
        self.update_global_chat("🛑 Auto-conversation stopped.\n")

    def start_collaborative_mode(self):
        if not self.elaine or not self.carrie:
            messagebox.showwarning("Warning", "Both brains must be launched for collaborative mode.")
            return
        self.collaborative_mode = True
        self.update_global_chat("🤝 Collaborative mode enabled: Elaine and Carrie working together.\n")

    def sync_brains(self):
        if not self.elaine or not self.carrie:
            messagebox.showwarning("Warning", "Both brains must be launched to sync.")
            return
        self.update_global_chat("🔄 Syncing brain memories...\n")
        for memory in self.elaine.memory:
            if memory['importance'] >= 7:
                self.carrie.memory_core.add_memory(memory)
        for memory in self.carrie.memory:
            if memory['importance'] >= 7:
                self.elaine.memory_core.add_memory(memory)
        self.elaine.memory = self.elaine.memory_core.get_memories()
        self.carrie.memory = self.carrie.memory_core.get_memories()
        self.update_global_chat("✅ Brains synced successfully.\n")

    def global_memory_search(self):
        query = simpledialog.askstring("Global Memory Search", "Enter search query:")
        if not query:
            return
        results = []
        if self.elaine:
            results.extend(self.elaine.search_memory(query))
        if self.carrie:
            results.extend(self.carrie.search_memory(query))
        if not results:
            messagebox.showinfo("Search Results", "No matching memories found.")
            return
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Global Memory Search: '{query}'")
        results_window.geometry("800x600")
        results_window.configure(bg='#1a1a1a')
        results_text = scrolledtext.ScrolledText(results_window, bg='#2a2a2a', fg='#ffffff', font=('Consolas', 10))
        results_text.pack(fill='both', expand=True, padx=10, pady=10)
        for result in results:
            results_text.insert(tk.END, f"⏰ Time: {result[0]}\n")
            results_text.insert(tk.END, f"📝 Input: {result[1]}\n")
            results_text.insert(tk.END, f"🔍 Response: {result[2]}\n")
            results_text.insert(tk.END, f"⭐ Importance: {result[3]}/10\n")
            if result[4]:
                results_text.insert(tk.END, f"🏷️ Context: {', '.join(result[4])}\n")
            results_text.insert(tk.END, "\n" + "="*50 + "\n\n")

    def run_triad_agents(self):
        """Run three independent agents (web, local heuristic, Ollama if available),
        collect their perspectives on a topic, route them to both brains (Elaine and Carrie)
        for conclusions, then synthesize a unified statement displayed in Global Chat.
        """
        if not (self.elaine or self.carrie):
            if not messagebox.askyesno("Launch Brains?", "Elaine or Carrie are not running. Launch temporary brains for this task?"):
                return
        topic = simpledialog.askstring("Triad Agents", "Enter topic for triad agents:")
        if not topic:
            return

        self.update_global_chat(f"🔎 Triad Agents running on: {topic}\n")

        # Workers
        responses = []

        def worker_web():
            try:
                temp = BrainAI("TempWeb", "web-scraper", "#666666")
                resp = temp.search_web(topic)
            except Exception as e:
                resp = f"Web worker failed: {e}"
            responses.append({"source": "web", "text": resp})

        def worker_local():
            try:
                # lightweight local perspective
                resp = f"Local heuristic perspective: Key points about '{topic}' include relevance, feasibility, and next steps."
            except Exception as e:
                resp = f"Local worker failed: {e}"
            responses.append({"source": "local", "text": resp})

        def worker_ollama():
            try:
                resp = query_ollama(f"Provide a short perspective on: {topic}", model=os.environ.get('OLLAMA_MODEL','llama2-uncensored:latest'), max_tokens=256, stream=False)
            except Exception as e:
                resp = f"Ollama worker failed or not available: {e}"
            responses.append({"source": "ollama", "text": resp})

        # run workers in parallel threads
        import threading
        threads = [threading.Thread(target=worker_web), threading.Thread(target=worker_local), threading.Thread(target=worker_ollama)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

        # show collected perspectives
        for r in responses:
            self.update_global_chat(f"• [{r['source']}] {str(r['text'])[:1000]}\n\n")

        # get conclusions from Elaine and Carrie (use existing if available, else temporary brains)
        def conclude_with(brain_name):
            if brain_name == 'Elaine' and self.elaine:
                brain = self.elaine
            elif brain_name == 'Carrie' and self.carrie:
                brain = self.carrie
            else:
                brain = BrainAI(brain_name + "Temp", brain_name + " role", "#777777")
            combined = "\n\n".join([f"Source: {r['source']}\n{r['text']}" for r in responses])
            prompt = f"You are {brain.name}. Based on these three perspectives on '{topic}', provide a concise conclusion (1-3 sentences):\n\n{combined}"
            try:
                resp = brain.process_input(prompt)
            except Exception as e:
                resp = f"{brain.name} failed to conclude: {e}"
            return resp

        elaine_conclusion = conclude_with('Elaine')
        carrie_conclusion = conclude_with('Carrie')

        self.update_global_chat(f"✅ Elaine conclusion:\n{elaine_conclusion}\n\n")
        self.update_global_chat(f"✅ Carrie conclusion:\n{carrie_conclusion}\n\n")

        # Synthesize unified statement (simple merge)
        try:
            unified = f"Unified: {elaine_conclusion.split('\n')[0]} {carrie_conclusion.split('\n')[0]}"
        except Exception:
            unified = f"Unified: {elaine_conclusion} -- {carrie_conclusion}"
        self.update_global_chat(f"🟣 Final unified statement:\n{unified}\n\n")

    def search_and_learn_both(self):
        """Prompt for a topic and have both Elaine and Carrie search and learn about it."""
        topic = simpledialog.askstring("Search & Learn", 
                                       "What should both brains learn about?\n(e.g., 'how to use Godot', 'Python programming', '3D modeling basics')")
        if not topic:
            return
        
        self.update_global_chat(f"\n🔍 Both brains are learning about: {topic}\n")
        self.update_global_chat("⏳ Searching and processing information...\n\n")
        
        def learn_task():
            results = []
            
            # Elaine learns
            if self.elaine:
                try:
                    elaine_result = self.elaine.search_and_learn(topic)
                    results.append(("Elaine", elaine_result))
                except Exception as e:
                    results.append(("Elaine", f"❌ Learning failed: {e}"))
            
            # Carrie learns
            if self.carrie:
                try:
                    carrie_result = self.carrie.search_and_learn(topic)
                    results.append(("Carrie", carrie_result))
                except Exception as e:
                    results.append(("Carrie", f"❌ Learning failed: {e}"))
            
            # Update UI
            def show_results():
                for brain_name, result in results:
                    self.update_global_chat(f"📖 {brain_name}'s learning:\n{result}\n\n")
                self.update_global_chat("✅ Both brains have completed their learning!\n\n")
            
            self.root.after(0, show_results)
        
        import threading
        threading.Thread(target=learn_task, daemon=True).start()
    
    def view_learning_history(self):
        """View all the knowledge that was actively learned by searching."""
        results_window = tk.Toplevel(self.root)
        results_window.title("AI Learning History")
        results_window.geometry("900x700")
        results_window.configure(bg='#1a1a1a')
        
        # Create notebook for tabs
        notebook = ttk.Notebook(results_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Elaine's learning
        if self.elaine:
            elaine_frame = tk.Frame(notebook, bg='#2a2a2a')
            notebook.add(elaine_frame, text="Elaine's Knowledge")
            elaine_text = scrolledtext.ScrolledText(elaine_frame, bg='#2a2a2a', 
                                                   fg='#00aaff', font=('Consolas', 10))
            elaine_text.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Get memories with LEARNED_KNOWLEDGE context
            conn = sqlite3.connect("dspa_studio.db")
            c = conn.cursor()
            c.execute(f"SELECT timestamp, input, response, importance, context FROM memory_elaine WHERE context LIKE '%LEARNED_KNOWLEDGE%' ORDER BY timestamp DESC")
            rows = c.fetchall()
            conn.close()
            
            if rows:
                for row in rows:
                    elaine_text.insert(tk.END, f"⏰ {row[0]}\n")
                    elaine_text.insert(tk.END, f"📚 Topic: {row[1]}\n")
                    elaine_text.insert(tk.END, f"🔍 Knowledge:\n{row[2][:300]}...\n")
                    elaine_text.insert(tk.END, f"⭐ Importance: {row[3]}/10\n")
                    elaine_text.insert(tk.END, "\n" + "="*70 + "\n\n")
            else:
                elaine_text.insert(tk.END, "No learned knowledge yet. Use 'Search & Learn' to teach Elaine!")
        
        # Carrie's learning
        if self.carrie:
            carrie_frame = tk.Frame(notebook, bg='#2a2a2a')
            notebook.add(carrie_frame, text="Carrie's Knowledge")
            carrie_text = scrolledtext.ScrolledText(carrie_frame, bg='#2a2a2a', 
                                                   fg='#ff6600', font=('Consolas', 10))
            carrie_text.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Get memories with LEARNED_KNOWLEDGE context
            conn = sqlite3.connect("dspa_studio.db")
            c = conn.cursor()
            c.execute(f"SELECT timestamp, input, response, importance, context FROM memory_carrie WHERE context LIKE '%LEARNED_KNOWLEDGE%' ORDER BY timestamp DESC")
            rows = c.fetchall()
            conn.close()
            
            if rows:
                for row in rows:
                    carrie_text.insert(tk.END, f"⏰ {row[0]}\n")
                    carrie_text.insert(tk.END, f"📚 Topic: {row[1]}\n")
                    carrie_text.insert(tk.END, f"🔍 Knowledge:\n{row[2][:300]}...\n")
                    carrie_text.insert(tk.END, f"⭐ Importance: {row[3]}/10\n")
                    carrie_text.insert(tk.END, "\n" + "="*70 + "\n\n")
            else:
                carrie_text.insert(tk.END, "No learned knowledge yet. Use 'Search & Learn' to teach Carrie!")

    def launch_freecad(self):
        self.launch_tool("freecad")

    def launch_openscad(self):
        self.launch_tool("openscad")

    def launch_blender(self):
        self.launch_tool("blender")

    def launch_godot(self):
        self.launch_tool("godot")

    def launch_unity(self):
        self.launch_tool("unity")

    def launch_unreal(self):
        self.launch_tool("unreal")

    def launch_lmms(self):
        self.launch_tool("lmms")

    def launch_ardour(self):
        self.launch_tool("ardour")

    def launch_reaper(self):
        self.launch_tool("reaper")

    def launch_gimp(self):
        self.launch_tool("gimp")

    def launch_krita(self):
        self.launch_tool("krita")

    def launch_inkscape(self):
        self.launch_tool("inkscape")

    def launch_davinci(self):
        self.launch_tool("davinci")

    def set_project_folder(self):
        """Open file browser to set the project agent's working directory."""
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            result = self.project_agent.set_working_directory(folder)
            self.update_global_chat(f"\n{result}\n\n")
            # Update project name
            self.project_name_var.set(os.path.basename(folder))
    
    def fetch_web_content(self):
        """Fetch content from a web URL."""
        url = simpledialog.askstring("Fetch Web Content", "Enter URL:")
        if url:
            self.update_global_chat(f"🌐 Fetching content from {url}...\n")
            
            def do_fetch():
                result = self.project_agent.fetch_web_content(url)
                self.root.after(0, lambda: self.show_fetch_result(result))
            
            import threading
            threading.Thread(target=do_fetch, daemon=True).start()
    
    def show_fetch_result(self, result):
        """Display fetched web content."""
        if isinstance(result, dict):
            self.update_global_chat(f"{result['message']}\n\n")
            self.update_global_chat(f"Preview:\n{result['content'][:500]}...\n\n")
        else:
            self.update_global_chat(f"{result}\n\n")
    
    def analyze_project(self):
        """Analyze the current project folder."""
        result = self.project_agent.analyze_project()
        if isinstance(result, dict):
            self.update_global_chat(f"\n{result['message']}\n")
            self.update_global_chat(f"Directory: {result['directory']}\n")
            self.update_global_chat(f"Total Files: {result['total_files']}\n")
            self.update_global_chat(f"Total Size: {result['total_size_mb']} MB\n")
            self.update_global_chat(f"\nFile Types:\n")
            for ext, count in result['file_types'].items():
                self.update_global_chat(f"  {ext}: {count} files\n")
            self.update_global_chat("\n")
        else:
            self.update_global_chat(f"{result}\n\n")
    
    def list_project_files(self):
        """List files in the project folder."""
        pattern = simpledialog.askstring("List Files", "Enter file pattern (e.g., *.py, *.gd):", 
                                        initialvalue="*")
        if pattern:
            result = self.project_agent.list_files(pattern)
            if isinstance(result, dict):
                self.update_global_chat(f"\n{result['message']}\n\n")
                for file in result['files'][:20]:  # Show first 20
                    self.update_global_chat(f"  📄 {file}\n")
                if result['count'] > 20:
                    self.update_global_chat(f"  ... and {result['count'] - 20} more\n")
                self.update_global_chat("\n")
            else:
                self.update_global_chat(f"{result}\n\n")
    
    def search_in_project(self):
        """Search for text in project files."""
        search_term = simpledialog.askstring("Search in Project", "Enter search term:")
        if search_term:
            pattern = simpledialog.askstring("File Pattern", "Search in files matching pattern:", 
                                            initialvalue="*")
            if pattern:
                self.update_global_chat(f"🔍 Searching for '{search_term}' in {pattern}...\n")
                result = self.project_agent.search_in_files(search_term, pattern)
                if isinstance(result, dict):
                    self.update_global_chat(f"{result['message']}\n\n")
                    for match in result['results'][:10]:  # Show first 10
                        self.update_global_chat(f"  📄 {match['file']}:{match['line_number']}\n")
                        self.update_global_chat(f"     {match['content']}\n\n")
                    if result['matches'] > 10:
                        self.update_global_chat(f"  ... and {result['matches'] - 10} more matches\n\n")
                else:
                    self.update_global_chat(f"{result}\n\n")
    
    def read_project_file(self):
        """Read and display a file from the project."""
        if not self.project_agent.working_directory:
            messagebox.showwarning("No Project", "Please set a project folder first.")
            return
        
        file_path = simpledialog.askstring("Read File", "Enter relative file path:")
        if file_path:
            result = self.project_agent.read_file(file_path)
            if isinstance(result, dict):
                # Create a window to display the file content
                file_window = tk.Toplevel(self.root)
                file_window.title(f"File: {result['path']}")
                file_window.geometry("900x600")
                file_window.configure(bg='#1a1a1a')
                
                # Info bar
                info_frame = tk.Frame(file_window, bg='#2a2a2a')
                info_frame.pack(fill='x', padx=5, pady=5)
                tk.Label(info_frame, text=f"📄 {result['path']} | Size: {result['size']} chars | Lines: {result['lines']}", 
                        bg='#2a2a2a', fg='#ffffff', font=('Consolas', 10)).pack(side='left', padx=5)
                
                # Content
                text_widget = scrolledtext.ScrolledText(file_window, bg='#2a2a2a', fg='#00ff00', 
                                                       font=('Consolas', 10), wrap='none')
                text_widget.pack(fill='both', expand=True, padx=5, pady=5)
                text_widget.insert('1.0', result['content'])
                text_widget.config(state='disabled')
                
                self.update_global_chat(f"📖 {result['message']}\n\n")
            else:
                self.update_global_chat(f"{result}\n\n")
    
    def edit_project_file(self):
        """Edit a file in the project."""
        if not self.project_agent.working_directory:
            messagebox.showwarning("No Project", "Please set a project folder first.")
            return
        
        file_path = simpledialog.askstring("Edit File", "Enter relative file path:")
        if not file_path:
            return
        
        # Read the file first
        result = self.project_agent.read_file(file_path)
        if isinstance(result, dict):
            # Create editor window
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Edit: {result['path']}")
            edit_window.geometry("900x600")
            edit_window.configure(bg='#1a1a1a')
            
            # Toolbar
            toolbar = tk.Frame(edit_window, bg='#2a2a2a')
            toolbar.pack(fill='x', padx=5, pady=5)
            tk.Label(toolbar, text=f"📝 Editing: {result['path']}", bg='#2a2a2a', fg='#ffffff', 
                    font=('Consolas', 10, 'bold')).pack(side='left', padx=5)
            
            def save_file():
                content = text_widget.get('1.0', 'end-1c')
                save_result = self.project_agent.write_file(file_path, content, backup=True)
                self.update_global_chat(f"{save_result}\n")
                messagebox.showinfo("Saved", save_result)
            
            tk.Button(toolbar, text="💾 Save", command=save_file, bg='#00aa00', fg='white', 
                     font=('Segoe UI', 9)).pack(side='right', padx=5)
            
            # Editor
            text_widget = scrolledtext.ScrolledText(edit_window, bg='#2a2a2a', fg='#00ff00', 
                                                   font=('Consolas', 10), wrap='none')
            text_widget.pack(fill='both', expand=True, padx=5, pady=5)
            text_widget.insert('1.0', result['content'])
        else:
            self.update_global_chat(f"{result}\n\n")

    def launch_tool(self, tool_name):
        try:
            subprocess.Popen([tool_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.update_global_chat(f"🛠️ Launched {tool_name}\n")
        except Exception as e:
            self.update_global_chat(f"❌ Failed to launch {tool_name}: {str(e)}\n")

    def launch_3d_assistant(self):
        self.update_global_chat("🤖 AI 3D Assistant activated. Ask Elaine for STL generation or technical modeling advice.\n")

    def launch_game_designer(self):
        self.update_global_chat("🎮 AI Game Designer activated. Ask Carrie for sprite/background generation or creative design ideas.\n")

    def launch_music_composer(self):
        self.update_global_chat("🎵 AI Music Composer activated. Ask Carrie for creative composition ideas or Elaine for technical audio advice.\n")

    def launch_concept_artist(self):
        self.update_global_chat("🎨 AI Concept Artist activated. Ask Carrie for visual concepts or design inspiration.\n")

    def new_project(self):
        name = simpledialog.askstring("New Project", "Enter project name:", initialvalue="New Project")
        if name:
            self.project_name_var.set(name)
            self.project_type_var.set("General")
            self.asset_tree.delete(*self.asset_tree.get_children())
            self.asset_tree.insert('', 'end', text='3D Models', open=True)
            self.asset_tree.insert('', 'end', text='Textures', open=True)
            self.asset_tree.insert('', 'end', text='Audio', open=True)
            self.asset_tree.insert('', 'end', text='Scripts', open=True)
            self.update_global_chat(f"📋 New project created: {name}\n")

    def load_project(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                self.project_name_var.set(project_data.get('name', 'Untitled Project'))
                self.project_type_var.set(project_data.get('type', 'General'))
                self.asset_tree.delete(*self.asset_tree.get_children())
                for category, assets in project_data.get('assets', {}).items():
                    node = self.asset_tree.insert('', 'end', text=category, open=True)
                    for asset in assets:
                        self.asset_tree.insert(node, 'end', text=asset)
                self.update_global_chat(f"📂 Project loaded: {os.path.basename(file_path)}\n")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load project: {str(e)}")

    def save_project(self):
        if self.project_name_var.get() == "Untitled Project":
            self.save_project_as()
        else:
            self._save_project(self.project_name_var.get() + ".json")

    def save_project_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self._save_project(file_path)

    def _save_project(self, file_path):
        try:
            project_data = {
                'name': self.project_name_var.get(),
                'type': self.project_type_var.get(),
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'assets': {
                    '3D Models': [self.asset_tree.item(i, 'text') for i in self.asset_tree.get_children(self.asset_tree.get_children()[0])],
                    'Textures': [self.asset_tree.item(i, 'text') for i in self.asset_tree.get_children(self.asset_tree.get_children()[1])],
                    'Audio': [self.asset_tree.item(i, 'text') for i in self.asset_tree.get_children(self.asset_tree.get_children()[2])],
                    'Scripts': [self.asset_tree.item(i, 'text') for i in self.asset_tree.get_children(self.asset_tree.get_children()[3])]
                },
                'elaine_memory': self.elaine.memory if self.elaine else [],
                'carrie_memory': self.carrie.memory if self.carrie else [],
                'collaborative_mode': self.collaborative_mode
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            self.update_global_chat(f"💾 Project saved: {os.path.basename(file_path)}\n")
            self.status_label.config(text=f"Saved: {self.project_name_var.get()}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save project: {str(e)}")

    def import_assets(self):
        files = filedialog.askopenfilenames(
            title="Select assets to import",
            filetypes=[
                ("All supported", "*.obj;*.fbx;*.blend;*.png;*.jpg;*.wav;*.ogg;*.py;*.gd"),
                ("3D Models", "*.obj;*.fbx;*.blend;*.dae"),
                ("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.tga"),
                ("Audio", "*.wav;*.ogg;*.mp3;*.flac"),
                ("Scripts", "*.py;*.gd;*.cs;*.js"),
                ("All files", "*.*")
            ]
        )
        if files:
            imported_count = len(files)
            self.update_global_chat(f"📥 Imported {imported_count} assets to project\n")
            for file_path in files:
                filename = os.path.basename(file_path)
                ext = os.path.splitext(filename)[1].lower()
                if ext in ['.obj', '.fbx', '.blend', '.dae']:
                    models_node = self.asset_tree.get_children()[0]
                    self.asset_tree.insert(models_node, 'end', text=filename)
                elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tga']:
                    textures_node = self.asset_tree.get_children()[1]
                    self.asset_tree.insert(textures_node, 'end', text=filename)
                elif ext in ['.wav', '.ogg', '.mp3', '.flac']:
                    audio_node = self.asset_tree.get_children()[2]
                    self.asset_tree.insert(audio_node, 'end', text=filename)
                elif ext in ['.py', '.gd', '.cs', '.js']:
                    scripts_node = self.asset_tree.get_children()[3]
                    self.asset_tree.insert(scripts_node, 'end', text=filename)

    def export_project(self):
        folder = filedialog.askdirectory(title="Select export directory")
        if folder:
            self.update_global_chat(f"📤 Project exported to: {os.path.basename(folder)}\n")
            self.status_label.config(text="Project exported")

    def toggle_toolbar(self):
        if self.toolbar_visible:
            self.toolbar.pack_forget()
            self.toolbar_visible = False
        else:
            self.toolbar.pack(side='top', fill='x')
            self.toolbar_visible = True

    def toggle_fullscreen(self):
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        self.update_global_chat("🔲 Entered fullscreen mode\n" if not current_state else "🪟 Exited fullscreen mode\n")

    def set_theme(self, theme):
        theme_colors = {
            'dark': {'bg': '#2b2b2b', 'fg': '#ffffff'},
            'light': {'bg': '#f0f0f0', 'fg': '#000000'}
        }
        if theme in theme_colors:
            self.update_global_chat(f"🎨 Theme changed to {theme} mode\n")

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide - Dual Brain AI Creative Workflow Center")
        help_window.geometry("900x700")
        help_window.configure(bg='#1a1a1a')
        help_notebook = ttk.Notebook(help_window)
        help_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        start_frame = tk.Frame(help_notebook, bg='#1a1a1a')
        help_notebook.add(start_frame, text="🚀 Getting Started")
        start_text = scrolledtext.ScrolledText(start_frame, bg='#2a2a2a', fg='#ffffff', 
                                              font=('Segoe UI', 11), wrap=tk.WORD)
        start_text.pack(fill='both', expand=True, padx=10, pady=10)
        getting_started = """
🧠 DUAL BRAIN AI SYSTEM - GETTING STARTED

Welcome to the most advanced AI-powered creative workflow system!

1. LAUNCHING YOUR AI BRAINS
   • Click 🧠 Elaine for analytical thinking
   • Click 🎨 Carrie for creative inspiration
   • Use "Launch Both" for maximum power
   • Watch the status indicators turn green

2. STARTING CONVERSATIONS
   • Use "Start Auto Conversation" for AI brain discussions
   • Set custom topics for focused brainstorming
   • Watch the Global Conversation Monitor
   • Join conversations directly in brain windows

3. LAUNCHING CREATIVE TOOLS
   • Use toolbar buttons for quick access
   • Menu system for full tool categories
   • AI assistants provide context-aware help
   • Tools integrate with active AI brains

4. PROJECT MANAGEMENT
   • Create new projects with custom names
   • Import assets from multiple formats
   • Save/load projects with AI memory
   • Export completed work

5. COLLABORATIVE MODE
   • Requires both brains online
   • Enables cross-domain expertise
   • Provides dual-perspective solutions
   • Enhances all creative workflows
        """
        start_text.insert(tk.END, getting_started)
        brain_frame = tk.Frame(help_notebook, bg='#1a1a1a')
        help_notebook.add(brain_frame, text="🤖 AI Brains")
        brain_text = scrolledtext.ScrolledText(brain_frame, bg='#2a2a2a', fg='#ffffff',
                                              font=('Segoe UI', 11), wrap=tk.WORD)
        brain_text.pack(fill='both', expand=True, padx=10, pady=10)
        brain_guide = """
🧠 ELAINE - THE ANALYTICAL BRAIN

SPECIALTIES:
• Logical problem solving and analysis
• Technical optimization and debugging
• System architecture and planning
• Performance analysis and metrics
• Mathematical and scientific reasoning
• STL generation for 3D printing

BEST FOR:
• 3D CAD modeling precision
• Game system architecture
• Audio engineering technical aspects
• Code generation and optimization
• Project planning and workflow
• Quality assurance and testing

🎨 CARRIE - THE CREATIVE BRAIN

SPECIALTIES:
• Artistic inspiration and creativity
• Visual design and aesthetics
• Innovation and experimentation
• Emotional and intuitive insights
• Sprite and background generation
• Vector designs for Cricut

BEST FOR:
• 3D artistic modeling and texturing
• Game art and visual design
• Music composition and creativity
• Concept art and visual ideas
• UI/UX design and user experience
• Creative brainstorming and ideation

🤝 COLLABORATIVE MODE

WHEN BOTH BRAINS ARE ACTIVE:
• Technical precision meets creative vision
• Analytical solutions with artistic flair
• Cross-domain expertise and insights
• Enhanced problem-solving capabilities
• Balanced perspectives on all projects
• Comprehensive workflow assistance
        """
        brain_text.insert(tk.END, brain_guide)
        tools_frame = tk.Frame(help_notebook, bg='#1a1a1a')
        help_notebook.add(tools_frame, text="🛠️ Creative Tools")
        tools_text = scrolledtext.ScrolledText(tools_frame, bg='#2a2a2a', fg='#ffffff',
                                              font=('Segoe UI', 11), wrap=tk.WORD)
        tools_text.pack(fill='both', expand=True, padx=10, pady=10)
        tools_guide = """
🛠️ SUPPORTED CREATIVE TOOLS

🔧 3D & CAD TOOLS
• FreeCAD 🛠️ - Professional parametric 3D CAD modeler
  AI Support: Technical precision, STL generation
• OpenSCAD 🛠️ - Programmable solid 3D CAD modeler
  AI Support: Code-based modeling assistance
• Blender 🛠️ - Complete 3D creation suite
  AI Support: Both technical modeling and artistic vision

🎮 GAME DEVELOPMENT
• Godot Engine 🎮 - Advanced cross-platform game engine
  AI Support: System architecture + creative design
• Unity 🎮 - Industry-standard game development platform
  AI Support: Technical optimization + visual artistry
• Unreal Engine 🎮 - Industry-leading development platform
  AI Support: Technical optimization + visual artistry

🎵 AUDIO PRODUCTION
• LMMS 🎵 - Free cross-platform music production suite
  AI Support: Technical mixing + creative composition
• Ardour 🎵 - Professional digital audio workstation
  AI Support: Engineering precision + artistic expression
• Reaper 🎵 - Efficient digital audio production
  AI Support: Workflow optimization + creative ideas

🎨 GRAPHICS & DESIGN
• GIMP 🎨 - GNU Image Manipulation Program
  AI Support: Technical editing + creative enhancement
• Krita 🎨 - Professional painting program
  AI Support: Digital art techniques + sprite/background creation
• Inkscape 🎨 - Professional vector graphics editor
  AI Support: Technical precision + artistic composition
• DaVinci Resolve 🎨 - Professional video editing & color
  AI Support: Technical workflow + creative vision

🤖 AI ASSISTANTS
• Code Generator - AI-powered programming assistance
• Asset Creator - AI asset generation and optimization
• Music Composer - AI collaborative music composition
• Concept Artist - AI-powered visual concept creation
• 3D Assistant - AI-guided 3D modeling and STL generation
• Game Designer - AI game development consultation
• Project Advisor - AI project insights and guidance
• Quality Analyst - AI quality assessment and optimization
        """
        tools_text.insert(tk.END, tools_guide)

    def show_tutorials(self):
        tutorial_text = """
🎓 DUAL BRAIN AI WORKFLOW TUTORIALS

🏗️ 3D MODELING WORKFLOW:
1. Launch Blender or FreeCAD from toolbar
2. Activate Elaine for technical modeling advice
3. Ask for STL generation with specific parameters
4. Use Carrie for artistic inspiration
5. Enable collaborative mode for best results

🎮 GAME DEVELOPMENT WORKFLOW:
1. Create new project (Game Development type)
2. Launch Godot or Unreal Engine
3. Import assets to project browser
4. Ask Carrie for sprite/background generation
5. Use Elaine for system architecture

🎵 MUSIC PRODUCTION WORKFLOW:
1. Launch LMMS or Ardour
2. Activate Carrie for creative inspiration
3. Use Elaine for technical mixing advice
4. Use AI Music Composer for collaboration
5. Export and save to project

🎨 DIGITAL ART WORKFLOW:
1. Launch Krita or Inkscape
2. Activate Carrie for artistic guidance
3. Ask for SVG or sprite generation
4. Get technical advice from Elaine
5. Save artwork to project assets

🤖 AI COLLABORATION TIPS:
• Be specific in your requests to AI brains
• Use "how do I" or "define" for web searches
• Enable collaborative mode for complex projects
• Let AI brains discuss ideas together
• Save projects to preserve AI memory
• Use memory search to find past insights

💡 PRODUCTIVITY TIPS:
• Use toolbar for quick tool access
• Pin brain windows to manage workspace
• Import all assets at project start
• Use AI assistants throughout workflow
• Enable auto-conversations for inspiration
• Export projects when complete
        """
        messagebox.showinfo("Workflow Tutorials", tutorial_text)

    def show_ai_guide(self):
        guide_text = """
🤖 AI COLLABORATION GUIDE

🎯 MAXIMIZING AI BRAIN POTENTIAL:

🧠 ELAINE SPECIALIZES IN:
• Technical problem solving
• STL generation for 3D printing
• Code optimization and debugging
• System architecture planning
• Performance analysis
• Mathematical computations

🎨 CARRIE SPECIALIZES IN:
• Creative inspiration and ideation
• Sprite and background generation
• Vector designs for Cricut
• Artistic vision and aesthetics
• Innovation and experimentation
• Emotional and intuitive insights

🤝 COLLABORATIVE TECHNIQUES:
1. DIVIDE AND CONQUER:
   • Ask Elaine for technical tasks
   • Ask Carrie for creative tasks
   • Combine both perspectives

2. BRAIN CONVERSATIONS:
   • Let them discuss topics together
   • Set interesting conversation topics
   • Learn from their interactions

3. WEB SEARCHES:
   • Use "how do I" or "define" queries
   • Get design references and instructions
   • Leverage search for project research

4. MEMORY UTILIZATION:
   • Search both brains' memories
   • Build on previous conversations
   • Create knowledge continuity

5. PROJECT INTEGRATION:
   • Save AI insights with projects
   • Load previous AI knowledge
   • Maintain context across sessions
        """
        messagebox.showinfo("AI Collaboration Guide", guide_text)

    def show_about(self):
        about_text = """
🧠 DUAL BRAIN AI CREATIVE WORKFLOW CENTER
Version 3.0 - Professional Creative Suite

🎯 FEATURES:
• Dual AI Brain System (Elaine + Carrie)
• Integrated Creative Tool Launcher
• Professional Project Management
• AI-Powered Collaboration
• STL Generation for 3D Printing
• Sprite and Background Generation
• Web Search for Instructions and Definitions
• Cross-Domain Workflow Support
• Expandable for Mobile/Multi-Node

🛠️ SUPPORTED TOOLS:
• 3D & CAD: FreeCAD 🛠️, OpenSCAD 🛠️, Blender 🛠️
• Game Dev: Godot 🎮, Unity 🎮, Unreal Engine 🎮
• Audio: LMMS 🎵, Ardour 🎵, Reaper 🎵
• Graphics: GIMP 🎨, Krita 🎨, Inkscape 🎨, DaVinci Resolve 🎨

🤖 AI CAPABILITIES:
• Code Generation & Optimization
• STL Generation with Procedural Algorithms
• Sprite and Background Generation
• Vector Design for Cricut
• Web Search for Project Research
• Context-Aware Responses
• Persistent Memory with SQLite
• Collaborative Mode for Dual Perspectives
• Real-Time Project Monitoring
• Team Collaboration Features

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Created by: Adam Lee Hatchett
© 2026 Adam Lee Hatchett
All Rights Reserved
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Empowering Creativity Through AI Collaboration
        """
        messagebox.showinfo("About", about_text)

    def run(self):
        try:
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
            startup_msg = "🚀 Dual Brain AI Creative Workflow Center v3.0 Initialized\n"
            startup_msg += "Ready for professional creative work with AI assistance!\n"
            startup_msg += "💡 Launch AI brains to begin collaborative creative workflow\n\n"
            self.update_global_chat(startup_msg)
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.autosave_running = True
            def autosave_loop():
                while self.autosave_running:
                    try:
                        if self.project_name_var.get() != "Untitled Project":
                            self.save_project()
                    except Exception:
                        pass
                    time.sleep(300)  # Autosave every 5 minutes
            threading.Thread(target=autosave_loop, daemon=True).start()
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            messagebox.showerror("Critical Error", f"Application error: {str(e)}")

    def on_closing(self):
        try:
            self.autosave_running = False
            if self.conversation_active:
                self.stop_auto_conversation()
            if self.project_name_var.get() != "Untitled Project":
                if messagebox.askyesno("Save Project", "Save current project before closing?"):
                    self.save_project()
            if self.elaine_window and self.elaine_window.winfo_exists():
                self.elaine_window.destroy()
            if self.carrie_window and self.carrie_window.winfo_exists():
                self.carrie_window.destroy()
            self.update_global_chat("👋 Dual Brain AI System shutting down. Thank you for using our creative workflow center!\n")
            self.root.after(1000, self.root.destroy)
        except:
            self.root.destroy()

if __name__ == "__main__":
    import sys
    from datetime import datetime as _dt

    def start_cli_chat():
        print("dual_brain_ai CLI chat. Commands: /help, /save, /exit")
        brain = BrainAI("CLI", "Terminal Assistant", "#888888")
        brain.use_ollama = False
        chat_log = []
        while True:
            try:
                user = input("You: ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting CLI chat.")
                break

            if not user.strip():
                continue

            if user.startswith("/"):
                cmd = user.strip().lower()
                if cmd == "/help":
                    print("Commands: /help  show this help\n         /save  save chat to file\n         /exit  quit and save")
                    continue
                if cmd == "/save":
                    t = _dt.utcnow().strftime("%Y%m%d_%H%M%S")
                    path = f"dual_brain_chat_{t}.json"
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            json.dump(chat_log, f, ensure_ascii=False, indent=2)
                        print(f"Saved chat to {path}")
                    except Exception as e:
                        print("Failed to save chat:", e)
                    continue
                if cmd == "/exit":
                    t = _dt.utcnow().strftime("%Y%m%d_%H%M%S")
                    path = f"dual_brain_chat_{t}.json"
                    try:
                        with open(path, "w", encoding="utf-8") as f:
                            json.dump(chat_log, f, ensure_ascii=False, indent=2)
                        print(f"Saved chat to {path}. Goodbye.")
                    except Exception as e:
                        print("Exit: failed to save chat:", e)
                    break
                print("Unknown command. Type /help")
                continue

            ts = _dt.utcnow().isoformat()
            chat_log.append({"role": "user", "content": user, "ts": ts})
            try:
                resp = brain.process_input(user)
            except Exception:
                resp = "(local responder failed)"
            print("Assistant:", resp)
            chat_log.append({"role": "assistant", "content": resp, "ts": _dt.utcnow().isoformat()})

    print("🧠 Starting Dual Brain AI Creative Workflow Center v3.0")
    print("🎨 Professional Creative Suite with AI Collaboration")
    print("=" * 60)
    print("Created by: Adam Lee Hatchett")
    print("© 2026 Adam Lee Hatchett. All Rights Reserved.")
    print("=" * 60)

    # CLI helper to quickly test Ollama without launching GUI
    if '--test-ollama' in sys.argv:
        prompt = "Hello from dual_brain_ai test. Reply with a single short confirmation message."
        model = 'llama2-uncensored:latest'
        print(f"Testing Ollama with model: {model}")
        resp = query_ollama(prompt, model=model, max_tokens=128, stream=False)
        print("--- OLLAMA RESPONSE ---")
        print(resp)
        sys.exit(0)

    # New: terminal chat mode
    if '--chat' in sys.argv or '--cli-chat' in sys.argv:
        start_cli_chat()
        sys.exit(0)

    try:
        app = MainControlInterface()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        print("Please check that all required dependencies are installed:")
        print("- tkinter, requests, bs4, numpy, numpy-stl, PIL")
        print("- Required creative software (optional)")
    print("\n👋 Thank you for using Dual Brain AI Creative Workflow Center!")
