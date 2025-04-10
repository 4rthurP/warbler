# Warbler
Warbler is a work-in-progress framework aiming to help monitor sources, structures logs and send notifications to multiple outputs.

# Setup
## Recommended installation
The recommended install method is via docker-compose

```
warbler:
    build:
        context: ./warbler/
        dockerfile: Dockerfile
        args:
            ENV_PATH: '.env'
            CRON_SCHEDULE: '5 * * * *'
    restart: unless-stopped
    tty: true
    volumes:
        - ./path/to/your/cron.log:/var/log/cron.log
```

## env variables
```
# Required env variables
WARBLER_DATABASE_HOST=
WARBLER_DATABASE_PORT=
WARBLER_DATABASE_USER=
WARBLER_DATABASE_PASSWORD=
WARBLER_DATABASE_NAME=

# Optional env variables
LOCAL_TZ='Europe/Paris'
```

## Configuration
Configuration is done through a dictionnary stored in src/config.py
Use the example.config.py file to create your config  file.

The dictionary should contain at least a 'watchers' key containing a list of watcher's configuration.
A watcher configuration should be a dictionary containing a class, name, source and list of notifiers.

```
config = {
    'watchers': [
        {
            'class': LogFileWatcher,
            'name': 'test',
            'source': "/var/log/cron.log",
            'notifiers': [
                    SlackNotifier(
                    name='slack_cron',
                    webhook_url=SLACK_WEBHOOK_URL,
                )
            ]
        }
    ]
}
```