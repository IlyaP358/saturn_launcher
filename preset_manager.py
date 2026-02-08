import os
import hashlib
import py7zr
import shutil
import json
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# ================================
# CONSTANTS
# ================================

BASE_DIR = "saturn_launcher"
PRESETS_DIR_NAME = "saturn_presets"
CONFIG_FILE = "config.json"

# ================================
# HASH FUNCTIONS
# ================================

def file_hash(path):
    """Calculate SHA256 hash of a file"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def generate_hashes(folder):
    """Generate hash dictionary for all files in a folder"""
    hashes = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, folder)
            hashes[relative_path] = file_hash(full_path)
    return hashes

# ================================
# INITIALIZATION
# ================================

def init_presets_directory():
    """Initialize presets directory structure"""
    presets_path = get_presets_dir()
    if not os.path.exists(presets_path):
        os.makedirs(presets_path)
        print(f"[green]Created presets directory: {presets_path}[/green]")

def get_presets_dir():
    """Get absolute path to presets directory"""
    return os.path.abspath(os.path.join(BASE_DIR, PRESETS_DIR_NAME))

def get_base_dir():
    """Get absolute path to base saturn_launcher directory"""
    return os.path.abspath(BASE_DIR)

# ================================
# PRESET OPERATIONS
# ================================

def list_presets():
    """List all available presets (directories and archives)"""
    presets = []
    presets_path = get_presets_dir()
    
    # Add default preset (the base saturn_launcher directory)
    presets.append({
        'name': 'default',
        'type': 'directory',
        'path': get_base_dir(),
        'compressed': False
    })
    
    # List presets in saturn_presets directory
    if os.path.exists(presets_path):
        for item in os.listdir(presets_path):
            item_path = os.path.join(presets_path, item)
            
            if os.path.isdir(item_path):
                presets.append({
                    'name': item,
                    'type': 'directory',
                    'path': item_path,
                    'compressed': False
                })
            elif item.endswith('.7z'):
                preset_name = item[:-3]  # Remove .7z extension
                presets.append({
                    'name': preset_name,
                    'type': 'archive',
                    'path': item_path,
                    'compressed': True
                })
    
    return presets

def get_preset_path(name):
    """Get full path to a preset directory"""
    if name == 'default':
        return get_base_dir()
    else:
        return os.path.join(get_presets_dir(), name)

def preset_exists(name):
    """Check if a preset exists (as directory or archive)"""
    presets = list_presets()
    return any(p['name'] == name for p in presets)

def is_preset_compressed(name):
    """Check if preset exists as compressed archive"""
    presets = list_presets()
    for preset in presets:
        if preset['name'] == name:
            return preset['compressed']
    return False

def resolve_duplicate_name(name):
    """Add (1), (2), etc. to duplicate names"""
    if not preset_exists(name):
        return name
    
    counter = 1
    while True:
        new_name = f"{name} ({counter})"
        if not preset_exists(new_name):
            return new_name
        counter += 1

def create_preset(name):
    """Create a new preset directory"""
    # Resolve duplicate names
    final_name = resolve_duplicate_name(name)
    
    preset_path = get_preset_path(final_name)
    
    if not os.path.exists(preset_path):
        os.makedirs(preset_path)
        print(f"[green]Created preset: {final_name}[/green]")
        return final_name
    else:
        print(f"[yellow]Preset already exists: {final_name}[/yellow]")
        return final_name

def switch_preset(name):
    """Switch active preset"""
    # Check if preset exists
    if not preset_exists(name):
        # Create new preset if it doesn't exist
        print(f"[yellow]Preset '{name}' does not exist. Creating new preset...[/yellow]")
        name = create_preset(name)
    
    # Check if preset is compressed
    if is_preset_compressed(name):
        print(f"[red]Preset '{name}' is compressed. Please decompress it first with: saturn presets --unzip \"{name}\"[/red]")
        return False
    
    # Update config
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        config['active_preset'] = name
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"[green]Switched to preset: {name}[/green]")
        return True
    except Exception as e:
        print(f"[red]Error switching preset: {e}[/red]")
        return False

def get_active_preset():
    """Get currently active preset name"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return config.get('active_preset', 'default')
        else:
            return 'default'
    except Exception as e:
        print(f"[yellow]Error reading config: {e}. Using default preset.[/yellow]")
        return 'default'

def delete_preset(name):
    """Delete a preset (directory or archive)"""
    if name == 'default':
        print("[red]Cannot delete the default preset![/red]")
        return False
    
    if not preset_exists(name):
        print(f"[red]Preset '{name}' does not exist[/red]")
        return False
    
    # Check if this is the active preset
    active = get_active_preset()
    if active == name:
        print(f"[red]Cannot delete active preset. Switch to another preset first.[/red]")
        return False
    
    # Find the preset
    presets = list_presets()
    preset_to_delete = None
    for preset in presets:
        if preset['name'] == name:
            preset_to_delete = preset
            break
    
    if not preset_to_delete:
        print(f"[red]Preset '{name}' not found[/red]")
        return False
    
    # Confirm deletion
    preset_type = "archive" if preset_to_delete['compressed'] else "directory"
    confirm = input(f"Are you sure you want to delete preset '{name}' ({preset_type})? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("[yellow]Deletion cancelled[/yellow]")
        return False
    
    try:
        if preset_to_delete['compressed']:
            # Delete archive file
            os.remove(preset_to_delete['path'])
            print(f"[green]Deleted preset archive: {name}[/green]")
        else:
            # Delete directory
            shutil.rmtree(preset_to_delete['path'])
            print(f"[green]Deleted preset directory: {name}[/green]")
        return True
    except Exception as e:
        print(f"[red]Error deleting preset: {e}[/red]")
        return False

# ================================
# COMPRESSION FUNCTIONS
# ================================

def compress_preset(name):
    """Compress a preset to .7z archive with hash verification"""
    if name == 'default':
        print("[red]Cannot compress the default preset![/red]")
        return False
    
    if not preset_exists(name):
        print(f"[red]Preset '{name}' does not exist[/red]")
        return False
    
    if is_preset_compressed(name):
        print(f"[yellow]Preset '{name}' is already compressed[/yellow]")
        return False
    
    preset_path = get_preset_path(name)
    archive_path = preset_path + '.7z'
    
    # Check if directory is empty
    if not os.listdir(preset_path):
        print(f"[yellow]Preset '{name}' is empty. Skipping compression.[/yellow]")
        return False
    
    try:
        print(f"[cyan]Generating hashes for verification...[/cyan]")
        original_hashes = generate_hashes(preset_path)
        
        print(f"[cyan]Compressing preset '{name}'...[/cyan]")
        with py7zr.SevenZipFile(archive_path, 'w') as archive:
            archive.writeall(preset_path, arcname=name)
        
        print(f"[green]Compression complete![/green]")
        
        # Verify archive integrity
        print(f"[cyan]Verifying archive integrity...[/cyan]")
        if verify_archive_integrity(archive_path, original_hashes, name):
            print(f"[green]✓ Archive integrity verified![/green]")
            
            # Delete original directory
            print(f"[cyan]Removing original directory...[/cyan]")
            shutil.rmtree(preset_path)
            print(f"[green]✓ Preset '{name}' compressed successfully![/green]")
            return True
        else:
            print(f"[red]✗ Archive verification failed! Keeping original directory.[/red]")
            os.remove(archive_path)
            return False
            
    except Exception as e:
        print(f"[red]Error compressing preset: {e}[/red]")
        if os.path.exists(archive_path):
            os.remove(archive_path)
        return False

def decompress_preset(name):
    """Decompress a .7z archive and verify integrity"""
    if not preset_exists(name):
        print(f"[red]Preset '{name}' does not exist[/red]")
        return False
    
    if not is_preset_compressed(name):
        print(f"[yellow]Preset '{name}' is not compressed[/yellow]")
        return False
    
    presets_path = get_presets_dir()
    archive_path = os.path.join(presets_path, name + '.7z')
    extract_path = os.path.join(presets_path, name)
    
    try:
        print(f"[cyan]Decompressing preset '{name}'...[/cyan]")
        
        # Extract archive
        with py7zr.SevenZipFile(archive_path, 'r') as archive:
            archive.extractall(path=presets_path)
        
        print(f"[green]Decompression complete![/green]")
        
        # Delete archive
        print(f"[cyan]Removing archive...[/cyan]")
        os.remove(archive_path)
        print(f"[green]✓ Preset '{name}' decompressed successfully![/green]")
        return True
        
    except Exception as e:
        print(f"[red]Error decompressing preset: {e}[/red]")
        # Clean up partial extraction
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        return False

def verify_archive_integrity(archive_path, original_hashes, arcname):
    """Verify that archive contents match original hashes"""
    try:
        temp_extract = archive_path + '_verify_temp'
        
        # Extract to temporary location
        with py7zr.SevenZipFile(archive_path, 'r') as archive:
            archive.extractall(path=temp_extract)
        
        # Generate hashes of extracted files
        extracted_folder = os.path.join(temp_extract, arcname)
        extracted_hashes = generate_hashes(extracted_folder)
        
        # Compare hashes
        if original_hashes == extracted_hashes:
            verified = True
        else:
            verified = False
            print(f"[red]Hash mismatch detected![/red]")
        
        # Clean up temp directory
        shutil.rmtree(temp_extract)
        
        return verified
        
    except Exception as e:
        print(f"[red]Verification error: {e}[/red]")
        if os.path.exists(temp_extract):
            shutil.rmtree(temp_extract)
        return False
