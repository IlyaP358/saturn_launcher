import minecraft_launcher_lib
import subprocess
import uuid
import pyfiglet
import os
import sys
import json
import psutil
import requests
import shlex
from rich import print
from rich.console import Console
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, track, BarColumn
from rich.table import Table
from image_ascii import get_logo_lines
import preset_manager

#remember commands history
try:
    import readline
except ImportError:
    import pyreadline3
try:
    console = Console()

# Get logo lines
    logo_lines = get_logo_lines()

#define figlet lines
    saturn_lines = pyfiglet.figlet_format('Saturn', font='slant').split('\n')
    launcher_lines = pyfiglet.figlet_format("Launcher", font="slant").split('\n')

# combine logo/text into one block
    combined_text_lines = saturn_lines + [''] + launcher_lines  # Add empty line between

# Pad text lines to match logo height (center vertically)
    text_height = len(combined_text_lines)
    logo_height = len(logo_lines)
    padding_top = (logo_height - text_height) // 2
    padding_bottom = logo_height - text_height - padding_top

# Create padded text lines
    padded_text_lines = [''] * padding_top + combined_text_lines + [''] * padding_bottom

# Print side by side line by line
    spacing = 3 # spaces between logo and text
    for idx, (logo_line, text_line) in enumerate(zip(logo_lines, padded_text_lines)):
        text_idx = idx - padding_top
        
        if text_idx < len(saturn_lines):
            console.print(logo_line + ' ' * spacing, Text(text_line, style="green"), sep='')
        elif text_idx >= len(saturn_lines) + 1:
            console.print(logo_line + ' ' * spacing, Text(text_line, style="yellow"), sep='')
        else:
            console.print(logo_line + ' ' * spacing + text_line)

    print("'saturn --help' to help")

# GET VERSION DATA
    try:
        latest_version = minecraft_launcher_lib.utils.get_latest_version()["release"]
        versions_data = minecraft_launcher_lib.utils.get_version_list()
    except Exception as e:
        print(f"[red]Error fetching versions: {e}[/red]")
        exit()

except Exception as e:
    print(f"[red]Fatal error during initialization: {e}[/red]")
    exit()

# ================================
# UPDATE SYSTEM FUNCTIONS
# ================================

def get_current_version():
    """Get current version from version.txt"""
    try:
        # Check if running as compiled executable
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        version_file = os.path.join(base_path, 'version.txt')
        
        with open(version_file, 'r') as f:
            return f.read().strip()
    except:
        return "unknown"

def get_latest_release():
    """Get latest release info from GitHub (Public Repo)"""
    try:
        # Public repository URL
        github_repo = 'IlyaP358/saturn-versions-rep'
        
        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/repos/{github_repo}/releases/latest'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            print("[yellow]No releases found in repository[/yellow]")
            return None
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"[red]Error connecting to GitHub: {e}[/red]")
        return None
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        return None

def compare_versions(current, latest):
    """Compare version strings (e.g., '0.1.0' vs '0.2.0')"""
    try:
        current_parts = [int(x) for x in current.split('.')]
        latest_parts = [int(x) for x in latest.split('.')]
        
        # Pad with zeros if needed
        while len(current_parts) < 3:
            current_parts.append(0)
        while len(latest_parts) < 3:
            latest_parts.append(0)
        
        return latest_parts > current_parts
    except:
        return False

def download_update(download_url, filename):
    """Download update file with progress bar"""
    try:
        print(f"[cyan]Downloading {filename}...[/cyan]")
        
        headers = {
            'Accept': 'application/octet-stream'
        }
        
        response = requests.get(download_url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        # Create temp directory
        temp_dir = os.path.join(os.getcwd(), '.saturn_temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'wb') as f:
            with Progress(
                BarColumn(),
                TextColumn("[progress.description]{task.description}"),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                transient=True,
            ) as progress:
                task = progress.add_task(f"Downloading", total=total_size)
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress.update(task, completed=downloaded)
        
        print(f"[green]✓ Download complete![/green]")
        return filepath
        
    except Exception as e:
        print(f"[red]Download failed: {e}[/red]")
        return None

def check_for_updates():
    """Check for updates and install if available"""
    print("[cyan]Checking for updates...[/cyan]\n")
    
    # Get current version
    current_version = get_current_version()
    print(f"Current version: [yellow]{current_version}[/yellow]")
    
    # Get latest release
    release = get_latest_release()
    if not release:
        return
    
    latest_version = release['tag_name'].lstrip('v')
    print(f"Latest version:  [yellow]{latest_version}[/yellow]\n")
    
    # Compare versions
    if not compare_versions(current_version, latest_version):
        print("[green]✓ You are running the latest version![/green]")
        return
    
    print("[green]New version available![/green]\n")
    
    # Show release notes if available
    if release.get('body'):
        print("[cyan]Changelog:[/cyan]")
        print(release['body'][:300])  # Show first 300 chars
        if len(release['body']) > 300:
            print("...")
        print()
    
    # Ask user to confirm
    response = input("Download and install update? (y/n): ").strip().lower()
    if response != 'y':
        print("[red]Update cancelled[/red]")
        return
    
    # Determine platform and find appropriate asset
    import platform
    system = platform.system()
    
    if system == "Windows":
        asset_name = "saturn_windows.exe"
    elif system == "Linux":
        asset_name = "saturn_linux"
    else:
        print(f"[red]Unsupported platform: {system}[/red]")
        return
    
    # Find asset in release
    asset = None
    for a in release.get('assets', []):
        if a['name'] == asset_name:
            asset = a
            break
    
    if not asset:
        print(f"[red]Asset '{asset_name}' not found in release[/red]")
        return
    
    # Download update
    new_exe_path = download_update(asset['url'], asset_name)
    if not new_exe_path:
        return
    
    # Get current executable path
    if getattr(sys, 'frozen', False):
        current_exe = sys.executable
    else:
        print("[yellow]Warning: Running from source, cannot auto-update[/yellow]")
        print(f"Downloaded file: {new_exe_path}")
        return
    
    # Launch updater script
    print("\n[cyan]Launching updater...[/cyan]")
    
    try:
        if system == "Windows":
            updater_script = os.path.join(os.getcwd(), 'saturn_updater.bat')
            with open(updater_script, 'w') as f:
                f.write(f'''@echo off
timeout /t 2 /nobreak >nul
del "{current_exe}"
move "{new_exe_path}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
''')
            subprocess.Popen([updater_script], shell=True)
            
        elif system == "Linux":
            updater_script = os.path.join(os.getcwd(), 'saturn_updater.sh')
            with open(updater_script, 'w') as f:
                f.write(f'''#!/bin/bash
sleep 2
mv "{new_exe_path}" "{current_exe}"
chmod +x "{current_exe}"
# Clear PyInstaller environment variables
export LD_LIBRARY_PATH=""
# Launch new version detached
(setsid "{current_exe}" &) >/dev/null 2>&1
rm "$0"
''')
            os.chmod(updater_script, 0o755)
            # Use subprocess to launch script detached
            subprocess.Popen(['/bin/bash', updater_script], start_new_session=True)
            
        print("[green]✓ Updater launched! Exiting...[/green]")
        sys.exit(0)
        
    except Exception as e:
        print(f"[red]Failed to launch updater: {e}[/red]")

# ================================
# MAIN PROGRAM
# ================================

try:
#installed version
    if not os.path.exists("saturn_launcher/versions"):
        os.makedirs("saturn_launcher/versions")
    versions_print = os.listdir("saturn_launcher/versions")
    versions_dir = os.path.abspath("saturn_launcher/versions")

# mods directory
    mods_dir = "saturn_launcher/mods"
    if not os.path.exists(mods_dir):
        os.makedirs(mods_dir)

# shaders directory
    shaders_dir = "saturn_launcher/shaderpacks"
    if not os.path.exists(shaders_dir):
        os.makedirs(shaders_dir)

# presets directory
    preset_manager.init_presets_directory()

# Shell Commands
    saturn_help = "saturn --help"
    saturn_display_versions = "saturn --versions"
    saturn_snapshot_versions = "saturn --snapshots"
    saturn_forge_versions = "saturn --forge"
    saturn_fabric_versions = "saturn --fabric"
    saturn_latest_versions = "saturn --latest"
    saturn_ram = "saturn --ram"
    saturn_ram_auto = "saturn --ram auto"
    start_launcher = "saturn --start"
    saturn_installed = "saturn --installed"
    saturn_update = "saturn --update"
    exit_command = "exit"

# MAIN LOOP
    while True:
        shell_commands = input("\nenter command: ").strip()

        # ================================
        # VANILLA RELEASE VERSIONS
        # ================================
        if shell_commands == saturn_display_versions:
            print("\n[cyan]Release versions list:[/cyan]")
            for version in versions_data:
                if version["type"] == "release":
                    print(f"[green]{version['id']}[/green]", end=", ")
            print("\n")

        # ================================
        # SNAPSHOT VERSIONS
        # ================================
        elif shell_commands == saturn_snapshot_versions:
            print("\n[magenta]Snapshot versions for all supported Minecraft versions:[/magenta]")
            snapshot_versions = [v["id"] for v in versions_data if v["type"] == "snapshot"]
            for mc_version in reversed(snapshot_versions):
                print(f"[magenta]{mc_version}[/magenta]")

        # ================================
        # FORGE VERSIONS LIST
        # ================================
        elif shell_commands == saturn_forge_versions:
            print("\n[yellow]Forge versions list:[/yellow]")
            try:
                forge_versions = minecraft_launcher_lib.forge.list_forge_versions()
                for v in reversed(forge_versions):
                    print(f"[yellow]Forge for MC {v}[/yellow]")
            except Exception as e:
                print(f"[red]Error loading Forge list: {e}[/red]")

        # ================================
        # FABRIC VERSIONS LIST
        # ================================
        elif shell_commands == saturn_fabric_versions:
            print("\n[magenta]Fabric Loader versions for all supported Minecraft versions:[/magenta]")
            try:
                # Fabric supports versions from 1.14 and above
                fabric_versions = [v["id"] for v in versions_data if v["type"] == "release" and v["id"] >= "1.14"]
                latest_loader = minecraft_launcher_lib.fabric.get_latest_loader_version()
                for mc_version in reversed(fabric_versions):
                    print(f"[magenta]MC {mc_version}: Fabric Loader {latest_loader}[/magenta]")
            except Exception as e:
                print(f"[red]Error loading Fabric list: {e}[/red]")

        # ================================
        # LATEST VERSION
        # ================================
        elif shell_commands == saturn_latest_versions:
            print(f"Latest version: {latest_version}")

        # ================================
        # INSTALLED VERSIONS 
        # ================================
        elif shell_commands == saturn_installed:
            #print installed versions
            print(pyfiglet.figlet_format("Installed versions"))
            print('\n'.join(versions_print))
            versions_in = "Versions in:", os.path.abspath("versions")
            print(versions_in)

        # ================================
        # RAM SETTINGS
        # ================================
        elif shell_commands == saturn_ram:
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config = {}

            # Ensure ram settings exist in config
            if 'ram' not in config:
                config['ram'] = {}
            if 'min' not in config['ram']:
                config['ram']['min'] = '1024M'
            if 'max' not in config['ram']:
                config['ram']['max'] = '2048M'

            min_ram = config['ram']['min']
            max_ram = config['ram']['max']

            # Calculate current RAM usage percentage
            if 'G' in max_ram:
                current_gb = int(max_ram.replace('G', ''))
            elif 'M' in max_ram:
                current_gb = int(max_ram.replace('M', '')) / 1024
            else:
                current_gb = int(max_ram) / 1024  # assume MB

            total_gb = psutil.virtual_memory().total // (1024**3)
            percentage = min(100, (current_gb / total_gb) * 100)

            # Show progress bar for current usage
            with Progress(BarColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task(f"RAM usage: {percentage:.1f}% of system RAM", total=100)
                progress.update(task, completed=int(percentage))

            print(f"[cyan]Current RAM settings:[/cyan]")
            print(f"Min RAM: [green]{min_ram}[/green]")
            print(f"Max RAM: [yellow]{max_ram}[/yellow]")
            print(f"System RAM: [blue]{total_gb}G[/blue]")

            # Ask for new max RAM
            new_max = input("Enter max RAM (example: 2G, 4G, 1024M) or press Enter to keep current: ").strip()
            if new_max:
                config['ram']['max'] = new_max
                with open('config.json', 'w') as f:
                    json.dump(config, f, indent=4)
                print(f"[green]Max RAM updated to: {new_max}[/green]")

        # ================================
        # AUTO RAM
        # ================================
        elif shell_commands == saturn_ram_auto:
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config = {}

            # Ensure ram settings exist in config
            if 'ram' not in config:
                config['ram'] = {}
            if 'min' not in config['ram']:
                config['ram']['min'] = '1024M'

            # Auto RAM selection
            total = psutil.virtual_memory().total // (1024**3)
            recommended = max(2, total // 2)
            recommended_str = f"{recommended}G"

            print(f"[blue]Total system RAM: {total}G[/blue]")
            print(f"[green]Recommended max RAM for Minecraft: {recommended_str}[/green]")
            confirm = input(f"Set max RAM to {recommended_str}? (y/n): ").strip().lower()
            if confirm == 'y':
                config['ram']['max'] = recommended_str
                with open('config.json', 'w') as f:
                    json.dump(config, f, indent=4)
                print(f"[green]Max RAM updated to: {recommended_str}[/green]")
            else:
                print("[yellow]RAM settings unchanged.[/yellow]")

        # ================================
        # START LAUNCHER (AUTO VANILLA / FORGE / FABRIC)
        # ================================
        elif shell_commands == start_launcher:
            #print installed versions
            print(pyfiglet.figlet_format("Installed versions"))
            print('\n'.join(versions_print))
            versions_in = "Versions in:", os.path.abspath("versions")
            print(versions_in)

            version = input("Enter version (vanilla or forge-1.xx or fabric-1.xx): ").strip()
            username = input("Enter Username: ")
            
            # Use active preset directory
            active_preset = preset_manager.get_active_preset()
            minecraft_directory = preset_manager.get_preset_path(active_preset)
            print(f"[cyan]Using preset: {active_preset}[/cyan]")

            # Auto-install Forge
            if version.startswith("forge-"):
                mc_version = version.replace("forge-", "")
                try:
                    forge_version = minecraft_launcher_lib.forge.find_forge_version(mc_version)
                    if forge_version is None:
                        print(f"[red]Forge version not found for Minecraft {mc_version}[/red]")
                        continue

                    installed_version = minecraft_launcher_lib.forge.forge_to_installed_version(forge_version)

                    # Check if already installed
                    if os.path.exists(os.path.join(minecraft_directory, "versions", installed_version, f"{installed_version}.json")):
                        print(f"[green]Forge {installed_version} is already installed[/green]")
                        version = installed_version
                    else:
                        print(f"Installing Forge for Minecraft {mc_version}...")
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            transient=True,
                        ) as progress:
                            task = progress.add_task("Installing Forge...", total=None)
                            minecraft_launcher_lib.forge.install_forge_version(
                                forge_version,
                                minecraft_directory
                            )
                            progress.update(task, completed=True)
                        version = installed_version
                        print(f"[yellow]Forge installed: {version}[/yellow]")
                except Exception as e:
                    print(f"[red]Forge install error: {e}[/red]")
                    continue

            # Auto-install Fabric
            elif version.startswith("fabric-"):
                mc_version = version.replace("fabric-", "")
                loader_version = minecraft_launcher_lib.fabric.get_latest_loader_version()
                installed_version = f"fabric-loader-{loader_version}-{mc_version}"

                # Check if already installed
                if os.path.exists(os.path.join(minecraft_directory, "versions", installed_version, f"{installed_version}.json")):
                    print(f"[green]Fabric {installed_version} is already installed[/green]")
                    version = installed_version
                else:
                    print(f"Installing Fabric {loader_version} for Minecraft {mc_version}...")
                    try:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            transient=True,
                        ) as progress:
                            task = progress.add_task("Installing Fabric...", total=None)
                            minecraft_launcher_lib.fabric.install_fabric(
                                mc_version,
                                minecraft_directory,
                                loader_version
                            )
                            progress.update(task, completed=True)
                        version = installed_version
                        print(f"[magenta]Fabric installed: {version}[/magenta]")
                    except Exception as e:
                        print(f"[red]Fabric install error: {e}[/red]")
                        continue

            # Vanilla install
            else:
                # Check if already installed
                if os.path.exists(os.path.join(minecraft_directory, "versions", version, f"{version}.json")):
                    print(f"[green]Minecraft {version} is already installed[/green]")
                else:
                    print(f"Installing Minecraft {version}...")
                    try:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            transient=True,
                        ) as progress:
                            task = progress.add_task("Installing Minecraft...", total=None)
                            minecraft_launcher_lib.install.install_minecraft_version(
                                version=version,
                                minecraft_directory=minecraft_directory
                            )
                            progress.update(task, completed=True)
                        print(f"[green]Minecraft {version} installed successfully[/green]")
                    except Exception as e:
                        print(f"[red]Error during installation: {e}[/red]")
                        continue

            # UUID setup
            offline_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))

            # Load RAM settings
            try:
                with open('config.json', 'r') as f:
                    config = json.load(f)
                min_ram = config.get('ram', {}).get('min', '1024M')
                max_ram = config.get('ram', {}).get('max', '2048M')
            except (FileNotFoundError, json.JSONDecodeError):
                min_ram = '1024M'
                max_ram = '2048M'

            options = {
                "username": username,
                "uuid": offline_uuid,
                "token": "",
                "jvmArguments": [f"-Xms{min_ram}", f"-Xmx{max_ram}"]
            }

            print("Launching...")

            try:
                command = minecraft_launcher_lib.command.get_minecraft_command(
                    version=version,
                    options=options,
                    minecraft_directory=minecraft_directory
                )
                subprocess.call(command)
            except Exception as e:
                print(f"[red]Error launching game: {e}[/red]")

        # ================================
        # UPDATE COMMAND
        # ================================
        elif shell_commands == saturn_update:
            check_for_updates()

        # ================================
        # EXIT
        # ================================
        elif shell_commands == exit_command:
            print("Goodbye")
            break

        # ================================
        # HELP 
        # ================================
        elif shell_commands == saturn_help:
            help_title = pyfiglet.figlet_format('Help tutorial', font='slant')
            print(f"[cyan]{help_title}[/cyan]")
            print("'saturn --versions' display release stable all versions")
            print("'saturn --snapshots' display all snaphots version")
            print("'saturn --forge' display all forge version")
            print("'saturn --fabric' display all fabric version")
            print("'saturn --latest' display latest stable version")
            print("'saturn --ram' display current RAM settings")
            print("'saturn --ram auto' to automatically set best amount RAM to your system")
            print("'saturn --start' initialize and start the Minecraft")
            print("'saturn --installed' to display all installed versions")
            print("'saturn --update' to update the launcher")
            print("\ntype 'exit' to exit launcher")

            print("\nafter 'saturn --start' type 'x.x.x' version to install/launch release stable version")
            print("\nif you need forge/fabric version type 'forge-x.x.x' or 'fabric-x.x.x'")
            print("\nMod commands:")
            print("'saturn --mods search <name>' search for mods and shaders on Modrinth")
            print("'saturn --mods install <name> <mc_version> <loader>' install mod")
            print("'saturn --mods list' list installed mods")
            print("'saturn --mods remove <name>' remove mod")
            print("\nShader commands:")
            print("'saturn --shaders install <name> <mc_version>' install shader")
            print("'saturn --shaders list' list installed shaders")
            print("'saturn --shaders remove <name>' remove shader")
            
            print("\nPreset commands:")
            print("'saturn presets --list' list all presets")
            print("'saturn presets --switch \"name\"' switch to or create a preset")
            print("'saturn presets --delete \"name\"' delete a preset")
            print("'saturn presets --zip \"name\"' compress preset to save space")
            print("'saturn presets --unzip \"name\"' decompress archived preset")
            

        # ================================
        # MODS MANAGEMENT
        # ================================
        elif shell_commands.startswith("saturn --mods"):
            parts = shlex.split(shell_commands)
            if len(parts) < 3:
                print("[red]Invalid mod command. Use 'saturn --mods search/install/list/remove'[/red]")
                continue

            subcommand = parts[2]

            if subcommand == "search":
                if len(parts) < 4:
                    print("[red]Usage: saturn --mods search <mod_name>[/red]")
                    continue
                mod_name = " ".join(parts[3:])
                try:
                    url = f"https://api.modrinth.com/v2/search?query={mod_name}&limit=10"
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()

                    if not data.get("hits"):
                        print(f"[yellow]No mods found for '{mod_name}'[/yellow]")
                        continue

                    table = Table(title=f"Search results for '{mod_name}'")
                    table.add_column("Name", style="cyan", no_wrap=True)
                    table.add_column("Type", style="blue")
                    table.add_column("Description", style="white")
                    table.add_column("Downloads", style="green")

                    for hit in data["hits"]:
                        name = hit.get("title", "Unknown")
                        project_type = hit.get("project_type", "mod").capitalize()
                        desc = hit.get("description", "No description")[:50] + "..." if len(hit.get("description", "")) > 50 else hit.get("description", "No description")
                        downloads = f"{hit.get('downloads', 0):,}"
                        table.add_row(name, project_type, desc, downloads)

                    console.print(table)
                except Exception as e:
                    print(f"[red]Error searching mods: {e}[/red]")

            elif subcommand == "install":
                if len(parts) < 6:
                    print("[red]Usage: saturn --mods install <mod_name> <mc_version> <loader>[/red]")
                    continue
                mod_name = " ".join(parts[3:-2])
                mc_version = parts[-2]
                loader = parts[-1]

                try:
                    url = f"https://api.modrinth.com/v2/search?query={mod_name}&limit=5"
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()

                    if not data.get("hits"):
                        print(f"[red]No mod found for '{mod_name}'[/red]")
                        continue

                    project = data["hits"][0]
                    project_id = project["project_id"]
                    mod_title = project["title"]

                    version_url = f"https://api.modrinth.com/v2/project/{project_id}/version?game_versions=[\"{mc_version}\"]&loaders=[\"{loader}\"]"
                    version_response = requests.get(version_url)
                    version_response.raise_for_status()
                    versions = version_response.json()

                    if not versions:
                        print(f"[red]No compatible version found for {mod_title} on MC {mc_version} with {loader}[/red]")
                        continue

                    version_data = versions[0]
                    primary_file = version_data["files"][0]
                    download_url = primary_file["url"]
                    filename = primary_file["filename"]

                    print(f"[cyan]Downloading {mod_title} ({filename})...[/cyan]")
                    with requests.get(download_url, stream=True) as r:
                        r.raise_for_status()
                        total_size = int(r.headers.get('content-length', 0))
                        with open(os.path.join(mods_dir, filename), 'wb') as f:
                            with Progress(
                                BarColumn(),
                                TextColumn("[progress.description]{task.description}"),
                                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                                transient=True,
                            ) as progress:
                                task = progress.add_task(f"Downloading {filename}", total=total_size)
                                downloaded = 0
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    progress.update(task, completed=downloaded)

                    print(f"[green]Installed {mod_title} successfully![/green]")
                except Exception as e:
                    print(f"[red]Error installing mod: {e}[/red]")

            elif subcommand == "list":
                mods = os.listdir(mods_dir)
                if not mods:
                    print("[yellow]No mods installed[/yellow]")
                else:
                    print("[cyan]Installed mods:[/cyan]")
                    for mod in sorted(mods):
                        print(f"[green]{mod}[/green]")

            elif subcommand == "remove":
                if len(parts) < 4:
                    print("[red]Usage: saturn --mods remove <mod_name>[/red]")
                    continue
                mod_name = " ".join(parts[3:])

                mods = os.listdir(mods_dir)
                removed = False
                for mod in mods:
                    if mod_name.lower() in mod.lower():
                        os.remove(os.path.join(mods_dir, mod))
                        print(f"[green]Removed {mod}[/green]")
                        removed = True
                        break

                if not removed:
                    print(f"[red]Mod '{mod_name}' not found[/red]")

            else:
                print("[red]Unknown mod subcommand. Use search, install, list, or remove[/red]")

        # ================================
        # SHADERS MANAGEMENT
        # ================================
        elif shell_commands.startswith("saturn --shaders"):
            parts = shlex.split(shell_commands)
            if len(parts) < 3:
                print("[red]Invalid shader command. Use 'saturn --shaders install/list/remove'[/red]")
                continue

            subcommand = parts[2]

            if subcommand == "install":
                if len(parts) < 5:
                    print("[red]Usage: saturn --shaders install <shader_name> <mc_version>[/red]")
                    continue
                shader_name = " ".join(parts[3:-1])
                mc_version = parts[-1]

                try:
                    url = f"https://api.modrinth.com/v2/search?query={shader_name}&limit=5&facets=[[\"project_type:shader\"]]"
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()

                    if not data.get("hits"):
                        print(f"[red]No shader found for '{shader_name}'[/red]")
                        continue

                    project = data["hits"][0]
                    project_id = project["project_id"]
                    shader_title = project["title"]

                    version_url = f"https://api.modrinth.com/v2/project/{project_id}/version?game_versions=[\"{mc_version}\"]"
                    version_response = requests.get(version_url)
                    version_response.raise_for_status()
                    versions = version_response.json()

                    if not versions:
                        print(f"[red]No compatible version found for {shader_title} on MC {mc_version}[/red]")
                        continue

                    version_data = versions[0]
                    primary_file = version_data["files"][0]
                    download_url = primary_file["url"]
                    filename = primary_file["filename"]

                    print(f"[cyan]Downloading {shader_title} ({filename})...[/cyan]")
                    with requests.get(download_url, stream=True) as r:
                        r.raise_for_status()
                        total_size = int(r.headers.get('content-length', 0))
                        with open(os.path.join(shaders_dir, filename), 'wb') as f:
                            with Progress(
                                BarColumn(),
                                TextColumn("[progress.description]{task.description}"),
                                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                                transient=True,
                            ) as progress:
                                task = progress.add_task(f"Downloading {filename}", total=total_size)
                                downloaded = 0
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    progress.update(task, completed=downloaded)

                    print(f"[green]Installed {shader_title} successfully![/green]")
                except Exception as e:
                    print(f"[red]Error installing shader: {e}[/red]")

            elif subcommand == "list":
                shaders = os.listdir(shaders_dir)
                if not shaders:
                    print("[yellow]No shaders installed[/yellow]")
                else:
                    print("[cyan]Installed shaders:[/cyan]")
                    for shader in sorted(shaders):
                        print(f"[magenta]{shader}[/magenta]")

            elif subcommand == "remove":
                if len(parts) < 4:
                    print("[red]Usage: saturn --shaders remove <shader_name>[/red]")
                    continue
                shader_name = " ".join(parts[3:])

                shaders = os.listdir(shaders_dir)
                removed = False
                for shader in shaders:
                    if shader_name.lower() in shader.lower():
                        os.remove(os.path.join(shaders_dir, shader))
                        print(f"[green]Removed {shader}[/green]")
                        removed = True
                        break

                if not removed:
                    print(f"[red]Shader '{shader_name}' not found[/red]")

            else:
                print("[red]Unknown shader subcommand. Use install, list, or remove[/red]")

        # ================================
        # PRESETS MANAGEMENT
        # ================================
        elif shell_commands.startswith("saturn presets"):
            parts = shlex.split(shell_commands)
            if len(parts) < 3:
                print("[red]Invalid preset command. Use 'saturn presets --list/--switch/--delete/--zip/--unzip'[/red]")
                continue
            
            subcommand = parts[2]
            
            if subcommand == "--list":
                presets = preset_manager.list_presets()
                active_preset = preset_manager.get_active_preset()
                
                if not presets:
                    print("[yellow]No presets found[/yellow]")
                else:
                    table = Table(title="Available Presets")
                    table.add_column("Name", style="cyan", no_wrap=True)
                    table.add_column("Type", style="blue")
                    table.add_column("Status", style="green")
                    
                    for preset in presets:
                        preset_name = preset['name']
                        preset_type = "Compressed" if preset['compressed'] else "Directory"
                        status = "● Active" if preset_name == active_preset else ""
                        
                        table.add_row(preset_name, preset_type, status)
                    
                    console.print(table)
            
            elif subcommand == "--switch":
                if len(parts) < 4:
                    print("[red]Usage: saturn presets --switch \"preset_name\"[/red]")
                    continue
                preset_name = parts[3]
                preset_manager.switch_preset(preset_name)
            
            elif subcommand == "--delete":
                if len(parts) < 4:
                    print("[red]Usage: saturn presets --delete \"preset_name\"[/red]")
                    continue
                preset_name = parts[3]
                preset_manager.delete_preset(preset_name)
            
            elif subcommand == "--zip":
                if len(parts) < 4:
                    print("[red]Usage: saturn presets --zip \"preset_name\"[/red]")
                    continue
                preset_name = parts[3]
                preset_manager.compress_preset(preset_name)
            
            elif subcommand == "--unzip":
                if len(parts) < 4:
                    print("[red]Usage: saturn presets --unzip \"preset_name\"[/red]")
                    continue
                preset_name = parts[3]
                preset_manager.decompress_preset(preset_name)
            
            else:
                print("[red]Unknown preset subcommand. Use --list, --switch, --delete, --zip, or --unzip[/red]")

        else:
            print("[red]ERROR: Unknown command[/red]")

except KeyboardInterrupt:
    print("\nGoodbye")
