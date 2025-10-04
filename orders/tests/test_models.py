from django.test import TestCase
from orders.models import Order, OrderItem
from django.db.models.fields import EmailField, BooleanField, CharField, DateTimeField, DecimalField, PositiveIntegerField
from store.models import Product

class OrderTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            postal_code='12345',
            city='Anytown',
            paid=True
        )


    def test_first_name_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')


    def test_last_name_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'last name')


    def test_email_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('email').verbose_name
        self.assertEqual(field_label, 'email')


    def test_address_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('address').verbose_name
        self.assertEqual(field_label, 'address')


    def test_postal_code_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('postal_code').verbose_name
        self.assertEqual(field_label, 'postal code')


    def test_city_label(self):   
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('city').verbose_name
        self.assertEqual(field_label, 'city')


    def test_paid_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('paid').verbose_name
        self.assertEqual(field_label, 'paid')


    def test_created_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('created').verbose_name
        self.assertEqual(field_label, 'created')


    def test_updated_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('updated').verbose_name
        self.assertEqual(field_label, 'updated')


    def test_order_str(self):
        order = Order.objects.get(id=1)
        expected_str = f'Order {order.id}'
        self.assertEqual(str(order), expected_str)


    def test_get_total_cost(self):
        order = Order.objects.get(id=1)
        total_cost = order.get_total_cost()
        self.assertEqual(total_cost, 0)


    def test_email_field_type(self):
        order = Order.objects.get(id=1)
        email_field = order._meta.get_field('email')
        self.assertTrue(type(email_field) is EmailField)


    def test_paid_field_type(self):
        order = Order.objects.get(id=1)
        paid_field = order._meta.get_field('paid')
        self.assertTrue(type(paid_field) is BooleanField)


    def test_first_name_field_type(self):
        order = Order.objects.get(id=1)
        first_name_field = order._meta.get_field('first_name')
        self.assertTrue(type(first_name_field) is CharField)


    def test_last_name_field_type(self):
        order = Order.objects.get(id=1)
        last_name_field = order._meta.get_field('last_name')
        self.assertTrue(type(last_name_field) is CharField)


    def test_address_field_type(self):
        order = Order.objects.get(id=1)
        address_field = order._meta.get_field('address')
        self.assertTrue(type(address_field) is CharField)


    def test_postal_code_field_type(self):
        order = Order.objects.get(id=1)
        postal_code_field = order._meta.get_field('postal_code')
        self.assertTrue(type(postal_code_field) is CharField)


    def test_city_field_type(self):
        order = Order.objects.get(id=1)
        city_field = order._meta.get_field('city')
        self.assertTrue(type(city_field) is CharField)


    def test_created_field_type(self):
        order = Order.objects.get(id=1)
        created_field = order._meta.get_field('created')
        self.assertTrue(type(created_field) is DateTimeField)


    def test_updated_field_type(self):
        order = Order.objects.get(id=1)
        updated_field = order._meta.get_field('updated')
        self.assertTrue(type(updated_field) is DateTimeField)



class OrderItemTests(TestCase):


    @classmethod
    def setUpTestData(cls):
        order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            address='123 Main St',
            postal_code='12345',
            city='Anytown',
            paid=True
        )

        product1 = Product.objects.create(
            title='test-title',
            brand='test-brand',
            description='test-description',
            slug='test-slug',
            price=10.00
        )

        product2 = Product.objects.create(
            title='test-title-2',
            brand='test-brand-2',
            description='test-description-2',
            slug='test-slug',
            price=5.00
        )

        OrderItem.objects.create(
            order=order,
            product=product1,
            quantity=2,
            price=product1.price,
            dimensions='10x20',
            frame_color='black',
            frame_type='wood'
        )

        OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=1,
            price=product2.price,
            dimensions='10x20',
            frame_color='black',
            frame_type='wood'
        )


    def test_quantity_label(self):
        order_item = OrderItem.objects.get(id=1)
        field_label = order_item._meta.get_field('quantity').verbose_name
        self.assertEqual(field_label, 'quantity')


    def test_price_label(self):
        order_item = OrderItem.objects.get(id=1)
        field_label = order_item._meta.get_field('price').verbose_name
        self.assertEqual(field_label, 'price')


    def test_get_cost(self):
        order_item = OrderItem.objects.get(id=1)
        cost = order_item.get_cost()
        self.assertEqual(cost, 20.00)


    def test_quantity_field_type(self):
        order_item = OrderItem.objects.get(id=1)
        quantity_field = order_item._meta.get_field('quantity')
        self.assertTrue(type(quantity_field) is PositiveIntegerField)


    def test_price_field_type(self):
        order_item = OrderItem.objects.get(id=1)
        price_field = order_item._meta.get_field('price')
        self.assertTrue(type(price_field) is DecimalField)


    def test_get_total_cost(self):
        order = Order.objects.get(id=1)
        total_cost = order.get_total_cost()
        self.assertEqual(total_cost, 25.00)


    def test_item_1_cost(self):
        order_item = OrderItem.objects.get(id=1)
        cost = order_item.get_cost()
        self.assertEqual(cost, 20.00)


    def test_item_2_cost(self):
        order_item = OrderItem.objects.get(id=2)
        cost = order_item.get_cost()
        self.assertEqual(cost, 5.00)