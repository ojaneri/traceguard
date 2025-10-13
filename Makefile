PY=python3

setup: worker/.venv/bin/activate
	. $< && pip install -r worker/requirements.txt

worker/.venv/bin/activate:
	$(PY) -m venv worker/.venv

serve:
	php -S 0.0.0.0:8181 -t public

clean:
	rm -rf storage/*