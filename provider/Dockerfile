FROM python:latest
RUN apt-get update -y
RUN apt-get install -y build-essential net-tools iputils-ping curl vim git wget unzip jq dnsutils tcpdump
RUN pip install --upgrade pip

RUN curl -L https://join.golem.network/as-provider --output as-provider.sh
RUN chmod +x as-provider.sh
ENV PATH="${PATH}:/root/.local/bin"
RUN GOLEM_ACCEPT_TOS=yes BATCH_MODE=yes ./as-provider.sh




