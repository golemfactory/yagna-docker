import sys


TEMPLATE = """  provider_%%PROVIDER_NO%%:
    image: provider
    build:
      context: .
      dockerfile: Dockerfile
      args:
        - 'YAGNA_VERSION=${YAGNA_VERSION}'
    ports:
      - '%%PORT_NO%%:7465'
    command: golemsp run --payment-network testnet --no-interactive
    devices:
      - /dev/kvm
    env_file:
      - node_env.env
    environment:
      - NODE_NAME=dock_prov_%%PROVIDER_NO%%
    volumes:
      - './dock_prov_%%PROVIDER_NO%%/ya-provider:/root/.local/share/ya-provider'
      - './dock_prov_%%PROVIDER_NO%%/yagna:/root/.local/share/yagna'
"""

# Description: This script generates a docker-compose file for running multiple providers on the same machine.
def generate_compose_file(number_of_providers: int = 2):
    comp_file = ""
    comp_file += "services:\n"
    for provider_no in range(0, number_of_providers):
        comp_file += (
        .replace("%%PROVIDER_NO%%", str(provider_no)).replace("%%PORT_NO%%", str(8555 + provider_no)))
    return comp_file


def main():
    num_prov = sys.argv[1] if len(sys.argv) > 1 else 2
    gen_file = generate_compose_file(num_prov)
    with open("docker-compose_generated.yml", "w") as f:
        f.write(gen_file)


if __name__ == "__main__":
    main()
