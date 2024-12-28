class Configuration(object):
    """
    A class used for configuring the SDK by a user.
    This class need not be instantiated and all properties and methods
    are accessible without instance creation.
    """

    # An enum for SDK environments
    class Environment(object):
        """
        Describe the setting where software and other products are actually put
        into operation for their intended uses by end users
        """
        SANDBOX = 'sandbox'
        PRODUCTION = 'production'

    # An enum for API servers
    class Server(object):
        BASE_URL = 'base_url'

    # The environment in which the SDK is running
    environment = Environment.PRODUCTION

    # All the environments the SDK can run in
    environments = {
        Environment.SANDBOX: {
            Server.BASE_URL: 'https://api-sandbox.tamara.co',
        },
        Environment.PRODUCTION: {
            Server.BASE_URL: 'https://api.tamara.co',
        },
    }

    # The api_token to use with basic authentication
    api_token = None

    @classmethod
    def get_base_uri(cls, server=Server.BASE_URL):
        """
        Generates the appropriate base URI for the environment and the server.
        """
        return cls.environments[cls.environment][server]
