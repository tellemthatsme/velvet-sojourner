"""
GitHub Repo Downloader - Webhook Integration
Real-time notifications when repositories are updated
"""
import os
import json
import hmac
import hashlib
import threading
import requests
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from flask import Flask, request, jsonify
import socket


class WebhookEventType(Enum):
    """GitHub webhook event types"""
    PUSH = "push"
    RELEASE = "release"
    ISSUES = "issues"
    PULL_REQUEST = "pull_request"
    CREATE = "create"
    DELETE = "delete"
    FORK = "fork"
    WATCH = "watch"
    DOWNLOAD = "download"
    COMMIT_COMMENT = "commit_comment"


@dataclass
class WebhookConfig:
    """Configuration for a webhook"""
    name: str
    repo_url: str
    events: List[WebhookEventType]
    callback_url: str
    secret: str = ""
    enabled: bool = True
    auto_download: bool = False
    last_triggered: datetime = None
    trigger_count: int = 0


@dataclass
class WebhookPayload:
    """Parsed webhook payload"""
    event_type: WebhookEventType
    repository: Dict
    sender: Dict
    action: str = ""
    ref: str = ""
    before: str = ""
    after: str = ""
    commits: List[Dict] = field(default_factory=list)
    releases: List[Dict] = field(default_factory=list)
    raw_data: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class WebhookServer:
    """
    Embedded Flask server for receiving GitHub webhooks
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, 
                 secret: str = "", plugin_manager=None):
        self.host = host
        self.port = port
        self.secret = secret
        self.plugin_manager = plugin_manager
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.app = self._create_app()
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Event handlers
        self.event_handlers: Dict[WebhookEventType, List[Callable]] = {
            event: [] for event in WebhookEventType
        }
    
    def _create_app(self) -> Flask:
        """Create Flask application"""
        app = Flask(__name__)
        
        @app.route('/webhook', methods=['POST'])
        def webhook():
            # Verify signature if secret is set
            if self.secret:
                signature = request.headers.get('X-Hub-Signature-256', '')
                if not self._verify_signature(request.data, signature):
                    return jsonify({'error': 'Invalid signature'}), 401
            
            event_type = request.headers.get('X-GitHub-Event', '')
            payload = request.json
            
            # Parse payload
            webhook_payload = self._parse_payload(event_type, payload)
            
            # Process webhook
            self._process_webhook(webhook_payload)
            
            return jsonify({'status': 'ok'}), 200
        
        @app.route('/health', methods=['GET'])
        def health():
            return jsonify({'status': 'healthy', 'webhooks': len(self.webhooks)}), 200
        
        @app.route('/webhooks', methods=['GET'])
        def list_webhooks():
            return jsonify({
                'webhooks': [
                    {
                        'name': w.name,
                        'repo': w.repo_url,
                        'enabled': w.enabled,
                        'trigger_count': w.trigger_count
                    }
                    for w in self.webhooks.values()
                ]
            }), 200
        
        return app
    
    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature"""
        if not signature.startswith('sha256='):
            return False
        
        expected = hmac.new(
            self.secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature[7:], expected)
    
    def _parse_payload(self, event_type: str, payload: Dict) -> WebhookPayload:
        """Parse webhook payload"""
        try:
            event = WebhookEventType(event_type)
        except ValueError:
            event = WebhookEventType.PUSH  # Default
        
        return WebhookPayload(
            event_type=event,
            repository=payload.get('repository', {}),
            sender=payload.get('sender', {}),
            action=payload.get('action', ''),
            ref=payload.get('ref', ''),
            before=payload.get('before', ''),
            after=payload.get('after', ''),
            commits=payload.get('commits', []),
            releases=payload.get('releases', []),
            raw_data=payload,
            timestamp=datetime.now()
        )
    
    def _process_webhook(self, payload: WebhookPayload):
        """Process incoming webhook"""
        # Find matching webhooks
        repo_url = payload.repository.get('html_url', '')
        
        for name, webhook in self.webhooks.items():
            if not webhook.enabled:
                continue
            
            if webhook.repo_url and webhook.repo_url not in repo_url:
                continue
            
            if payload.event_type not in webhook.events:
                continue
            
            # Trigger webhook
            webhook.last_triggered = datetime.now()
            webhook.trigger_count += 1
            
            # Call registered handlers
            for handler in self.event_handlers.get(payload.event_type, []):
                try:
                    handler(payload, webhook)
                except Exception as e:
                    print(f"Webhook handler error: {e}")
            
            # Auto-download if enabled
            if webhook.auto_download and self.plugin_manager:
                self._trigger_auto_download(payload, webhook)
    
    def _trigger_auto_download(self, payload: WebhookPayload, webhook: WebhookConfig):
        """Trigger automatic download on webhook"""
        if self.plugin_manager and self.plugin_manager.downloader:
            try:
                self.plugin_manager.downloader.create_download_task(
                    repo_url=payload.repository.get('html_url', ''),
                    output_path=webhook.callback_url,  # Use callback_url as output path
                    method=None  # Use default
                )
            except Exception as e:
                print(f"Auto-download error: {e}")
    
    def add_webhook(self, webhook: WebhookConfig):
        """Add a webhook configuration"""
        self.webhooks[webhook.name] = webhook
    
    def remove_webhook(self, name: str):
        """Remove a webhook"""
        if name in self.webhooks:
            del self.webhooks[name]
    
    def register_handler(self, event_type: WebhookEventType, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def start(self):
        """Start the webhook server"""
        if self.running:
            return
        
        self.running = True
        self.server_thread = threading.Thread(
            target=self.app.run,
            kwargs={'host': self.host, 'port': self.port, 'debug': False},
            daemon=True
        )
        self.server_thread.start()
        print(f"Webhook server started on http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the webhook server"""
        self.running = False
        # Flask doesn't have a clean shutdown, but thread will terminate on exit


class WebhookManager:
    """
    Manages webhook configurations and integrations
    """
    
    def __init__(self, user_auth, user_id: int):
        self.user_auth = user_auth
        self.user_id = user_id
        self.webhook_file = os.path.join(
            os.environ.get('APPDATA', os.path.expanduser('~')),
            'GitHubDownloader', 'webhooks.json'
        )
        self.webhooks: Dict[str, WebhookConfig] = self.load_webhooks()
        self.server = WebhookServer()
        
        # Register default handlers
        self._register_default_handlers()
    
    def load_webhooks(self) -> Dict[str, WebhookConfig]:
        """Load webhooks from file"""
        if os.path.exists(self.webhook_file):
            try:
                with open(self.webhook_file, 'r') as f:
                    data = json.load(f)
                    return {
                        name: WebhookConfig(**config) 
                        for name, config in data.items()
                    }
            except:
                return {}
        return {}
    
    def save_webhooks(self):
        """Save webhooks to file"""
        os.makedirs(os.path.dirname(self.webhook_file), exist_ok=True)
        with open(self.webhook_file, 'w') as f:
            json.dump({
                name: {
                    'name': w.name,
                    'repo_url': w.repo_url,
                    'events': [e.value for e in w.events],
                    'callback_url': w.callback_url,
                    'secret': w.secret,
                    'enabled': w.enabled,
                    'auto_download': w.auto_download,
                    'last_triggered': w.last_triggered.isoformat() if w.last_triggered else None,
                    'trigger_count': w.trigger_count
                }
                for name, w in self.webhooks.items()
            }, f, indent=2)
    
    def create_webhook(self, name: str, repo_url: str, events: List[str],
                       callback_url: str = "", secret: str = "",
                       auto_download: bool = False) -> WebhookConfig:
        """Create a new webhook configuration"""
        webhook = WebhookConfig(
            name=name,
            repo_url=repo_url,
            events=[WebhookEventType(e) for e in events],
            callback_url=callback_url,
            secret=secret,
            auto_download=auto_download
        )
        
        self.webhooks[name] = webhook
        self.save_webhooks()
        return webhook
    
    def get_webhook(self, name: str) -> Optional[WebhookConfig]:
        """Get a webhook by name"""
        return self.webhooks.get(name)
    
    def list_webhooks(self) -> List[WebhookConfig]:
        """List all webhooks"""
        return list(self.webhooks.values())
    
    def delete_webhook(self, name: str):
        """Delete a webhook"""
        if name in self.webhooks:
            del self.webhooks[name]
            self.save_webhooks()
    
    def toggle_webhook(self, name: str, enabled: bool):
        """Enable or disable a webhook"""
        if name in self.webhooks:
            self.webhooks[name].enabled = enabled
            self.save_webhooks()
    
    def generate_github_webhook_url(self, name: str, server_url: str) -> str:
        """Generate the webhook URL for GitHub"""
        webhook = self.get_webhook(name)
        if not webhook:
            return ""
        return f"{server_url}/webhook"
    
    def _register_default_handlers(self):
        """Register default event handlers"""
        self.server.register_handler(
            WebhookEventType.RELEASE,
            self._handle_release
        )
        self.server.register_handler(
            WebhookEventType.PUSH,
            self._handle_push
        )
    
    def _handle_release(self, payload: WebhookPayload, webhook: WebhookConfig):
        """Handle release events"""
        print(f"New release: {payload.repository.get('full_name')} - {payload.action}")
    
    def _handle_push(self, payload: WebhookPayload, webhook: WebhookConfig):
        """Handle push events"""
        print(f"New push: {payload.repository.get('full_name')} - {len(payload.commits)} commits")
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the webhook server"""
        self.server.host = host
        self.server.port = port
        self.server.start()
    
    def stop_server(self):
        """Stop the webhook server"""
        self.server.stop()


class DiscordNotifier:
    """
    Send notifications to Discord via webhooks
    """
    
    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url
    
    def send_notification(self, title: str, description: str, 
                          color: int = 0x5865F2, fields: List[Dict] = None):
        """Send a rich embed notification to Discord"""
        if not self.webhook_url:
            return False
        
        payload = {
            'embeds': [{
                'title': title,
                'description': description,
                'color': color,
                'fields': fields or [],
                'timestamp': datetime.now().isoformat()
            }]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 204
        except:
            return False
    
    def notify_download_complete(self, repo_name: str, status: str, 
                                 details: str = ""):
        """Notify download completion"""
        color = 0x57F287 if status == "success" else 0xED4245
        return self.send_notification(
            title=f"Download {status.title()}",
            description=f"Repository: {repo_name}",
            color=color,
            fields=[{'name': 'Details', 'value': details, 'inline': True}]
        )
    
    def notify_new_release(self, repo_name: str, release_name: str, 
                           tag: str, url: str):
        """Notify new release"""
        return self.send_notification(
            title=f"New Release: {release_name}",
            description=f"Repository: {repo_name}",
            color=0x5865F2,
            fields=[
                {'name': 'Tag', 'value': tag, 'inline': True},
                {'name': 'URL', 'value': url, 'inline': True}
            ]
        )


class SlackNotifier:
    """
    Send notifications to Slack via webhooks
    """
    
    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url
    
    def send_notification(self, text: str, blocks: List[Dict] = None):
        """Send notification to Slack"""
        if not self.webhook_url:
            return False
        
        payload = {
            'text': text,
            'blocks': blocks or []
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
        except:
            return False
    
    def notify_download_complete(self, repo_name: str, status: str):
        """Notify download completion"""
        emoji = ":white_check_mark:" if status == "success" else ":x:"
        return self.send_notification(
            f"{emoji} Download {status}: {repo_name}"
        )


class EmailNotifier:
    """
    Send email notifications
    """
    
    def __init__(self, smtp_config: Dict, from_email: str, to_email: str):
        self.smtp_config = smtp_config
        self.from_email = from_email
        self.to_email = to_email
    
    def send_notification(self, subject: str, body: str):
        """Send email notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = self.to_email
            
            with smtplib.SMTP(
                self.smtp_config.get('host', 'localhost'),
                self.smtp_config.get('port', 587)
            ) as server:
                if self.smtp_config.get('tls'):
                    server.starttls()
                if self.smtp_config.get('user'):
                    server.login(
                        self.smtp_config['user'],
                        self.smtp_config['password']
                    )
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email notification error: {e}")
            return False
    
    def notify_download_complete(self, repo_name: str, status: str):
        """Notify download completion"""
        subject = f"Download {status.title()}: {repo_name}"
        body = f"Repository: {repo_name}\nStatus: {status}\nTime: {datetime.now()}"
        return self.send_notification(subject, body)


class NotificationManager:
    """
    Unified notification manager with multiple channels
    """
    
    def __init__(self):
        self.channels = {
            'discord': None,
            'slack': None,
            'email': None,
            'system': True  # System tray notifications
        }
    
    def configure_discord(self, webhook_url: str):
        self.channels['discord'] = DiscordNotifier(webhook_url)
    
    def configure_slack(self, webhook_url: str):
        self.channels['slack'] = SlackNotifier(webhook_url)
    
    def configure_email(self, smtp_config: Dict, from_email: str, to_email: str):
        self.channels['email'] = EmailNotifier(smtp_config, from_email, to_email)
    
    def notify_download_complete(self, repo_name: str, status: str, details: str = ""):
        """Notify via all configured channels"""
        for channel in self.channels.values():
            if channel:
                if hasattr(channel, 'notify_download_complete'):
                    channel.notify_download_complete(repo_name, status)
                elif hasattr(channel, 'send_notification'):
                    channel.send_notification(
                        f"Download {status}: {repo_name}",
                        details
                    )
    
    def notify_new_release(self, repo_name: str, release_name: str, tag: str, url: str):
        """Notify new release via all channels"""
        for channel in self.channels.values():
            if channel and hasattr(channel, 'notify_new_release'):
                channel.notify_new_release(repo_name, release_name, tag, url)


# Example plugin that uses webhooks
class UpdateCheckerPlugin:
    """
    Plugin that checks for repository updates and notifies
    """
    
    def __init__(self, webhook_manager: WebhookManager, 
                 notification_manager: NotificationManager):
        self.webhook_manager = webhook_manager
        self.notification_manager = notification_manager
        self.tracked_repos: Dict[str, Dict] = {}
    
    def track_repository(self, repo_url: str, notify_on: List[str] = None):
        """Start tracking a repository"""
        if notify_on is None:
            notify_on = ['release', 'push']
        
        self.tracked_repos[repo_url] = {
            'notify_on': notify_on,
            'last_check': datetime.now(),
            'last_release': None,
            'last_commit': None
        }
        
        # Create webhook
        self.webhook_manager.create_webhook(
            name=f"tracker_{repo_url.split('/')[-1]}",
            repo_url=repo_url,
            events=notify_on,
            auto_download=False
        )
    
    def untrack_repository(self, repo_url: str):
        """Stop tracking a repository"""
        if repo_url in self.tracked_repos:
            del self.tracked_repos[repo_url]
            
            # Remove webhook
            name = f"tracker_{repo_url.split('/')[-1]}"
            self.webhook_manager.delete_webhook(name)
    
    def check_for_updates(self, repo_url: str) -> Dict:
        """Manually check for updates"""
        # This would call the GitHub API to check for updates
        return {
            'has_update': False,
            'latest_release': None,
            'latest_commit': None
        }
