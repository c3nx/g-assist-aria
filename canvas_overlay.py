#!/usr/bin/env python3
"""
Canvas-based Aria Overlay - Single window with sprite shifting
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QLabel, QDesktopWidget, QWidget
from PyQt5.QtCore import Qt, QPoint, QTimer, QRect
from PyQt5.QtGui import QPixmap, QMouseEvent, QPainter, QFont, QPen, QBrush, QColor, QPainterPath

class CanvasAriaOverlay(QLabel):
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_position = QPoint()
        self.current_frame = 0
        self.sprite_sheet = None
        self.frame_width = 0
        self.frame_height = 0
        
        # Speech bubble properties
        self.speech_text = ""
        self.speech_visible = False
        self.speech_timer = QTimer()
        self.speech_timer.timeout.connect(self.hideSpeechBubble)
        self.last_log_size = 0
        
        # Response accumulation
        self.accumulating_response = False
        self.response_chunks = []
        self.complete_timer = QTimer()
        self.complete_timer.timeout.connect(self.completeResponse)
        self.complete_timer.setSingleShot(True)
        
        self.setupWindow()
        self.loadSpriteSheet()
        self.setupAnimationTimer()
        self.setupLogWatcher()
        
    def setupWindow(self):
        self.setWindowTitle("Aria Avatar")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(450, 550)
        
        # Position at bottom-right
        self.positionBottomRight()
        
    def positionBottomRight(self):
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry()
        x = screen_rect.width() - self.width() - 20
        y = screen_rect.height() - self.height() - 20
        self.move(x, y)
        
    def loadSpriteSheet(self):
        """Load 5x2 sprite sheet"""
        sprite_paths = [
            os.path.join(os.path.dirname(__file__), "sprites", "aria.png"),
            r"C:\Users\User\G-Assist\avatar\sprites\aria.png",
            r"C:\ProgramData\NVIDIA Corporation\nvtopps\rise\plugins\aria\sprites\companion_sprites.png"
        ]
        
        for sprite_path in sprite_paths:
            if os.path.exists(sprite_path):
                self.sprite_sheet = QPixmap(sprite_path)
                # Calculate frame dimensions (5x2 grid)
                self.frame_width = self.sprite_sheet.width() // 5
                self.frame_height = self.sprite_sheet.height() // 2
                
                # Start with frame 0 (idle)
                self.displayFrame(0)
                print(f"Loaded sprite sheet: {sprite_path}")
                print(f"Frame size: {self.frame_width}x{self.frame_height}")
                return
        
        # Fallback
        self.setText("ARIA")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color: white; font-size: 24px; background-color: rgba(255, 182, 193, 150); border-radius: 20px;")
        
    def displayFrame(self, frame_number):
        """Display specific frame by cropping from sprite sheet"""
        if not self.sprite_sheet or self.sprite_sheet.isNull():
            return
            
        # Calculate position in 5x2 grid
        col = frame_number % 5
        row = frame_number // 5
        
        # Crop the frame
        x = col * self.frame_width
        y = row * self.frame_height
        
        frame = self.sprite_sheet.copy(x, y, self.frame_width, self.frame_height)
        
        # Scale to overlay size
        scaled_frame = frame.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Create a new pixmap with space for speech bubble
        full_pixmap = QPixmap(450, 550)
        full_pixmap.fill(Qt.transparent)
        
        painter = QPainter(full_pixmap)
        
        # Draw speech bubble if visible
        if self.speech_visible and self.speech_text:
            self.drawSpeechBubble(painter)
        
        # Draw sprite at bottom
        sprite_y = 150
        sprite_x = (450 - scaled_frame.width()) // 2
        painter.drawPixmap(sprite_x, sprite_y, scaled_frame)
        
        painter.end()
        self.setPixmap(full_pixmap)
        
        self.current_frame = frame_number
        
    def setupAnimationTimer(self):
        """Setup timer for checking emotions"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.checkEmotionState)
        self.animation_timer.start(1000)
        
    def setupLogWatcher(self):
        """Setup G-Assist shutdown detection and speech monitoring"""
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.checkGAssistRunning)
        self.log_timer.start(5000)
        
        # Initialize log size for speech detection
        self.log_file = os.path.join(os.environ.get("USERPROFILE", "."), 'aria_plugin.log')
        if os.path.exists(self.log_file):
            self.last_log_size = os.path.getsize(self.log_file)
        
        # Initialize chat context monitoring
        self.chat_context_file = os.path.join(os.environ.get("USERPROFILE", "."), 'aria_chat_context.txt')
        self.last_chat_context = ""
        
        print(f"Monitoring log file: {self.log_file}")
        print(f"Monitoring chat context: {self.chat_context_file}")
        
    def checkEmotionState(self):
        """Check log file for emotion keywords and monitor speech"""
        try:
            if not os.path.exists(self.log_file):
                return
            
            # Check for new chat context
            self.checkForNewChatContext()
            
            # Enable speech monitoring
            self.checkForNewSpeech(self.log_file)
                
            # Read recent log entries
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                recent_lines = ''.join(lines[-10:]).lower()
                
            # Emotion detection
            new_frame = None
            
            if any(word in recent_lines for word in [
                'angry', 'mad', 'pissed', 'furious', 'rage', 'hate'
            ]):
                new_frame = 2  # Angry
                
            elif any(word in recent_lines for word in [
                'sad', 'sorry', 'upset', 'disappointed', 'depressed', 'cry'
            ]):
                new_frame = 4  # Sad
                
            elif any(word in recent_lines for word in [
                'hello', 'hi', 'hey', 'greetings', 'good morning'
            ]):
                new_frame = 3  # Greeting
                
            elif any(word in recent_lines for word in [
                'happy', 'great', 'awesome', 'love', 'amazing', 'win'
            ]):
                new_frame = 1  # Happy
                
            elif 'response chunk' in recent_lines:
                new_frame = 9  # Speaking
                
            else:
                new_frame = 0  # Idle
                
            if new_frame is not None and new_frame != self.current_frame:
                self.displayFrame(new_frame)
                
        except Exception as e:
            print(f"Error checking emotion state: {e}")
            
    def checkGAssistRunning(self):
        """Check if G-Assist is still active"""
        try:
            if os.path.exists(self.log_file):
                file_age = time.time() - os.path.getmtime(self.log_file)
                
                if file_age > 120:
                    print("G-Assist inactive, closing overlay...")
                    self.close()
                    QApplication.quit()
            else:
                print("G-Assist log not found, closing overlay...")
                self.close()
                QApplication.quit()
                
        except Exception as e:
            print(f"Error checking G-Assist status: {e}")
    
    def checkForNewChatContext(self):
        """Check for new chat context and update display"""
        try:
            if not os.path.exists(self.chat_context_file):
                return
                
            with open(self.chat_context_file, 'r', encoding='utf-8') as f:
                new_context = f.read().strip()
            
            if new_context != self.last_chat_context:
                self.last_chat_context = new_context
                if new_context:
                    self.showChatContext(new_context)
                    
        except Exception as e:
            print(f"Error checking chat context: {e}")
    
    def showChatContext(self, context_text):
        """Show chat context as speech bubble"""
        self.speech_text = context_text
        self.speech_visible = True
        self.displayFrame(self.current_frame)
        self.speech_timer.stop()
        self.speech_timer.start(8000)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def checkForNewSpeech(self, log_file):
        """Monitor log file for new Aria responses"""
        try:
            current_size = os.path.getsize(log_file)
            
            if current_size > self.last_log_size:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(self.last_log_size)
                    new_content = f.read()
                    
                self.last_log_size = current_size
                
                lines = new_content.split('\n')
                
                for i, line in enumerate(lines):
                    if 'response chunk:' in line.lower():
                        try:
                            parts = line.split('Response chunk:', 1)
                            if len(parts) > 1:
                                chunk = parts[1].strip()
                                if chunk:
                                    if not self.accumulating_response:
                                        self.accumulating_response = True
                                        self.response_chunks = []
                                    
                                    self.response_chunks.append(chunk)
                                    self.complete_timer.stop()
                                    self.complete_timer.start(300)
                                    
                        except Exception as e:
                            print(f"Error processing chunk: {e}")
                    
                    elif 'response completed successfully' in line.lower():
                        if self.accumulating_response and self.response_chunks:
                            self.completeResponse()
                            
        except Exception as e:
            print(f"Error monitoring speech: {e}")
    
    def completeResponse(self):
        """Complete the accumulated response and show in speech bubble"""
        if self.response_chunks:
            # Smart chunk joining
            full_response = ""
            for i, chunk in enumerate(self.response_chunks):
                if i == 0:
                    full_response = chunk
                else:
                    if (chunk.startswith(('!', '?', '.', ',', '~', '^', '_')) or 
                        full_response.endswith((' ')) or
                        chunk.startswith(' ')):
                        full_response += chunk
                    else:
                        full_response += ' ' + chunk
            
            full_response = full_response.strip()
            self.showSpeechBubble(full_response)
            
            self.accumulating_response = False
            self.response_chunks = []
            self.complete_timer.stop()
    
    def showSpeechBubble(self, text):
        """Show speech bubble with Aria's response"""
        text = text.strip()
        
        if len(text) > 300:
            text = text[:297] + "..."
            
        self.speech_text = text
        self.speech_visible = True
        self.displayFrame(self.current_frame)
        
        self.speech_timer.stop()
        self.speech_timer.start(15000)
    
    def hideSpeechBubble(self):
        """Hide the speech bubble"""
        self.speech_visible = False
        self.speech_timer.stop()
        self.displayFrame(self.current_frame)
    
    def drawSpeechBubble(self, painter):
        """Draw G-Assist style chat box"""
        if not self.speech_text:
            return
            
        painter.setRenderHint(QPainter.Antialiasing)
        
        font = QFont("Segoe UI", 12, QFont.Normal)
        painter.setFont(font)
        
        # Dynamic dimensions
        padding = 20
        text_length = len(self.speech_text)
        
        if text_length < 30:
            box_width = 300
        elif text_length < 60:
            box_width = 400
        elif text_length < 120:
            box_width = 480
        else:
            box_width = 520
        
        # Calculate text height
        fm = painter.fontMetrics()
        from PyQt5.QtGui import QTextDocument
        doc = QTextDocument()
        doc.setDefaultFont(font)
        doc.setTextWidth(box_width - padding * 2)
        doc.setPlainText(self.speech_text)
        text_height = int(doc.size().height())
        
        min_height = 60
        max_height = 250
        box_height = max(min_height, min(max_height, text_height + padding * 2))
        
        # Position
        box_x = (450 - box_width) // 2
        if box_x < 0:
            box_x = -15
        box_y = 20
        
        # Draw box
        shadow_rect = QRect(box_x + 2, box_y + 2, box_width, box_height)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 50))
        
        main_rect = QRect(box_x, box_y, box_width, box_height)
        painter.fillRect(main_rect, QColor(30, 30, 30, 240))
        
        painter.setPen(QPen(QColor(100, 100, 100, 200), 1))
        painter.drawRect(main_rect)
        
        # Draw text with manual line breaking
        painter.setPen(QPen(QColor(255, 255, 255)))
        
        words = self.speech_text.split()
        lines = []
        current_line = ""
        max_width = box_width - padding * 2
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if fm.horizontalAdvance(test_line) > max_width:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        # Draw each line
        line_height = fm.height() + 2
        start_y = box_y + padding + fm.ascent()
        
        for i, line in enumerate(lines):
            painter.drawText(box_x + padding, start_y + (i * line_height), line)

def main():
    # Use Windows lock file to prevent multiple instances
    import tempfile
    import msvcrt
    
    lock_file_path = os.path.join(tempfile.gettempdir(), "aria_canvas_overlay.lock")
    lock_file = None
    
    try:
        lock_file = open(lock_file_path, 'w')
        
        try:
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        except IOError:
            print("Another canvas overlay is already running!")
            print("Exiting to prevent duplicates...")
            lock_file.close()
            return
        
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        print(f"Lock acquired for PID: {os.getpid()}")
        
    except Exception as e:
        print(f"Lock file error: {e}")
        print("Exiting to prevent duplicates...")
        if lock_file:
            lock_file.close()
        return
    
    app = QApplication(sys.argv)
    overlay = CanvasAriaOverlay()
    overlay.show()
    
    print("=== ARIA CANVAS OVERLAY ===")
    print("• Single persistent window")
    print("• Frame-based sprite animations") 
    print("• Emotion-responsive expressions")
    print("• Manga-style speech bubbles")
    print("• Drag to move around screen")
    print("• Auto-closes when G-Assist stops")
    
    try:
        result = app.exec_()
        
        # Cleanup lock file
        try:
            lock_file.close()
            if os.path.exists(lock_file_path):
                os.remove(lock_file_path)
            print("Lock file cleaned up")
        except:
            pass
            
        sys.exit(result)
        
    except KeyboardInterrupt:
        print("\nClosing canvas overlay...")
        overlay.close()
        app.quit()
        
        try:
            lock_file.close()
            if os.path.exists(lock_file_path):
                os.remove(lock_file_path)
        except:
            pass

if __name__ == "__main__":
    main()