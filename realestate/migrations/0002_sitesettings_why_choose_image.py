from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('realestate', '0001_initial')]
    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='why_choose_image',
            field=models.ImageField(blank=True, help_text='Optional photo shown on the Why Choose Us section of the homepage.', null=True, upload_to='site/'),
        ),
    ]
