# -*- coding: utf-8 -*-

"""
 (c) 2015 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>

"""

import flask

import pagure
import pagure.exceptions
import pagure.lib
from pagure import SESSION
from pagure.api import API, api_method, APIERROR


@API.route('/<repo>/git/tags')
@API.route('/fork/<username>/<repo>/git/tags')
@api_method
def api_git_tags(repo, username=None):
    """
    Project git tags
    ----------------
    List the tags made on the project Git repository.

    ::

        GET /api/0/<repo>/git/tags

    ::

        GET /api/0/fork/<username>/<repo>/git/tags

    Sample response
    ^^^^^^^^^^^^^^^

    ::

        {
          "tags": ["0.0.1", "0.0.2"]
        }

    """
    repo = pagure.lib.get_project(SESSION, repo, user=username)

    if repo is None:
        raise pagure.exceptions.APIError(404, error_code=APIERROR.ENOPROJECT)

    tags = pagure.lib.git.get_git_tags(repo)

    jsonout = flask.jsonify({'tags': tags})
    return jsonout
