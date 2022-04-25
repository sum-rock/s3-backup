compile-requirements:
	pip install --no-cache-dir -U pip-tools && \
	pip-compile requirements/base.in &> requirements/base.txt && \
	pip-compile requirements/dev.in &> requirements/dev.txt

install-dev-requirements:
	pip install --no-cache-dir -U pip && \
	pip install --no-cache-dir -r requirements/dev.txt
