from solo.admin import SingletonModelAdmin


class SingletonAdmin(SingletonModelAdmin):
    # django-des overridea el change_form_template de la clase padre(!), volvemos al default de django
    change_form_template = 'admin/change_form.html'
