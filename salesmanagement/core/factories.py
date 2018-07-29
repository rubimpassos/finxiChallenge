import factory
from django.contrib.auth import get_user_model


class RandomUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Faker('first_name')
    password = factory.PostGenerationMethodCall('set_password', 'some_password')

    is_superuser = True
    is_staff = True
    is_active = True
