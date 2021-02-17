# datatable-server-side-django3
This is python package for implement datatable server side in django3

Code Source: https://github.com/monnierj/django-datatables-server-side 

(Adjust code from that repo and has been implemented and tested to django 3)

PyPi: https://pypi.org/project/datatables-server-side-django/

# Exampe Usage 

## In Your Url
### let's say i have a file app_customer/urls.<span>py</span>
```python
from django.conf.urls import url
from app_customer.views import list, load, detail
app_name = 'app_customer'

urlpatterns = [
    url(r'^customer/$', list.Execute.as_view(), name='customer-list'),
    url(r'^load/customer/$', load.Execute.as_view(), name='load-customer'),

    # In case you need detail page, if you don't need just ignore all code about detail page
    url(r'^customer/detail/(?P<pk>[\w-]+)/$', detail.Execute.as_view(), name='customer-detail'),

]
```

## In Your view

### Example view for displaying table
#### let's say i have a file app_customer/views/list<span>.py</span>
```python
from django.views import generic
from app_customer import models


class Execute(generic.ListView):
    model = models.Customer
    template_name = 'app_customer/list.html'
```

#### let's say i have a file app_customer/views/detail<span>.py</span>
```python
from django.views import generic
from app_customer import models


class Execute(generic.DetailView):
    model = models.Customer
    template_name = 'app_customer/detail.html'
```

### Example view for load data and configuration for datatables such as columns, searchable_columns, etc
#### let's say i have a file app_customer/views/load<span>.py</span>
```python
    from django.http import JsonResponse    
    from app_customer.models import Customer
    from _dt_server_side.views import DatatablesServerSideView
    import datetime

    class ViewLoadCustomer(DatatablesServerSideView):
        model = Customer
        columns = ['id', 'first_name', 'last_name', 'email', 'gender']
        searchable_columns = ['first_name', 'last_name', 'email', 'gender']

        foreign_fields = {'gender': 'gender__description'}
        
        def get_initial_queryset(self):
            qs = super(ViewLoadCustomer, self).get_initial_queryset()

            gender_id = self.request.GET.get('gender_id', None)
            if gender_id:
                qs = qs.filter(gender=gender_id)

            return qs
```

## In your Template
### Example template for show table
#### let's say i have a file templates/app_customer/list<span>.html</span>

```html
{% load static %}
{% block content %}
<div class="table-responsive">
    <div class="row">
        <div class="form-group col-sm-3">
            <select id="id_gender">
                <option value="male">Male</option>
                <option value="female">Female</option>
            </select>
        </div>
    </div>
    <div class="row">
        <div class="form-group col-sm-12" style="text-align: right;">
            <button type="button" id="filterData" class="btn btn-primary">Filter</button>
        </div>
    </div>
    <table 
        class="table table-bordered" 
        id="dataTable"
        load-customer-url="{% url 'app_customer:load-customer' %}"
        customer-detail-url="{% url 'app_customer:customer-detail' pk=0 %}"
    >
        <thead>
            <tr>
                <th>First Name</th>
                <th>Last Name</th>
                <th>Email Address</th>
                <th>Gender</th>
                <th style="text-align: center;">Action</th>
            </tr>
        </thead>
        <tbody></tbody>
    </table>
</div>
<script src="{% static 'jquery.min.js' %}"></script>
<script src="{% static 'app_customer/custom.js' %}"></script>
<script>
    $(document).ready(function() {
        const table = $("#dataTable")

        const createDetailButton = (data, type, row, meta) => {
            let detailUrl = table.attr('customer-detail-url');
            detailUrl = detailUrl.replace('0', row.id)

            return `
                <div class="btn-group">
                    <a href="${detailUrl}" class="btn btn-info">Detail</a>
                </div>
            `
        }

        const generateDataTable = (data) => {
            load_customer_url = table.attr('load-customer-url')

            const dataTable = createDataTableInstance({
                tableSelector: table,
                url: load_customer_url,
                additionalParam: data,
                columns: [
                    {name: "first_name", data: "first_name"},
                    {name: "last_name", data: "last_name"},
                    {name: "email", data: "email"},
                    {name: "gender", data: "gender"}
                ],
                columnDefs: [
                    {render: createDetailButton, targets: [4]}
                ],
                order: [0, 'asc']
            })
        }

        generateDataTable()

        $("#filterData").click(function() {
            const gender_id = $("#id_gender").val()

            const additionalParameter = function ( d ) {
                d.gender_id = gender_id;
            }
            generateDataTable(additionalParameter)
        });
    })

</script>
{% endblock %}
```

#### let's say i have a file templates/app_customer/detail<span>.html</span>
```html
    This is detail page
```

## In your Static
#### let's say i have a file static/app_customer/custom<span>.js</span>

```javascript
function createDataTableInstance({
    tableSelector, 
    url, 
    additionalParam,
    columns,
    columnDefs,
    order
}) {
    const dataTable = tableSelector.DataTable({
        order:order,
        destroy: true, // Destroy if datatable is exist
        pageLength: 10,
        serverSide: true,
        ajax: {
            url: url,
            data: additionalParam
        },
        columns: columns,
        "columnDefs": columnDefs,
    });

    // Override datatable filter to on change
    $('.dataTables_filter input').unbind().on('change', function() {
        dataTable.search(this.value).draw();    
    });

    return dataTable
}
```