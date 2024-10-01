// This listener is for the entries towards the top.  The material and description fields, etc.
document.addEventListener('DOMContentLoaded', function () {
    const materialField = document.getElementById('materialGaugeQuantity');
    const descriptionField = document.getElementById('description');

    function autoExpand(field) {
        field.style.height = 'inherit';
        const computed = window.getComputedStyle(field);
        const height = parseInt(computed.getPropertyValue('border-top-width'), 10)
            + parseInt(computed.getPropertyValue('padding-top'), 10)
            + field.scrollHeight
            + parseInt(computed.getPropertyValue('padding-bottom'), 10)
            + parseInt(computed.getPropertyValue('border-bottom-width'), 10);
        field.style.height = `${height}px`;
    }

    function addAutoExpand(field) {
        field.addEventListener('input', function () {
            autoExpand(field);
        });
        autoExpand(field);
    }

    if (materialField) addAutoExpand(materialField);
    if (descriptionField) addAutoExpand(descriptionField);
});

// This listener is for the job pricing grid
document.addEventListener('DOMContentLoaded', function () {
    function currencyFormatter(params) {
        return '$' + params.value.toFixed(2);
    }

    function numberParser(params) {
        return Number(params.newValue);
    }

    function calculateTotal(params) {
        const gridType = params.context.gridType;
        if (gridType === 'TimeTable') {
            return (params.data.items || 0) * (params.data.rate || 0);
        } else if (gridType === 'MaterialsTable') {
            return (params.data.quantity || 0) * (params.data.rate || 0);
        } else if (gridType === 'AdjustmentsTable') {
            return (params.data.quantity || 0) * (params.data.amount || 0);
        }
        return 0;
    }

    function calculateTotalMinutes(params) {
        return params.data.items * params.data.minsPerItem;
    }

    function deleteIconCellRenderer(params) {
        const isLastRow = params.api.getDisplayedRowCount() === 1;
        const iconClass = isLastRow ? 'delete-icon disabled' : 'delete-icon';
        return `<span class="${iconClass}">🗑️</span>`;
    }

    function onDeleteIconClicked(params) {
        if (params.api.getDisplayedRowCount() > 1) {
            params.api.applyTransaction({remove: [params.node.data]});
        }
    }

    function createNewRow(gridType) {
        if (gridType === 'TimeTable') {
            return {description: '', items: 0, minsPerItem: 0, totalMinutes: 0, rate: 0, total: 0};
        } else if (gridType === 'MaterialsTable') {
            return {itemCode: '', description: '', markup: 0, quantity: 0, rate: 0, total: 0, comments: ''};
        } else if (gridType === 'AdjustmentsTable') {
            return {description: '', quantity: 0, amount: 0, total: 0, comments: ''};
        }
        return null;
    }

    function onCellKeyDown(params) {
        if (params.event.key === 'Enter') {
            const isLastRow = params.api.getDisplayedRowCount() - 1 === params.rowIndex;
            if (isLastRow) {
                const newRow = createNewRow(params.context.gridType);
                if (newRow) {
                    params.api.applyTransaction({add: [newRow]});
                    setTimeout(() => {
                        params.api.setFocusedCell(params.rowIndex + 1, params.column.colId);
                        params.api.startEditingCell({
                            rowIndex: params.rowIndex + 1,
                            colKey: params.column.colId
                        });
                    }, 0);
                }
            }
        }
    }

    function createDefaultRowData(gridType) {
        const defaultData = {
            Time: {description: '', items: 0, minsPerItem: 0, totalMinutes: 0, rate: 0, total: 0},
            Materials: {itemCode: '', description: '', markup: 0, quantity: 0, rate: 0, total: 0, comments: ''},
            Adjustments: {description: '', quantity: 0, amount: 0, total: 0, comments: ''}
        };
        return [defaultData[gridType] || {}];
    }

    function calculateTotals() {
        const totals = {
            time: {estimate: 0, quote: 0, reality: 0},
            materials: {estimate: 0, quote: 0, reality: 0},
            adjustments: {estimate: 0, quote: 0, reality: 0}
        };
        const sections = ['estimate', 'quote', 'reality'];
        const gridTypes = ['Time', 'Materials', 'Adjustments'];

        sections.forEach(section => {
            gridTypes.forEach(gridType => {
                const gridKey = `${section}${gridType}Table`;
                const gridData = window.grids[gridKey];
                if (gridData && gridData.api) {
                    gridData.api.forEachNode(node => {
                        const total = parseFloat(node.data.total) || 0;
                        const totalType = gridType.toLowerCase();
                        if (totals[totalType] && totals[totalType][section] !== undefined) {
                            totals[totalType][section] += total;
                        }
                    });
                }
            });
        });

        const totalsGrid = window.grids['totalsTable'];
        if (totalsGrid && totalsGrid.api) {
            totalsGrid.api.forEachNode((node, index) => {
                const data = node.data;
                switch (index) {
                    case 0: // Total Time
                        data.estimate = totals.time.estimate;
                        data.quote = totals.time.quote;
                        data.reality = totals.time.reality;
                        break;
                    case 1: // Total Materials
                        data.estimate = totals.materials.estimate;
                        data.quote = totals.materials.quote;
                        data.reality = totals.materials.reality;
                        break;
                    case 2: // Total Adjustments
                        data.estimate = totals.adjustments.estimate;
                        data.quote = totals.adjustments.quote;
                        data.reality = totals.adjustments.reality;
                        break;
                    case 3: // Total Project Cost
                        data.estimate = totals.time.estimate + totals.materials.estimate + totals.adjustments.estimate;
                        data.quote = totals.time.quote + totals.materials.quote + totals.adjustments.quote;
                        data.reality = totals.time.reality + totals.materials.reality + totals.adjustments.reality;
                        break;
                }
            });
            totalsGrid.api.refreshCells();
        }
    }

    const commonGridOptions = {
        rowHeight: 28,
        headerHeight: 32,
        suppressPaginationPanel: true,
        suppressHorizontalScroll: true,
        defaultColDef: {
            sortable: true,
            resizable: true
        },
        onGridReady: function (params) {
            params.api.sizeColumnsToFit();
            setTimeout(() => {
                params.api.resetRowHeights();
            }, 0);

            const gridKey = params.context.gridKey;
            window.grids[gridKey] = {gridInstance: params.api, api: params.api};
        },
        onGridSizeChanged: params => {
            params.api.sizeColumnsToFit();
        },
        enterNavigatesVertically: true,
        enterNavigatesVerticallyAfterEdit: true,
        stopEditingWhenCellsLoseFocus: true,
        onCellKeyDown: onCellKeyDown,
        onCellValueChanged: function (event) {
            const gridType = event.context.gridType;
            const data = event.data;
            if (gridType === 'TimeTable') {
                data.totalMinutes = (data.items || 0) * (data.minsPerItem || 0);
                data.total = (data.items || 0) * (data.rate || 0);
            } else if (gridType === 'MaterialsTable') {
                data.total = (data.quantity || 0) * (data.rate || 0);
            } else if (gridType === 'AdjustmentsTable') {
                data.total = (data.quantity || 0) * (data.amount || 0);
            }
            event.api.refreshCells({rowNodes: [event.node], columns: ['total', 'totalMinutes'], force: true});
            debouncedAutosaveData(event);
            calculateTotals();
        }
    };

    const timeGridOptions = {
        ...commonGridOptions,
        columnDefs: [
            {headerName: 'Description', field: 'description', editable: true},
            {headerName: 'Items', field: 'items', editable: true, valueParser: numberParser},
            {headerName: 'Mins/Item', field: 'minsPerItem', editable: true, valueParser: numberParser},
            {headerName: 'Total Minutes', field: 'totalMinutes', editable: false},
            {
                headerName: 'Rate',
                field: 'rate',
                editable: true,
                valueParser: numberParser,
                valueFormatter: currencyFormatter
            },
            {headerName: 'Total', field: 'total', editable: false, valueFormatter: currencyFormatter},
            {
                headerName: '',
                field: '',
                width: 40,
                cellRenderer: deleteIconCellRenderer,
                onCellClicked: onDeleteIconClicked
            }
        ],
        rowData: [{description: '', items: 0, minsPerItem: 0, totalMinutes: 0, rate: 0, total: 0}],
        context: {gridType: 'TimeTable'},
    };

    const materialsGridOptions = {
        ...commonGridOptions,
        columnDefs: [
            {headerName: 'Item Code', field: 'itemCode', editable: true},
            {headerName: 'Description', field: 'description', editable: true},
            {headerName: 'Markup %', field: 'markup', editable: true, valueParser: numberParser},
            {headerName: 'Quantity', field: 'quantity', editable: true, valueParser: numberParser},
            {
                headerName: 'Rate',
                field: 'rate',
                editable: true,
                valueParser: numberParser,
                valueFormatter: currencyFormatter
            },
            {headerName: 'Total', field: 'total', editable: false, valueFormatter: currencyFormatter},
            {headerName: 'Comments', field: 'comments', editable: true},
            {
                headerName: '',
                field: '',
                width: 40,
                cellRenderer: deleteIconCellRenderer,
                onCellClicked: onDeleteIconClicked
            }
        ],
        rowData: [{itemCode: '', description: '', markup: 0, quantity: 0, rate: 0, total: 0, comments: ''}],
        context: {gridType: 'MaterialsTable'}
    };

    const adjustmentsGridOptions = {
        ...commonGridOptions,
        columnDefs: [
            {headerName: 'Description', field: 'description', editable: true},
            {headerName: 'Quantity', field: 'quantity', editable: true, valueParser: numberParser},
            {
                headerName: 'Amount',
                field: 'amount',
                editable: true,
                valueParser: numberParser,
                valueFormatter: currencyFormatter
            },
            {headerName: 'Total', field: 'total', editable: false, valueFormatter: currencyFormatter},
            {headerName: 'Comments', field: 'comments', editable: true},
            {
                headerName: '',
                field: '',
                width: 40,
                cellRenderer: deleteIconCellRenderer,
                onCellClicked: onDeleteIconClicked
            }
        ],
        rowData: [{description: '', quantity: 0, amount: 0, total: 0, comments: ''}],
        context: {gridType: 'AdjustmentsTable'}
    };

    const sections = ['estimate', 'quote', 'reality'];
    const workType = ['Time', 'Materials', 'Adjustments'];
    window.grids = {};

    sections.forEach(section => {
        workType.forEach(gridType => {
            const gridKey = `${section}${gridType}Table`;
            const gridElement = document.querySelector(`#${gridKey}`);

            if (!gridElement) {
                console.error(`Grid element not found for ${gridKey}`);
                return;
            }

            let specificGridOptions;
            switch (gridType) {
                case 'Time':
                    specificGridOptions = timeGridOptions;
                    break;
                case 'Materials':
                    specificGridOptions = materialsGridOptions;
                    break;
                case 'Adjustments':
                    specificGridOptions = adjustmentsGridOptions;
                    break;
            }

            const rowData = createDefaultRowData(gridType);
            const gridOptions = {
                ...commonGridOptions,
                ...specificGridOptions,
                context: {section, gridType: `${gridType}Table`, gridKey: gridKey},
                rowData: rowData,
            };

            try {
                const gridInstance = agGrid.createGrid(gridElement, gridOptions);
                window.grids[gridKey] = { api: gridInstance.api };
            } catch (error) {
                console.error(`Error initializing grid for ${gridKey}:`, error);
            }
        });
    });

    const expectedGridCount = sections.length * 3;
    const actualGridCount = Object.keys(window.grids).length;
    if (actualGridCount !== expectedGridCount) {
        console.error(`Not all grids were initialized. Expected: ${expectedGridCount}, Actual: ${actualGridCount}`);
    }

    // Grid options for Totals table (default 4 rows, autoHeight for proper resizing)
    const totalsGridOptions = {
        columnDefs: [
            {headerName: 'Category', field: 'category', editable: false},
            {headerName: 'Estimate', field: 'estimate', editable: false, valueFormatter: currencyFormatter},
            {headerName: 'Quote', field: 'quote', editable: false, valueFormatter: currencyFormatter},
            {headerName: 'Reality', field: 'reality', editable: false, valueFormatter: currencyFormatter},
        ],
        rowData: [
            {category: 'Total Time', estimate: 0, quote: 0, reality: 0},
            {category: 'Total Materials', estimate: 0, quote: 0, reality: 0},
            {category: 'Total Adjustments', estimate: 0, quote: 0, reality: 0},
            {category: 'Total Project Cost', estimate: 0, quote: 0, reality: 0}
        ],  // Default 4 rows
        domLayout: 'autoHeight',  // Ensure table height adjusts automatically
        rowHeight: 28,
        headerHeight: 32,
        suppressPaginationPanel: true,
        suppressHorizontalScroll: true,
        onGridReady: params => {
            window.grids['totalsTable'] = {gridInstance: params.api, api: params.api};
            console.log('Totals grid ready:', window.grids['totalsTable']);
            params.api.sizeColumnsToFit();
        },
        onGridSizeChanged: params => {
            params.api.sizeColumnsToFit();
        }
    };

    const totalsTableEl = document.querySelector('#totalsTable');
    if (totalsTableEl) {
        try {
            agGrid.createGrid(totalsTableEl, totalsGridOptions);
            // console.log('Totals table initialized:', totalsGrid);
        } catch (error) {
            console.error('Error initializing totals table:', error);
        }
    } else {
        console.error('Totals table element not found');
    }

    // Copy Estimate to Quote (stub)
    const copyEstimateButton = document.getElementById('copyEstimateToQuote');
    if (copyEstimateButton) {
        copyEstimateButton.addEventListener('click', function () {
            alert('Copy estimate feature coming soon!');
            // console.log('Copying estimate to quote');
            // Implement the actual copying logic here
        });
    }

    // Submit Quote to Client (stub)
    const submitQuoteButton = document.getElementById('submitQuoteToClient');
    if (submitQuoteButton) {
        submitQuoteButton.addEventListener('click', function () {
            alert('Submit quote feature coming soon!');
            // console.log('Submitting quote to client');
            // Implement the actual submission logic here
        });
    }

    const reviseQuoteButton = document.getElementById('reviseQuote');
    if (reviseQuoteButton) {
        reviseQuoteButton.addEventListener('click', function () {
            alert('Revise Quote feature coming soon!');
            // console.log('Revise the quote');
            // Implement the actual submission logic here
        });
    }

    const invoiceJobButton = document.getElementById('invoiceJobButton');
    if (invoiceJobButton) {
        invoiceJobButton.addEventListener('click', function () {
            alert('Invoice Job feature coming soon!');
            // console.log('Invoice Job');
            // Implement the actual invoice logic here
        });
    }

    const contactClientButton = document.getElementById('contactClientButton');
    if (contactClientButton) {
        contactClientButton.addEventListener('click', function () {
            alert('Contact Client feature coming soon!');
            // console.log('Contact Client');
            // Implement the actual contact logic here
        });
    }

    setTimeout(() => {
        // console.log('Calling initial calculateTotals');
        calculateTotals();
    }, 1000);
});
