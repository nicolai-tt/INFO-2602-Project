let allWorkouts = [];
let addWorkoutFilter = null;
let currentRemixRwId = null;

const workoutImages = {
    "Bench Press":            "bench-press.jpg",
    "Push Up":                "push-up.jpg",
    "Incline Dumbbell Press": "incline-dumbbell-press.jpg",
    "Cable Chest Fly":        "cable-chest-fly.jpg",
    "Pull Up":                "pull-up.jpg",
    "Barbell Row":            "barbell-row.jpg",
    "Lat Pulldown":           "lat-pulldown.jpg",
    "Seated Cable Row":       "seated-cable-row.jpg",
    "Squat":                  "squat.jpg",
    "Leg Press":              "leg-press.jpg",
    "Romanian Deadlift":      "romanian-deadlift.jpg",
    "Lunges":                 "lunges.jpg",
    "Overhead Press":         "overhead-press.jpg",
    "Lateral Raise":          "lateral-raise.jpg",
    "Front Raise":            "front-raise.jpg",
    "Barbell Curl":           "barbell-curl.jpg",
    "Tricep Pushdown":        "tricep-pushdown.jpg",
    "Hammer Curl":            "hammer-curl.jpg",
    "Skull Crushers":         "skull-crushers.jpg",
    "Plank":                  "plank.jpg",
    "Crunches":               "crunches.jpg",
    "Hanging Leg Raise":      "hanging-leg-raise.jpg",
    "Running":                "running.jpg",
    "Jump Rope":              "jump-rope.jpg",
    "Burpees":                "burpees.gif",
};

function getWorkoutImage(name) {
    const filename = workoutImages[name];
    if (filename) {
        return `/static/img/workouts/${filename}`;
    }
    return `/static/img/workouts/placeholder.jpg`;
}

const groupColors = {
    chest:     'badge-chest',
    back:      'badge-back',
    legs:      'badge-legs',
    shoulders: 'badge-shoulders',
    arms:      'badge-arms',
    core:      'badge-core',
    cardio:    'badge-cardio',
};

const groupBgColors = {
    chest:     '#e63946',
    back:      '#457b9d',
    legs:      '#2a9d8f',
    shoulders: '#e9c46a',
    arms:      '#f4a261',
    core:      '#6a4c93',
    cardio:    '#e76f51',
};

function getBadgeClass(muscleGroup) {
    if (groupColors[muscleGroup]) {
        return groupColors[muscleGroup];
    }
    return 'bg-secondary';
}

function getBgColor(muscleGroup) {
    if (groupBgColors[muscleGroup]) {
        return groupBgColors[muscleGroup];
    }
    return '#adb5bd';
}

function showToast(title, message) {
    document.getElementById('toastTitle').textContent = title;
    document.getElementById('toastContent').textContent = message;
    const toast = new bootstrap.Toast(document.getElementById('appToast'));
    toast.show();
}

async function loadRoutine() {
    const response = await fetch(`/api/routines/${routineId}`);
    if (!response.ok) {
        document.getElementById('routine-name').textContent = 'Routine not found';
        return;
    }
    const routine = await response.json();
    renderRoutine(routine);
}

function renderRoutine(routine) {
    document.getElementById('routine-name').textContent = routine.name;

    let totalSets = 0;
    for (const rw of routine.workouts) {
        totalSets += rw.sets;
    }
    const minutes = Math.round(totalSets * 2);

    let description = routine.description || '';
    if (routine.workouts.length > 0) {
        description += ` · ${routine.workouts.length} exercises · ~${minutes} min`;
    }
    
    document.getElementById('routine-description').textContent = description;

    document.getElementById('editRoutineName').value = routine.name;
    document.getElementById('editRoutineDesc').value = routine.description || '';

    const list = document.getElementById('workout-list');

    if (routine.workouts.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <span class="material-symbols-outlined" style="font-size:48px">fitness_center</span>
                <p class="mt-2">No workouts yet. Add some using the button above!</p>
            </div>`;
        return;
    }

    list.innerHTML = '';
    for (const rw of routine.workouts) {
        const w = rw.workout;
        const badgeClass = getBadgeClass(w.muscle_group);
        const bgColor = getBgColor(w.muscle_group);
        const imgSrc = getWorkoutImage(w.name);
        const workoutName = w.name.replace(/'/g, '');

        list.innerHTML += `
            <div class="workout-row">
                <div style="width:140px; height:100px; border-radius:0.5rem; flex-shrink:0; overflow:hidden; background:${bgColor};">
                    <img src="${imgSrc}" alt="${w.name}"
                        onerror="this.style.display='none'"
                        style="width:100%; height:100%; object-fit:cover; object-position:top;">
                </div>
                <div class="workout-info">
                    <h6>${w.name}</h6>
                    <small>
                        <span class="badge ${badgeClass} me-1">${w.muscle_group}</span>
                        ${w.difficulty}
                    </small>
                </div>
                <div class="sets-reps-badge">
                    ${rw.sets} sets x ${rw.reps} reps
                </div>
                <div class="workout-actions">
                    <button class="btn btn-sm btn-outline-secondary" title="Edit sets/reps"
                        onclick="openEditSets(${rw.id}, ${rw.sets}, ${rw.reps})">
                        <span class="material-symbols-outlined" style="font-size:16px">edit</span>
                    </button>
                    <button class="btn btn-sm btn-outline-primary" title="Remix - swap for an alternative"
                        onclick="openRemix(${rw.id}, ${rw.workout_id}, '${workoutName}', '${w.muscle_group}')">
                        <span class="material-symbols-outlined" style="font-size:16px">shuffle</span>
                        Remix
                    </button>
                    <button class="btn btn-sm btn-outline-danger" title="Remove from routine"
                        onclick="removeWorkout(${rw.id})">
                        <span class="material-symbols-outlined" style="font-size:16px">remove</span>
                    </button>
                </div>
            </div>`;
    }
}

document.getElementById('editRoutineForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const data = {
        name: document.getElementById('editRoutineName').value,
        description: document.getElementById('editRoutineDesc').value,
    };

    const response = await fetch(`/api/routines/${routineId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        bootstrap.Modal.getInstance(document.getElementById('editRoutineModal')).hide();
        loadRoutine();
        showToast('Saved', 'Routine updated.');
    } 
    
    else {
        showToast('Error', 'Could not update routine.');
    }
});

async function loadAllWorkouts() {
    let url = '/api/workouts';
    if (addWorkoutFilter) {
        url = `/api/workouts?muscle_group=${addWorkoutFilter}`;
    }
    const response = await fetch(url);
    allWorkouts = await response.json();
    renderAddWorkoutList(allWorkouts);
}

function renderAddWorkoutList(workouts) {
    const container = document.getElementById('add-workout-list');

    if (workouts.length === 0) {
        container.innerHTML = '<p class="text-muted">No workouts found.</p>';
        return;
    }

    container.innerHTML = '';
    for (const w of workouts) {
        const bgColor = getBgColor(w.muscle_group);
        const imgSrc = getWorkoutImage(w.name);

        container.innerHTML += `
            <div class="d-flex justify-content-between align-items-center py-2 border-bottom gap-3">
                <div style="width:60px; height:45px; border-radius:0.4rem; flex-shrink:0; overflow:hidden; background:${bgColor};">
                    <img src="${imgSrc}" alt="${w.name}"
                        onerror="this.style.display='none'"
                        style="width:100%; height:100%; object-fit:cover; object-position:top;">
                </div>
                <div style="flex:1;">
                    <strong>${w.name}</strong>
                    <span class="text-muted small ms-2">${w.difficulty}</span>
                </div>
                <button class="btn btn-sm btn-primary" onclick="addWorkout(${w.id})">Add</button>
            </div>`;
    }
}

function filterAddWorkouts(group, btn) {
    addWorkoutFilter = group;
    document.querySelectorAll('#add-workout-filters .btn').forEach(function(b) {
        b.classList.remove('active');
    });
    btn.classList.add('active');
    loadAllWorkouts();
}

document.getElementById('addWorkoutModal').addEventListener('show.bs.modal', loadAllWorkouts);

async function addWorkout(workoutId) {
    const response = await fetch(`/api/routines/${routineId}/workouts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workout_id: workoutId, sets: 3, reps: 10 })
    });

    if (response.ok) {
        bootstrap.Modal.getInstance(document.getElementById('addWorkoutModal')).hide();
        loadRoutine();
        showToast('Added!', 'Workout added to routine.');
    } 
    
    else {
        showToast('Error', 'Could not add workout.');
    }
}

function openEditSets(rwId, sets, reps) {
    document.getElementById('editRwId').value = rwId;
    document.getElementById('editSets').value = sets;
    document.getElementById('editReps').value = reps;
    new bootstrap.Modal(document.getElementById('editSetsModal')).show();
}

document.getElementById('editSetsForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const rwId = document.getElementById('editRwId').value;
    const data = {
        sets: parseInt(document.getElementById('editSets').value),
        reps: parseInt(document.getElementById('editReps').value),
    };

    const response = await fetch(`/api/routines/${routineId}/workouts/${rwId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        bootstrap.Modal.getInstance(document.getElementById('editSetsModal')).hide();
        loadRoutine();
        showToast('Updated', 'Sets and reps saved.');
    } 
    
    else {
        showToast('Error', 'Could not update sets/reps.');
    }
});


async function removeWorkout(rwId) {
    if (!confirm('Remove this workout from the routine?')) 
        return;

    const response = await fetch(`/api/routines/${routineId}/workouts/${rwId}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        loadRoutine();
        showToast('Removed', 'Workout removed from routine.');
    } 
    
    else {
        showToast('Error', 'Could not remove workout.');
    }
}

async function openRemix(rwId, workoutId, workoutName, muscleGroup) {

    currentRemixRwId = rwId;
    document.getElementById('remixCurrentName').textContent = workoutName;
    document.getElementById('remixGroup').textContent = muscleGroup;

    const optionsEl = document.getElementById('remix-options');
    optionsEl.innerHTML = '<p class="text-muted">Loading alternatives...</p>';

    new bootstrap.Modal(document.getElementById('remixModal')).show();

    const response = await fetch(`/api/workouts/${workoutId}/alternatives`);
    const alternatives = await response.json();

    if (alternatives.length === 0) {
        optionsEl.innerHTML = '<p class="text-muted">No alternative workouts found for this muscle group.</p>';
        return;
    }

    optionsEl.innerHTML = '';

    for (const alt of alternatives) {
        let desc = '';
        if (alt.description) {
            desc = alt.description;
        }
        const altName = alt.name.replace(/'/g, '');

        optionsEl.innerHTML += `
            <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <div>
                    <strong>${alt.name}</strong>
                    <span class="text-muted small ms-2">${alt.difficulty}</span>
                    <p class="mb-0 text-muted small">${desc}</p>
                </div>
                <button class="btn btn-sm btn-primary ms-2" onclick="applyRemix(${alt.id}, '${altName}')">
                    Swap
                </button>
            </div>`;
    }
}

async function applyRemix(newWorkoutId, newWorkoutName) {
    const response = await fetch(`/api/routines/${routineId}/workouts/${currentRemixRwId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workout_id: newWorkoutId })
    });

    if (response.ok) {
        bootstrap.Modal.getInstance(document.getElementById('remixModal')).hide();
        loadRoutine();
        showToast('Remixed!', `Swapped to ${newWorkoutName}.`);
    } 
    
    else {
        showToast('Error', 'Could not apply remix.');
    }
}

loadRoutine();