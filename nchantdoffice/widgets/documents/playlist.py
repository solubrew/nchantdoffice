"""PyfficePlaylist document implementation for NchantdOffice."""

from typing import Dict, List, Any, Optional
from pyffice.documents import PyfficePlaylist as BasePyfficePlaylist
from nchantrs.logging import logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma.off(__name__)


class NchantdOfficePlaylist(NchantdOfficeDocument, BasePyfficePlaylist):
    """Playlist document - implements PyfficePlaylist.
    
    Provides playlist management for media files with
    ordering, shuffling, and export capabilities.
    """
    
    PYTYPE = 'playlist'
    DEFAULT_TOOLS = [
        {'id': 'add_media', 'icon': 'plus', 'label': 'Add Media', 'method': 'add_media'},
        {'id': 'remove_media', 'icon': 'minus', 'label': 'Remove', 'method': 'remove_media'},
        {'id': 'reorder', 'icon': 'arrows', 'label': 'Reorder', 'method': 'reorder_items'},
        {'id': 'shuffle', 'icon': 'shuffle', 'label': 'Shuffle', 'method': 'shuffle_playlist'},
        {'id': 'sort', 'icon': 'sort', 'label': 'Sort', 'method': 'sort_playlist'},
        {'id': 'play', 'icon': 'play', 'label': 'Play', 'method': 'play_playlist'},
        {'id': 'export_m3u', 'icon': 'file-audio', 'label': 'Export M3U', 'method': 'export_m3u'},
        {'id': 'export_xspf', 'icon': 'file-code', 'label': 'Export XSPF', 'method': 'export_xspf'},
        {'id': 'import_m3u', 'icon': 'download', 'label': 'Import M3U', 'method': 'import_m3u'},
        {'id': 'duplicate', 'icon': 'copy', 'label': 'Duplicate', 'method': 'duplicate'},
    ]
    
    @classmethod
    def get_pyffice_tools(cls) -> List[Dict[str, Any]]:
        """Return toolbox tools for playlist document."""
        return cls.DEFAULT_TOOLS
    
    def add_media(self, filepath: str, title: str = None, artist: str = None) -> Optional[str]:
        """Add media file to playlist."""
        try:
            media_id = f"media_{len(self._items)}"
            self._items[media_id] = {
                'filepath': filepath,
                'title': title or filepath.split('/')[-1],
                'artist': artist,
                'duration': self._get_duration(filepath),
                'order': len(self._items),
            }
            return media_id
        except Exception as e:
            logma.error(f"Failed to add media: {e}")
            return None
    
    def remove_media(self, media_id: str) -> bool:
        """Remove media from playlist."""
        try:
            if media_id in self._items:
                del self._items[media_id]
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to remove media: {e}")
            return False
    
    def reorder_items(self, media_id: str, new_position: int) -> bool:
        """Reorder media in playlist."""
        try:
            items = list(self._items.items())
            for i, (mid, item) in enumerate(items):
                if mid == media_id:
                    items.pop(i)
                    items.insert(new_position, (mid, item))
                    break
            # Update order values
            for i, (mid, item) in enumerate(items):
                item['order'] = i
            self._items = dict(items)
            return True
        except Exception as e:
            logma.error(f"Failed to reorder: {e}")
            return False
    
    def shuffle_playlist(self) -> bool:
        """Shuffle playlist order."""
        try:
            import random
            items = list(self._items.values())
            random.shuffle(items)
            for i, item in enumerate(items):
                item['order'] = i
            self._items = {f"media_{i}": item for i, item in enumerate(items)}
            return True
        except Exception as e:
            logma.error(f"Failed to shuffle: {e}")
            return False
    
    def sort_playlist(self, key: str = 'title') -> bool:
        """Sort playlist by key (title, artist, duration)."""
        try:
            items = list(self._items.values())
            items.sort(key=lambda x: x.get(key, ''))
            for i, item in enumerate(items):
                item['order'] = i
            self._items = {f"media_{i}": item for i, item in enumerate(items)}
            return True
        except Exception as e:
            logma.error(f"Failed to sort: {e}")
            return False
    
    def play_playlist(self, start_index: int = 0) -> bool:
        """Start playing playlist from index."""
        try:
            self._current_index = start_index
            logma.info(f"Playing playlist from index {start_index}")
            return True
        except Exception as e:
            logma.error(f"Failed to play: {e}")
            return False
    
    def export_m3u(self, filepath: str) -> bool:
        """Export playlist as M3U file."""
        try:
            with open(filepath, 'w') as f:
                f.write("#EXTM3U\n")
                for item in self._items.values():
                    f.write(f"#EXTINF:{item.get('duration', 0)},{item.get('artist', '')} - {item.get('title', '')}\n")
                    f.write(f"{item['filepath']}\n")
            return True
        except Exception as e:
            logma.error(f"Failed to export M3U: {e}")
            return False
    
    def export_xspf(self, filepath: str) -> bool:
        """Export playlist as XSPF file."""
        try:
            import xml.etree.ElementTree as ET
            root = ET.Element('playlist')
            root.set('version', '1')
            tracklist = ET.SubElement(root, 'trackList')
            for item in self._items.values():
                track = ET.SubElement(tracklist, 'track')
                ET.SubElement(track, 'location').text = item['filepath']
                ET.SubElement(track, 'title').text = item.get('title', '')
                ET.SubElement(track, 'creator').text = item.get('artist', '')
            tree = ET.ElementTree(root)
            tree.write(filepath, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            logma.error(f"Failed to export XSPF: {e}")
            return False
    
    def import_m3u(self, filepath: str) -> bool:
        """Import playlist from M3U file."""
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            current_title = None
            current_artist = None
            current_duration = 0
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    # Parse EXTINF line
                    parts = line[8:].split(',', 1)
                    if len(parts) == 2:
                        duration_info = parts[0].split(':')
                        if len(duration_info) > 1:
                            current_duration = int(duration_info[1])
                        artist_title = parts[1].split(' - ', 1)
                        if len(artist_title) == 2:
                            current_artist, current_title = artist_title
                        else:
                            current_title = artist_title[0]
                elif line and not line.startswith('#'):
                    self.add_media(line, current_title, current_artist)
            return True
        except Exception as e:
            logma.error(f"Failed to import M3U: {e}")
            return False
    
    def duplicate(self) -> 'NchantdOfficePlaylist':
        """Create a copy of this playlist."""
        try:
            new_playlist = self.__class__()
            new_playlist._items = {k: v.copy() for k, v in self._items.items()}
            return new_playlist
        except Exception as e:
            logma.error(f"Failed to duplicate: {e}")
            return None
    
    def _get_duration(self, filepath: str) -> int:
        """Get media file duration in seconds."""
        # Placeholder - would use media library to get actual duration
        return 0
