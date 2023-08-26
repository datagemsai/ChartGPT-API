from app import ENV, db, logger


def check_maintenance_mode():
    """Get maintenance_mode flag from Firestore, or set if it doesn't exist"""
    if ENV == "LOCAL":
        return False
    
    maintenance_mode_ref = db.collection('app_settings').document('maintenance_mode')
    maintenance_mode_data = maintenance_mode_ref.get().to_dict()

    if maintenance_mode_data is None:
        maintenance_mode_data = {'value': False}
        maintenance_mode_ref.set(maintenance_mode_data)

    maintenance_mode = maintenance_mode_data.get('value', False)

    if maintenance_mode:
        logger.info("Application in maintenance mode")

    return maintenance_mode
