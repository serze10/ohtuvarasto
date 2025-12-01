import unittest
from app import create_app
from models import db, Warehouse, Item


class TestWarehouseAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'TESTING': True
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_list_warehouses_empty(self):
        response = self.client.get('/warehouses')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_create_warehouse_api(self):
        response = self.client.post('/warehouses', json={
            'name': 'Test Warehouse',
            'location': 'Helsinki',
            'description': 'Test description'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data['name'], 'Test Warehouse')
        self.assertEqual(data['location'], 'Helsinki')
        self.assertEqual(data['description'], 'Test description')

    def test_create_warehouse_without_name(self):
        response = self.client.post('/warehouses', json={
            'location': 'Helsinki'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_create_warehouse_duplicate_name(self):
        self.client.post('/warehouses', json={'name': 'Warehouse1'})
        response = self.client.post('/warehouses', json={'name': 'Warehouse1'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('already exists', response.json['error'])

    def test_get_warehouse(self):
        create_resp = self.client.post('/warehouses', json={
            'name': 'Test Warehouse'
        })
        warehouse_id = create_resp.json['id']

        response = self.client.get(f'/warehouses/{warehouse_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test Warehouse')

    def test_get_warehouse_not_found(self):
        response = self.client.get('/warehouses/9999')
        self.assertEqual(response.status_code, 404)

    def test_update_warehouse(self):
        create_resp = self.client.post('/warehouses', json={
            'name': 'Original Name'
        })
        warehouse_id = create_resp.json['id']

        response = self.client.put(f'/warehouses/{warehouse_id}', json={
            'name': 'Updated Name',
            'location': 'Updated Location'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Updated Name')
        self.assertEqual(response.json['location'], 'Updated Location')

    def test_update_warehouse_duplicate_name(self):
        self.client.post('/warehouses', json={'name': 'Warehouse1'})
        create_resp = self.client.post('/warehouses', json={
            'name': 'Warehouse2'
        })
        warehouse_id = create_resp.json['id']

        response = self.client.put(f'/warehouses/{warehouse_id}', json={
            'name': 'Warehouse1'
        })
        self.assertEqual(response.status_code, 400)

    def test_update_warehouse_empty_name(self):
        create_resp = self.client.post('/warehouses', json={
            'name': 'Test Warehouse'
        })
        warehouse_id = create_resp.json['id']

        response = self.client.put(f'/warehouses/{warehouse_id}', json={
            'name': ''
        })
        self.assertEqual(response.status_code, 400)

    def test_delete_warehouse(self):
        create_resp = self.client.post('/warehouses', json={
            'name': 'Test Warehouse'
        })
        warehouse_id = create_resp.json['id']

        response = self.client.delete(f'/warehouses/{warehouse_id}')
        self.assertEqual(response.status_code, 200)

        get_resp = self.client.get(f'/warehouses/{warehouse_id}')
        self.assertEqual(get_resp.status_code, 404)

    def test_delete_warehouse_not_found(self):
        response = self.client.delete('/warehouses/9999')
        self.assertEqual(response.status_code, 404)


class TestItemAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'TESTING': True
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            warehouse = Warehouse(name='Test Warehouse')
            db.session.add(warehouse)
            db.session.commit()
            self.warehouse_id = warehouse.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_add_item(self):
        response = self.client.post(
            f'/warehouses/{self.warehouse_id}/items',
            json={'name': 'Test Item', 'quantity': 10.5}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'Test Item')
        self.assertAlmostEqual(response.json['quantity'], 10.5)

    def test_add_item_without_name(self):
        response = self.client.post(
            f'/warehouses/{self.warehouse_id}/items',
            json={'quantity': 10}
        )
        self.assertEqual(response.status_code, 400)

    def test_add_item_negative_quantity(self):
        response = self.client.post(
            f'/warehouses/{self.warehouse_id}/items',
            json={'name': 'Test Item', 'quantity': -5}
        )
        self.assertEqual(response.status_code, 400)

    def test_add_item_to_nonexistent_warehouse(self):
        response = self.client.post(
            '/warehouses/9999/items',
            json={'name': 'Test Item'}
        )
        self.assertEqual(response.status_code, 404)

    def test_remove_item(self):
        add_resp = self.client.post(
            f'/warehouses/{self.warehouse_id}/items',
            json={'name': 'Test Item', 'quantity': 5}
        )
        item_id = add_resp.json['id']

        response = self.client.delete(
            f'/warehouses/{self.warehouse_id}/items/{item_id}'
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_item_not_found(self):
        response = self.client.delete(
            f'/warehouses/{self.warehouse_id}/items/9999'
        )
        self.assertEqual(response.status_code, 404)

    def test_item_appears_in_warehouse(self):
        self.client.post(
            f'/warehouses/{self.warehouse_id}/items',
            json={'name': 'Item1', 'quantity': 10}
        )
        self.client.post(
            f'/warehouses/{self.warehouse_id}/items',
            json={'name': 'Item2', 'quantity': 20}
        )

        response = self.client.get(f'/warehouses/{self.warehouse_id}')
        self.assertEqual(len(response.json['items']), 2)


class TestWarehouseUI(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'TESTING': True
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Management', response.data)

    def test_create_warehouse_form(self):
        response = self.client.post('/warehouses', data={
            'name': 'Form Warehouse',
            'location': 'Test Location'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Form Warehouse', response.data)

    def test_edit_warehouse_page(self):
        with self.app.app_context():
            warehouse = Warehouse(name='Edit Test')
            db.session.add(warehouse)
            db.session.commit()
            warehouse_id = warehouse.id

        response = self.client.get(f'/warehouses/{warehouse_id}/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Test', response.data)

    def test_view_warehouse_page(self):
        with self.app.app_context():
            warehouse = Warehouse(name='View Test')
            db.session.add(warehouse)
            db.session.commit()
            warehouse_id = warehouse.id

        response = self.client.get(f'/warehouses/{warehouse_id}/view')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'View Test', response.data)

    def test_delete_warehouse_form(self):
        with self.app.app_context():
            warehouse = Warehouse(name='Delete Test')
            db.session.add(warehouse)
            db.session.commit()
            warehouse_id = warehouse.id

        response = self.client.post(
            f'/warehouses/{warehouse_id}/delete',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Delete Test', response.data)


class TestWarehouseModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'TESTING': True
        })
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_warehouse_to_dict(self):
        with self.app.app_context():
            warehouse = Warehouse(
                name='Test',
                location='Location',
                description='Desc'
            )
            db.session.add(warehouse)
            db.session.commit()

            result = warehouse.to_dict()
            self.assertEqual(result['name'], 'Test')
            self.assertEqual(result['location'], 'Location')
            self.assertEqual(result['description'], 'Desc')
            self.assertEqual(result['items'], [])

    def test_item_to_dict(self):
        with self.app.app_context():
            warehouse = Warehouse(name='Test')
            db.session.add(warehouse)
            db.session.commit()

            item = Item(name='Item', quantity=5.0, warehouse_id=warehouse.id)
            db.session.add(item)
            db.session.commit()

            result = item.to_dict()
            self.assertEqual(result['name'], 'Item')
            self.assertAlmostEqual(result['quantity'], 5.0)

    def test_cascade_delete(self):
        with self.app.app_context():
            warehouse = Warehouse(name='Test')
            db.session.add(warehouse)
            db.session.commit()

            item = Item(name='Item', quantity=5.0, warehouse_id=warehouse.id)
            db.session.add(item)
            db.session.commit()
            item_id = item.id

            db.session.delete(warehouse)
            db.session.commit()

            remaining_item = Item.query.get(item_id)
            self.assertIsNone(remaining_item)


if __name__ == '__main__':
    unittest.main()
