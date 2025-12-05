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

def version_list():
    user_input = input("print 'y' to see latest version ")
    if user_input == "y" or "Y":
       print(f"Latests versions {latest_version}") 
    elif user_input == "n" or "N":
        print("")
    else:
       print("ERROR")

version_list()

version = input("Enter Minecraft version: ")
username = input("Enter Username: ")

minecraft_directory = "saturn_launcher"

print(f"Checking/Installing version {version}...")
minecraft_launcher_lib.install.install_minecraft_version(version=version, minecraft_directory=minecraft_directory)

offline_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))

options = {
    "username": username,
    "uuid": offline_uuid,
    "token": ""
}

# Launch Minecraft 
print("Launching...")
command = minecraft_launcher_lib.command.get_minecraft_command(version=version, options=options, minecraft_directory=minecraft_directory)
subprocess.call(command)
