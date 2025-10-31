# users/management/commands/seed_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea usuaris de prova per al desenvolupament'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help="Nombre d'usuaris a crear"
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help="Elimina tots els usuaris existents (excepte superusuaris)"
        )

    def handle(self, *args, **options):
        num_users = options['users']

        if options['clear']:
            self.stdout.write('Eliminant usuaris existents...')
            count = 0
            for user in User.objects.all():
                if not user.is_superuser:
                    user.delete()
                    count += 1
            self.stdout.write(self.style.SUCCESS(f'Eliminats {count} usuaris'))

        with transaction.atomic():
            # Crear grups
            groups = self.create_groups()
            # Crear usuaris
            users_created = self.create_users(num_users, groups)

        self.stdout.write(
            self.style.SUCCESS(f'{users_created} usuaris creats correctament!')
        )

    def create_groups(self):
        """Crea els grups necessaris"""
        group_names = ['Organitzadors', 'Participants', 'Moderadors']
        groups = {}

        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            groups[name] = group
            if created:
                self.stdout.write(f'  ✓ Grup "{name}" creat')

        return groups

    def create_users(self, num_users, groups):
        """Crea usuaris de prova"""
        users_created = 0

        # Crear un admin si no existeix
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@streamevents.com',
                'first_name': 'Admin',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('  ✓ Superusuari admin creat')
            users_created += 1

        # Crear usuaris normals
        for i in range(1, num_users + 1):
            username = f'user{i:03d}'

            # Determinar grup segons el número
            if i % 3 == 0:
                group = groups['Organitzadors']
                role = 'org'
            elif i % 2 == 0:
                group = groups['Moderadors']
                role = 'mod'
            else:
                group = groups['Participants']
                role = 'part'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@streamevents.com',
                    'first_name': f'Nom{i}',
                    'last_name': f'Cognom{i}',
                    'is_active': True,
                }
            )

            if created:
                user.set_password('password123')
                user.groups.add(group)
                user.save()
                users_created += 1
                self.stdout.write(f'  ✓ Usuari {username} ({role}) creat')

        return users_created