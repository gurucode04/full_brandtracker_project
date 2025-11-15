import os
from pathlib import Path
from django.conf import settings

def get_built_assets():
    """Find the latest built React assets"""
    static_dir = Path(settings.BASE_DIR) / 'tracker' / 'static' / 'tracker'
    assets_dir = static_dir / 'assets'
    
    if not assets_dir.exists():
        return None, None
    
    css_file = None
    js_file = None
    
    for file in assets_dir.iterdir():
        if file.suffix == '.css' and 'index' in file.name:
            css_file = f'tracker/assets/{file.name}'
        elif file.suffix == '.js' and 'index' in file.name:
            js_file = f'tracker/assets/{file.name}'
    
    return css_file, js_file

