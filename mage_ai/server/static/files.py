from tornado.web import StaticFileHandler as TornadoStaticFileHandler


class StaticFileHandler(TornadoStaticFileHandler):
    def check_origin(self, origin):
        allowed_origins = ['https://mage-audit.aws.khushibaby.org']
        return origin in allowed_origins
    def set_default_headers(self):
        super().set_default_headers()
        self.set_header('Access-Control-Allow-Origin', 'https://mage-audit.aws.khushibaby.org')
        self.set_header(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'
        )
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')

    def set_extra_headers(self, path):
        self.set_header('Access-Control-Allow-Origin', 'https://mage-audit.aws.khushibaby.org')
        self.set_header(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'
        )
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')

    def prepare(self):
        super().prepare()
        self.set_header('Access-Control-Allow-Origin', 'https://mage-audit.aws.khushibaby.org')

    def write_error(self, status_code, **kwargs):
        self.set_header('Access-Control-Allow-Origin', 'https://mage-audit.aws.khushibaby.org')
        self.set_header(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'
        )
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        if status_code == 404:
            self.write({'error': 'File not found'})
        else:
            self.write({'error': 'Internal server error'})
