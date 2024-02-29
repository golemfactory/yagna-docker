# instructions

To select yagna version installed create file .env
Add for example
```YAGNA_VERSION=v0.14.0```

to install version 0.14.0

or 
```YAGNA_VERSION=pre-rel-v0.14.0```

for pre-les versions (basically tag created to test the release)

To add more providers duplicate entries in docker-compose

Run using:

```docker-compose up -d --build```

In node_env.env you can put environment variables for the node (both yagna, ya-provider, exe-unit and ya-runtime-vm)

In dock_prov_0 you can find all logs and db. Remove the files to clean data in yagna nodes.

