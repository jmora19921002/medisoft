// JS para treeview y modales de laboratorio

document.addEventListener('DOMContentLoaded', function() {
    // Mostrar modal de selección de examen
    document.getElementById('btnAddExamen').addEventListener('click', function() {
        const modal = new bootstrap.Modal(document.getElementById('modalSeleccionExamen'));
        modal.show();
    });

    // Doble clic en examen para abrir modal de resultados
    document.querySelectorAll('.examen-row').forEach(function(row) {
        row.addEventListener('dblclick', function() {
            const examenId = this.dataset.examenId;
            // Cargar datos del examen si es necesario
            document.getElementById('modalExamenId').value = examenId;
            const modal = new bootstrap.Modal(document.getElementById('modalResultadosExamen'));
            modal.show();
        });
    });

    // Agregar examen seleccionado al treeview
    document.querySelectorAll('.btn-seleccionar-examen').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const examenId = this.dataset.examenId;
            const examenNombre = this.dataset.examenNombre;
            // Agregar al treeview
            const tree = document.getElementById('treeExamenes');
            const li = document.createElement('li');
            li.textContent = examenNombre;
            li.classList.add('list-group-item', 'examen-row');
            li.dataset.examenId = examenId;
            tree.appendChild(li);
            // Cerrar modal
            bootstrap.Modal.getInstance(document.getElementById('modalSeleccionExamen')).hide();
        });
    });
});
