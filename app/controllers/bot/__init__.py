from aiogram.loggers import dispatcher, event, middlewares, scene, webhook

# Disables aiogram loggers
dispatcher.propagate = False
event.propagate = False
middlewares.propagate = False
scene.propagate = False
webhook.propagate = False
