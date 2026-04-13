import typer
from sqlmodel import select
from app.database import get_cli_session, create_db_and_tables
from app.models.user import User
from app.models.workout import Workout
from app.utilities.security import encrypt_password

app = typer.Typer()

sample_workouts = [

    # Chest
    {"name": "Bench Press",            "description": "Classic chest press with a barbell on a flat bench.",      "muscle_group": "chest",     "difficulty": "intermediate"},
    {"name": "Push Up",                "description": "Bodyweight chest exercise done on the floor.",              "muscle_group": "chest",     "difficulty": "beginner"},
    {"name": "Incline Dumbbell Press", "description": "Chest press on an inclined bench with dumbbells.",          "muscle_group": "chest",     "difficulty": "intermediate"},
    {"name": "Cable Chest Fly",        "description": "Isolation exercise for the chest using cables.",            "muscle_group": "chest",     "difficulty": "beginner"},
    # Back
    {"name": "Pull Up",                "description": "Upper body exercise pulling yourself up to a bar.",         "muscle_group": "back",      "difficulty": "intermediate"},
    {"name": "Barbell Row",            "description": "Compound back exercise using a barbell.",                   "muscle_group": "back",      "difficulty": "intermediate"},
    {"name": "Lat Pulldown",           "description": "Cable machine exercise targeting the lats.",                "muscle_group": "back",      "difficulty": "beginner"},
    {"name": "Seated Cable Row",       "description": "Horizontal pulling movement on a cable machine.",           "muscle_group": "back",      "difficulty": "beginner"},
    # Legs
    {"name": "Squat",                  "description": "Fundamental lower body exercise with a barbell.",           "muscle_group": "legs",      "difficulty": "intermediate"},
    {"name": "Leg Press",              "description": "Machine-based lower body pressing movement.",               "muscle_group": "legs",      "difficulty": "beginner"},
    {"name": "Romanian Deadlift",      "description": "Hip hinge movement targeting the hamstrings.",              "muscle_group": "legs",      "difficulty": "intermediate"},
    {"name": "Lunges",                 "description": "Single-leg exercise for quads and glutes.",                 "muscle_group": "legs",      "difficulty": "beginner"},
    # Shoulders
    {"name": "Overhead Press",         "description": "Pressing a barbell or dumbbells overhead.",                 "muscle_group": "shoulders", "difficulty": "intermediate"},
    {"name": "Lateral Raise",          "description": "Isolation exercise for the side delts.",                    "muscle_group": "shoulders", "difficulty": "beginner"},
    {"name": "Front Raise",            "description": "Dumbbell raise targeting the front delts.",                 "muscle_group": "shoulders", "difficulty": "beginner"},
    # Arms
    {"name": "Barbell Curl",           "description": "Classic bicep curl with a barbell.",                        "muscle_group": "arms",      "difficulty": "beginner"},
    {"name": "Tricep Pushdown",        "description": "Cable exercise targeting the triceps.",                     "muscle_group": "arms",      "difficulty": "beginner"},
    {"name": "Hammer Curl",            "description": "Neutral grip dumbbell curl for biceps and forearms.",       "muscle_group": "arms",      "difficulty": "beginner"},
    {"name": "Skull Crushers",         "description": "EZ-bar exercise lying down targeting the triceps.",         "muscle_group": "arms",      "difficulty": "intermediate"},
    # Core
    {"name": "Plank",                  "description": "Isometric core exercise holding a push-up position.",       "muscle_group": "core",      "difficulty": "beginner"},
    {"name": "Crunches",               "description": "Classic abdominal exercise on the floor.",                  "muscle_group": "core",      "difficulty": "beginner"},
    {"name": "Hanging Leg Raise",      "description": "Core exercise hanging from a pull-up bar.",                 "muscle_group": "core",      "difficulty": "intermediate"},
    # Cardio
    {"name": "Running",                "description": "Running on a treadmill or outdoors.",                       "muscle_group": "cardio",    "difficulty": "beginner"},
    {"name": "Jump Rope",              "description": "Cardio exercise using a jump rope.",                        "muscle_group": "cardio",    "difficulty": "beginner"},
    {"name": "Burpees",                "description": "Full body cardio and strength movement.",                    "muscle_group": "cardio",    "difficulty": "intermediate"},
]


def create_user_if_missing(db, username, email, password, role):
    existing = db.exec(select(User).where(User.username == username)).one_or_none()
    if not existing:
        user = User(
            username=username,
            email=email,
            password=encrypt_password(password),
            role=role
        )
        db.add(user)
        print(f"Created user: {username} / {password}")


@app.command()
def init_db():
    
    create_db_and_tables()

    with get_cli_session() as db:
        create_user_if_missing(db, "bob",   "bob@mail.com",   "bobpass",   "regular_user")
        create_user_if_missing(db, "admin", "admin@mail.com", "adminpass", "admin")

        current_workouts = db.exec(select(Workout)).all()
        if not current_workouts:
            for data in sample_workouts:
                workout = Workout(
                    name=data["name"],
                    description=data["description"],
                    muscle_group=data["muscle_group"],
                    difficulty=data["difficulty"]
                )
                db.add(workout)
            print(f"Created {len(sample_workouts)} workouts")
        else:
            print(f"Workouts already exist ({len(current_workouts)} found), skipping")

        db.commit()
        print("Done!")


if __name__ == "__main__":
    app()