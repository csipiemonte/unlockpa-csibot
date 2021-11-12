# ==================== Base Service Error Class ====================


class ServiceError(Exception):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    @property
    def dict(self):
        return {
            'code': self.code,
            'description': self.description
        }


# ==================== No Error Class ====================


class ServiceNoError(ServiceError):

    def __init__(self):
        self.code = 0

    @property
    def dict(self):
        return {
            'code': self.code
        }


# ==================== All Services Errors (10) ====================


class ServiceNotFoundError(ServiceError):

    def __init__(self, service):
        self.code = 10
        self.description = f'Service {service} not found'


class ServiceDictError(ServiceError):

    def __init__(self, service, description):
        self.code = 11
        self.description = f'{description} ({service})'


class DBConnectionError(ServiceError):

    def __init__(self):
        self.code = 12
        self.description = 'Database connection failed'


class BotmanagerDown(ServiceError):

    def __init__(self):
        self.code = 13
        self.description = 'Botmanager is not responding'


class DBOperationError(ServiceError):

    def __init__(self, description):
        self.code = 14
        self.description = description


# ==================== Ping Service Errors (20) ====================


class PingGenericError(ServiceError):

    def __init__(self, description=None):
        self.code = 20
        self.description = description or 'Unknown error in the service ping'


# ==================== Model Service Errors (30) ====================


class ModelGenericError(ServiceError):

    def __init__(self, description=None):
        self.code = 30
        self.description = description or 'Unknown error in the service model'


class ModelBadRequestError(ServiceError):

    def __init__(self):
        self.code = 31
        self.description = 'id (int) or description (str) required'


class PickleNotFoundError(ServiceError):

    def __init__(self, file):
        self.code = 32
        self.description = f'Model file for the bot not found: {file}'


# ==================== Train Service Errors (40) ====================


class TrainGenericError(ServiceError):

    def __init__(self, description=None):
        self.code = 40
        self.description = description or 'Unknown error in the service train'


class PathNotFoundError(ServiceError):

    def __init__(self, path):
        self.code = 41
        self.description = f'Directory {path} not found'


class BotNotFoundError(ServiceError):

    def __init__(self, idbot):
        self.code = 42
        self.description = f'Bot {idbot} not found'


class BotNotTrained(ServiceError):

    def __init__(self, idbot):
        self.code = 43
        self.description = f'Bot {idbot} is created but not trained yet'


class BotTopicsError(ServiceError):
    def __init__(self, idbot, ntopics, qnumb):
        self.code = 44
        self.description = f'Bot {idbot} not trained: topic numbers {ntopics} must be less than number of questions {qnumb}'


class BotClusterError(ServiceError):
    def __init__(self, idbot, ncluster, qnumb):
        self.code = 45
        self.description = f'Bot {idbot} not trained: cluster numbers {ncluster} must be less than number of questions {qnumb}'


class W2vFileError(ServiceError):
        def __init__(self, idbot, file):
            self.code = 46
            self.description = f'Word2vec input file {file} not found or not well-formatted for Bot {idbot}'

# ==================== Insert Service Errors (50) ====================


class InsertGenericError(ServiceError):

    def __init__(self, description=None):
        self.code = 50
        self.description = description or 'Unknown error in the service insert'


# ==================== Remove Service Errors (60) ====================


class RemoveGenericError(ServiceError):

    def __init__(self, description=None):
        self.code = 60
        self.description = description or 'Unknown error in the service remove'


# ==================== Running Service Errors (70) ====================


class RunningGenericError(ServiceError):

    def __init__(self, description=None):
        self.code = 70
        self.description = description or 'Unknown error in the service running'


# ==================== Monitor Service Errors (80) ====================


class MonitorGenericError(ServiceError):

    def __init__(self, description=None):
        self.code = 80
        self.description = description or 'Unknown error in the service monitor'


# ==================== Update Service Errors (90) ====================


class UpdateGenericError(ServiceError):

    def __init__(self, description=None):
        self.code = 90
        self.description = description or 'Unknown error in the service update'


class InstanceIsDownError(ServiceError):

    def __init__(self, endpoint):
        self.code = 91
        self.description = f'Chatbot at {endpoint} is down'
