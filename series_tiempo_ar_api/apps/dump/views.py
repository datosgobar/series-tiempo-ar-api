from django.shortcuts import render

from django.http import FileResponse
from .csv import generate_csv


def test_view(request):
    generate_csv()

    return FileResponse(open('test.csv', 'rb'))

