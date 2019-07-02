GUI - Web Module
==================================================

## Users

### User Permissions

There are five user permissions: superuser, admin, standard, read-only, reports-only.
Permissions are defined for each project except superuser that is global.
Permission access is documented in the table below. 

<table id="permissionTable">
    <thead>
        <tr>
            <th>Page</th>
            <th>Permission</th>
            <th>superuser</th>
            <th>admin</th>
            <th>standard</th>
            <th>read-only</th>
            <th>reports-only</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="6" class="align-left">Suite/Test/Page List</td>
            <td class="align-left">view</td>
            <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td></td>
        </tr>
        <tr>
            <td class="align-left">add</td>
            <td>✓</td><td>✓</td><td>✓</td><td></td><td></td>
        </tr>
        <tr>
            <td class="align-left">duplicate</td>
            <td>✓</td><td>✓</td><td>✓</td><td></td><td></td>
        </tr>
        <tr>
            <td class="align-left">rename</td>
            <td>✓</td><td>✓</td><td>✓</td><td></td><td></td>
        </tr>
        <tr>
            <td class="align-left">run</td>
            <td>✓</td><td>✓</td><td>✓</td><td></td><td></td>
        </tr>
        <tr>
            <td class="align-left">delete</td>
            <td>✓</td><td>✓</td><td></td><td></td><td></td>
        </tr>
        <tr>
            <td rowspan="3" class="align-left">Suite/Test/Page Builder</td>
            <td class="align-left">view</td>
            <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td></td>
        </tr>
        <tr>
            <td class="align-left">edit</td>
            <td>✓</td><td>✓</td><td>✓</td><td></td><td></td>
        </tr>
        <tr>
            <td class="align-left">run</td>
            <td>✓</td><td>✓</td><td>✓</td><td></td><td></td>
        </tr>
        <tr>
            <td rowspan="2" class="align-left">Environments</td>
            <td class="align-left">view</td>
            <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td></td></tr>
        <tr>
            <td class="align-left">edit</td>
            <td>✓</td><td>✓</td><td></td><td></td><td></td>
        </tr>
        <tr>
            <td rowspan="2" class="align-left">Project Settings</td>
            <td class="align-left">view</td>
            <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td></td>
        </tr>
        <tr>
            <td class="align-left">edit</td>
            <td>✓</td><td>✓</td><td></td><td></td><td></td>
        </tr>
        <tr>
            <td class="align-left">Global Settings</td>
            <td class="align-left">view/edit</td>
            <td>✓</td><td></td><td></td><td></td><td></td>
        </tr>
        <tr>
            <td class="align-left">User Management</td>
            <td class="align-left">view/edit</td>
            <td>✓</td><td></td><td></td><td></td><td></td>
        </tr>
        <tr>
            <td rowspan="2" class="align-left">Reports</td>
            <td class="align-left">view</td>
            <td>✓</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td>
        </tr>
        <tr>
            <td class="align-left">delete</td>
            <td>✓</td><td>✓</td><td></td><td></td><td></td>
        </tr>
    </tbody>
</table>


### Creating Users

Superusers can be created using the [createsuperuser](command-line-interface.html#createsuperuser) command.
Non superusers have to be created from the User Management page.

## Secret Key

For security purposes, each test directory is generated with a unique **secret key** stored in the *.golem* file.

**Example .golem file:**
```
[gui]
secret_key = <your_super_secret_key_string>
```

If the secret key is not provided, a default key will be used (not recommended).


## Using a Production Server

The default server (Flask development server) is not suited for production.

The Golem GUI web application can be run with a production WSGI server just like any other Flask application. 

As an example, these are the steps to use Waitress:

```
pip install waitress

waitress-serve --call "golem.gui:create_app"
```
 
There are a lot of different options. Here is a complete guide: <http://flask.pocoo.org/docs/latest/deploying/>
