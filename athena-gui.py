#!/usr/bin/env python3
from config_lib.install import InstallConfig, create_initial_configs
from gui.app import AthenaApp


def main():
    create_initial_configs(InstallConfig(), skip_generator=True)

    app = AthenaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
