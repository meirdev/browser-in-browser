FROM --platform=linux/x86_64 ubuntu:23.10

RUN \
    apt update && apt install -y \
    ca-certificates \
    curl \
    gnupg

RUN \
    curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    echo "deb https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

RUN apt update && apt install -y google-chrome-stable

EXPOSE 9222
