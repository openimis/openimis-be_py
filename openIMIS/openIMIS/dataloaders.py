from django.apps import apps


def get_dataloaders():
    dataloaders = dict()
    for app in apps.get_app_configs():
        if hasattr(app, "set_dataloaders"):
            app.set_dataloaders(dataloaders)

    return dataloaders
