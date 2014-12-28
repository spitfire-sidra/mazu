# Documentation

## Sharing Extension Customization

### Prerequisites

To create an app called `sharing` and define a form called `SelectExtensionForm`. `SelectExtensionForm` displays all available sharing extensions under the folder `extensions`. So that, an user can choice to share a sample via the extension which he selected.

Then define a View and an URL for displaying `SelectExtensionForm` and getting the sha256 value of the sample which would be shared.

If the `SelectExtensionForm` is valid, then redirect to the extension.

# Sharing extension customization

### Step 1

Create an app under the folder `extensions`, just like a normal django app.

```
./manage.py startapp my_sharing_app
mv my_sharing_app extensions/
```

### Step 2

Define your `models.py`, `forms.py`, `views.py`, `urls.py` or anything you want.

## Step 3

3.1 Define an URL called `sharing.via,modulename`. Take `HPFeeds` as an example, the name of the URL is `sharing.via.hpfeeds`. When an user choices to share a sample, the user will be redirected to this URL.

3.2 This URL **must** define a parameter called `sha256`. Then you will know which sample will be shared.

For example,

```
url(r'^sample/(?P<sha256>\w{128})/$', my_hpfeeds_view, name='sharing.via.hpfeeds')
```

### Step 4

Including your `urls.py` in `mazu/urls.py`

For example,

```
url(r'^ext/hpfeeds/', include('extensions.hpfeeds.urls')),
```

## Step 5

Register your app in `settings/sharing_extensions.py`

```
CHOICES = (
    ('hpfeeds', 'app description'),
    ('my_sharing_app', 'app description'),
)
```

This constant will be load in `SelectExtensionForm`. Then mazu would know there is a module can be load.

### Other

If you defined `models.py` in the extensions module, you need register your app in the `settings/production.py`

```
INSTALLED_APPS = (
    ...,
    'extensions.modules.my_sharing_app',
)
```
