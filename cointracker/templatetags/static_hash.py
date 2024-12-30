import os
import hashlib
from django import template
from django.conf import settings
from django.contrib.staticfiles.finders import find

register = template.Library()


@register.simple_tag
def static_hash(path):
    """
    Returns a path with a content hash appended as a query parameter.
    This ensures browser cache is busted when file content changes.
    """
    try:
        # Use Django's static file finder to locate the file
        absolute_path = find(path)
        if absolute_path:
            with open(absolute_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:8]
            return f"{path}?v={file_hash}"
        return path
    except Exception:
        return path
