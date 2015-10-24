__author__ = 'clover'

import os
import flasker
import unittest
import tempfile

class FlakerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd,flasker.app.config['DATABASE'] = tempfile.mkstemp()
        flasker.app.config['TESTING'] = True
        self.app = flasker.app.test_client()
        flasker.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flasker.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login',data=dict(username=username,password=password
                                                ),follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    #test root url
    def test_empty_db(self):
        rv = self.app.get('/')

    #test login,logout
    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logout out' in rv.data
        rv = self.login('adminx', 'default')
        assert 'invalid in' in rv.data
        rv = self.login('admin', 'defaultx')
        assert 'invalid password' in rv.data

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(title='<hello>',text='<strong>HTML</strong> allowed here'),follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data

if __name__ == '__main__':
    unittest.main()