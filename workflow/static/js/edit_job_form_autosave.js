import {createNewRow} from '/static/js/deseralise_job_pricing.js';

let dropboxToken = null;

// Debounce function to avoid frequent autosave calls
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// Function to collect all data from the form
export function collectAllData() {
    const data = {};  // Collects main form data

    // Collect data directly from visible input fields in the form
    const formElements = document.querySelectorAll('.autosave-input');

    formElements.forEach(element => {
        let value = element.type === 'checkbox' ? element.checked : element.value.trim() || null;
        if (element.name === 'client_id' && !value) {
            console.error('Client ID missing. Ensure client selection updates the hidden input.');
        }
        data[element.name] = value;
    });

    // Collect additional fields not present in form inputs
    const additionalFields = {
        client_name: document.getElementById('job-client-name')?.textContent || 'N/A',
        created_at: document.getElementById('job-created-at')?.textContent || 'N/A',
    };
    Object.assign(data, additionalFields);

    // 2. Get all historical pricings that were passed in the initial context
    let historicalPricings = JSON.parse(JSON.stringify(window.historical_job_pricings_json));

    // 3. Collect latest revisions from AG Grid
    data.latest_estimate_pricing = collectGridData('estimate');
    data.latest_quote_pricing = collectGridData('quote');
    data.latest_reality_pricing = collectGridData('reality');

    // 4. Add the historical pricings to jobData
    data.historical_pricings = historicalPricings;

    // console.log('Collected Data:', data);
    data.job_is_valid = checkJobValidity(data);

    return data;
}

function checkJobValidity(data) {
    console.log('Checking job validity...');
    console.log('Data:', data);
    const requiredFields = ['name', 'client_id', 'contact_person', 'job_number'];
    const invalidFields = requiredFields.filter(field => !data[field] || data[field].trim() === '');

    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));


    if (invalidFields.length > 0) {
        console.warn(`Invalid fields: ${invalidFields.join(', ')}`);


        let firstInvalidElement = null;

        invalidFields.forEach(field => {
            const element = document.querySelector(`[name='${field}']`);
            if (element) {
                element.classList.add('is-invalid');
                if (!firstInvalidElement) {
                    firstInvalidElement = element;
                }
            }
        });

        // Scroll to the first invalid field
        if (firstInvalidElement) {
            firstInvalidElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstInvalidElement.focus();
        }

        return false;

    } else {
        return true;
    }
}

function isNonDefaultRow(data, gridName) {
    const defaultRow = createNewRow(gridName);

    // Compare data to the default row
    for (const key in defaultRow) {
        if (defaultRow[key] !== data[key]) {
            return true; // Not a default row
        }
    }

    return false; // Matches default row, so it's invalid
}

function collectGridData(section) {
    const grids = ['TimeTable', 'MaterialsTable', 'AdjustmentsTable'];
    const sectionData = {};

    grids.forEach(gridName => {
        const gridKey = `${section}${gridName}`;
        const gridData = window.grids[gridKey];

        if (gridData && gridData.api) {
            const rowData = [];
            gridData.api.forEachNode(node => {
                if (isNonDefaultRow(node.data, gridName)) {
                    const data = { ...node.data };
                    data.minutes_per_item = data.mins_per_item;
                    delete data.mins_per_item
                    rowData.push(data);
                }
            });

            // Convert to the correct key name
            let entryKey = gridName.toLowerCase().replace('table', '')
            if (entryKey === 'time') entryKey = 'time';
            if (entryKey === 'materials') entryKey = 'material';
            if (entryKey === 'adjustments') entryKey = 'adjustment';
            entryKey += '_entries';

            sectionData[entryKey] = rowData;
        } else {
            console.error(`Grid or API not found for ${gridKey}`);
        }
    });

    return sectionData;
}

function collectCostsData() {
    const costsTable = window.grids.costsTable;
    if (!costsTable || !costsTable.api) {
        console.error('Costs table not found or missing API.');
        return { headers: [], rows: [] };
    }

    const gridApi = costsTable.api;
    const columns = gridApi.getColumnDefs().filter(col => col.headerName && col.headerName !== 'Actions');
    const headers = columns.map(col => col.headerName);

    const rowData = [];
    gridApi.forEachNode(node => {
        const row = columns.map(col => {
            const value = node.data[col.field];
            if (["estimate", "quote", "reality"].includes(col.field) && typeof value === 'number') {
                return `$${value.toFixed(2)}`;
            }
            return value !== undefined ? value : 'N/A';
        });
        rowData.push(row);
    });

    console.log("Collected Costs Data:", { headers, rows: rowData });

    return { headers, rows: rowData };
}

async function getDropboxToken() {
    if (!dropboxToken) {
        const response = await fetch('/api/get-env-variable/?var_name=DROPBOX_ACCESS_TOKEN');
        if (response.ok) {
            const data = await response.json();
            dropboxToken = data.value; // Cache the token
            console.log('Fetched and cached Dropbox token:', dropboxToken);
        } else {
            console.error('Failed to fetch Dropbox token');
        }
    }
    return dropboxToken;
}

async function uploadToDropbox(file, dropboxPath) {
    const accessToken = await getDropboxToken();
    if (!accessToken) {
        console.error('No Dropbox token available');
        return false;
    }

    try {
        const response = await fetch('https://content.dropboxapi.com/2/files/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Dropbox-API-Arg': JSON.stringify({
                    path: dropboxPath,
                    mode: 'overwrite',
                    autorename: false,
                    mute: false,
                }),
                'Content-Type': 'application/octet-stream',
            },
            body: file,
        });

        if (!response.ok) {
            // Check Content-Type to handle non-JSON errors
            const contentType = response.headers.get('Content-Type');
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                console.error('Dropbox API error:', errorData);
            } else {
                const errorText = await response.text(); // Handle non-JSON responses
                console.error('Dropbox upload failed (non-JSON):', errorText);
            }
            return false;
        }

        // Parse and log the successful response
        const data = await response.json();
        console.log('File uploaded to Dropbox:', data);
        return true;
    } catch (error) {
        console.error('Dropbox upload failed:', error);
        return false;
    }
}

async function fetchImageAsBase64(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch image: ${response.statusText}`);
        }
        const blob = await response.blob();
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result); // Base64 da imagem
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    } catch (error) {
        console.error(`Error fetching image from ${url}:`, error);
        throw error;
    }
}

async function exportJobToPDF(jobData) {
    return new Promise(async (resolve, reject) => {
        try {
            const logoBase64 = await fetchImageAsBase64('/static/logo_msm.png');
    
            const pricingSections = [
                { section: "Estimate", grids: [
                    {name: "estimateTimeTable", label: "Time"},
                    {name: "estimateMaterialsTable", label: "Materials"}, 
                    {name: "estimateAdjustmentsTable", label: "Adjustments"}
                ]},
                { section: "Quote", grids: [
                    {name: "quoteTimeTable", label: "Time"},
                    {name: "quoteMaterialsTable", label: "Materials"},
                    {name: "quoteAdjustmentsTable", label: "Adjustments"}
                ]},
                { section: "Reality", grids: [
                    {name: "realityTimeTable", label: "Time"},
                    {name: "realityMaterialsTable", label: "Materials"},
                    {name: "realityAdjustmentsTable", label: "Adjustments"}
                ]},
            ];
    
            const pricingContent = pricingSections.map(({ section, grids }) => {
                const sectionContent = [
                    { text: section, style: 'sectionHeader', margin: [0, 20, 0, 10] },
                ];
    
                grids.forEach((grid) => {
                    const gridInstance = window.grids[grid.name];
                    if (!gridInstance || !gridInstance.api) {
                        sectionContent.push({ text: `Grid '${grid.name}' not found or missing API.`, style: 'error' });
                        return;
                    }
    
                    sectionContent.push({ text: grid.label, style: 'gridHeader', margin: [0, 10, 0, 5] });
    
                    const gridApi = gridInstance.api;
                    const columns = gridApi.getColumnDefs().filter(col => col.headerName !== '' && col.headerName !== 'Timesheet');
                    const headers = columns.map(col => col.headerName || 'N/A');
    
                    const rowData = [];
                    gridApi.forEachNode(node => {
                        const row = columns.map(col => {
                            const value = node.data[col.field];
                            if (["cost", "revenue", "price_adjustment", "cost_adjustment"].includes(col.field) && typeof value === 'number') {
                                return `$${value.toFixed(2)}`;
                            }
                            return value || 'N/A';
                        });
                        rowData.push(row);
                    });
    
                    if (rowData.length > 0) {
                        sectionContent.push({
                            table: {
                                headerRows: 1,
                                widths: Array(headers.length).fill('*'),
                                body: [
                                    headers.map(header => ({
                                        text: header,
                                        fillColor: '#004aad',
                                        color: '#ffffff',
                                        bold: true,
                                        fontSize: 12,
                                    })),
                                    ...rowData,
                                ],
                            },
                            margin: [0, 5, 0, 15],
                        });
                    } else {
                        sectionContent.push({ text: `No data available for '${grid.label}'.`, style: 'error' });
                    }
                });
    
                return sectionContent;
            }).flat();
    
            const revenueAndCostsContent = ["revenueTable", "costsTable"].map((gridKey) => {
                const grid = window.grids[gridKey];
                if (!grid || !grid.api) {
                    return { text: `Grid '${gridKey}' not found or missing API.`, style: 'error' };
                }
            
                const title = gridKey === "revenueTable" ? "Revenue Details" : "Costs Details";
                const gridApi = grid.api;
                const columns = gridApi.getColumnDefs().filter(col => col.headerName !== '' && col.headerName !== 'Timesheet');
                const headers = columns.map(col => col.headerName || 'N/A');
            
                const rowData = [];
                gridApi.forEachNode(node => {
                    const row = columns.map(col => {
                        const value = node.data[col.field];
                        if (["estimate", "quote", "reality"].includes(col.field) && typeof value === 'number') {
                            return `$${value.toFixed(2)}`;
                        }
                        return value || 'N/A';
                    });
                    rowData.push(row);
                });
            
                return [
                    { text: title, style: 'sectionHeader', margin: [0, 20, 0, 10] },
                    {
                        table: {
                            headerRows: 1,
                            widths: Array(headers.length).fill('*'),
                            body: [
                                headers.map(header => ({
                                    text: header,
                                    fillColor: '#004aad',
                                    color: '#ffffff',
                                    bold: true,
                                    fontSize: 12,
                                })),
                                ...rowData,
                            ],
                        },
                        margin: [0, 5, 0, 15],
                    },
                ];
            }).flat();
    
            const docDefinition = {
                content: [
                    {
                        image: logoBase64,
                        width: 150,
                        alignment: 'center',
                        margin: [0, 0, 0, 20],
                    },
                    {
                        text: 'Job Summary',
                        style: 'header',
                        margin: [0, 0, 0, 20],
                    },
                    {
                        text: `Generated on: ${new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}`,
                        style: 'subheader',
                        alignment: 'right',
                    },
                    { text: 'Job Details', style: 'sectionHeader', margin: [0, 20, 0, 10] },
                    {
                        table: {
                            headerRows: 1,
                            widths: ['*', '*'],
                            body: [
                                [
                                    { text: 'Field', fillColor: '#004aad', color: '#ffffff', bold: true },
                                    { text: 'Value', fillColor: '#004aad', color: '#ffffff', bold: true }
                                ],
                                ['Job Name', jobData.name || 'N/A'],
                                ['Job Number', jobData.job_number || 'N/A'],
                                ['Client', jobData.client_name || 'N/A'],
                                ['Contact Person', jobData.contact_person || 'N/A'],
                                ['Description', jobData.description || 'N/A'],
                                ['Job Created On', new Date(jobData.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" }) || 'N/A'],
                            ],
                        },
                        margin: [0, 0, 0, 20],
                    },
                    ...pricingContent,
                    ...revenueAndCostsContent,
                ],
                styles: {
                    header: { fontSize: 22, bold: true, alignment: 'center' },
                    subheader: { fontSize: 12, italic: true },
                    sectionHeader: { fontSize: 16, bold: true, margin: [0, 20, 0, 10] },
                    gridHeader: { fontSize: 14, bold: true, color: '#444444' },
                    error: { fontSize: 12, color: 'red', italic: true },
                },
            };
    
            pdfMake.createPdf(docDefinition).getBlob((blob) => {
                resolve(blob);
            });
        } catch (error) {
            console.error('Error generating Job PDF:', error);
        }
    });
}

async function exportCostsToPDF(costsData, jobData) {
    try {
        const logoBase64 = await fetchImageAsBase64('/static/logo_msm.png');    
        const docDefinition = {
            content: [
                {
                    image: logoBase64,
                    width: 150,
                    alignment: 'center',
                    margin: [0, 0, 0, 20],
                },
                {
                    text: 'Costs Summary',
                    style: 'header',
                    margin: [0, 0, 0, 20],
                },
                {
                    text: `Generated on: ${new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}`,
                    style: 'subheader',
                    alignment: 'right',
                },
                { text: 'Job Summary', style: 'sectionHeader', margin: [0, 20, 0, 10] },
                {
                    table: {
                        headerRows: 1,
                        widths: ['*', '*'],
                        body: [
                            ['Field', 'Value'],
                            ['Job Name', jobData.name || 'N/A'],
                            ['Job Number', jobData.job_number || 'N/A'],
                            ['Client', jobData.client_name || 'N/A'],
                            ['Created At', new Date(jobData.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" }) || 'N/A'],
                            ['Description', jobData.description || 'N/A'],
                        ],
                    },
                },
                { text: 'Cost Details', style: 'sectionHeader', margin: [0, 20, 0, 10] },
                {
                    table: {
                        headerRows: 1,
                        widths: ['*', 'auto', 'auto', 'auto'],
                        body: [
                            costsData.headers,
                            ...costsData.rows,
                        ],
                    },
                },
            ],
            styles: {
                header: { fontSize: 22, bold: true, alignment: 'center' },
                subheader: { fontSize: 12, italic: true },
                sectionHeader: { fontSize: 16, bold: true, margin: [0, 20, 0, 10] },
            },
        };
    
        pdfMake.createPdf(docDefinition).open();
    } catch (error) {
        console.error('Error fetching logo:', error);
    }
}

function addGridToPDF(doc, title, rowData, startY) {
    // Extract column headers from the first row's keys
    const columns = Object.keys(rowData[0] || {});
    const rows = rowData.map((row) => columns.map((col) => row[col] || ''));

    // Add table to the PDF
    doc.text(title, 10, startY);
    doc.autoTable({
        head: [columns],
        body: rows,
        startY: startY + 10,
    });

    // Return the new Y position after the table
    return doc.lastAutoTable.finalY + 10;
}


async function handlePDF(pdfBlob, mode, jobData) {
    const pdfURL = URL.createObjectURL(pdfBlob);

    switch (mode) {
        case 'dropbox': // Warning, hasn't been tested in a while
            const dropboxPath = `/MSM Workflow/Job-${jobData.job_number}/JobSummary.pdf`;
            if (!(await uploadToDropbox(pdfBlob, dropboxPath))) {
                throw new Error(`Failed to upload PDF for Job ${jobData.job_number}`);
            }
            break;
        case 'upload':
            const formData = new FormData();
            formData.append('job_number', jobData.job_number);
            formData.append('files', new File([pdfBlob], `${jobData.name}.pdf`, { type: 'application/pdf' }));

            // The correct endpoint for job file POST/GET is just "/api/job-files" 
            fetch('/api/job-files/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() },
                body: formData
            }).then(response => {
                if (!response.ok) {
                    console.error(`Failed to upload PDF for Job ${jobData.job_number}`);
                }
            });
            break;
        case 'print':
            const newWindow = window.open(pdfURL, '_blank');
            if (!newWindow) throw new Error('Popup blocked. Unable to print the PDF.');
            newWindow.print();
            break;
        case 'preview':
            window.open(pdfURL, '_blank');
            break;
        case 'download':
            const link = document.createElement('a');
            link.href = pdfURL;
            link.download = `${jobData.name}.pdf`;
            link.click();
            break;
        default:
            throw new Error(`Unsupported mode: ${mode}`);
    }
}

let isGeneratingPDF = false;

export function handlePrintJob() {
    try {
        if (isGeneratingPDF) {
            console.warn('PDF generation is already in progress.');
            return;
        }

        isGeneratingPDF = true;

        const collectedData = collectAllData();

        if (!collectedData.job_is_valid) {
            console.error('Job is not valid. Please complete all required fields before printing.');
            isGeneratingPDF = false;
            return;
        }

        exportJobToPDF(collectedData)
            .then((pdfBlob) => {
                handlePDF(pdfBlob, 'preview', collectedData);
                isGeneratingPDF = false;
            })
            .catch((error) => {
                console.error('Error generating Job PDF:', error);
                isGeneratingPDF = false;
            });
    } catch (error) {
        console.error('Error during Print Job process:', error);
        isGeneratingPDF = false;
    }
}

export function handleExportCosts() {
    try {
        const jobData = collectAllData();
        const costsData = collectCostsData();

        if (!jobData.job_is_valid) {
            console.error('Job is not valid. Complete all required fields.');
            return;
        }

        exportCostsToPDF(costsData, jobData);
    } catch (error) {
        console.error('Error exporting costs with PDFMake:', error);
    }
}

// Autosave function to send data to the server
export function autosaveData() {
    const collectedData = collectAllData();

    // Skip autosave if the job is not yet ready for saving
    if (collectedData.job_is_valid) {
        saveDataToServer(collectedData);
    } else {
        console.log('Job is not valid. Skipping autosave.');
        renderMessages([{ level: 'error', message: 'Please complete all required fields before saving.' }], 'job-details');
        return
    }
}


function saveDataToServer(collectedData) {
    if (!checkJobValidity(collectedData)) {
        console.error('Collected data is invalid. Skipping autosave.');
        return;
    }

    console.log('Autosaving data to /api/autosave-job/...', collectedData);

    fetch('/api/autosave-job/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(collectedData),
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    if (data.errors) {
                        handleValidationErrors(data.errors);
                        renderMessages([{ level: 'error', message: 'Failed to save data. Please try again.' }], 'job-details');
                    }
                    throw new Error('Validation errors occurred');
                });
            }
            return response.json();
        })
        .then(data => {
            exportJobToPDF(collectedData)
                .then((pdfBlob) => {
                    handlePDF(pdfBlob, 'upload', collectedData);
                    console.log('Autosave successful:', data);
                    renderMessages([{ level: 'success', message: 'Job updated successfully.' }], 'job-details');
                });
        })
        .catch(error => {
            renderMessages([{ level: 'error', message: `Autosave failed: ${error.message}` }]);
        });
}

function handleValidationErrors(errors) {
    // Clear previous error messages
    document.querySelectorAll('.invalid-feedback').forEach(errorMsg => errorMsg.remove());
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

    // Display new errors
    for (const [field, messages] of Object.entries(errors)) {
        const element = document.querySelector(`[name='${field}']`);
        if (element) {
            element.classList.add('is-invalid');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.innerText = messages.join(', ');
            element.parentElement.appendChild(errorDiv);

            // Attach listener to remove the error once the user modifies the field
            element.addEventListener('input', () => {
                element.classList.remove('is-invalid');
                if (element.nextElementSibling && element.nextElementSibling.classList.contains('invalid-feedback')) {
                    element.nextElementSibling.remove();
                }
            }, { once: true });
        }
    }
}

// Helper function to get CSRF token for Django
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function removeValidationError(element) {
    element.classList.remove('is-invalid');
    if (element.nextElementSibling && element.nextElementSibling.classList.contains('invalid-feedback')) {
        element.nextElementSibling.remove();
    }
}

// Debounced version of the autosave function
export const debouncedAutosave = debounce(function () {
    console.log('Debounced autosave called');
    autosaveData();
}, 1000);

const debouncedRemoveValidation = debounce(function (element) {
    console.log('Debounced validation removal called for element:', element);
    removeValidationError(element);
}, 1000);



// Attach autosave to form elements (input, select, textarea)
// Synchronize visible UI fields with hidden form fields
document.addEventListener('DOMContentLoaded', function () {
    // Synchronize all elements with the 'autosave-input' class
    const autosaveInputs = document.querySelectorAll('.autosave-input');


    // Attach change event listener to handle special input types like checkboxes
    autosaveInputs.forEach(fieldElement => {
        fieldElement.addEventListener('blur', function () {
            console.log('Blur event fired for:', fieldElement);
            debouncedRemoveValidation(fieldElement);
            debouncedAutosave();
        });

       if (fieldElement.type === 'checkbox' || fieldElement.tagName === 'SELECT') {
            fieldElement.addEventListener('change', function () {
                if (fieldElement.classList.contains('is-invalid')) {
                    fieldElement.classList.remove('is-invalid');
                }
                debouncedRemoveValidation(fieldElement)
                debouncedAutosave();
            });
        }
    });
});

function getAllRowData(gridApi) {
    const rowData = [];
    gridApi.forEachNode(node => rowData.push(node.data));
    return rowData;
}

function copyGridData(sourceGridApi, targetGridApi) {
    if (!sourceGridApi || !targetGridApi) {
        console.error('Source or target grid API is not defined.');
        return;
    }

    const sourceData = getAllRowData(sourceGridApi);
    const targetData = getAllRowData(targetGridApi);

    targetGridApi.applyTransaction({ remove: targetData });
    targetGridApi.applyTransaction({ add: sourceData });
}

export function copyEstimateToQuote() {
    const grids = ['TimeTable', 'MaterialsTable', 'AdjustmentsTable'];

    grids.forEach(gridName => {
        const estimateGridKey = `estimate${gridName}`;
        const quoteGridKey = `quote${gridName}`;
        const estimateGridApi = window.grids[estimateGridKey]?.api;
        const quoteGridApi = window.grids[quoteGridKey]?.api;

        if (estimateGridApi && quoteGridApi) {
            copyGridData(estimateGridApi, quoteGridApi); // Uses the generic method
        } else {
            console.error(
                `Grid API not found or not initialized for keys: ${estimateGridKey}, ${quoteGridKey}`
            );
        }
    });

    // Trigger autosave to sync changes
    debouncedAutosave();

    // Display success message
    renderMessages([
        {
            level: 'success',
            message: 'Estimates successfully copied to Quotes.',
        },
    ], 'estimate');
}
