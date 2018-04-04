# coding=utf-8

"""
 (c) 2017 - Copyright Red Hat Inc

 Authors:
   Pierre-Yves Chibon <pingou@pingoured.fr>
   Vivek Anand <vivekanand1101@gmail.com>

"""

__requires__ = ['SQLAlchemy >= 0.8']
import pkg_resources

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import pagure.config
import pagure.lib
import tests


class TestStarProjectUI(tests.SimplePagureTest):
    def setUp(self):
        """ Set up the environnment, ran before every tests. """
        super(TestStarProjectUI, self).setUp()

        tests.create_projects(self.session)
        tests.create_projects_git(os.path.join(self.path, 'repos'), bare=True)

    def _check_star_count(self, data, stars=1):
        """ Check if the star count is correct or not """
        output = self.app.get(
            '/test/', data=data, follow_redirects=True)
        if stars == 1:
            self.assertIn(
                '<a href="/test/stargazers/" class="btn '
                'btn-sm btn-primary">1</a>',
                output.get_data(as_text=True)
            )
        elif stars == 0:
            self.assertIn(
                '<a href="/test/stargazers/" class="btn '
                'btn-sm btn-primary">0</a>',
                output.get_data(as_text=True)
            )

    def test_star_project_no_project(self):
        """ Test the star_project endpoint. """

        # No such project
        output = self.app.post('/test42/star/1')
        self.assertEqual(output.status_code, 404)

    def test_star_project_no_csrf(self):
        """ Test the star_project endpoint for the case when there
        is no CSRF token given """

        user = tests.FakeUser()
        user.username = 'pingou'
        with tests.user_set(self.app.application, user):

            data = {}
            output = self.app.post(
                '/test/star/1', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 400)

    def test_star_project_invalid_star(self):
        """ Test the star_project endpoint for invalid star """

        user = tests.FakeUser()
        user.username = 'pingou'
        with tests.user_set(self.app.application, user):
            csrf_token = self.get_csrf()
            data = {
                'csrf_token': csrf_token,
            }
            output = self.app.post(
                '/test/star/2', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 400)
            self._check_star_count(data=data, stars=0)

    def test_star_project_valid_star(self):
        """ Test the star_project endpoint for correct star """

        user = tests.FakeUser()
        user.username = 'pingou'
        with tests.user_set(self.app.application, user):
            csrf_token = self.get_csrf()
            data = {
                'csrf_token': csrf_token,
            }

            # try starring the project for pingou
            output = self.app.post(
                '/test/star/1', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertIn(
                '</button>\n                      You starred '
                'this project\n                    </div>',
                output.get_data(as_text=True)
            )

            # check home page of project for star count
            self._check_star_count(data=data, stars=1)

            # try unstarring the project for pingou
            output = self.app.post(
                '/test/star/0', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertIn(
                '</button>\n                      You unstarred '
                'this project\n                    </div>',
                output.get_data(as_text=True)
            )
            self._check_star_count(data=data, stars=0)

    def test_repo_stargazers(self):
        """ Test the repo_stargazers endpoint of pagure.ui.repo """

        # make pingou star the project
        # first create pingou
        user = tests.FakeUser()
        user.username = 'pingou'
        with tests.user_set(self.app.application, user):
            csrf_token = self.get_csrf()
            data = {
                'csrf_token': csrf_token,
            }

            output = self.app.post(
                '/test/star/1', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertIn(
                '</button>\n                      You starred '
                'this project\n                    </div>',
                output.get_data(as_text=True)
            )
            self._check_star_count(data=data, stars=1)

        # now, test if pingou's name comes in repo stargazers
        output = self.app.get(
            '/test/stargazers/'
        )
        self.assertIn(
            '<title>Stargazers of test  - Pagure</title>',
            output.get_data(as_text=True)
        )
        self.assertIn(
            '<a href="/user/pingou">pingou\n              </a>',
            output.get_data(as_text=True)
        )

        # make pingou unstar the project
        user = tests.FakeUser()
        user.username = 'pingou'
        with tests.user_set(self.app.application, user):
            csrf_token = self.get_csrf()
            data = {
                'csrf_token': csrf_token,
            }

            output = self.app.post(
                '/test/star/0', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertIn(
                '</button>\n                      You unstarred '
                'this project\n                    </div>',
                output.get_data(as_text=True)
            )
            self._check_star_count(data=data, stars=0)

        # now, test if pingou's name comes in repo stargazers
        # it shouldn't because, he just unstarred
        output = self.app.get(
            '/test/stargazers/'
        )
        self.assertIn(
            '<title>Stargazers of test  - Pagure</title>',
            output.get_data(as_text=True)
        )
        self.assertNotIn(
            '<a href="/user/pingou">pingou\n              </a>',
            output.get_data(as_text=True)
        )

    def test_user_stars(self):
        """ Test the user_stars endpoint of pagure.ui.app """

        # make pingou star the project
        # first create pingou
        user = tests.FakeUser()
        user.username = 'pingou'
        with tests.user_set(self.app.application, user):
            csrf_token = self.get_csrf()
            data = {
                'csrf_token': csrf_token,
            }

            output = self.app.post(
                '/test/star/1', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertIn(
                '</button>\n                      You starred '
                'this project\n                    </div>',
                output.get_data(as_text=True)
            )
            self._check_star_count(data=data, stars=1)

        # now, test if the project 'test' comes in pingou's stars
        output = self.app.get(
            '/user/pingou/stars'
        )
        self.assertIn(
            "<title>pingou's starred Projects - Pagure</title>",
            output.get_data(as_text=True)
        )
        self.assertIn(
            '<a class="list-group-item" href="/test">', output.get_data(as_text=True))
        self.assertEqual(output.get_data(as_text=True).count('class="list-group-item"'), 1)
        self.assertEqual(
            output.get_data(as_text=True).count('<span class="oi" data-glyph="document"></span>'),
            1)

        # make pingou unstar the project
        user = tests.FakeUser()
        user.username = 'pingou'
        with tests.user_set(self.app.application, user):
            csrf_token = self.get_csrf()
            data = {
                'csrf_token': csrf_token,
            }
            output = self.app.post(
                '/test/star/0', data=data, follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertIn(
                '</button>\n                      You unstarred '
                'this project\n                    </div>',
                output.get_data(as_text=True)
            )
            self._check_star_count(data=data, stars=0)

        # now, test if test's name comes in pingou's stars
        # it shouldn't because, he just unstarred
        output = self.app.get(
            '/user/pingou/stars/'
        )
        self.assertIn(
            "<title>pingou's starred Projects - Pagure</title>",
            output.get_data(as_text=True)
        )
        self.assertNotIn(
            '<a class="list-group-item" href="/test">test</a>\n',
            output.get_data(as_text=True)
        )
        self.assertEqual(
            output.get_data(as_text=True).count('<span class="oi" data-glyph="document"></span>'),
            0)
        self.assertEqual(output.get_data(as_text=True).count('class="list-group-item"'), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
