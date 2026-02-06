## Commonly asked questions on Athena

### Why did you build Athena?
The simple version is...no one else was doing what I wanted for my desktop. I wanted a simple way to run any of my applications and have them listed irrespective of how they were installed. Today this includes things like Android support, old web games, emulators, remotely installed applications, and a plugin system for adding more types of programs to be detected. And of course works across every major operating desktop system. I also like game streaming, but I like owning my hardware; this gives me that.

Athena over the years has evolved from a shell script to an application with a CLI, API, and programmable library. That and support for multiple operating systems. I fully intend to maintain it and continue to utilize it for the foreseeable future.

If you want more context, feel free to check project history.

### Usecase
For me this is primarily used to run applications on my laptop from a different room, my thin client (a very weak machine that is mostly used for web browsing and programming), and when traveling. That and to keep everything in one place. As a big fan of game preservation and as someone who regularly maxs out 100% of the machine they connect to with various applications, I like that I know I am not going to cause problems for anything else I am doing on my machine. It's also a good way to get a little extra performance out of an application (as the machine I am connecting to doesn't have a chat program, web browser open, music streaming, etc). Encoding with sunshine is around 2-3ms for my setup locally.

I use this workflow daily and any breakage is likely be fixed in hours because it breaks my own ability to use my machine. Plus there is something nice about running: `athena "Cyberpunk 2077"` and playing it comfortably from another room or my laptop.

### Why Python?
It's a good glue language. We can always add in Rust or C code if necessary for speed.

### A lot of dependencies here
Athena integrates with a lot of programs. Calling these dependencies through a system call makes a lot of sense rather than integration with a nontrivial number of the applications directly or trying to get changes merged into all of them. Of note is the Athena daemon being separate from the Sunshine daemon; Athena does write an asset file which is commonly used by Sunshine to launch the program requested, but attempting to integrate this change into every Sunshine fork or maintaining our own...not worth the complexity.
