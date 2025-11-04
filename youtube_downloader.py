import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.request import urlopen
from io import BytesIO
import threading
import os
import shutil
from PIL import Image, ImageTk
import yt_dlp
import time

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=40, corner_radius=10, bg='#f0f4f8', fg='#334e68', hover_color='#627d98'):
        # Calculate responsive dimensions based on parent window size
        window_width = parent.winfo_screenwidth()
        scale_factor = window_width / 1920  # Base width for scaling
        adj_width = int(width * scale_factor)
        adj_height = int(height * scale_factor)
        adj_radius = int(corner_radius * scale_factor)
        
        super().__init__(parent, width=adj_width, height=adj_height, bg=bg, highlightthickness=0)
        self.command = command
        self.corner_radius = adj_radius
        self.bg = bg
        self.fg = fg
        self.hover_color = hover_color
        self.current_color = self.bg
        
        # Store original dimensions for responsive updates
        self.original_dims = {'width': width, 'height': height, 'radius': corner_radius}
        parent.bind('<Configure>', self.on_parent_resize)
        
        # Create rounded rectangle button with glowing effect
        self.rect = self.create_rounded_rect(0, 0, width, height, corner_radius, fill=self.bg)
        self.glow = self.create_rounded_rect(2, 2, width-2, height-2, corner_radius-1, fill=self.bg)
        self.text = self.create_text(width//2, height//2, text=text, fill=fg, font=('Segoe UI', 10, 'bold'))
        
        # Bind events
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
                 x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
                 x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, e):
        self.animate_color(self.hover_color)
        self.animate_glow(True)
        self.configure(cursor='hand2')

    def on_leave(self, e):
        self.animate_color(self.bg)
        self.animate_glow(False)
        self.configure(cursor='')

    def on_click(self, e):
        self.animate_press()

    def on_release(self, e):
        self.animate_release()
        if self.command:
            self.command()

    def animate_color(self, target_color, steps=10):
        def interpolate_color(start_color, end_color, step, total_steps):
            rs, gs, bs = int(start_color[1:3], 16), int(start_color[3:5], 16), int(start_color[5:7], 16)
            re, ge, be = int(end_color[1:3], 16), int(end_color[3:5], 16), int(end_color[5:7], 16)
            r = rs + (re - rs) * step // total_steps
            g = gs + (ge - gs) * step // total_steps
            b = bs + (be - bs) * step // total_steps
            return f'#{r:02x}{g:02x}{b:02x}'

        def animate_step(step=0):
            if step <= steps:
                color = interpolate_color(self.current_color, target_color, step, steps)
                self.itemconfig(self.rect, fill=color)
                self.itemconfig(self.glow, fill=color)
                self.after(20, lambda: animate_step(step + 1))
        
        self.current_color = target_color
        animate_step()

    def animate_glow(self, is_hover):
        glow_color = '#88C0D0' if is_hover else self.current_color
        steps = 10
        
        def animate_step(step=0):
            if step <= steps:
                alpha = step/steps if is_hover else (1 - step/steps)
                color = self.blend_colors(self.current_color, glow_color, alpha)
                self.itemconfig(self.glow, fill=color)
                self.after(20, lambda: animate_step(step + 1))
        
        animate_step()

    def blend_colors(self, color1, color2, ratio):
        try:
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            r = int(r1 * (1-ratio) + r2 * ratio)
            g = int(g1 * (1-ratio) + g2 * ratio)
            b = int(b1 * (1-ratio) + b2 * ratio)
            return f'#{r:02x}{g:02x}{b:02x}'
        except (ValueError, IndexError):
            return color1  # Return original color if blending fails

    def on_parent_resize(self, event):
        """Handle parent window resize events to maintain responsive sizing"""
        if event.widget == self.master:
            # Calculate new dimensions
            scale_factor = event.width / 1920
            new_width = int(self.original_dims['width'] * scale_factor)
            new_height = int(self.original_dims['height'] * scale_factor)
            new_radius = int(self.original_dims['radius'] * scale_factor)
            
            # Update canvas size
            self.configure(width=new_width, height=new_height)
            
            # Redraw shapes with new dimensions
            self.delete('all')
            self.rect = self.create_rounded_rect(0, 0, new_width, new_height, new_radius, fill=self.current_color)
            self.glow = self.create_rounded_rect(2, 2, new_width-2, new_height-2, new_radius-1, fill=self.current_color)
            
            # Update text position and size
            font_size = int(10 * scale_factor)
            text_item = self.find_withtag('text')
            if text_item:
                self.itemconfig(text_item, font=('Segoe UI', font_size, 'bold'))
                self.coords(text_item, new_width//2, new_height//2)


    def animate_press(self):
        self.scale_button(0.95)

    def animate_release(self):
        self.scale_button(1.0)

    def scale_button(self, scale_factor):
        center_x = self.winfo_width() / 2
        center_y = self.winfo_height() / 2
        self.scale('all', center_x, center_y, scale_factor, scale_factor)

class ModernEntry(ttk.Entry):
    def __init__(self, *args, **kwargs):
        self.default_fg = '#334e68'
        self.placeholder_fg = '#829ab1'
        self.default_bg = '#f0f4f8'
        self.active_bg = '#e6edf3'
        
        # Get parent window width for responsive sizing
        parent = args[0] if args else kwargs.get('master')
        if parent:
            window_width = parent.winfo_screenwidth()
            scale_factor = window_width / 1920
            font_size = int(10 * scale_factor)  # Base font size is 10
            kwargs['font'] = ('Segoe UI', font_size)
        
        style = ttk.Style()
        style.configure('Modern.TEntry',
                       fieldbackground=self.default_bg,
                       foreground=self.default_fg,
                       borderwidth=0,
                       relief='flat')
        
        super().__init__(*args, **kwargs)
        self.configure(style='Modern.TEntry')
        
        # Bind resize event
        parent = args[0] if args else kwargs.get('master')
        if parent:
            parent.bind('<Configure>', self.on_parent_resize)
            
    def on_parent_resize(self, event):
        """Update font size on window resize"""
        if event.widget == self.master:
            scale_factor = event.width / 1920
            font_size = int(10 * scale_factor)
            self.configure(font=('Segoe UI', font_size))
        
    def set_placeholder(self, text):
        self.placeholder_text = text
        self.insert(0, text)
        self.configure(foreground=self.placeholder_fg)
        
        def handle_focus_in(event):
            if self.get() == self.placeholder_text:
                self.delete(0, tk.END)
                self.configure(foreground=self.default_fg)
                
        def handle_focus_out(event):
            if not self.get():
                self.insert(0, self.placeholder_text)
                self.configure(foreground=self.placeholder_fg)
                
        self.bind('<FocusIn>', handle_focus_in)
        self.bind('<FocusOut>', handle_focus_out)

class YouTubeDownloader:
    def __init__(self):
        self.setup_window()
        self.setup_styles()
        self.create_main_layout()
        self.setup_variables()
        self.check_dependencies()
        self.animate_startup()

    def setup_window(self):
        self.root = tk.Tk()
        self.root.title("YouTube Downloader Pro")
        
        # Calculate window size based on screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Use 70% of screen width and height for window size
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.7)
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg='#f0f4f8')
        
        # Enable window resizing with minimum size
        self.root.minsize(800, 600)
        self.root.bind('<Configure>', self.on_window_resize)
        
    def on_window_resize(self, event):
        """Handle main window resize events"""
        if event.widget == self.root:
            # Update layout spacing based on window size
            width = event.width
            height = event.height
            
            # Calculate new padding and spacing values
            base_width = 900  # Original design width
            scale_factor = width / base_width
            
            # Update padding and spacing for widgets
            new_padding = int(20 * scale_factor)
            new_spacing = int(10 * scale_factor)
            
            # Update widget layouts
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame):
                    widget.configure(padx=new_padding, pady=new_padding)
                elif isinstance(widget, ttk.Separator):
                    widget.configure(pad=new_spacing)
        self.root.minsize(900, 700)
        
        # Add window fade-in effect
        try:
            self.root.attributes('-alpha', 0.0)
        except:
            pass

    def animate_startup(self):
        def fade_in(alpha=0):
            alpha += 0.1
            try:
                self.root.attributes('-alpha', alpha)
            except:
                pass
            if alpha < 1.0:
                self.root.after(20, lambda: fade_in(alpha))
        fade_in()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure modern styles with gradients and effects
        self.style.configure('Modern.TFrame',
                           background='#f0f4f8')
        self.style.configure('Modern.TLabel',
                           background='#f0f4f8',
                           foreground='#334e68',
                           font=('Segoe UI', 10))
        self.style.configure('Title.TLabel',
                           font=('Segoe UI', 24, 'bold'),
                           background='#f0f4f8',
                           foreground='#486581')
                           
        # Configure progress bar style
        self.style.layout('Modern.TProgressbar',
                         [('Modern.Horizontal.TProgressbar.trough',
                           {'children': [('Modern.Horizontal.TProgressbar.pbar',
                                        {'side': 'left', 'sticky': 'ns'})],
                            'sticky': 'nswe'})])
        self.style.configure('Modern.TProgressbar',
                           background='#627d98',
                           troughcolor='#e6edf3',
                           borderwidth=0,
                           thickness=10)

    def create_main_layout(self):
        # Main container with modern padding and shadow effect
        self.main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # App title with animation
        self.create_title_section()
        
        # URL Input Section with modern styling
        self.create_url_section()
        
        # Video Info Section with animations
        self.create_info_section()
        
        # Download Options Section with modern controls
        self.create_download_section()
        
        # Progress Section with animated progress bar
        self.create_progress_section()

    def create_title_section(self):
        title_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        title = ttk.Label(title_frame, text="YouTube Downloader Pro",
                         style='Title.TLabel')
        title.pack(anchor='center')
        
        subtitle = ttk.Label(title_frame, 
                           text="Download videos and music with style",
                           style='Modern.TLabel')
        subtitle.pack(anchor='center')

    def create_url_section(self):
        url_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        url_frame.pack(fill=tk.X, pady=(0, 20))

        # Modern URL input with placeholder
        self.url_var = tk.StringVar()
        self.url_entry = ModernEntry(url_frame, textvariable=self.url_var,
                                   width=50, font=('Segoe UI', 10))
        self.url_entry.set_placeholder("Paste YouTube URL here...")
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Fetch button with glow effect
        self.fetch_btn = ModernButton(url_frame, text="✨ Fetch Info",
                                    command=self.fetch_video_info,
                                    width=120, height=35,
                                    bg='#627d98',
                                    fg='#f0f4f8',
                                    hover_color='#486581')
        self.fetch_btn.pack(side=tk.LEFT)

    def check_url(self):
        """Check if the URL is valid"""
        url = self.url_var.get().strip()
        return url and url != "Paste YouTube URL here..."

    def create_info_section(self):
        info_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        info_frame.pack(fill=tk.X, pady=20)

        # Thumbnail with shadow effect
        self.thumb_frame = ttk.Frame(info_frame, style='Modern.TFrame')
        self.thumb_frame.pack(side=tk.LEFT)
        
        self.thumb_canvas = tk.Canvas(self.thumb_frame, width=240, height=135,
                                    bg="#2E3440", highlightthickness=0)
        self.thumb_canvas.pack()

        # Video Details with animations
        details_frame = ttk.Frame(info_frame, style='Modern.TFrame')
        details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)
        
        self.title_label = ttk.Label(details_frame, text="",
                                   style='Title.TLabel', wraplength=500)
        self.title_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.author_label = ttk.Label(details_frame, text="",
                                    style='Modern.TLabel')
        self.author_label.pack(anchor=tk.W)

    def create_download_section(self):
        options_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        options_frame.pack(fill=tk.X, pady=20)

        # Quality selector with modern styling
        quality_frame = ttk.Frame(options_frame, style='Modern.TFrame')
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        quality_label = ttk.Label(quality_frame, text="Quality:",
                                style='Modern.TLabel')
        quality_label.pack(side=tk.LEFT)
        
        self.quality_var = tk.StringVar()
        self.quality_combo = ttk.Combobox(quality_frame,
                                        textvariable=self.quality_var,
                                        width=50, state="readonly",
                                        font=('Segoe UI', 10))
        self.quality_combo.pack(side=tk.LEFT, padx=10)

        # Modern radio buttons for download type
        type_frame = ttk.Frame(options_frame, style='Modern.TFrame')
        type_frame.pack(fill=tk.X, pady=10)
        
        self.download_type = tk.StringVar(value="video")
        for text, value in [("🎥 Video", "video"), ("🎵 Audio", "audio")]:
            rb = ttk.Radiobutton(type_frame, text=text,
                               variable=self.download_type,
                               value=value,
                               command=self.update_quality_options,
                               style='Modern.TLabel')
            rb.pack(side=tk.LEFT, padx=10)

        # Save location with modern styling
        location_frame = ttk.Frame(options_frame, style='Modern.TFrame')
        location_frame.pack(fill=tk.X, pady=(10, 0))
        
        save_label = ttk.Label(location_frame, text="Save to:",
                             style='Modern.TLabel')
        save_label.pack(side=tk.LEFT)
        
        self.save_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.path_entry = ModernEntry(location_frame,
                                    textvariable=self.save_path,
                                    width=50)
        self.path_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        browse_btn = ModernButton(location_frame, text="📁 Browse",
                                command=self.browse_location,
                                width=100, height=35,
                                bg='#4C566A',
                                hover_color='#5E81AC')
        browse_btn.pack(side=tk.LEFT)

        # Download button with pulsing effect
        self.download_btn = ModernButton(self.main_frame, text="⬇️ Start Download",
                                       command=self.start_download,
                                       width=200, height=45,
                                       bg='#A3BE8C',
                                       fg='#2E3440',
                                       hover_color='#88C0D0')
        self.download_btn.pack(pady=20)

    def create_progress_section(self):
        progress_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        progress_frame.pack(fill=tk.X, pady=20)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                          style='Modern.TProgressbar',
                                          variable=self.progress_var,
                                          maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
        self.status_label = ttk.Label(progress_frame, text="Ready",
                                    style='Modern.TLabel')
        self.status_label.pack(pady=(10, 0))

    def setup_variables(self):
        self.video_info = None
        self.streams = []
        self.thumbnail_image = None
        self.playlist_videos = []
        self.playlist_total = 0
        self.playlist_current = 0

    def check_dependencies(self):
        if not yt_dlp:
            messagebox.showerror("Error", "yt-dlp is not installed. Please run: pip install yt-dlp")
            self.root.quit()
            
        # Check for ffmpeg in local directory first
        ffmpeg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg')
        ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
        
        if not os.path.exists(ffmpeg_path):
            # Check system PATH as fallback
            ffmpeg_path = shutil.which('ffmpeg')
            
        if not ffmpeg_path:
            result = messagebox.askquestion("FFmpeg Not Found", 
                "FFmpeg is not installed, which is recommended for better video/audio quality and format support.\n\n"
                "Would you like to open the FFmpeg download page?")
            if result == 'yes':
                import webbrowser
                webbrowser.open('https://github.com/yt-dlp/yt-dlp/wiki/Installation#ffmpeg-installation')
            self.update_status("⚠️ FFmpeg not found - some features may be limited")

    def animate_progress(self, value):
        current = self.progress_var.get()
        if abs(current - value) > 0.1:
            step = (value - current) / 10
            new_value = current + step
            self.progress_var.set(new_value)
            self.root.after(20, lambda: self.animate_progress(value))

    def update_status(self, message):
        self.status_label.config(text=message)

    def browse_location(self):
        folder = filedialog.askdirectory(initialdir=self.save_path.get())
        if folder:
            self.save_path.set(folder)

    def update_quality_options(self):
        if not self.video_info:
            return

        self.quality_combo['values'] = []
        formats = self.video_info.get('formats', [])
        
        if self.download_type.get() == "video":
            options = []
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    height = f.get('height', 0)
                    fps = f.get('fps', '')
                    size = f.get('filesize', 0) or f.get('filesize_approx', 0)
                    size_mb = f"{round(size/1024/1024, 1)}MB" if size else "?"
                    options.append({
                        'text': f"{height}p {fps}fps ({size_mb})",
                        'format_id': f.get('format_id'),
                        'height': height
                    })
            
            options.sort(key=lambda x: x['height'], reverse=True)
            self.streams = options
            self.quality_combo['values'] = [opt['text'] for opt in options]
            
        else:
            options = []
            for f in formats:
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    abr = f.get('abr', '?')
                    size = f.get('filesize', 0) or f.get('filesize_approx', 0)
                    size_mb = f"{round(size/1024/1024, 1)}MB" if size else "?"
                    options.append({
                        'text': f"{abr}kbps ({size_mb})",
                        'format_id': f.get('format_id'),
                        'abr': abr
                    })
            
            options.sort(key=lambda x: float(x['abr']) if isinstance(x['abr'], (int, float)) else 0,
                       reverse=True)
            self.streams = options
            self.quality_combo['values'] = [opt['text'] for opt in options]

        if self.streams:
            self.quality_combo.current(0)

    def fetch_video_info(self):
        url = self.url_var.get().strip()
        if url == "Paste YouTube URL here..." or not url:
            self.show_error_animation("Please enter a YouTube URL")
            return

        self.update_status("✨ Fetching information...")
        self.fetch_btn.configure(state='disabled')

        def fetch_thread():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': False,
                    'extract_flat': True,
                    'format': 'best',
                    'logger': self.create_logger()
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                
                self.video_info = info
                
                # Check if it's a playlist
                if info.get('_type') == 'playlist':
                    self.root.after(0, lambda: self.show_playlist_dialog(info))
                else:
                    self.root.after(0, lambda: self.update_video_info(info))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error_animation(str(e)))
            finally:
                self.root.after(0, lambda: self.fetch_btn.configure(state='normal'))

        threading.Thread(target=fetch_thread, daemon=True).start()

    def show_playlist_dialog(self, playlist_info):
        # Create playlist selection window
        playlist_window = tk.Toplevel(self.root)
        playlist_window.title("Playlist Selection")
        playlist_window.geometry("800x600")
        playlist_window.configure(bg='#2E3440')
        
        # Title
        title_label = ttk.Label(playlist_window, 
                              text=f"Playlist: {playlist_info.get('title', 'Unknown')}",
                              style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Create frame for the list
        list_frame = ttk.Frame(playlist_window, style='Modern.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox for videos
        listbox = tk.Listbox(list_frame, 
                            selectmode=tk.MULTIPLE,
                            bg='#3B4252',
                            fg='#ECEFF4',
                            selectbackground='#5E81AC',
                            font=('Segoe UI', 10),
                            height=20)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate list
        self.playlist_videos = playlist_info.get('entries', [])
        for i, video in enumerate(self.playlist_videos, 1):
            title = video.get('title', 'Unknown Title')
            duration = video.get('duration_string', '?:??')
            listbox.insert(tk.END, f"{i}. {title} [{duration}]")
        
        # Select all button
        def toggle_all():
            if listbox.size() == len(listbox.curselection()):
                listbox.selection_clear(0, tk.END)
            else:
                listbox.selection_set(0, tk.END)
                
        select_btn = ModernButton(playlist_window, 
                                text="Toggle All",
                                command=toggle_all,
                                width=120, height=35)
        select_btn.pack(pady=10)
        
        # Download button
        def start_playlist_download():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Warning", "Please select at least one video")
                return
                
            selected_videos = [self.playlist_videos[i] for i in selected_indices]
            playlist_window.destroy()
            self.download_playlist(selected_videos)
            
        download_btn = ModernButton(playlist_window,
                                  text="Download Selected",
                                  command=start_playlist_download,
                                  width=200, height=45,
                                  bg='#A3BE8C',
                                  fg='#2E3440',
                                  hover_color='#88C0D0')
        download_btn.pack(pady=20)
        
        # Cancel button
        def on_cancel():
            playlist_window.destroy()
            self.update_status("Ready")
            
        cancel_btn = ModernButton(playlist_window,
                                text="Cancel",
                                command=on_cancel,
                                width=120, height=35)
        cancel_btn.pack(pady=10)

    def download_playlist(self, videos):
        if not videos:
            return
            
        self.playlist_total = len(videos)
        self.playlist_current = 0
        
        output_path = self.save_path.get()
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                self.show_error_animation(f"Could not create output directory: {e}")
                return
                
        self.download_btn.configure(state='disabled')
        self.progress_var.set(0)
        
        def download_video(video):
            try:
                url = f"https://www.youtube.com/watch?v={video['id']}"
                ydl_opts = {
                    'format': 'best' if self.download_type.get() == "video" else 'bestaudio',
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.update_playlist_progress],
                    'quiet': True,
                    'no_warnings': True,
                    'logger': self.create_logger(),
                    'prefer_ffmpeg': True
                }
                
                if self.download_type.get() == "audio":
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                    
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                self.playlist_current += 1
                progress = (self.playlist_current / self.playlist_total) * 100
                self.root.after(0, lambda: self.progress_var.set(progress))
                self.root.after(0, lambda: self.update_status(
                    f"✨ Downloaded {self.playlist_current}/{self.playlist_total} videos"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.show_error_animation(
                    f"Error downloading {video.get('title', 'video')}: {str(e)}"))
                
        def download_all():
            for video in videos:
                download_video(video)
            self.root.after(0, lambda: self.download_btn.configure(state='normal'))
            self.root.after(0, lambda: self.show_success_animation())
            
        self.update_status(f"⬇️ Downloading playlist ({len(videos)} videos)...")
        threading.Thread(target=download_all, daemon=True).start()
        
    def update_playlist_progress(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                # Calculate progress for current video
                video_progress = (downloaded / total) * 100
                # Calculate overall progress
                single_video_weight = 100 / self.playlist_total
                overall_progress = (self.playlist_current * single_video_weight + 
                                 (video_progress * single_video_weight / 100))
                self.root.after(0, lambda: self.progress_var.set(overall_progress))
                
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024
                    self.root.after(0, lambda: self.update_status(
                        f"⬇️ Video {self.playlist_current + 1}/{self.playlist_total} "
                        f"({video_progress:.1f}%) - {speed_mb:.1f} MB/s"))

    def create_logger(self):
        class Logger:
            def debug(self, msg):
                pass
                
            def warning(self, msg):
                if "ffmpeg not found" in msg.lower():
                    return  # We already handle this elsewhere
                if "falling back to generic" in msg.lower():
                    return  # Skip generic fallback warnings
                if "nsig extraction failed" in msg.lower():
                    return  # Skip signature extraction warnings
                if any(x in msg.lower() for x in ["sabr streaming", "skipped", "malformed"]):
                    return  # Skip streaming related warnings
                print(f"Warning: {msg}")
                
            def error(self, msg):
                print(f"Error: {msg}")
                
        return Logger()

    def show_error_animation(self, message):
        def flash_red():
            self.status_label.configure(foreground='#BF616A')
            self.root.after(500, lambda: self.status_label.configure(foreground='#ECEFF4'))
        
        self.update_status(f"❌ {message}")
        flash_red()

    def update_video_info(self, info):
        # Animate title update with typewriter effect
        def animate_text(widget, text, index=0):
            if index <= len(text):
                widget.configure(text=text[:index])
                self.root.after(50, lambda: animate_text(widget, text, index + 1))
        
        animate_text(self.title_label, info.get('title', 'Unknown Title'))
        self.author_label.configure(text=f"👤 By: {info.get('uploader', 'Unknown')}")

        # Animate thumbnail with zoom and fade effect
        thumb_url = info.get('thumbnail')
        if thumb_url:
            try:
                with urlopen(thumb_url) as response:
                    raw_data = response.read()
                image = Image.open(BytesIO(raw_data))
                
                def zoom_in(scale=0.5, steps=10):
                    if scale <= 1.0:
                        size = (int(240 * scale), int(135 * scale))
                        scaled = image.resize(size, Image.Resampling.LANCZOS)
                        
                        # Add fade effect
                        alpha = int(255 * scale)
                        alpha_img = Image.new('RGBA', size, (46, 52, 64, alpha))
                        blend = Image.blend(scaled.convert('RGBA'), alpha_img, 0.3)
                        
                        self.thumbnail_image = ImageTk.PhotoImage(blend)
                        self.thumb_canvas.delete('all')
                        self.thumb_canvas.create_image(120, 67, image=self.thumbnail_image)
                        
                        self.root.after(50, lambda: zoom_in(scale + 0.1))
                
                zoom_in()
            except Exception:
                pass

        self.update_quality_options()
        self.update_status("✅ Ready to download")

    def start_download(self):
        if not self.video_info or not self.streams:
            self.show_error_animation("Please fetch video information first")
            return

        selected_index = self.quality_combo.current()
        if selected_index < 0:
            self.show_error_animation("Please select a quality option")
            return

        selected_format = self.streams[selected_index]['format_id']
        output_path = self.save_path.get()

        # Create a logger to suppress unwanted messages
        class Logger:
            def debug(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass

        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                self.show_error_animation(f"Could not create output directory: {e}")
                return

        # Animate button to show processing state
        self.download_btn.configure(state='disabled')
        self.progress_var.set(0)

        def pulse_animation():
            if self.download_btn['state'] == 'disabled':
                self.download_btn.animate_color('#4C566A')
                self.root.after(1000, lambda: self.download_btn.animate_color('#A3BE8C'))
                self.root.after(2000, pulse_animation)

        pulse_animation()

        def download():
            try:
                ydl_opts = {
                    'format': selected_format,
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.update_progress],
                    'quiet': True,
                    'no_warnings': True,
                    'logger': self.create_logger(),
                    'prefer_ffmpeg': True
                }

                if self.download_type.get() == "audio":
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url_var.get().strip()])

                self.root.after(0, lambda: self.show_success_animation())
            except Exception as e:
                self.root.after(0, lambda: self.show_error_animation(f"Download failed: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.download_btn.configure(state='normal'))

        self.update_status("⬇️ Downloading...")
        threading.Thread(target=download, daemon=True).start()

    def show_success_animation(self):
        self.update_status("✨ Download completed!")
        self.progress_var.set(100)
        
        # Celebratory animation
        def celebrate(count=0):
            colors = ['#A3BE8C', '#88C0D0', '#5E81AC', '#B48EAD']
            if count < 5:  # Flash 5 times
                self.status_label.configure(foreground=colors[count % len(colors)])
                self.root.after(200, lambda: celebrate(count + 1))
            else:
                self.status_label.configure(foreground='#ECEFF4')
        
        celebrate()
        messagebox.showinfo("Success ✨", "Download completed successfully!")

    def update_progress(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                progress = (downloaded / total) * 100
                self.animate_progress(progress)
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024
                    self.update_status(f"⬇️ Downloading: {progress:.1f}% ({speed_mb:.1f} MB/s)")
                else:
                    self.update_status(f"⬇️ Downloading: {progress:.1f}%")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()