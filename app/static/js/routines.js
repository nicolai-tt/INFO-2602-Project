function showToast(title, message) {
    document.getElementById('toastTitle').textContent = title;
    document.getElementById('toastContent').textContent = message;
    const toast = new bootstrap.Toast(document.getElementById('appToast'));
    toast.show();
}

async function loadRoutines() {
    const response = await fetch('/api/routines');
    if (!response.ok) {
        document.getElementById('routines-grid').innerHTML =
            '<p class="text-danger">Could not load routines.</p>';
        return;
    }
    const routines = await response.json();
    renderRoutines(routines);
}

function estimateDuration(workoutCount) {
    const minutes = workoutCount * 10;
    if (minutes >= 60) {
        const hours = Math.round(minutes / 60);
        const remaining = minutes % 60;
        if (remaining > 0) {
            return `~${hours}h ${remaining}m`;
        }
        return `~${hours}h`;
    }
    return `~${minutes} min`;
}

function renderRoutines(routines) {
    const grid = document.getElementById('routines-grid');

    if (routines.length === 0) {
        grid.innerHTML = `
            <div class="col-12 text-center text-muted py-5">
                <span class="material-symbols-outlined" style="font-size:48px">format_list_bulleted</span>
                <p class="mt-2">You haven't created any routines yet.</p>
                <button class="btn btn-primary mt-2" data-bs-toggle="modal" data-bs-target="#createRoutineModal">
                    Create your first routine
                </button>
            </div>`;
        return;
    }

    grid.innerHTML = '';
    
    for (const r of routines) {
        let countLabel = `${r.workout_count} workouts`;
        if (r.workout_count === 1) {
            countLabel = '1 workout';
        }

        let durationHtml = '';
        if (r.workout_count > 0) {
            const duration = estimateDuration(r.workout_count);
            durationHtml = `
                <span class="text-muted small">
                    <span class="material-symbols-outlined align-middle" style="font-size:15px">schedule</span>
                    ${duration}
                </span>`;
        }

        let desc = 'No description.';
        if (r.description) {
            desc = r.description;
        }

        grid.innerHTML += `
            <div class="col-md-4 col-sm-6">
                <div class="card routine-card h-100" onclick="window.location='/routines/${r.id}'">
                    <div class="card-body">
                        <h5 class="card-title fw-bold">${r.name}</h5>
                        <p class="card-text text-muted small">${desc}</p>
                        <div class="d-flex gap-3 mt-2">
                            <span class="text-muted small">
                                <span class="material-symbols-outlined align-middle" style="font-size:15px">fitness_center</span>
                                ${countLabel}
                            </span>
                            ${durationHtml}
                        </div>
                    </div>
                    <div class="card-footer d-flex justify-content-between align-items-center">
                        <span class="text-muted small">Click to view</span>
                        <button class="btn btn-sm btn-outline-danger"
                            onclick="deleteRoutine(${r.id}, event)">
                            <span class="material-symbols-outlined" style="font-size:16px">delete</span>
                        </button>
                    </div>
                </div>
            </div>`;
    }
}

async function deleteRoutine(routineId, event) {

    event.stopPropagation();

    if (!confirm('Delete this routine and all its workouts?')) 
        return;

    const response = await fetch(`/api/routines/${routineId}`, { method: 'DELETE' });

    if (response.ok) {
        loadRoutines();
        showToast('Deleted', 'Routine removed.');
    } 
    
    else {
        showToast('Error', 'Could not delete routine.');
    }
}

document.getElementById('createRoutineForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const form = new FormData(this);
    const data = Object.fromEntries(form.entries());

    const response = await fetch('/api/routines', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        bootstrap.Modal.getInstance(document.getElementById('createRoutineModal')).hide();
        this.reset();
        loadRoutines();
        showToast('Created!', 'New routine ready.');
    } 
    
    else {
        showToast('Error', 'Could not create routine.');
    }
});

loadRoutines();