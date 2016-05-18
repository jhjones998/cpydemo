import cherrypy
import json
import urlparse
from sqlalchemy_orm import Path


class MaterializedPath(object):
    _root_path_exists = False

    def __init__(self):
        pass

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def default(self, *args, **kwargs):
        return getattr(self, cherrypy.request.method)()

    def _confirm_root_exists(self):
        if not self._root_path_exists:
            root_rec = cherrypy.request.db\
                .query(Path).filter(Path.path == '').first()
            if not root_rec:
                cherrypy.request.db.add(
                    Path(parent_path_id=None, path='', data='{"name": "root"}')
                )
            self._root_path_exists = True

        return self._root_path_exists

    def _get_path(self):
        self._confirm_root_exists()
        parsed_url = urlparse.urlparse(cherrypy.url())
        path = parsed_url.path
        while path[-1] == '/':
            path = path[:-1]

        return path.replace(cherrypy.request.script_name, '')

    def _clean_body(self, body):
        cleaned_params = {}
        body.pop('children', None)
        cleaned_params['href'] = body.pop('href', None)
        return body, cleaned_params

    def _list(self, real_path):
        path_res = cherrypy.request.db\
            .query(Path).filter(Path.path == real_path).limit(1).first()
        if path_res:
            data = json.loads(path_res.data)
            data['children'] = []
            data['href'] = cherrypy.url(real_path)
            for child in path_res.children:
                data['children'].append({'href': cherrypy.url(child.path)})

            return data

        raise cherrypy.NotFound(cherrypy.url(real_path))

    def _create(self, real_path, data):
        if real_path[0] != '/':
            real_path = '/' + real_path
        cherrypy.request.db.query(Path).filter(Path.path == real_path).delete()
        parent_path = '/'.join(real_path.split('/')[:-1])
        parent_rec = cherrypy.request.db\
            .query(Path).filter(Path.path == parent_path).first()

        if parent_rec:
            cherrypy.request.db.add(
                Path(
                    parent=parent_rec,
                    path=real_path,
                    data=json.dumps(data)
                )
            )

            return

        raise cherrypy.NotFound(cherrypy.url(parent_path))

    def _update(self, real_path, data):
        path_rec_q = cherrypy.request.db\
            .query(Path).filter(Path.path == real_path)
        path_rec = path_rec_q.first()

        if path_rec:
            path_rec_q.update(
                {
                    'data': json.dumps(data)
                }
            )

            return

        raise cherrypy.NotFound(cherrypy.url(real_path))

    def _delete(self, real_path):
        path_rec_q = cherrypy.request.db\
            .query(Path).filter(Path.path == real_path)
        path_rec = path_rec_q.first()

        if path_rec:
            path_rec_q.delete()

            return

        raise cherrypy.NotFound(cherrypy.url(real_path))

    def GET(self):
        return self._list(self._get_path())

    def POST(self):
        body, cleaned_params = self._clean_body(cherrypy.request.json)
        real_path = self._get_path()

        if cleaned_params['href']:
            while cleaned_params['href'][0] == '/':
                cleaned_params['href'] = cleaned_params['href'][1:]
            while cleaned_params['href'][-1] == '/':
                cleaned_params['href'] = cleaned_params['href'][:-1]
            new_real_path = real_path + cleaned_params['href']

            self._create(new_real_path, body)

        else:
            self._update(real_path, body)

        return self._list(real_path)

    def PUT(self):
        body = self._clean_body(cherrypy.request.json)[0]
        real_path = self._get_path()
        self._create(real_path, body)
        return self._list(real_path)

    def PATCH(self):
        body = self._clean_body(cherrypy.request.json)[0]
        real_path = self._get_path()
        self._update(real_path, body)
        return self._list(real_path)

    def DELETE(self):
        self._delete(self._get_path())
        cherrypy.response.status = 204
        return
