import unittest

from app import Movie, User, WIN, app, db, forge, init


class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )

        db.create_all()

        user = User(name='Foo', username='foo')
        user.set_password('123')
        movie = Movie(title='Old Movie Title', year='2024')
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self):
        self.client.post('/login', data=dict(
            username='foo',
            password='123'
        ), follow_redirects=True)

    def test_app_exist(self):
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn("Foo's Watchlist", data)
        self.assertIn('Old Movie Title', data)
        self.assertEqual(response.status_code, 200)

    def test_create_item(self):
        self.login()

        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2024'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('New Movie', data)

        response = self.client.post('/', data=dict(
            title='',
            year='2024'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

        response = self.client.post('/', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

    def test_update_item(self):
        self.login()

        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Old Movie Title', data)
        self.assertIn('2024', data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='Old Movie Edited',
            year='2024'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.', data)
        self.assertIn('Old Movie Edited', data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2024'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertIn('Invalid input.', data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='Old Movie Edited Again',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.', data)
        self.assertNotIn('Old Movie Edited Again', data)
        self.assertIn('Invalid input.', data)

    def test_delete_item(self):
        self.login()

        response = self.client.post('movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Old Movie Title', data)

    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('<form method="POST">', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Delete', data)

    def test_login(self):
        response = self.client.post('/login', data=dict(
            username='foo',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('<form method="POST">', data)
        self.assertIn('Edit', data)
        self.assertIn('Delete', data)

        response = self.client.post('/login', data=dict(
            username='foo',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        response = self.client.post('/login', data=dict(
            username='bar',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

        response = self.client.post('/login', data=dict(
            username='foo',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye.', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('<form method="POST">', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Delete', data)

    def test_settings(self):
        self.login()

        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Your Name', data)

        response = self.client.post('/settings', data=dict(
            name='Pooh Bear'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated.', data)
        self.assertIn('Pooh Bear', data)

        response = self.client.post('/settings', data=dict(
            name=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated.', data)
        self.assertIn('Invalid input.', data)

    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done.', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    def test_init_command(self):
        result = self.runner.invoke(init)
        self.assertIn('Initialized database.', result.output)

    def test_admin_command(self):
        db.drop_all()
        db.create_all()

        result = self.runner.invoke(
            args=['admin', '--username', 'foo', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'foo')
        self.assertTrue(User.query.first().validate_password('123'))

    def test_admin_command_update(self):
        result = self.runner.invoke(
            args=['admin', '--username', 'bar', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'bar')
        self.assertTrue(User.query.first().validate_password('456'))


if __name__ == '__main__':
    unittest.main()
