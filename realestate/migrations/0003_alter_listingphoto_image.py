from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("realestate", "0002_sitesettings_why_choose_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listingphoto",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="listings/%Y/%m/"),
        ),
    ]
