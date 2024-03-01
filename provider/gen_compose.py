import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Description: This is a template for the docker-compose file.
# You can use it as base for building your own custom docker-compose file.


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
        entr = TEMPLATE.replace("%%PROVIDER_NO%%", str(provider_no))
        entr = entr.replace("%%PORT_NO%%", str(8555 + provider_no))
        comp_file += entr
    return comp_file


def main():
    args = argparse.ArgumentParser()

    args.add_argument("-n", "--num-providers", type=int, help="Number of providers to be generated", default=2)
    args.add_argument("-o", "--output-file", type=str, help="Output file generated",
                      default="docker-compose_generated.yml")

    args = args.parse_args()
    num_prov = args.num_providers
    gen_file = generate_compose_file(num_prov)
    with open(args.output_file, "w") as f:
        logger.info(f"Writing to file {args.output_file}")
        f.write(gen_file)


if __name__ == "__main__":
    main()
