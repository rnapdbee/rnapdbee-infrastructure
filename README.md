# rnapdbee-infrastructure

## Cloning with submodules

To clone this repository along with all its submodules, use the following command:

```bash
git clone --recurse-submodules https://github.com/rnapdbee/rnapdbee-infrastructure.git
```

If you have already cloned the repository without submodules, you can initialize and update them with:

```bash
git submodule update --init --recursive
```

To pull the latest changes for the main repository and all submodules, use:

```bash
git pull --recurse-submodules
```

## Usage

### Local Development

For local development, use the following command to build and start all services:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

The development environment runs a reverse proxy as part of Docker Compose without HTTPS support. The application will be available at [http://localhost](http://localhost).

The frontend's API host defaults to `http://localhost`. When the development stack runs on a remote machine (e.g. a VM) and is accessed from another computer, override it with the hostname or IP address that the user's browser can reach:

```bash
API_HOST=http://<vm-hostname-or-ip> docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Note that `API_HOST` is a build-time setting baked into the frontend bundle, so the frontend image must be rebuilt (`--build`) after changing it. The given host must be reachable from the browser, not just from inside the Docker network.

To stop the services, use:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

### Production

For production deployment, use the following command:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

This setup expects that a reverse proxy with Let's Encrypt is installed and configured on the host OS.

To stop the services, use:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

## Funding

This work was supported by the National Science Centre, Poland (Narodowe Centrum Nauki) under grant No. 2023/51/D/ST6/01207, "Exploring Multiple Loop Motifs in RNA Structures".
