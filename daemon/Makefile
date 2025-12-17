REMOTE_USER = ${ATHENA_REMOTE_USER}
REMOTE_IP = ${ATHENA_REMOTE_IP}
REMOTE_PATH = ${ATHENA_REMOTE_PATH}

build: clean
	pyinstaller main.py
	mv dist/main/_internal dist/
	mv dist/main/main dist/athena
	rm -rf dist/main

build-test: build
	cp config.json dist/
	cp initial_config.bin dist/

build-test-unix: build-test
	ssh -t -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${REMOTE_USER}@${REMOTE_IP} "sudo rm -rf ${REMOTE_PATH}; sudo mkdir ${REMOTE_PATH}"
	ssh -t -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${REMOTE_USER}@${REMOTE_IP} "sudo chown -R ${REMOTE_USER}:${REMOTE_USER} ${REMOTE_PATH}"
	scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r dist/* ${REMOTE_USER}@${REMOTE_IP}:${REMOTE_PATH}
	ssh -t -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${REMOTE_USER}@${REMOTE_IP} "sudo systemctl restart athena"

deps:
	pip install pyinstaller
	pip install cryptography

clean:
	rm -rf build
	rm -rf dist
