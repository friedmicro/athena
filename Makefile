.ONESHELL:
REMOTE_USER = ${ATHENA_REMOTE_USER}
REMOTE_IP = ${ATHENA_REMOTE_IP}
REMOTE_PATH = ${ATHENA_REMOTE_PATH}

build: clean
	pyinstaller athena-shared.spec
	mv dist/athena-cli dist/athena
	mv dist/athena/athena-cli dist/athena/athena
	mv dist/scan_games dist/scanner
	mv dist/scanner/scan_games dist/scanner/scanner
	cd ..

dev-ncurses:
	python3 athena-ncurses.py

build-ncurses:
	pyinstaller athena-ncurses.py

dev-cli:
	python3 athena-cli.py

build-cli:
	pyinstaller athena-cli.py
	mv dist/athena-cli dist/athena
	mv dist/athena/athena-cli dist/athena/athena

dev-scanner:
	python3 scan_games.py

build-scanner:
	pyinstaller scan_games.py
	mv dist/scan_games dist/scanner
	mv dist/scanner/scan_games dist/scanner/scanner

dev-generator:
	python3 generators/generator.py

build-generator:
	pyinstaller generators/generator.py

dev-api:
	python3 athena-api.py

dev-api:
	pyinstaller athena-api.py

dev-desktop-gui:
	electron desktop-gui/main.js

dev-npm-desktop-gui:
	cd desktop-gui
	npm run start

build-desktop-gui:
	cp -r dist/ desktop-gui/tools
	rm -rf desktop-gui/tools/athena-ncurses
	rm -rf desktop-gui/tools/athena-client-daemon
	rm -rf desktop-gui/tools/athena-daemon
	cd desktop-gui
	npm run make
	npm run package
	cd ..

build-test: build
	./dist/generator/generator

build-test-ui: build-test
	./dist/athena/athena

build-test-daemon:
	cp daemon/config.json dist/
	cp initial_config.bin dist/

build-test-unix-daemon: build-test
	ssh -t -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${REMOTE_USER}@${REMOTE_IP} "sudo rm -rf ${REMOTE_PATH}; sudo mkdir ${REMOTE_PATH}"
	ssh -t -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${REMOTE_USER}@${REMOTE_IP} "sudo chown -R ${REMOTE_USER}:${REMOTE_USER} ${REMOTE_PATH}"
	scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r dist/* ${REMOTE_USER}@${REMOTE_IP}:${REMOTE_PATH}
	ssh -t -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${REMOTE_USER}@${REMOTE_IP} "sudo systemctl restart athena"

virtual-env:
	pyenv install 3.13.7
	pyenv virtualenv 3.13.7 athena

deps:
	pip install -r requirements.txt
	cd desktop-gui
	npm install
	cd ..

dep-windows: deps
	pip install windows-curses

clean:
	rm -rf build
	rm -rf dist
	rm -rf desktop-gui/out
	rm -rf desktop-gui/tools
