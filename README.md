# Dynamic JS Injector

A lightweight, containerized loader that serves dynamically generated JavaScript injection files based on the requested endpoint URL. 

This is designed for systems that only support a single JavaScript injection URL (like a PBX), allowing you to bypass that limitation and inject multiple, role-specific scripts dynamically without restarting services.

## PBX Integration

To use this service, you must point your PBX to the Traefik-routed domain of this container. 
Update the **`EXTRA_JS`** UI configuration in your PBX to point to the desired role endpoint.

Example `EXTRA_JS` value: 
`https://injector.yourdomain.com/superuser`

## Prerequisites

- Docker and Docker Compose
- Traefik configured as a reverse proxy on a shared external Docker network
- A valid DNS record pointing to your Docker host for the injector domain

## Deployment

1. **Clone the repository:**
```bash
git clone https://github.com/your-org/js-injector.git
cd js-injector
```

2. **Configure environment variables:**
Create a .env file to define your routing.
```bash
cp .env.example .env
vim .env
```

3. **Edit the configuration file:**

```bash
vim config/endpoints.json
```

**Example endpoints.json:**
```JSON
{
    "default":[
        "https://cdn.example.com/js/fallback.js"
    ],
    "superuser":[
        "https://cdn.example.com/js/vendor.js",
        "https://cdn.example.com/js/superuser-tools.js"
    ]
}
```

4. **Build and start the container:**
```bash
docker compose up -d --build
```

5. **Verify deployment:**
Check the logs to ensure Uvicorn started and the configuration was read successfully.
```bash
docker compose logs -f
```


# Operation & Configuration Management

The application loads its routing configuration entirely from `config/endpoints.json`.

You can define any arbitrary endpoint URL by adding a new key to the JSON file. If an unconfigured endpoint is requested, the system will attempt to serve the `default` key. If no default exists, it returns a `404 Not Found`.

### Dynamically Updating Scripts (No Downtime)

To add, remove, or modify the injected scripts, simply edit the JSON file:
```bash
vim config/endpoints.json
```

**Do not restart the container.**

The application caches the configuration in memory and monitors the file's modification time (mtime). Upon saving the file, the next HTTP request will automatically trigger a cache invalidation and load the new script list instantly.

If you introduce a JSON syntax error, the application logs the error and safely continues serving the last-known-good configuration to prevent production outages.
