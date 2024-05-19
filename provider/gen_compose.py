import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Description: This is a template for the docker-compose file.
# You can use it as base for building your own custom docker-compose file.
TEMPLATE = """  provider_%%PROVIDER_NO%%:
    image: yagna-provider
%%TEMPLATE_PORTS%%    command: golemsp run --payment-network testnet --no-interactive
    devices:
      - /dev/kvm
    env_file:
      - node_env.env
    environment:
      - NODE_NAME=%%PROVIDER_NAME_PREFIX%%_%%PROVIDER_NO%%
      - SUBNET=%%SUBNET%%
    volumes:
      - './dock_prov_%%PROVIDER_NO%%/ya-provider:/root/.local/share/ya-provider'
      - './dock_prov_%%PROVIDER_NO%%/yagna:/root/.local/share/yagna'
"""

# Exposing ports is optional (enabled by default)
TEMPLATE_PORTS = """    ports:
      - '%%PORT_NO%%:7465'
"""


# Description: This script generates a docker-compose file for running multiple providers on the same machine.
def generate_compose_file(
        number_of_providers: int = 2,
        expose_ports: bool = False,
        provider_name_prefix: str = "dock-prov",
        subnet: str = "change_me") -> str:
    comp_file = ""
    comp_file += "services:\n"
    for provider_no in range(0, number_of_providers):
        entr = TEMPLATE.replace("%%PROVIDER_NO%%", str(provider_no))
        if expose_ports:
            ports = TEMPLATE_PORTS.replace("%%PORT_NO%%", str(8555 + provider_no))
        else:
            ports = ""
        entr = entr.replace("%%TEMPLATE_PORTS%%", ports)
        entr = entr.replace("%%PROVIDER_NAME_PREFIX%%", provider_name_prefix)
        entr = entr.replace("%%SUBNET%%", subnet)
        comp_file += entr
    return comp_file


def main():
    args = argparse.ArgumentParser()

    args.add_argument("-n", "--num-providers", type=int, help="Number of providers to be generated", default=2)
    args.add_argument("--no-ports", type=bool, help="Hide yagna ports")
    args.add_argument("-o", "--output-file", type=str, help="Output file generated",
                      default="docker-compose_generated.yml")
    args.add_argument("--provider-name-prefix", type=str, help="Provider name prefix",
                      default="dock-prov")
    args.add_argument("--subnet", type=str, help="Subnet for the providers",
                      default="change_me")

    args = args.parse_args()
    num_prov = args.num_providers
    gen_file = generate_compose_file(
        number_of_providers=num_prov,
        expose_ports=not args.no_ports,
        provider_name_prefix=args.provider_name_prefix,
        subnet=args.subnet)

    with open(args.output_file, "w") as f:
        logger.info(f"Writing to file {args.output_file}")
        f.write(gen_file)


if __name__ == "__main__":
    main()
