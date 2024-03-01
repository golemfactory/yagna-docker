# Notes

Running provider with runtime vm is not supported on OSX

On Windows it works if you have Docker Desktop with WSL2 backend installed.

# instructions

To select yagna version installed create file .env
Add for example
```YAGNA_VERSION=v0.14.0```

to install version 0.14.0

or 
```YAGNA_VERSION=pre-rel-v0.15.0-rc16```

for pre-les versions (basically tag created to test the release)

To add more providers duplicate entries in docker-compose

Run using:

```docker-compose up -d --build```

In node_env.env you can put environment variables for the node (both yagna, ya-provider, exe-unit and ya-runtime-vm)

In dock_prov_0 you can find all logs and db. Remove the files to clean data in yagna nodes.

# useful tricks

To see current logs of yagna nodes run:

```docker-compose logs```

To run yagna command run when your container are running:

```docker-compose exec provider_0 yagna payment status```

```docker-compose exec provider_1 yagna payment status```

You can run other commands in yagna api to communicate with the yagna nodes.

All files are mapped to your local filesystem so you can access yagna and ya-provider logs and databases.

