#!/usr/bin/env python3

from typing import Tuple
import json
from getpass import getpass
from functions import *


def get_user_input() -> dict:
    output_dict = {
        "distro_name": "ubuntu",
        "distro_version": "",
        "distro_link": "",
        "de_name": "cli",
        "username": "localuser",
        "password": "",
        "hostname": "eupnea-chromebook",
        "device": "image",
        "rebind_search": False
    }
    with open("distros.json", "r") as file:
        distros = json.load(file)

    # Print welcome message
    print_header("Welcome to Eupnea")
    print_header("This script will create a bootable Eupnea USB-drive/SD-card/image for you.")
    print_header("You will now be asked a few questions. If you dont know what to answer, just press 'enter' and the"
                 " recommended answer will be used.")
    input("(Press enter to continue)")
    print_question("Which Linux distro(flavor) would you like to use?")

    while True:
        temp_distro_name = input("\033[94m" + "Available options: Ubuntu(default, recommended), Debian, Arch, Fedora\n"
                                 + "\033[0m")
        match temp_distro_name:
            case "Ubuntu" | "ubuntu" | "":
                output_dict["distro_name"] = "ubuntu"
                while True:
                    print_question("Use latest Ubuntu version?")
                    output_dict["distro_version"] = input("\033[94m" + "Press enter for yes, or type in the version "
                                                                       "number(example: '21.10'): " + "\033[0m")
                    if output_dict["distro_version"] == "":
                        # get highest version number
                        output_dict["distro_version"] = max(distros["ubuntu"])
                        print("Ubuntu: " + output_dict["distro_version"] + " selected")
                        break
                    else:
                        if output_dict["distro_version"] in distros["ubuntu"]:
                            print("Ubuntu: " + output_dict["distro_version"] + " selected")
                            break
                        else:
                            print_warning("Version not available, please choose another")
                            continue
                break
            case "Debian" | "debian":
                print("Debian stable selected")
                output_dict["distro_name"] = "debian"
                # TODO: Add non stable debian versions
                break
            case "Arch" | "arch" | "arch btw":
                print("Arch selected")
                output_dict["distro_name"] = "arch"
                output_dict["distro_link"] = distros["arch"]
                break
            case "Fedora" | "fedora":
                output_dict["distro_name"] = "fedora"
                while True:
                    print_question("Use latest Fedora version?")
                    output_dict["distro_version"] = input("\033[94m" + "Press enter for yes, or type in the version "
                                                                       "number(example: '36'): " + "\033[0m")
                    if output_dict["distro_version"] == "":
                        # remove rawhide, then get the highest version number
                        temp_fedora_dict = distros["fedora"]
                        temp_fedora_dict.pop("Rawhide")
                        output_dict["distro_version"] = max(temp_fedora_dict)
                        output_dict["distro_link"] = distros["fedora"][output_dict["distro_version"]]
                        print("Using Fedora version: " + output_dict["distro_version"])
                        break
                    else:
                        if output_dict["distro_version"] in distros["fedora"]:
                            output_dict["distro_link"] = distros["fedora"][output_dict["distro_version"]]
                            print("Fedora: " + output_dict["distro_version"] + " selected")
                            break
                        else:
                            print_warning("Version not available, please choose another")
                            continue
                break
            case _:
                print_warning("Check your spelling and try again")
                continue

    print_question("Which desktop environment(Desktop GUI) would you like to use?")
    match output_dict["distro_name"]:
        case "ubuntu":
            available_de = "Gnome(default, recommended), KDE(recommended), MATE, Xfce(recommended for weak devices), " \
                           "LXQt(recommended for weak devices), deepin, budgie, cli"
        case "debian":
            available_de = "Gnome(default, recommended), KDE(recommended), MATE, Xfce(recommended for weak devices), " \
                           "LXQt(recommended for weak devices), budgie, cli"
        case "arch":
            available_de = "Gnome(default, recommended), KDE(recommended), MATE, Xfce(recommended for weak devices), " \
                           "LXQt(recommended for weak devices), deepin, budgie, cli"
        case "fedora":
            available_de = "Gnome(default, recommended), KDE(recommended), MATE, Xfce(recommended for weak devices), " \
                           "LXQt(recommended for weak devices), deepin, cli"

    while True:
        temp_de_name = input("\033[94m" + "Available options: " + available_de + "\033[0m" + "\n")
        match temp_de_name:
            case "Gnome" | "gnome" | "":
                print("Gnome selected")
                output_dict["de_name"] = "gnome"
                break
            case "KDE" | "kde":
                print("KDE selected")
                output_dict["de_name"] = "kde"
                break
            case "MATE" | "mate":
                print("MATE selected")
                output_dict["de_name"] = "mate"
                break
            case "xfce" | "Xfce":
                print("Xfce selected")
                output_dict["de_name"] = "xfce"
                break
            case "lxqt" | "Lxqt":
                print("Lxqt selected")
                output_dict["de_name"] = "lxqt"
                break
            case "deepin":
                if output_dict["distro_name"] == "debian":
                    print_warning("Deepin is not available for Debian, please choose another DE")
                else:
                    print("Deepin selected")
                    output_dict["de_name"] = "deepin"
                    break
            case "budgie":
                if output_dict["distro_name"] == "fedora":
                    print_warning("Budgie is not available for Fedora, please choose another DE")
                else:
                    print("Budgie selected")
                    output_dict["de_name"] = "budgie"
                    break
            case "cli" | "none":
                print_warning("Warning: No desktop environment will be installed!")
                if input("\033[94mType 'yes' to continue or Press Enter to choose a desktop environment" +
                         "\033[0m\n") == "yes":
                    print("No desktop will be installed")
                    output_dict["de_name"] = "cli"
                    break
            case _:
                print_warning("No such Desktop environment. Check your spelling and try again")

    # Gnome has a first time setup -> skip this part for gnome, as there will be a first time setup
    if not output_dict["de_name"] == "gnome":
        print_question("Enter username to be used in Eupnea")
        while True:
            output_dict["username"] = input("\033[94m" + "Username(default: 'localuser'): " + "\033[0m")
            if output_dict["username"] == "":
                print("Using 'localuser' as username")
                output_dict["username"] = "localuser"
                break
            found_invalid_char = False
            for char in output_dict["username"]:
                if char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-":
                    print_warning(f"Hostname contains invalid character: {char}")
                    found_invalid_char = True
                    break
            if not found_invalid_char:
                print(f"Using {output_dict['username']} as username")
                break

        print_question("Please set a secure password")
        while True:
            passwd_temp = getpass("\033[94m" + "Password: " + "\033[0m")
            if passwd_temp == "":
                print_warning("Password cannot be empty")
                continue

            # temporary fix for ) and ( crashing chpasswd in build.py
            elif passwd_temp.find(")") != -1:
                print_warning("Password cannot contain: )")
                continue
            elif passwd_temp.find("(") != -1:
                print_warning("Password cannot contain: (")
                continue

            else:
                passwd_temp_repeat = getpass("\033[94m" + "Repeat password: " + "\033[0m")
                if passwd_temp == passwd_temp_repeat:
                    output_dict["password"] = passwd_temp
                    print("Password set")
                    break
                else:
                    print_warning("Passwords do not match, please try again")
                    continue

    # TODO: Maybe skip this, as its not really needed for the average user to set themselves
    print_question("Enter hostname for the chromebook.(Hostname is something like a device name)")
    while True:
        output_dict["hostname"] = input("\033[94m" + "Hostname(default: 'eupnea-chromebook'): " + "\033[0m")
        if output_dict["hostname"] == "":
            print("Using eupnea-chromebook as hostname")
            output_dict["hostname"] = "eupnea-chromebook"
            break
        if output_dict["hostname"][0] == "-":
            print_warning("Hostname cannot start with a '-'")
            continue
        found_invalid_char = False
        for char in output_dict["hostname"]:
            if char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-":
                print_warning(f"Hostname contains invalid character: {char}")
                found_invalid_char = True
                break
        if not found_invalid_char:
            print(f"Using {output_dict['hostname']} as hostname")
            break

    print_question("Would you like to rebind the Search/Super/Win key to Caps Lock?(NOT RECOMMENDED)")
    if input("\033[94m" + "Type yes to rebind. Press enter to keep old binding: " "\033[0m") == "yes":
        print("Search key will be a CAPS LOCK key")
        rebind_search = True
    else:
        print("Search key will be Super/Win key")
        rebind_search = False

    while True:
        usb_array = []
        lsblk_out = bash("lsblk -o NAME,MODEL,SIZE,TRAN").splitlines()
        for line in lsblk_out[2:]:
            # MassStorageClass is not a real device, so ignore it
            if not line.find("usb") == -1 and line.find("MassStorageClass") == -1:  # Print USB devices only
                usb_array.append(line[:3])
                print(line[:-3])  # this is for the user to see the list
        if len(usb_array) == 0:
            print_status("No available USBs/SD-cards found. Building image file.")
            break
        else:
            device = input("\033[92m" + 'Enter USB-drive/SD-card name(example: sdb) or "image" to build an image'
                           + "\033[0m" + "\n").strip()
            if device == "image":
                print("Building image instead of writing directly")
                break
            elif device in usb_array:
                print(f"Writing directly to /dev/{device}")
                output_dict["device"] = device
                break
            else:
                print_warning("No such device. Check your spelling and try again")
                continue

    print_status("User input complete")
    return output_dict


if __name__ == "__main__":
    print_error("Do not run this file. Run main.py")
