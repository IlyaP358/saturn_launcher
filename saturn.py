import minecraft_launcher_lib
import subprocess
import uuid
import pyfiglet
import os
import json
import psutil
from rich import print
from rich.console import Console
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, track, BarColumn
from image_ascii import get_logo_lines

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

#installed version
    if not os.path.exists("saturn_launcher/versions"):
        os.makedirs("saturn_launcher/versions")
    versions_print = os.listdir("saturn_launcher/versions")
    versions_dir = os.path.abspath("saturn_launcher/versions")

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
            minecraft_directory = "saturn_launcher"

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
            print("\ntype 'exit' to exit launcher")

            print("\nafter 'saturn --start' type 'x.x.x' version to install/launch release stable version")
            print("\nif you need forge/fabric version type 'forge-x.x.x' or 'fabric-x.x.x'")

        else:
            print("[red]ERROR: Unknown command[/red]")

except KeyboardInterrupt:
    print("\nGoodbye")
