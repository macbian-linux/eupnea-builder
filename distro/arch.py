from functions import *


def config(de_name: str, distro_version: str, root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)
    print_status("Configuring Arch")

    # Uncomment worldwide arch mirror
    with open("/mnt/eupnea/etc/pacman.d/mirrorlist", "r") as read:
        mirrors = read.readlines()
    # Uncomment first worldwide mirror
    mirrors[6] = mirrors[6][1:]
    with open("/mnt/eupnea/etc/pacman.d/mirrorlist", "w") as write:
        write.writelines(mirrors)

    # Apply temporary fix for pacman
    bash("mount --bind /mnt/eupnea /mnt/eupnea")
    with open("/mnt/eupnea/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # temporarily comment out CheckSpace, coz Pacman fails to check available storage space when run from a chroot
    temp_pacman[34] = f"#{temp_pacman[34]}"
    with open("/mnt/eupnea/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)

    print_status("Preparing pacman")
    chroot("pacman-key --init")
    chroot("pacman-key --populate archlinux")
    chroot("pacman -Syy --noconfirm")
    chroot("pacman -Syu --noconfirm")

    print_status("Installing packages")
    start_progress()  # start fake progress
    chroot("pacman -S --noconfirm base base-devel nano networkmanager xkeyboard-config linux-firmware sudo cloud-utils")
    stop_progress()  # stop fake progress

    print_status("Downloading and installing de, might take a while")
    start_progress()  # start fake progress
    match de_name:
        case "gnome":
            print_status("Installing GNOME")
            chroot("pacman -S --noconfirm gnome gnome-extra gnome-initial-setup")
            chroot("systemctl enable gdm.service")
        case "kde":
            print_status("Installing KDE")
            chroot("pacman -S --noconfirm plasma-meta plasma-wayland-session kde-applications")
            chroot("systemctl enable sddm.service")
        case "mate":
            print_status("Installing MATE")
            # no wayland support in mate
            chroot("pacman -S --noconfirm mate mate-extra xorg xorg-server lightdm lightdm-gtk-greeter")
            chroot("systemctl enable lightdm.service")
        case "xfce":
            print_status("Installing Xfce")
            # no wayland support in xfce
            chroot("pacman -S --noconfirm xfce4 xfce4-goodies xorg xorg-server lightdm lightdm-gtk-greeter")
            chroot("systemctl enable lightdm.service")
        case "lxqt":
            print_status("Installing LXQt")
            chroot("pacman -S --noconfirm lxqt breeze-icons xorg xorg-server sddm")
            chroot("systemctl enable sddm.service")
        case "deepin":
            print_status("Installing deepin")
            chroot("pacman -S --noconfirm deepin deepin-kwin deepin-extra xorg xorg-server lightdm")
            # enable deepin specific login style
            with open("/mnt/eupnea/etc/lightdm/lightdm.conf", "a") as conf:
                conf.write("greeter-session=lightdm-deepin-greeter")
            chroot("systemctl enable lightdm.service")
        case "budgie":
            print_status("Installing Budgie")
            chroot("pacman -S --noconfirm budgie-desktop budgie-desktop-view budgie-screensaver budgie-control-center "
                   "lightdm lightdm-gtk-greeter")
            chroot("systemctl enable lightdm.service")
        case "cli":
            print_status("Skipping desktop environment install")
        case _:
            print_error("Invalid desktop environment! Please create an issue")
            exit(1)
    stop_progress()  # stop fake progress
    print_status("Desktop environment setup complete")

    # enable networkmanager systemd service
    chroot("systemctl enable NetworkManager.service")

    # Configure sudo
    with open("/mnt/eupnea/etc/sudoers", "r") as conf:
        temp_sudoers = conf.readlines()
    # uncomment wheel group
    temp_sudoers[84] = temp_sudoers[84][2:]
    temp_sudoers[87] = temp_sudoers[87][2:]
    temp_sudoers[90] = temp_sudoers[90][2:]
    with open("/mnt/eupnea/etc/sudoers", "w") as conf:
        conf.writelines(temp_sudoers)

    print_status("Restoring pacman config")
    with open("/mnt/eupnea/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # comment out CheckSpace
    temp_pacman[34] = temp_pacman[34][1:]
    with open("/mnt/eupnea/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)

    # TODO: add eupnea to arch name
    # Add eupnea to version(this is purely cosmetic)
    with open("/mnt/eupnea/etc/os-release", "r") as f:
        os_release = f.readlines()
    os_release[0] = os_release[0][:-2] + ' (Eupnea)"\n'
    os_release[1] = os_release[1][:-2] + ' (Eupnea)"\n'
    with open("/mnt/eupnea/etc/os-release", "w") as f:
        f.writelines(os_release)

    print_status("Arch configuration complete")


# using arch-chroot for arch
def chroot(command: str):
    if verbose:
        bash(f'arch-chroot /mnt/eupnea bash -c "{command}"')
    else:
        bash(f'arch-chroot /mnt/eupnea bash -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output


if __name__ == "__main__":
    print_error("Do not run this file. Use main.py")
