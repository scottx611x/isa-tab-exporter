# isa-tab-exporter/docker_context

This Dockerfile is used to build [scottx611x/aws-linux-python-3.6](https://hub.docker.com/r/scottx611x/aws-linux-python-3.6/)

Some dependencies of the [`isatools`](https://github.com/ISA-tools/isa-api/blob/v0.10.3/setup.py#L49) requirement for our Lambda (namely `numpy`) are required to be built on the same OS that the Lamba will be invoked within.

Here we simply reference [`amazonlinux`](https://hub.docker.com/_/amazonlinux/) as our parent image and install the same `python` runtime, and `pip` used in our Lambda (`Python 3.6`).