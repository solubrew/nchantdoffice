"""
Images Document Module for Nchantd Office

Provides image document functionality following the Nchantd patterns.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import base64
import io
from PIL import Image as PILImage


class ImageDocument:
    """
    Image document for storing and manipulating image data.
    
    This class follows the Nchantd pattern for document management,
    providing a consistent interface for image operations.
    """
    
    def __init__(
        self,
        file_path: Optional[str] = None,
        content: Optional[bytes] = None,
        format: str = 'PNG',
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an ImageDocument.
        
        Args:
            file_path: Path to an image file
            content: Raw image bytes
            format: Image format (PNG, JPEG, GIF, etc.)
            metadata: Additional metadata for the image
        """
        self.file_path = file_path
        self.format = format
        self.metadata = metadata or {}
        self._image: Optional[PILImage.Image] = None
        
        if content:
            self._load_from_bytes(content)
        elif file_path:
            self._load_from_file(file_path)
    
    def _load_from_file(self, file_path: str) -> None:
        """Load image from file path."""
        self._image = PILImage.open(file_path)
        self.file_path = file_path
        self.format = self._image.format or self.format
        self.metadata['size'] = self._image.size
        self.metadata['mode'] = self._image.mode
    
    def _load_from_bytes(self, content: bytes) -> None:
        """Load image from bytes."""
        self._image = PILImage.open(io.BytesIO(content))
        self.metadata['size'] = self._image.size
        self.metadata['mode'] = self._image.mode
    
    @property
    def image(self) -> Optional[PILImage.Image]:
        """Get the PIL Image object."""
        return self._image
    
    @property
    def size(self) -> Optional[tuple]:
        """Get image dimensions (width, height)."""
        if self._image:
            return self._image.size
        return None
    
    @property
    def mode(self) -> Optional[str]:
        """Get image mode (RGB, RGBA, L, etc.)."""
        if self._image:
            return self._image.mode
        return None
    
    def resize(self, width: int, height: int, resample: int = PILImage.LANCZOS) -> 'ImageDocument':
        """
        Resize the image to new dimensions.
        
        Args:
            width: New width
            height: New height
            resample: Resampling filter
            
        Returns:
            Self for chaining
        """
        if self._image:
            self._image = self._image.resize((width, height), resample)
        return self
    
    def crop(self, box: tuple) -> 'ImageDocument':
        """
        Crop the image.
        
        Args:
            box: (left, top, right, bottom) tuple
            
        Returns:
            Self for chaining
        """
        if self._image:
            self._image = self._image.crop(box)
        return self
    
    def convert(self, mode: str) -> 'ImageDocument':
        """
        Convert image color mode.
        
        Args:
            mode: Target mode (RGB, RGBA, L, etc.)
            
        Returns:
            Self for chaining
        """
        if self._image:
            self._image = self._image.convert(mode)
        return self
    
    def save(self, file_path: Optional[str] = None, format: Optional[str] = None) -> bytes:
        """
        Save image to file or return bytes.
        
        Args:
            file_path: Optional path to save to
            format: Optional format override
            
        Returns:
            Image bytes if not saving to file
        """
        if not self._image:
            raise ValueError("No image loaded")
        
        save_format = format or self.format
        
        if file_path:
            self._image.save(file_path, format=save_format)
            return b''
        else:
            buffer = io.BytesIO()
            self._image.save(buffer, format=save_format)
            return buffer.getvalue()
    
    def to_base64(self, format: Optional[str] = None) -> str:
        """
        Convert image to base64 string.
        
        Args:
            format: Optional format override
            
        Returns:
            Base64 encoded string
        """
        if not self._image:
            raise ValueError("No image loaded")
        
        save_format = format or self.format
        buffer = io.BytesIO()
        self._image.save(buffer, format=save_format)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    @classmethod
    def from_base64(cls, b64_string: str, format: str = 'PNG') -> 'ImageDocument':
        """
        Create ImageDocument from base64 string.
        
        Args:
            b64_string: Base64 encoded image data
            format: Image format
            
        Returns:
            New ImageDocument instance
        """
        content = base64.b64decode(b64_string)
        return cls(content=content, format=format)
    
    def get_thumbnail(self, size: tuple = (128, 128)) -> 'ImageDocument':
        """
        Create a thumbnail copy of the image.
        
        Args:
            size: Thumbnail size
            
        Returns:
            New ImageDocument with thumbnail
        """
        if not self._image:
            raise ValueError("No image loaded")
        
        thumb = self._image.copy()
        thumb.thumbnail(size)
        
        new_doc = ImageDocument(format=self.format, metadata=self.metadata.copy())
        new_doc._image = thumb
        return new_doc
    
    def rotate(self, angle: float, expand: bool = True) -> 'ImageDocument':
        """
        Rotate the image.
        
        Args:
            angle: Rotation angle in degrees
            expand: Whether to expand canvas to fit rotated image
            
        Returns:
            Self for chaining
        """
        if self._image:
            self._image = self._image.rotate(angle, expand=expand)
        return self
    
    def flip(self, direction: str = 'horizontal') -> 'ImageDocument':
        """
        Flip the image.
        
        Args:
            direction: 'horizontal' or 'vertical'
            
        Returns:
            Self for chaining
        """
        if self._image:
            if direction == 'horizontal':
                self._image = self._image.transpose(PILImage.FLIP_LEFT_RIGHT)
            else:
                self._image = self._image.transpose(PILImage.FLIP_TOP_BOTTOM)
        return self
    
    def apply_filter(self, filter_name: str) -> 'ImageDocument':
        """
        Apply an image filter.
        
        Args:
            filter_name: Name of filter (BLUR, SHARPEN, etc.)
            
        Returns:
            Self for chaining
        """
        from PIL import ImageFilter, ImageEnhance
        
        if not self._image:
            raise ValueError("No image loaded")
        
        filters = {
            'BLUR': ImageFilter.BLUR,
            'SHARPEN': ImageFilter.SHARPEN,
            'SMOOTH': ImageFilter.SMOOTH,
            'EDGE_ENHANCE': ImageFilter.EDGE_ENHANCE,
        }
        
        if filter_name in filters:
            self._image = self._image.filter(filters[filter_name])
        return self
    
    def adjust_brightness(self, factor: float) -> 'ImageDocument':
        """
        Adjust image brightness.
        
        Args:
            factor: Brightness factor (1.0 = original)
            
        Returns:
            Self for chaining
        """
        if not self._image:
            raise ValueError("No image loaded")
        
        enhancer = ImageEnhance.Brightness(self._image)
        self._image = enhancer.enhance(factor)
        return self
    
    def adjust_contrast(self, factor: float) -> 'ImageDocument':
        """
        Adjust image contrast.
        
        Args:
            factor: Contrast factor (1.0 = original)
            
        Returns:
            Self for chaining
        """
        if not self._image:
            raise ValueError("No image loaded")
        
        enhancer = ImageEnhance.Contrast(self._image)
        self._image = enhancer.enhance(factor)
        return self
    
    def __repr__(self) -> str:
        return f"ImageDocument(path={self.file_path}, format={self.format}, size={self.size})"


def create_image_document(
    file_path: Optional[str] = None,
    content: Optional[bytes] = None,
    format: str = 'PNG'
) -> ImageDocument:
    """
    Factory function to create an ImageDocument.
    
    Args:
        file_path: Path to image file
        content: Raw image bytes
        format: Image format
        
    Returns:
        ImageDocument instance
    """
    return ImageDocument(file_path=file_path, content=content, format=format)


__all__ = ['ImageDocument', 'create_image_document']
