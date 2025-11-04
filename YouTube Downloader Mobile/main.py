from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import AsyncImage
from kivy.metrics import dp
import yt_dlp
import os
import sys
import threading
import shutil
from logger import DownloadLogger

def get_ffmpeg_path():
    """Get the path to FFmpeg, checking both local and system locations"""
    # Check if we're running on Android
    if hasattr(sys, 'frozen') and getattr(sys, '_MEIPASS', False):
        # Running as APK, use bundled FFmpeg
        base_path = os.path.dirname(os.path.abspath(__file__))
        if sys.platform == 'android':
            return os.path.join(base_path, 'ffmpeg', 'ffmpeg')
    
    # Check local ffmpeg directory first
    local_ffmpeg = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg', 'ffmpeg.exe')
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
    
    # Check in parent directory (for development setup)
    parent_ffmpeg = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ffmpeg', 'ffmpeg.exe')
    if os.path.exists(parent_ffmpeg):
        return parent_ffmpeg
    
    # Check system PATH
    system_ffmpeg = shutil.which('ffmpeg')
    if system_ffmpeg:
        return system_ffmpeg
    
    return None

class YouTubeDownloaderApp(App):
    def build(self):
        # Set dark theme colors
        self.theme_cls = {
            'background': '#2E3440',
            'primary': '#88C0D0',
            'secondary': '#A3BE8C',
            'text': '#ECEFF4',
            'error': '#BF616A'
        }
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        self.main_layout.background_color = self.theme_cls['background']
        
        # Title
        title = Label(
            text='YouTube Downloader',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(40)
        )
        self.main_layout.add_widget(title)
        
        # URL input
        self.url_input = TextInput(
            hint_text='Paste YouTube URL here...',
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            padding=[dp(10), dp(10)]
        )
        self.main_layout.add_widget(self.url_input)
        
        # Fetch button
        self.fetch_button = Button(
            text='Fetch Info',
            size_hint_y=None,
            height=dp(50),
            background_color=self.theme_cls['primary']
        )
        self.fetch_button.bind(on_press=self.fetch_video_info)
        self.main_layout.add_widget(self.fetch_button)
        
        # Thumbnail
        self.thumbnail = AsyncImage(
            size_hint=(1, None),
            height=dp(200),
            fit_mode='contain'
        )
        self.main_layout.add_widget(self.thumbnail)
        
        # Title label
        self.title_label = Label(
            text='',
            size_hint_y=None,
            height=dp(60),
            text_size=(Window.width - dp(40), None)
        )
        self.main_layout.add_widget(self.title_label)
        
        # Quality spinner
        self.quality_spinner = Spinner(
            text='Select Quality',
            values=[],
            size_hint_y=None,
            height=dp(50)
        )
        self.main_layout.add_widget(self.quality_spinner)
        
        # Download type buttons
        type_layout = BoxLayout(size_hint_y=None, height=dp(50))
        self.video_button = ToggleButton(
            text='Video',
            state='down',
            background_color=self.theme_cls['primary'],
            group='download_type'
        )
        self.audio_button = ToggleButton(
            text='Audio Only',
            background_color=self.theme_cls['secondary'],
            group='download_type'
        )
        self.video_button.bind(state=lambda x, y: self.set_download_type('video') if y == 'down' else None)
        self.audio_button.bind(state=lambda x, y: self.set_download_type('audio') if y == 'down' else None)
        type_layout.add_widget(self.video_button)
        type_layout.add_widget(self.audio_button)
        self.main_layout.add_widget(type_layout)
        
        # Progress bar
        self.progress = ProgressBar(max=100)
        self.main_layout.add_widget(self.progress)
        
        # Status label
        self.status_label = Label(
            text='Ready',
            size_hint_y=None,
            height=dp(30)
        )
        self.main_layout.add_widget(self.status_label)
        
        # Download button
        self.download_button = Button(
            text='Download',
            size_hint_y=None,
            height=dp(60),
            background_color=self.theme_cls['secondary']
        )
        self.download_button.bind(on_press=self.start_download)
        self.main_layout.add_widget(self.download_button)
        
        # Initialize variables
        self.video_info = None
        self.streams = []
        self.download_type = 'video'
        
        return self.main_layout

    def set_download_type(self, dtype):
        self.download_type = dtype
        self.update_quality_options()

    def fetch_video_info(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.show_error('Please enter a YouTube URL')
            return

        self.status_label.text = 'Fetching info...'
        self.fetch_button.disabled = True
        
        def fetch():
            try:
                logger = DownloadLogger()
                with yt_dlp.YoutubeDL({'quiet': True, 'logger': logger}) as ydl:
                    info = ydl.extract_info(url, download=False)
                Clock.schedule_once(lambda dt: self.update_video_info(info))
            except Exception as error:
                error_msg = str(error)
                Clock.schedule_once(lambda dt: self.show_error(error_msg))
            finally:
                Clock.schedule_once(lambda dt: setattr(self.fetch_button, 'disabled', False))
        
        threading.Thread(target=fetch, daemon=True).start()

    def update_video_info(self, info):
        self.video_info = info
        self.title_label.text = info.get('title', 'Unknown Title')
        self.thumbnail.source = info.get('thumbnail', '')
        self.update_quality_options()
        self.status_label.text = 'Ready to download'

    def update_quality_options(self):
        if not self.video_info:
            return

        formats = self.video_info.get('formats', [])
        options = []
        
        if self.download_type == 'video':
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
        else:
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

        options.sort(key=lambda x: x.get('height', 0) if 'height' in x else x.get('abr', 0),
                    reverse=True)
        self.streams = options
        self.quality_spinner.values = [opt['text'] for opt in options]
        if options:
            self.quality_spinner.text = options[0]['text']

    def progress_callback(self, d):
        try:
            if not isinstance(d, dict):
                print(f"Invalid progress data type: {type(d)}")
                return

            status = d.get('status', '')
            if status == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    try:
                        progress = min((downloaded / total) * 100, 100)
                        def update_ui(dt):
                            try:
                                self.progress.value = progress
                                speed = d.get('speed', 0)
                                if speed:
                                    speed_mb = speed / 1024 / 1024
                                    self.status_label.text = f'Downloading... {speed_mb:.1f} MB/s'
                                else:
                                    self.status_label.text = 'Downloading...'
                            except Exception as ui_error:
                                print(f"UI update error: {str(ui_error)}")
                        Clock.schedule_once(update_ui)
                    except Exception as calc_error:
                        print(f"Progress calculation error: {str(calc_error)}")
            elif status == 'finished':
                def update_complete(dt):
                    self.status_label.text = 'Download completed!'
                    self.progress.value = 100
                Clock.schedule_once(update_complete)
        except Exception as e:
            print(f"Progress callback error: {str(e)}")

    def start_download(self, instance):
        if not self.video_info or not self.streams:
            self.show_error('Please fetch video information first')
            return

        try:
            selected_index = self.quality_spinner.values.index(self.quality_spinner.text)
        except ValueError:
            self.show_error('Please select a quality option')
            return

        selected_format = self.streams[selected_index]['format_id']
        
        # Get the downloads directory path
        if os.name == 'posix':  # Android
            output_path = '/storage/emulated/0/Download'
        else:  # Other platforms
            output_path = os.path.expanduser("~/Downloads")

        self.download_button.disabled = True
        self.progress.value = 0

        def download():
            try:
                # Ensure output directory exists
                if not os.path.exists(output_path):
                    os.makedirs(output_path)

                logger = DownloadLogger()
                
                # Get FFmpeg path
                ffmpeg_location = get_ffmpeg_path()
                if not ffmpeg_location:
                    Clock.schedule_once(lambda dt: self.show_error("FFmpeg not found. Please ensure FFmpeg is installed."))
                    return
                
                ydl_opts = {
                    'format': selected_format,
                    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.progress_callback],
                    'quiet': True,
                    'no_warnings': True,
                    'noprogress': False,
                    'logger': logger,
                    'ffmpeg_location': ffmpeg_location
                }

                if self.download_type == "audio":
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]

                # Get video URL
                video_url = self.video_info.get('webpage_url') or self.video_info.get('url')
                if not video_url:
                    raise ValueError("Could not get video URL")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Download with error handling
                    try:
                        ydl.download([video_url])
                    except Exception as e:
                        print(f"Download error: {str(e)}")
                        raise

                Clock.schedule_once(lambda dt: self.show_success())
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(f"Download failed: {str(e)}"))
            finally:
                Clock.schedule_once(lambda dt: setattr(self.download_button, 'disabled', False))

        self.status_label.text = "Downloading..."
        threading.Thread(target=download, daemon=True).start()

    def show_error(self, message):
        self.status_label.text = f"Error: {message}"
        self.status_label.color = self.theme_cls['error']

    def show_success(self):
        self.status_label.text = "Download completed!"
        self.status_label.color = self.theme_cls['secondary']
        self.progress.value = 100

if __name__ == '__main__':
    Window.clearcolor = (0.18, 0.20, 0.25, 1)  # Dark theme background
    YouTubeDownloaderApp().run()