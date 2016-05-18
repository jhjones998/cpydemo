from web_app import MaterializedPath
from plugins_and_tools import SAEnginePlugin, SATool
import cherrypy


def main(mount_path):
    SAEnginePlugin(cherrypy.engine, 'sqlite:///cpydemo.sqlite').subscribe()
    cherrypy.tools.db = SATool()
    cherrypy.tree.mount(
        MaterializedPath(),
        mount_path,
        {
            '/': {
                'tools.db.on': True,
                'request.methods_with_bodies': ('POST', 'PUT', 'PATCH'),
            }
        }
    )
    cherrypy.engine.start()
    cherrypy.engine.block()

main('/cpydemo')
