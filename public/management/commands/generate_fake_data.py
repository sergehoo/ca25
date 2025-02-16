import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

from administration.models import Event, Session, Attendance

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = "Génère des données fictives pour l'événement SIADE 25"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🔄 Génération des données fictives en cours..."))

        # Création de l'organisateur
        organizer = User.objects.create_user(
            username="organisateur_siade3",
            email="organisateur@siade.com",
            password="password123",
            role="organisateur",
            company="SIADE Organization",
            sector="Événementiel"
        )

        # Création de l'événement unique SIADE 25
        event = Event.objects.create(
            name="SIADE 25",
            description="Salon International de l'Art et du Design Événementiel 2025",
            start_date=datetime(2025, 5, 15, 9, 0),
            end_date=datetime(2025, 5, 18, 18, 0),
            location="Palais des Congrès, Paris",
            organizer=organizer
        )

        self.stdout.write(self.style.SUCCESS(f"✅ Événement créé : {event.name}"))

        # Création de 5 sessions
        sessions = []
        for i in range(8):
            start_time = event.start_date + timedelta(hours=random.randint(0, 48))
            end_time = start_time + timedelta(hours=random.randint(1, 4))
            session = Session.objects.create(
                event=event,
                title=fake.sentence(nb_words=4),
                description=fake.text(),
                start_time=start_time,
                end_time=end_time
            )
            sessions.append(session)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(sessions)} sessions créées."))

        # Création de 10 utilisateurs avec différents rôles
        roles = ['participant', 'exposant', 'sponsor', 'media']
        users = []
        for _ in range(500):
            unique_username = fake.user_name()

            # Vérifier que le username n'existe pas déjà
            while User.objects.filter(username=unique_username).exists():
                unique_username = fake.user_name()  # Générer un autre username

            user = User.objects.create_user(
                username=unique_username,
                email=fake.email(),
                password="password123",
                role=random.choice(roles),
                company=fake.company() if random.choice([True, False]) else None,
                sector=fake.word() if random.choice([True, False]) else None,
                description=fake.text() if random.choice([True, False]) else None,
                preferences={"diet": random.choice(["vegan", "vegetarian", "none"])}
            )
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(users)} utilisateurs créés."))

        # Génération des présences (chaque utilisateur assiste à au moins une session)
        attendances = []
        for user in users:
            attended_sessions = random.sample(sessions, random.randint(1, 5))
            for session in attended_sessions:
                attendance = Attendance.objects.create(
                    user=user,
                    session=session
                )
                attendances.append(attendance)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(attendances)} présences générées."))

        self.stdout.write(self.style.SUCCESS("🎉 Données fictives générées avec succès !"))