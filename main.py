#!/usr/bin/env python3
# This script will later become the gui. For now, it's a simple wrapper for the build script.

import sys
import os
import argparse

from functions import *


# parse arguments from the cli. Only for testing/advanced use. All other parameters are handled by cli_input.py
def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local-path', dest="local_path",
                        help="Use local files, instead of downloading from the internet (not recommended). Required "
                             "files: bzImage, modules.tar.xz, folder with firmware(named 'firmware'), Rootfs: "
                             "ubuntu-rootfs.tar.xz or arch-rootfs.tar.gz or fedora-rootfs.raw.xz or pre-debootstrapped "
                             "folder(named 'debian')")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
                        help="Print more output")
    parser.add_argument("--dev", action="store_true", dest="dev_build", default=False,
                        help="Use latest dev build. May be unstable.")
    parser.add_argument("--alt", action="store_true", dest="alt", default=False,
                        help="Use alt kernel. Only for older devices.")
    parser.add_argument("--exp", action="store_true", dest="exp", default=False,
                        help="Use experimental 5.15 kernel.")
    parser.add_argument("--mainline", action="store_true", dest="mainline", default=False,
                        help="Use mainline linux kernel instead of modified chromeos kernel.")
    return parser.parse_args()


if __name__ == "__main__":
    if os.geteuid() == 0 and not path_exists("/tmp/username"):
        print_error("Please start the script as non-root/without sudo")
        exit(1)

    args = process_args()  # process args before elevating to root for better ux

    # Restart script as root
    if not os.geteuid() == 0:
        # save username
        with open("/tmp/username", "w") as file:
            file.write(bash("whoami").strip())  # get non root username. os.getlogin() seems to fail in chroots
        sudo_args = ['sudo', sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *sudo_args)

    # read username
    with open("/tmp/username", "r") as file:
        user_id = file.read()

    # Check python version
    if sys.version_info < (3, 10):  # python 3.10 or higher is required
        if path_exists("/usr/bin/apt"):
            if input(
                    "\033[92m" + "Python 3.10 or higher is required. Attempt to install? (Y/n)\n" +
                    "\033[0m").lower() == "y" or "":
                print_status("Switching to unstable channel")
                # switch to unstable channel
                with open("/etc/apt/sources.list", "r") as file:
                    original_sources = file.readlines()
                sources = original_sources
                sources[1] = sources[1].replace("bullseye", "unstable")
                with open("/etc/apt/sources.list", "w") as file:
                    file.writelines(sources)

                # update and install python
                print_status("Installing python 3.10")
                bash("apt-get update -y")
                bash("apt-get install -y python3")
                print_status("Python 3.10 installed")

                # revert to stable channel
                with open("/etc/apt/sources.list", "w") as file:
                    file.writelines(original_sources)

                print_header("\033[92m" + 'Please restart the script with: "./main.py"' + "\033[0m")
                exit(1)
            else:
                print_error("Please run the script with python 3.10 or higher")
                exit(1)
        else:
            print_error("Please run the script with python 3.10 or higher")
            exit(1)

    # import files after python version check is successful
    import build
    import cli_input

    # parse arguments
    dev_release = args.dev_build
    kernel_type = "stable"
    if args.dev_build:
        print_warning("Using dev release")
    if args.alt:
        print_warning("Using alt kernel")
        kernel_type = "alt"
    if args.exp:
        print_warning("Using experimental kernel")
        kernel_type = "exp"
    if args.mainline:
        print_warning("Using mainline kernel")
        kernel_type = "mainline"
    if args.local_path:
        print_warning("Using local files")
    if args.verbose:
        print_warning("Verbosity increased")
    build = build.start_build(args.verbose, local_path=args.local_path, kernel_type=kernel_type,
                              dev_release=dev_release, user_id=user_id, build_options=cli_input.get_user_input())
