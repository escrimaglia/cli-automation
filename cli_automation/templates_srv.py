import json
from .files_srv import ManageFiles

class Templates():
    def __init__(self, set_verbose: dict):
        self.logger = set_verbose.get('logger')
        self.file = ManageFiles(logger=self.logger)

    async def create_template(self, file_name: str = None) -> None:
        hosts = {   
            'devices': [
                {
                    'host': 'X.X.X.X',
                    'username': 'user',
                    'password': 'password',
                    'device_type': 'type',
                    'session_log': 'cla.log',
                    'ssh_config_file': '~/.ssh/config'
                }
            ]
        }
        
        commands = {
            'X.X.X.X': {
                'commands': [
                    'show version',
                    'show ip int brief'
                ]
            }
        }

        config = {
            "tunnel": False,
            "version": "1.0.4",
            "app": "cla"
        }

        templates = [hosts, commands, config]
        if file_name is None:
            for template in templates:
                var_name = [name for name, value in locals().items() if value is template][0]
                if var_name != "config":
                    await self.file.create_file("template_"+var_name+".json", json.dumps(template, indent=2))
                else:
                    await self.file.create_file(var_name+".json", json.dumps(template, indent=2))
        else:
            file_name = file_name.split(".")[0] if "." in file_name else file_name
            if file_name in templates:
                var_name = [name for name, value in locals().items() if value is template][0]
                if file_name != "config":
                    await self.file.create_file("template_"+var_name+".json", json.dumps(file_name, indent=2))
                else:
                    await self.file.create_file(var_name+".json", json.dumps(file_name, indent=2))
            else:
                print (f"** Error creating the template {var_name}. The template does not exist")
                self.logger.error(f"Error creating the template {var_name}. The template does not exist")
                raise SystemExit(1)

        self.logger.info("** All the templates have been successfully created")