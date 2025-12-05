import minecraft_launcher_lib
import subprocess
import uuid
import pyfiglet
from rich import print

title = pyfiglet.figlet_format('Saturn', font='slant')
titleLauncher = pyfiglet.figlet_format("Launcher", font="slant")
print(f'[green]{title}[/green] \n [yellow]{titleLauncher}[/yellow]')

latest_version = minecraft_launcher_lib.utils.get_latest_version()["release"]
versions_data = minecraft_launcher_lib.utils.get_version_list()

# Shell Commands
def shell():
    return input("type command: ") # interpretate defined program terminal commands

saturn_display_versions = "SSS"
saturn_latest_versions = "LLL"
start_launcher = "KKK"

def list_version(shell_commands):
    #PRINT ALL VERSIONS
    if shell_commands == saturn_display_versions:
        user_input = input("See all version y/n? ")
        if user_input.lower() == "y":
            print(f"Latest version: {versions_data}")
        elif user_input.lower() == "n":
            print("")
            shell()
    #PRINT LATEST VERSION
    elif shell_commands == saturn_latest_versions:
        user_input = input("See latest version y/n? ")
        if user_input.lower() == "y":
            print(f"Latest version: {latest_version}")
        elif user_input.lower() == "n":
            print("")
            shell()
        else:
            print("ERROR")
    # START LAUNCHER LOGIC
    elif shell_commands == start_launcher:
        # Setup Startup
        version = input("Enter Minecraft version: ")
        username = input("Enter Username: ")
        minecraft_directory = "saturn_launcher"

        print(f"Checking/Installing version {version}...")
        minecraft_launcher_lib.install.install_minecraft_version(
            version=version, minecraft_directory=minecraft_directory
        )

        offline_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))

        options = {
            "username": username,
            "uuid": offline_uuid,
            "token": ""
        }

        print("Launching...")
        command = minecraft_launcher_lib.command.get_minecraft_command(
            version=version, options=options, minecraft_directory=minecraft_directory
        )
        subprocess.call(command)

    else:
        print("ERROR")

# Start command system
shell_commands = shell()
list_version(shell_commands)

