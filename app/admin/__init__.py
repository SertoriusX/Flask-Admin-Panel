# Admin registry - register modules here
ADMIN_MODELS = {}

def register_model(name, model):
    """Register a model to admin"""
    ADMIN_MODELS[name] = model
