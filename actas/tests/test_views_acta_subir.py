# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.core.urlresolvers import reverse


class ViewsActaSubirTestCase(TestCase):

    def setup(self):
        self.client = Client()

    def test_obtener_subir(self):
        response = self.client.get(reverse('actas:subir'))
        self.assertEquals(200, response.status_code)
        self.assertIsNotNone(response.cookies.get('csrftoken'))
