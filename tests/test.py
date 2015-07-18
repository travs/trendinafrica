import sys, os
sys.path.insert(0, '..')
import tempfile, trendlinks, models, html
import logging as log

from helpers import *
from nose import *
from nose.tools import nottest

class TestTrendlinks(object):

    @classmethod
    def setUpClass(self):
        self.db, trendlinks.app.config['DATABASE'] = tempfile.mkstemp()
        trendlinks.app.config['TESTING'] = True
        trendlinks.app.config['WTF_CSRF_ENABLED'] = False
        self.app = trendlinks.app.test_client()

    @classmethod
    def tearDownClass(self):
        os.close(self.db)
        os.unlink(trendlinks.app.config['DATABASE'])

    def check_status_OK(self, url):
        """ Check that the URL returns a '200 OK' status """
        assert self.app.get(url).status_code == 200

    @nottest
    def test_URLs_render(self):
        """ 
        Generate tests for a list of URLs.
        Pass if the URL does not return an error when sent a GET request.
        """
        URL_LIST = list_URLs(self.app)
        for url in URL_LIST:
            yield self.check_status_OK, url

    def test_bad_login(self):
        """
        Test that a User receives a fail message with bad password.
        """
        fail_message = "Your email or password doesn't match." 
        r = self.login('user@cool.io', 'wrongpass')
        response_string = html.unescape(r.get_data().decode('utf8'))
        assert fail_message in response_string

    def test_good_login(self):
        """
        Test that a registered User can log in to the site.
        """
        success_message = "You've been successfully logged in!"
        r = self.login('user@cool.io', 'securepass')
        response_string = html.unescape(r.get_data().decode('utf8'))
        assert success_message in response_string

    def test_good_register(self):
        """
        Test that you can register to the site.
        Passes if the User is redirected to the index.
        """
        response = self.register('user@cool.io', 'securepass')
        assert response.headers.get('location') == '/'

    def test_duplicate_register(self):
        """
        Tests that you can't register with the same email twice.
        """
        dupe_message = 'User with that email already exists.'
        self.register('popular@gmail.com', 'mypass')
        response = self.register('popular@gmail.com', 'someotherpass')
        response_string = html.unescape(r.get_data().decode('utf8'))
        assert dupe_message in response_string

    def login(self, email, password):
        """
        Do a login.
        """
        return self.app.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def register(self, email, password):
        """
        Do a registration.
        """
        return self.app.post('/register', data=dict(
            email=email,
            password=password,
            password2=password
        ), follow_redirects=True)

if __name__ == '__main__':
    import nose
    nose.main()
