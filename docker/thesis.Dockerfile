FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        biber \
        ca-certificates \
        latexmk \
        make \
        texlive-fonts-recommended \
        texlive-lang-greek \
        texlive-latex-extra \
        texlive-xetex \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/thesis
