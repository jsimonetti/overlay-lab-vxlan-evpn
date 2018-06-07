FROM python:3.6
RUN set -x && \
	pip install nornir
VOLUME [ "/nornir" ]
WORKDIR "/nornir"
ENTRYPOINT [ "/usr/local/bin/python" ]
