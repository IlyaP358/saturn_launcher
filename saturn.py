import minecraft_launcher_lib
import subprocess
import uuid
import pyfiglet
from rich import print

title = pyfiglet.figlet_format('Saturn', font='slant')
titleLauncher = pyfiglet.figlet_format("Launcher", font="slant")
print(f'[green]{title}[/green] \n [yellow]{titleLauncher}[/yellow]')
print("type 'saturn --help' to help")

# GET VERSION DATA
try:
    latest_version = minecraft_launcher_lib.utils.get_latest_version()["release"]
    versions_data = minecraft_launcher_lib.utils.get_version_list()
except Exception as e:
    print(f"[red]Error fetching versions: {e}[/red]")
    exit()

# Shell Commands
saturn_help = "saturn --help"
saturn_display_versions = "saturn --versions"
saturn_snapshot_versions = "saturn --snapshots"
saturn_forge_versions = "saturn --forge"
saturn_fabric_versions = "saturn --fabric"
saturn_latest_versions = "saturn --latest"
start_launcher = "saturn --start"
exit_command = "exit"

# MAIN LOOP
while True:
    shell_commands = input("\ntype command: ").strip()

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
        print("\n[cyan]Snapshot versions list:[/cyan]")
        for version in versions_data:
            if version["type"] == "snapshot":
                print(f"[magenta]{version['id']}[/magenta]", end=", ")
        print("\n")

    # ================================
    # FORGE VERSIONS LIST
    # ================================
    elif shell_commands == saturn_forge_versions:
        print("\n[yellow]Forge versions list:[/yellow]")
        try:
            forge_versions = minecraft_launcher_lib.forge.list_forge_versions()
            for v in forge_versions:
                print(f"[yellow]Forge for MC {v}[/yellow]", end=", ")
        except Exception as e:
            print(f"[red]Error loading Forge list: {e}[/red]")
        print("\n")

    # ================================
    # FABRIC VERSIONS LIST
    # ================================
    elif shell_commands == saturn_fabric_versions:
        print("\n[magenta]Fabric Loader versions list:[/magenta]")
        try:
            fabric_versions = minecraft_launcher_lib.fabric.get_all_loader_versions()
            for v in fabric_versions:
                print(f"[magenta]Fabric Loader {v['version']}[/magenta]", end=", ")
        except Exception as e:
            print(f"[red]Error loading Fabric list: {e}[/red]")
        print("\n")

    # ================================
    # LATEST VERSION
    # ================================
    elif shell_commands == saturn_latest_versions:
        print(f"Latest version: {latest_version}")

    # ================================
    # START LAUNCHER (AUTO VANILLA / FORGE / FABRIC)
    # ================================
    elif shell_commands == start_launcher:
        version = input("Enter version (vanilla or forge-1.xx or fabric-1.xx): ").strip()
        username = input("Enter Username: ")
        minecraft_directory = "saturn_launcher"

        # Auto-install Forge
        if version.startswith("forge-"):
            mc_version = version.replace("forge-", "")
            print(f"Installing Forge for Minecraft {mc_version}...")
            try:
                forge_version = minecraft_launcher_lib.forge.find_forge_version(mc_version)
                if forge_version is None:
                    print(f"[red]Forge version not found for Minecraft {mc_version}[/red]")
                    continue

                minecraft_launcher_lib.forge.install_forge_version(
                    forge_version,
                    minecraft_directory
                )
                # Construct the installed version ID
                version = minecraft_launcher_lib.forge.forge_to_installed_version(forge_version)
                print(f"[yellow]Forge installed: {version}[/yellow]")
            except Exception as e:
                print(f"[red]Forge install error: {e}[/red]")
                continue

        # Auto-install Fabric
        elif version.startswith("fabric-"):
            mc_version = version.replace("fabric-", "")
            loader_version = minecraft_launcher_lib.fabric.get_latest_loader_version()

            print(f"Installing Fabric {loader_version} for Minecraft {mc_version}...")
            try:
                minecraft_launcher_lib.fabric.install_fabric(
                    mc_version,
                    minecraft_directory,
                    loader_version
                )
                # Construct the installed version ID
                version = f"fabric-loader-{loader_version}-{mc_version}"
                print(f"[magenta]Fabric installed: {version}[/magenta]")
            except Exception as e:
                print(f"[red]Fabric install error: {e}[/red]")
                continue

        # Vanilla install
        else:
            print(f"Installing Minecraft {version}...")
            try:
                minecraft_launcher_lib.install.install_minecraft_version(
                    version=version,
                    minecraft_directory=minecraft_directory
                )
            except Exception as e:
                print(f"[red]Error during installation: {e}[/red]")
                continue

        # UUID setup
        offline_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))
        options = {
            "username": username,
            "uuid": offline_uuid,
            "token": ""
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
        print("'saturn --start' start launch logic")

        print("\nafter 'saturn --start' type 'x.x.x' version to install/launch release stable version")
        print("\nif you need forge/fabric version type 'forge-x.x.x' or 'fabric-x.x.x'")

    else:
        print("[red]ERROR: Unknown command[/red]")

