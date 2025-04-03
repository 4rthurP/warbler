from watchers.file_watcher import FileWatcher

test_service = {
    'name': 'test_service',
    'source': 'test_source',
    'service_type': 'test',
    'config': {
        'test': 'test'
    }
}

test_notifier = {
    'name': 'test_notifier',
    'source': 'test_source',
    'notifier_type': 'test',
    'config': {
        'test': 'test'
    }
}


config = {
    'watchers': [
        {
            'class': FileWatcher,
            'name': 'test',
            'source': '',
            'services': [test_service],
            'notifiers': [test_notifier],
        }
    ]
}