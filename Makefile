PY=python3

setup:
	cd worker && $(PY) -m venv .venv && . worker/.venv/bin/activate && pip install -r worker/requirements.txt && $(PY) -m playwright install --with-deps chromium

serve:
	php -S 0.0.0.0:8080 -t public

clean:
	rm -rf storage/*