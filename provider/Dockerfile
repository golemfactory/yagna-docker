ARG YAGNA_VERSION=v0.15.0-deposits-beta5

# Full python toolset for ease of development
# If you need something smaller, you can use ubuntu slim or alpine without python
FROM debian:bookworm

# This tools are not needed but are helpful for debugging
RUN apt-get update -y
RUN apt-get install -y build-essential net-tools iputils-ping curl vim git wget unzip jq dnsutils tcpdump procps

# Download official installer
RUN curl -L https://join.golem.network/as-provider --output as-provider.sh
RUN chmod +x as-provider.sh

# Installer is checking if binaries in in this PATH, so we need to add it beforehand
ENV PATH="${PATH}:/root/.local/bin"

# switch to any yagna version if necessery
ARG YAGNA_VERSION

# yagna installator normally asks for user input, so we need to set some environment variables to avoid that
RUN GOLEM_ACCEPT_TOS=yes BATCH_MODE=yes YA_INSTALLER_CORE=${YAGNA_VERSION} ./as-provider.sh
RUN wget https://github.com/golemfactory/golem-ftp/releases/download/v0.4.0-rc2/gftp-linux-x86_64.tar.xz && tar -xf gftp-linux-x86_64.tar.xz && rm gftp-linux-x86_64.tar.xz && mv gftp /usr/local/bin/



