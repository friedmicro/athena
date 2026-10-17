# athena
There's a lot more information on Athena on my website with respect to the writeup on what this program is. http://git.friedmicro-lab.org/Homelab_Infra_Public/arch-upstream-recompile

If you want a bit of history on what this is the bulk of the writeup is on there. But a short summary here.

Athena is an application launcher designed to unify launching applications across local and remote systems. It's designed so that opening any program is a simple command and remote systems can have their state properly handled by automated tooling rather than by a user. It's core usecase is laptops and thin clients.

There's a lot of supported areas\features, but a short list:
* Waydroid integration
* Emulator integration (configurable by the user)
* Streaming protocols: VNC, Sunshine\Moonlight, RDP
* Launching applications through steam on local and remote
* Application scanning\generating lists of installed applications on local and remote systems
* Time management\time limits for blocking launching the application during certain days\times or even based upon an external timekeeper\timeclock API
* Multiple-device configuration
* Automated filtering of unreachable services (will not show games installed remotely if the machine cannot be reached)
* CLI interface for launching applications, generating application list, controling remote system state
* Ncurses interface for Linux, Mac, and Windows (largely untested on Windows)
* Web games\applications including fullscreen\kiosk mode integration
* Delays in shutdown\background daemon to manage remote system state
* Script hooks for: starting remote machine, stopping remote machine, running an script on the remote machine before the application starts starts (ex fixing settings), running a script on the remote machine when the application stops (ex backing up data or rebooting a VM to get around issues)
* REST API integration for custom tooling
* Remote daemon support (running scripts on the remote or scanning for applications) on: Mac, Linux, and Windows
* Plain script overrides for unsupported features

## Why
The simple version is when this was written there really wasn't a lot of good tooling for controling a remote system and I got tired of the tedium of jumping between applications\operating systems manually. The additional friction greatly reduced my enjoyment and I couldn't easily move away from application streaming due to my more powerful compute system needing to be in a different room for VR just due to space. So I opted to write some code to streamline this process and make it a much more enjoyable experience to use. This is an application that gets use by me multiple times a week.

## Additional projects:
Athena on my system makes use of a set of binaries for controlling the remote machine state with the hooks in the project. I opted to make these a seperate project, but it is available here for the curious: https://github.com/friedmicro/os-control-binaries
