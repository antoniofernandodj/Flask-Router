import os
import importlib
import pkgutil
from quart import Quart

Module = type(pkgutil)
modules_visited = set()



class FlaskRouter:
    def __init__(self, app):
        self.app = app

    def register_pages(self, methods:list=['GET'], root_name:str='pages'):
        try:
            pages = importlib.import_module(f'{root_name}')
        except ImportError as error:
            print(f"Error importing 'pages': {error}")
            return

        self.check_and_register_package(
            root_name=root_name,
            current_package=pages,
            methods=methods,
            package_path=pages.__path__[0],
            app=self.app
        )



    def check_name(self, prefix: str, methods: list):
        name = prefix.replace("/", ".")[1:]
        name = name.replace('_', ':')
        
        replacements = {
            '[': '',
            ']': '',
            ',': ':',
            "'": '',
            ' ': ''
        }
        
        methods_str = str(methods)
        for char, replacement in replacements.items():
            methods_str = methods_str.replace(char, replacement)
        methods_str = ':' + methods_str
        
        complete_name = name + methods_str
        complete_name = 'index' if complete_name.startswith(':') else complete_name
        return complete_name


    def check_path(self, path: str):
        replacements = {
            '(': '<',
            ')': '>',
            '_': ':',
        }
        strip_name = path.lstrip('/')

        for char, replacement in replacements.items():
            strip_name = strip_name.replace(char, replacement)

        return strip_name


    def check_and_register_package(
            self,
            root_name: str,
            current_package: Module,
            methods: list,
            package_path: str,
            app: Quart
        ):
        try:
            prefix = package_path.split(f'/{root_name}')[1]
            name = current_package.__name__.split('.')[-1]
        except IndexError:
            prefix = None
            name = 'index'

        try:
            if f'{prefix}.{name}' == f'.{root_name}':
                name = 'index'
            checked_prefix = self.check_path(path=prefix)
            name = self.check_name(prefix, methods)
            try:
                app.add_url_rule(
                    f'/{checked_prefix}', name,
                    importlib.import_module(f'{current_package.__name__}.index').index,
                    methods=methods
                )
            except:
                app.add_url_rule(
                    f'/{prefix}', name,
                    importlib.import_module(f'{current_package.__name__}.index').index,
                    methods=methods
                )

        except AttributeError as error:
            print(f"Error registering route for {name}: {error}")
            
        modules_visited.add(current_package.__name__)
        for mod in pkgutil.iter_modules([package_path]):
            if mod.name not in modules_visited:
                try:
                    if mod.ispkg:
                        mod_path = os.path.join(package_path, mod.name)
                        sub_package = importlib.import_module(
                            f"{current_package.__name__}.{mod.name}"
                        )
                        self.check_and_register_package(
                            root_name,
                            sub_package,
                            methods,
                            mod_path, 
                            app
                        )
                except Exception as error:
                    print(f"Error while processing {mod.name}: {error}")


