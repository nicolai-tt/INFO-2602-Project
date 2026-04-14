let currentFilter = null;
let selectedWorkoutId = null;
let currentPage = 1;
const PER_PAGE = 9;

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

const difficultyColors = {
    beginner:     'bg-success',
    intermediate: 'bg-warning text-dark',
    advanced:     'bg-danger',
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

function getDiffClass(difficulty) {
    if (difficultyColors[difficulty]) {
        return difficultyColors[difficulty];
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

let allWorkouts = [];

async function loadWorkouts() {
    const response = await fetch('/api/workouts');
    allWorkouts = await response.json();
    applySearch();
}

function getFiltered() {

    const query = document.getElementById('workout-search').value.toLowerCase();
    const filtered = [];

    for (const w of allWorkouts) {
        if (currentFilter && w.muscle_group !== currentFilter) 
            continue;
        if (query && !w.name.toLowerCase().includes(query)) 
            continue;
        filtered.push(w);
    }

    return filtered;
}

function applySearch() {
    currentPage = 1;
    renderWorkouts(getFiltered());
}

function goToPage(page) {
    currentPage = page;
    renderWorkouts(getFiltered());
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function changePage(dir) {
    const filtered = getFiltered();
    const totalPages = Math.ceil(filtered.length / PER_PAGE);
    currentPage = currentPage + dir;
    if (currentPage < 1) currentPage = 1;
    if (currentPage > totalPages) currentPage = totalPages;
    renderWorkouts(filtered);
}

function renderWorkouts(workouts) {

    const grid = document.getElementById('workout-grid');
    const paginationBar = document.getElementById('pagination-bar');

    if (workouts.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center text-muted py-5">
                <span class="material-symbols-outlined" style="font-size:48px">search_off</span>
                <p class="mt-2">No workouts found.</p>
            </div>`;
        paginationBar.style.display = 'none';
        return;
    }

    const totalPages = Math.ceil(workouts.length / PER_PAGE);
    const start = (currentPage - 1) * PER_PAGE;
    const paged = workouts.slice(start, start + PER_PAGE);

    paginationBar.style.display = 'flex';
    document.getElementById('pagination-info').textContent =
        `Showing ${start + 1}-${Math.min(start + PER_PAGE, workouts.length)} of ${workouts.length} workouts`;
    document.getElementById('prev-btn').disabled = currentPage === 1;
    document.getElementById('next-btn').disabled = currentPage === totalPages;

    const pageNums = document.getElementById('page-numbers');
    pageNums.innerHTML = '';
    for (let i = 1; i <= totalPages; i++) {
        let btnClass = 'btn-outline-secondary';
        if (i === currentPage) {
            btnClass = 'btn-primary';
        }
        pageNums.innerHTML += `
            <button class="btn btn-sm ${btnClass}" onclick="goToPage(${i})">${i}</button>`;
    }

    grid.innerHTML = '';

    for (const w of paged) {
        const badgeClass = getBadgeClass(w.muscle_group);
        const diffClass = getDiffClass(w.difficulty);
        const bgColor = getBgColor(w.muscle_group);
        const imgSrc = getWorkoutImage(w.name);

        let imgPosition = 'top';
        if (w.name === 'Lunges') {
            imgPosition = 'center';
        }

        let deleteBtn = '';

        if (isAdmin) {
            deleteBtn = `
                <button class="btn btn-sm btn-outline-danger" onclick="deleteWorkout(${w.id}, event)">
                    <span class="material-symbols-outlined" style="font-size:16px">delete</span>
                </button>`;
        }

        let desc = 'No description.';
        if (w.description) {
            desc = w.description;
        }

        const workoutName = w.name.replace(/'/g, '');

        grid.innerHTML += `
            <div class="col-md-4 col-sm-6">
                <div class="card workout-card h-100">
                    <div style="height:260px; background:${bgColor}; overflow:hidden;">
                        <img src="${imgSrc}"
                            class="card-img-top" alt="${w.name}"
                            onerror="this.style.display='none'"
                            style="object-fit:cover; object-position:${imgPosition}; height:260px; width:100%;">
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title mb-0">${w.name}</h5>
                            ${deleteBtn}
                        </div>
                        <div class="mb-2">
                            <span class="badge ${badgeClass} me-1">${w.muscle_group}</span>
                            <span class="badge ${diffClass}">${w.difficulty}</span>
                        </div>
                        <p class="card-text text-muted small">${desc}</p>
                    </div>
                    <div class="card-footer bg-transparent border-0 pt-0 pb-3 px-3">
                        <button class="btn btn-sm btn-outline-primary w-100"
                            onclick="openAddToRoutine(${w.id}, '${workoutName}')">
                            + Add to Routine
                        </button>
                    </div>
                </div>
            </div>`;
    }
}

function setFilter(group, btn) {
    currentFilter = group;
    document.querySelectorAll('.filter-btn').forEach(function(b) {
        b.classList.remove('active');
    });
    btn.classList.add('active');
    applySearch();
}

async function openAddToRoutine(workoutId, workoutName) {
    selectedWorkoutId = workoutId;
    document.getElementById('selectedWorkoutName').textContent = workoutName;

    const listEl = document.getElementById('routine-list');
    listEl.innerHTML = '<p class="text-muted">Loading...</p>';

    new bootstrap.Modal(document.getElementById('addToRoutineModal')).show();

    const response = await fetch('/api/routines');
    if (!response.ok) {
        listEl.innerHTML = '<p class="text-danger">Could not load routines.</p>';
        return;
    }

    const routines = await response.json();

    if (routines.length === 0) {
        listEl.innerHTML = '<p class="text-muted">You have no routines yet.</p>';
        return;
    }

    listEl.innerHTML = '';
    for (const r of routines) {
        listEl.innerHTML += `
            <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <span>${r.name}</span>
                <button class="btn btn-sm btn-primary" onclick="addToRoutine(${r.id})">Add</button>
            </div>`;
    }
}

async function addToRoutine(routineId) {
    const response = await fetch(`/api/routines/${routineId}/workouts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workout_id: selectedWorkoutId, sets: 3, reps: 10 })
    });

    bootstrap.Modal.getInstance(document.getElementById('addToRoutineModal')).hide();

    if (response.ok) {
        showToast('Done!', 'Workout added to your routine.');
    } 
    
    else {
        showToast('Error', 'Could not add workout to routine.');
    }
}

async function deleteWorkout(workoutId, event) {
    event.stopPropagation();
    if (!confirm('Delete this workout?')) return;

    const response = await fetch(`/api/workouts/${workoutId}`, { method: 'DELETE' });

    if (response.ok) {
        loadWorkouts();
        showToast('Deleted', 'Workout removed.');
    } 
    
    else {
        showToast('Error', 'Could not delete workout.');
    }
}

document.getElementById('addWorkoutForm').addEventListener('submit', async function (e) {

    e.preventDefault();

    const form = new FormData(this);
    const data = Object.fromEntries(form.entries());

    const response = await fetch('/api/workouts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        bootstrap.Modal.getInstance(document.getElementById('addWorkoutModal')).hide();
        this.reset();
        loadWorkouts();
        showToast('Created!', 'New workout added.');
    } 
    
    else {
        showToast('Error', 'Could not create workout.');
    }
});

function main() {
    
    if (isAdmin) {
        document.getElementById('addWorkoutBtn').style.display = 'inline-flex';
    }

    document.getElementById('workout-search').addEventListener('input', applySearch);
    loadWorkouts();
}

main();