# Generated by Django 5.2.3 on 2025-06-15 18:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_cliente_password_alter_cliente_endereco_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="itemcarrinho",
            name="preco",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
