# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-07-16 13:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('amount', models.FloatField()),
                ('amount_remaining', models.FloatField(blank=True)),
                ('period', models.PositiveSmallIntegerField(choices=[(1, 'Daily'), (2, 'Weekly'), (3, 'Monthly'), (4, 'Quarterly'), (5, 'Semi-Annually'), (6, 'Annually')], db_index=True, default=3)),
                ('date_start', models.DateField(db_index=True)),
                ('date_end', models.DateField(db_index=True)),
            ],
            options={
                'verbose_name': 'Budget',
                'verbose_name_plural': 'Budgets',
                'ordering': ['-date_start', 'date_end'],
            },
        ),
        migrations.CreateModel(
            name='FinanceAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('account_type', models.PositiveSmallIntegerField(choices=[(0, 'Cash'), (1, 'Current'), (2, 'Savings'), (3, 'Fixed Deposit')], db_index=True, default=0)),
                ('amount', models.FloatField(default=0.0)),
                ('slug', models.SlugField(blank=True, max_length=256, unique=True)),
            ],
            options={
                'verbose_name': 'Finance Account',
                'verbose_name_plural': 'Finance Accounts',
                'ordering': ['name', 'amount'],
            },
        ),
        migrations.CreateModel(
            name='PlannedTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.PositiveSmallIntegerField(choices=[(1, 'Income'), (2, 'Expense'), (3, '(Transfer) Income'), (4, '(Transfer) Expense')], db_index=True, default=2)),
                ('date', models.DateField(blank=True, db_index=True)),
                ('amount', models.FloatField()),
                ('note', models.TextField()),
                ('repeat', models.PositiveSmallIntegerField(choices=[(0, 'Once'), (1, 'Daily'), (2, 'Weekly'), (3, 'Monthly'), (4, 'Quarterly'), (5, 'Semi-Annually'), (6, 'Annually')], db_index=True, default=0)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planned_transactions', to='finance.FinanceAccount')),
            ],
            options={
                'verbose_name': 'Planned Transaction',
                'verbose_name_plural': 'Planned Transactions',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.PositiveSmallIntegerField(choices=[(1, 'Income'), (2, 'Expense'), (3, '(Transfer) Income'), (4, '(Transfer) Expense')], db_index=True, default=2)),
                ('date', models.DateField(blank=True, db_index=True)),
                ('amount', models.FloatField()),
                ('note', models.TextField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='finance.FinanceAccount')),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
                'ordering': ['-date', 'id'],
            },
        ),
        migrations.CreateModel(
            name='TransactionCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('slug', models.SlugField(blank=True, max_length=256, unique=True)),
            ],
            options={
                'verbose_name': 'Transaction Category',
                'verbose_name_plural': 'Transaction Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TransactionTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('slug', models.SlugField(blank=True, max_length=256, unique=True)),
            ],
            options={
                'verbose_name': 'Transaction Tag',
                'verbose_name_plural': 'Transaction Tags',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TransferTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, db_index=True)),
                ('amount', models.FloatField()),
                ('note', models.TextField()),
                ('account_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_expenses', to='finance.FinanceAccount')),
                ('account_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_incomes', to='finance.FinanceAccount')),
            ],
            options={
                'verbose_name': 'Transfer Transaction',
                'verbose_name_plural': 'Transfer Transactions',
                'ordering': ['-date'],
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='finance.TransactionCategory'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='tags',
            field=models.ManyToManyField(related_name='transactions', to='finance.TransactionTag'),
        ),
        migrations.AddField(
            model_name='plannedtransaction',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planned_transactions', to='finance.TransactionCategory'),
        ),
        migrations.AddField(
            model_name='plannedtransaction',
            name='tags',
            field=models.ManyToManyField(related_name='planned_transactions', to='finance.TransactionTag'),
        ),
    ]