function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function collectGridData() {
    console.log('collectGridData() called');
    const gridData = [];

    const grid = window.grid;
    console.log('Grid instance:', grid);

    if (!grid) {
        console.error('Could not get grid instance');
        return gridData;
    }

    grid.forEachNode(node => {
        console.log('Processing node:', node);
        if (!node || !node.data) {
            console.log('Skipping invalid node');
            return;
        }

        const rowData = node.data; 
        if (rowData.job_number && (rowData.hours > 0 || (rowData.description && rowData.description.trim() !== ''))) {          // It's fetching the data correctly
            const entry = {
                id: rowData.id,
                staff_id: rowData.staff_id,
                job_number: rowData.job_number,
                description: rowData.description,
                hours: rowData.hours,
                mins_per_item: rowData.mins_per_item,
                items: rowData.items,
                wage_amount: rowData.wage_amount,
                charge_out_rate: 1,
                timesheet_date: window.timesheet_data.timesheet_date,
                bill_amount: rowData.bill_amount,
                date: rowData.date,
                job_data: rowData.job_data,
                is_billable: rowData.is_billable || true,
                notes: rowData.notes || '',
                rate_type: rowData.rate_type || 'ORDINARY'
            };
            gridData.push(entry);
        }
    });

    console.log('Final collected data:', gridData);
    return gridData;
}

function autosaveData() {
    const collectedData = collectGridData();
    if (!collectedData.length) {
        console.error("No timesheet data available for autosave.");
        return;
    }
    saveDataToServer({ time_entries: collectedData });
}

// Send data to the server
function saveDataToServer(collectedData) {
    console.log('Autosaving timesheet data to /api/autosave-timesheet/...', collectedData);

    fetch('/api/autosave-timesheet/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(collectedData)
    })
    .then(response => {
        if (!response.ok) {
            console.error('Server responded with an error:', response.status);
            return response.json().then(data => {
                console.error('Error details:', data);
                throw new Error(data.error || 'Server error');
            });
        }
        console.log('Autosave successful');
        return response.json();
    })
    .then(data => {
        console.log('Autosave successful:', data);
    })
    .catch(error => {
        console.error('Autosave failed:', error);
    });
}

// Get CSRF token for Django
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Debounced autosave function
const debouncedAutosave = debounce(autosaveData, 1000);

// Removed.  We debounce explicitly from the grid
// // Attach autosave to grid events
// document.addEventListener('DOMContentLoaded', () => {
//     window.gridOptions.api.addEventListener('cellValueChanged', () => {
//         console.log('Grid value changed, triggering debounced autosave.');
//         debouncedAutosave();
//     });
// });
