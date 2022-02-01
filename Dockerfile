# syntax=docker/dockerfile:1
FROM deniskhodus/python-yarn

RUN mkdir /opt/project
WORKDIR /opt/project
RUN python3 -m venv .venv
RUN source .venv/bin/activate
RUN pip install wefram
