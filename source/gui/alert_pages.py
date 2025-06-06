import customtkinter as ctk
from threading import Thread
import time
import random
import math
import webbrowser

class ParticleLine:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = max(width, 100)  # Ensure minimum dimensions
        self.height = max(height, 100)
        self.reset_position()
        self.length = random.randint(8, 15)
        self.speed = random.uniform(0.3, 1.2)
        self.angle = random.uniform(0, math.pi*2)
        self.color = self._select_color()
        self.line = self.canvas.create_line(
            self.x, self.y,
            self.x + math.cos(self.angle) * self.length,
            self.y + math.sin(self.angle) * self.length,
            fill=self.color, width=1
        )
        
    def reset_position(self):
        """Reset particle to random position within canvas"""
        self.x = random.randint(0, self.width)
        self.y = random.randint(0, self.height)
        
    def _select_color(self):
        colors = ["#FF4444", "#AAAAAA", "#888888", "#FF3333"]
        return random.choice(colors)
        
    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        # Wrap around edges
        if self.x < 0: self.x = self.width
        if self.x > self.width: self.x = 0
        if self.y < 0: self.y = self.height
        if self.y > self.height: self.y = 0
        self.canvas.coords(
            self.line,
            self.x, self.y,
            self.x + math.cos(self.angle) * self.length,
            self.y + math.sin(self.angle) * self.length
        )

class Particle:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = max(width, 100)  # Ensure minimum dimensions
        self.height = max(height, 100)
        self.reset_position()
        self.radius = 2
        self.speed = random.uniform(0.5, 1.2)
        self.angle = random.uniform(0, math.pi * 2)
        self.color = "#AAAAAA"
        self.id = self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=self.color, outline=""
        )
        
    def reset_position(self):
        self.x = random.randint(0, self.width)
        self.y = random.randint(0, self.height)
        
    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        # Wrap around edges
        if self.x < 0: self.x = self.width
        if self.x > self.width: self.x = 0
        if self.y < 0: self.y = self.height
        if self.y > self.height: self.y = 0
        self.canvas.coords(
            self.id,
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius
        )

class InAppAlert:
    def __init__(self, root):
        self.root = root
        self.alert_active = False
        self.particles_dot = []
        self.particles_line = []
        self.lines = []

    def _create_particle_background(self, overlay, particle_type="line"):
        # Create canvas for particles
        self.particle_canvas = ctk.CTkCanvas(
            overlay, 
            bg="#111111",
            highlightthickness=0
        )
        self.particle_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Force update to get proper dimensions
        overlay.update_idletasks()
        
        # Get actual dimensions after rendering
        width = max(overlay.winfo_width(), 100)
        height = max(overlay.winfo_height(), 100)
        
        # Set explicit dimensions
        self.particle_canvas.config(width=width, height=height)
        
        # Initialize based on type
        if particle_type == "line":
            self.particles_line = [ParticleLine(self.particle_canvas, width, height) for _ in range(40)]
            self._animate_particles("line")
        elif particle_type == "dot":
            self.particles_dot = [Particle(self.particle_canvas, width, height) for _ in range(60)]
            self._animate_particles("dot")
        elif particle_type == "dot+line":
            self.particles_dot = [Particle(self.particle_canvas, width, height) for _ in range(60)]
            self._animate_dots_with_lines()

    def _animate_particles(self, particle_type="line"):
        if not self.alert_active or not hasattr(self, 'particle_canvas'):
            return

        if particle_type == "line":
            for p in self.particles_line:
                p.move()
        elif particle_type == "dot":
            for p in self.particles_dot:
                p.move()

        self.root.after(30, lambda: self._animate_particles(particle_type))

    def _animate_dots_with_lines(self):
        if not self.alert_active or not hasattr(self, 'particle_canvas'):
            return

        # Clear existing lines
        for line in self.lines:
            self.particle_canvas.delete(line)
        self.lines.clear()

        max_link_distance = 120
        # Draw connections between close particles
        for i, p1 in enumerate(self.particles_dot):
            for j, p2 in enumerate(self.particles_dot[i+1:], start=i+1):
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                dist = math.hypot(dx, dy)
                if dist < max_link_distance:
                    alpha = int(255 * (1 - dist / max_link_distance))
                    color = f'#AAAAAA'
                    line_id = self.particle_canvas.create_line(
                        p1.x, p1.y, p2.x, p2.y,
                        fill=color, width=1
                    )
                    self.lines.append(line_id)

        # Move all particles
        for p in self.particles_dot:
            p.move()

        self.root.after(30, self._animate_dots_with_lines)

    def show_alert(self, message_type="warning", title="", message="", duration=0, 
                  particle_type="line", button_action="close", button_text=None, 
                  action_target=None):
        """
        Display a customizable alert
        
            Parameters:
        - message_type: "warning", "error", "success", or "info"
        - title: The header text for the alert
        - message: The main content of the alert
        - duration: Auto-close after seconds (0 = manual close)
        - particle_type: "line", "dot", "dot+line", "off"
        - button_action: "close" to close alert, "url" to open URL, "command" to execute function
        - button_text: Custom text for the button (defaults to "ACKNOWLEDGE" or "OPEN LINK")
        - action_target: URL if button_action="url", function if button_action="command"
        """
        if self.alert_active:
            return
        self.alert_active = True

        # Color schemes for different message types
        color_palette = {
            "warning": {"bg": "#1A1A1A", "border": "#FF9500", "text": "#FF9500", "secondary": "#AAAAAA"},
            "error": {"bg": "#1A1A1A", "border": "#FF4444", "text": "#FF4444", "secondary": "#AAAAAA"},
            "success": {"bg": "#1A1A1A", "border": "#4CAF50", "text": "#4CAF50", "secondary": "#AAAAAA"},
            "info": {"bg": "#1A1A1A", "border": "#2196F3", "text": "#2196F3", "secondary": "#AAAAAA"}
        }

        colors = color_palette.get(message_type.lower(), color_palette["warning"])

        # Create overlay frame
        self.overlay = ctk.CTkFrame(
            self.root,
            fg_color="#111111" if particle_type != "off" else colors["bg"],
            corner_radius=0
        )
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Create particle background if needed
        if particle_type != "off":
            self._create_particle_background(self.overlay, particle_type)

        # Alert frame
        self.alert_frame = ctk.CTkFrame(
            self.overlay,
            fg_color=colors["bg"],
            border_color=colors["border"],
            border_width=1,
            corner_radius=8,
            width=500,
            height=300
        )
        self.alert_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.alert_frame.lift()

        # Header
        header_frame = ctk.CTkFrame(self.alert_frame, fg_color="transparent")
        header_frame.pack(pady=(25, 15), fill="x")
        ctk.CTkLabel(
            header_frame,
            text=message_type.upper(),
            font=("Arial", 18, "bold"),
            text_color=colors["secondary"]
        ).pack()
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=("Arial", 22, "bold"),
            text_color=colors["text"]
        ).pack(pady=(5, 0))

        # Divider line
        ctk.CTkFrame(
            self.alert_frame,
            fg_color=colors["border"],
            height=1
        ).pack(fill="x", padx=30, pady=10)

        # Message content
        ctk.CTkLabel(
            self.alert_frame,
            text=message,
            font=("Arial", 15),
            text_color="white",
            wraplength=450,
            justify="center"
        ).pack(pady=10, padx=30)

        # Determine button text
        if button_text is None:
            button_text = "OPEN LINK" if button_action == "url" else "ACKNOWLEDGE"

        # Button command based on action type
        if button_action == "close":
            button_command = self._cleanup
        elif button_action == "url":
            button_command = lambda: [webbrowser.open(action_target), self._cleanup()]
        elif button_action == "command":
            button_command = lambda: [action_target(), self._cleanup()]
        else:
            button_command = self._cleanup

        # Button
        button_frame = ctk.CTkFrame(self.alert_frame, fg_color="transparent")
        button_frame.pack(pady=(10, 20))
        ctk.CTkButton(
            button_frame,
            text=button_text,
            fg_color="transparent",
            border_color=colors["border"],
            border_width=1,
            hover_color="#2A2A2A",
            text_color=colors["text"],
            width=140,
            height=32,
            corner_radius=4,
            command=button_command
        ).pack()

        # Auto-close if duration specified
        if duration > 0:
            Thread(target=self._auto_close, args=(duration,), daemon=True).start()

    def _auto_close(self, duration):
        time.sleep(duration)
        self.root.after(0, self._cleanup)

    def _cleanup(self):
        if hasattr(self, 'overlay'):
            self.overlay.destroy()
        self.alert_active = False
        self.particles_dot = []
        self.particles_line = []
        self.lines = []

# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("800x600")
    alert = InAppAlert(root)

    def custom_action():
        print("Custom function executed!")
    
    def show_close_alert():
        alert.show_alert(
            message_type="error",
            title="STANDARD ALERT",
            message="This will close when you click the button",
            particle_type="dot+line",
            button_action="close"
        )
    
    def show_url_alert():
        alert.show_alert(
            message_type="info",
            title="EXTERNAL LINK",
            message="Click the button to visit our website",
            particle_type="line",
            button_action="url",
            button_text="VISIT WEBSITE",
            action_target="https://example.com"
        )
    
    def show_command_alert():
        alert.show_alert(
            message_type="success",
            title="CUSTOM ACTION",
            message="This will execute a function when clicked",
            particle_type="dot",
            button_action="command",
            button_text="EXECUTE",
            action_target=custom_action
        )

    ctk.CTkButton(root, text="Standard Close Alert", command=show_close_alert).pack(pady=10)
    ctk.CTkButton(root, text="URL Alert", command=show_url_alert).pack(pady=10)
    ctk.CTkButton(root, text="Command Alert", command=show_command_alert).pack(pady=10)
    root.mainloop()