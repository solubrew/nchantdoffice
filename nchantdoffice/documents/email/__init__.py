"""Email Document Module for nchantdoffice.

Provides email document handling functionality including
message composition, sending, receiving, and management.

Classes:
    EmailDocument: Core email document class
    EmailMessage: Individual email message representation
    EmailFolder: Email folder organization
    EmailAccount: Email account configuration
    EmailClient: Email client operations
    EmailTemplate: Reusable email templates

Author: nchantdoffice
Version: 1.0.0
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import re


class EmailPriority(Enum):
    """Email priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailStatus(Enum):
    """Email status states."""
    DRAFT = "draft"
    SENT = "sent"
    RECEIVED = "received"
    READ = "read"
    UNREAD = "unread"
    REPLIED = "replied"
    FORWARDED = "forwarded"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class Attachment:
    """Email attachment representation."""
    filename: str
    content_type: str
    size: int
    data: bytes = field(default=b"")
    content_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert attachment to dictionary."""
        return {
            "filename": self.filename,
            "content_type": self.content_type,
            "size": self.size,
            "content_id": self.content_id
        }


@dataclass
class EmailHeader:
    """Email header information."""
    message_id: str
    in_reply_to: Optional[str] = None
    references: List[str] = field(default_factory=list)
    date: datetime = field(default_factory=datetime.now)
    subject: str = ""
    from_address: str = ""
    to_addresses: List[str] = field(default_factory=list)
    cc_addresses: List[str] = field(default_factory=list)
    bcc_addresses: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert header to dictionary."""
        return {
            "message_id": self.message_id,
            "in_reply_to": self.in_reply_to,
            "references": self.references,
            "date": self.date.isoformat(),
            "subject": self.subject,
            "from": self.from_address,
            "to": self.to_addresses,
            "cc": self.cc_addresses,
            "bcc": self.bcc_addresses
        }


@dataclass
class EmailMessage:
    """Individual email message representation."""
    header: EmailHeader
    body: str = ""
    html_body: Optional[str] = None
    attachments: List[Attachment] = field(default_factory=list)
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.DRAFT
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "header": self.header.to_dict(),
            "body": self.body,
            "html_body": self.html_body,
            "attachments": [a.to_dict() for a in self.attachments],
            "priority": self.priority.value,
            "status": self.status.value,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat()
        }
    
    def add_attachment(self, attachment: Attachment) -> None:
        """Add an attachment to the message."""
        self.attachments.append(attachment)
        self.modified_at = datetime.now()
    
    def remove_attachment(self, filename: str) -> bool:
        """Remove an attachment by filename."""
        for i, att in enumerate(self.attachments):
            if att.filename == filename:
                self.attachments.pop(i)
                self.modified_at = datetime.now()
                return True
        return False


@dataclass
class EmailFolder:
    """Email folder organization."""
    name: str
    path: str
    messages: List[EmailMessage] = field(default_factory=list)
    subfolders: List['EmailFolder'] = field(default_factory=list)
    
    @property
    def message_count(self) -> int:
        """Get total message count including subfolders."""
        count = len(self.messages)
        for subfolder in self.subfolders:
            count += subfolder.message_count
        return count
    
    def add_message(self, message: EmailMessage) -> None:
        """Add a message to the folder."""
        self.messages.append(message)
    
    def get_messages(self, 
                     status: Optional[EmailStatus] = None,
                     priority: Optional[EmailPriority] = None,
                     tag: Optional[str] = None) -> List[EmailMessage]:
        """Get messages with optional filtering."""
        results = []
        for msg in self.messages:
            if status and msg.status != status:
                continue
            if priority and msg.priority != priority:
                continue
            if tag and tag not in msg.tags:
                continue
            results.append(msg)
        return results


class EmailDocument:
    """Core email document class for nchantdoffice.
    
    Provides email composition, sending, receiving, and management
    functionality with support for multiple accounts and folders.
    
    Example:
        >>> doc = EmailDocument()
        >>> doc.create_account("work@example.com", "smtp.example.com")
        >>> message = doc.compose(to="colleague@example.com", 
        ...                       subject="Meeting",
        ...                       body="Let's meet tomorrow")
        >>> doc.send(message)
    """
    
    DEFAULT_FOLDERS = ["inbox", "sent", "drafts", "trash", "archive"]
    
    def __init__(self):
        """Initialize the email document."""
        self.accounts: Dict[str, 'EmailAccount'] = {}
        self.folders: Dict[str, EmailFolder] = {}
        self.templates: Dict[str, 'EmailTemplate'] = {}
        self._initialize_default_folders()
    
    def _initialize_default_folders(self) -> None:
        """Initialize default email folders."""
        for folder_name in self.DEFAULT_FOLDERS:
            self.folders[folder_name] = EmailFolder(
                name=folder_name,
                path=f"/{folder_name}"
            )
    
    def create_account(self, 
                       email: str,
                       smtp_server: str,
                       imap_server: Optional[str] = None,
                       username: Optional[str] = None,
                       password: Optional[str] = None) -> 'EmailAccount':
        """Create a new email account.
        
        Args:
            email: Email address for the account
            smtp_server: SMTP server hostname
            imap_server: IMAP server hostname (defaults to smtp_server)
            username: Username for authentication (defaults to email)
            password: Password for authentication
            
        Returns:
            The created EmailAccount instance
        """
        if not username:
            username = email
            
        account = EmailAccount(
            email=email,
            smtp_server=smtp_server,
            imap_server=imap_server or smtp_server,
            username=username,
            password=password
        )
        self.accounts[email] = account
        return account
    
    def get_account(self, email: str) -> Optional['EmailAccount']:
        """Get an account by email address."""
        return self.accounts.get(email)
    
    def compose(self,
                to: Union[str, List[str]],
                subject: str = "",
                body: str = "",
                html_body: Optional[str] = None,
                cc: Optional[Union[str, List[str]]] = None,
                bcc: Optional[Union[str, List[str]]] = None,
                priority: EmailPriority = EmailPriority.NORMAL,
                account: Optional[str] = None) -> EmailMessage:
        """Compose a new email message.
        
        Args:
            to: Recipient email address(es)
            subject: Email subject line
            body: Plain text body
            html_body: HTML body content
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            priority: Message priority
            account: Account to use (defaults to first account)
            
        Returns:
            The composed EmailMessage
        """
        if isinstance(to, str):
            to = [to]
        if isinstance(cc, str):
            cc = [cc]
        if isinstance(bcc, str):
            bcc = [bcc]
            
        from_addr = account or (list(self.accounts.keys())[0] if self.accounts else "")
        
        header = EmailHeader(
            message_id=self._generate_message_id(from_addr),
            date=datetime.now(),
            subject=subject,
            from_address=from_addr,
            to_addresses=to,
            cc_addresses=cc or [],
            bcc_addresses=bcc or []
        )
        
        message = EmailMessage(
            header=header,
            body=body,
            html_body=html_body,
            priority=priority,
            status=EmailStatus.DRAFT
        )
        
        return message
    
    def _generate_message_id(self, domain: str) -> str:
        """Generate a unique message ID."""
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"<{timestamp}.{unique_id}@{domain}>"
    
    def send(self, message: EmailMessage, account: Optional[str] = None) -> bool:
        """Send an email message.
        
        Args:
            message: The message to send
            account: Account to use (defaults to message sender)
            
        Returns:
            True if sent successfully, False otherwise
        """
        sender = account or message.header.from_address
        acc = self.get_account(sender)
        
        if not acc:
            return False
        
        # Placeholder for actual SMTP sending logic
        message.status = EmailStatus.SENT
        
        # Add to sent folder
        if "sent" in self.folders:
            self.folders["sent"].add_message(message)
        
        return True
    
    def save_draft(self, message: EmailMessage) -> None:
        """Save a message as a draft."""
        message.status = EmailStatus.DRAFT
        if "drafts" in self.folders:
            self.folders["drafts"].add_message(message)
    
    def get_inbox(self) -> EmailFolder:
        """Get the inbox folder."""
        return self.folders.get("inbox", EmailFolder(name="inbox", path="/inbox"))
    
    def get_folder(self, name: str) -> Optional[EmailFolder]:
        """Get a folder by name."""
        return self.folders.get(name.lower())
    
    def create_template(self,
                        name: str,
                        subject: str,
                        body: str,
                        html_body: Optional[str] = None) -> 'EmailTemplate':
        """Create a reusable email template."""
        template = EmailTemplate(
            name=name,
            subject=subject,
            body=body,
            html_body=html_body
        )
        self.templates[name] = template
        return template
    
    def create_from_template(self, 
                             template_name: str,
                             replacements: Dict[str, str]) -> Optional[EmailMessage]:
        """Create a message from a template with variable replacements."""
        template = self.templates.get(template_name)
        if not template:
            return None
        
        subject = template.subject
        body = template.body
        
        for key, value in replacements.items():
            placeholder = f"{{{key}}}"
            subject = subject.replace(placeholder, value)
            body = body.replace(placeholder, value)
        
        return self.compose(subject=subject, body=body)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "accounts": {k: v.to_dict() for k, v in self.accounts.items()},
            "folders": {k: {"name": v.name, "path": v.path, "count": v.message_count}
                       for k, v in self.folders.items()},
            "templates": {k: v.to_dict() for k, v in self.templates.items()}
        }
    
    def to_json(self) -> str:
        """Convert document to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailDocument':
        """Create document from dictionary."""
        doc = cls()
        # Reconstruct accounts, folders, templates as needed
        return doc


@dataclass
class EmailAccount:
    """Email account configuration."""
    email: str
    smtp_server: str
    imap_server: str
    username: str
    password: Optional[str] = None
    smtp_port: int = 587
    imap_port: int = 993
    use_tls: bool = True
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert account to dictionary."""
        return {
            "email": self.email,
            "smtp_server": self.smtp_server,
            "imap_server": self.imap_server,
            "username": self.username,
            "smtp_port": self.smtp_port,
            "imap_port": self.imap_port,
            "use_tls": self.use_tls,
            "signature": self.signature
        }


@dataclass
class EmailTemplate:
    """Reusable email template."""
    name: str
    subject: str
    body: str
    html_body: Optional[str] = None
    variables: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "subject": self.subject,
            "body": self.body,
            "html_body": self.html_body,
            "variables": self.variables
        }


def create_email_document() -> EmailDocument:
    """Factory function to create a new email document."""
    return EmailDocument()


# Export public API
__all__ = [
    'EmailDocument',
    'EmailMessage', 
    'EmailFolder',
    'EmailAccount',
    'EmailTemplate',
    'EmailHeader',
    'Attachment',
    'EmailPriority',
    'EmailStatus',
    'create_email_document'
]
