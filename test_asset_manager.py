import flask_testing
from asset_manager import create_test_app, db, app
import unittest
import json

class MyTest(flask_testing.TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    # I removed some config passing here
    def create_app(self):
        return create_test_app()

    def setUp(self):

        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()

    def test_empty_db(self):
        rv = self.client.get('/assets')
        print rv
        self.assert200(rv)

# POST tests
        #Get a 400 if you send a non json request
    def test_not_json(self):
        r = self.client.post('/assets', data='test')
        print r
        self.assert400(r)

    def test_correct_post(self):
        r = self.client.post('/assets', data=json.dumps(dict(name="correct",
        asset_type="antenna",
        asset_class="yagi",
        asset_details="test",
        )),content_type='application/json')
        print(r.data)
        self.assertEqual(r.status_code, 201)

    def test_invalid_asset_class(self):
        r = self.client.post('/assets', data=json.dumps(dict(name="correct",
        asset_type="antenna",
        asset_class="motorola",
        asset_details="test",
        )),content_type='application/json')
        print(r.data)
        self.assertEqual(r.status_code, 400)

    def test_invalid_asset_type(self):
        r = self.client.post('/assets', data=json.dumps(dict(name="correct",
        asset_type="furby",
        asset_class="yagi",
        asset_details="test",
        )),content_type='application/json')
        print(r.data)
        self.assertEqual(r.status_code, 400)

    def test_underscore_before_name(self):
        r = self.client.post('/assets', data=json.dumps(dict(name="_correct",
        asset_type="antenna",
        asset_class="yagi",
        asset_details="test",
        )),content_type='application/json')
        print(r.data)
        self.assertEqual(r.status_code, 400)

    def test_dash_before_name(self):
        r = self.client.post('/assets', data=json.dumps(dict(name="-correct",
        asset_type="antenna",
        asset_class="yagi",
        asset_details="test",
        )),content_type='application/json')
        print(r.data)
        self.assertEqual(r.status_code, 400)

    def test_name_less_than_four_characters(self):
        r = self.client.post('/assets', data=json.dumps(dict(name="yo",
        asset_type="antenna",
        asset_class="yagi",
        asset_details="test",
        )),content_type='application/json')
        print(r.data)
        self.assertEqual(r.status_code, 400)

    def test_name_longer_than_64_characters(self):
        r = self.client.post('/assets', data=json.dumps(dict(name="yoddddddddyoddddddddyoddddddddyoddddddddyoddddddddyodddddddd4353563",
        asset_type="antenna",
        asset_class="yagi",
        asset_details="test",
        )),content_type='application/json')
        print(r.data)
        self.assertEqual(r.status_code, 400)

# Can't get non-ascii string
    # def test_non_ascii_name(self):
    #     r = self.client.post('/assets', data=json.dumps(dict(name="Unicode Rocks!",
    #     asset_type="antenna",
    #     asset_class="yagi",
    #     asset_details="test",
    #     )),content_type='application/json')
    #     print(r.data)
    #     self.assertEqual(r.status_code, 400)


if __name__ == '__main__':
    unittest.main()
