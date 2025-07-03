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

## Usage

Before starting, create an empty environment file for the adapters service:
```bash
touch rnapdbee-adapters/.env
```

To build and start all services, run:
```bash
docker-compose up --build -d
```

The application will be available at [http://localhost](http://localhost).

To stop the services, use:
```bash
docker-compose down
```
