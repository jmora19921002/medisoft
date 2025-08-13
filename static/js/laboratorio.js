// --- Adicionar Examen en Nuevo Examen de Laboratorio ---
document.addEventListener('DOMContentLoaded', function() {
	const btnAddExamen = document.getElementById('btnAddExamen');
	const modalSeleccionExamen = new bootstrap.Modal(document.getElementById('modalSeleccionExamen'));
	const treeExamenes = document.getElementById('treeExamenes');
	const examenesSeleccionadosInput = document.getElementById('examenes_seleccionados');

	// Permitir que examenesSeleccionados sea global si ya existe
	let examenesSeleccionados = window.examenesSeleccionados || [];

	if (btnAddExamen) {
		btnAddExamen.addEventListener('click', function() {
			modalSeleccionExamen.show();
		});
	}

	// Seleccionar examen desde la tabla del modal
	document.querySelectorAll('.btn-seleccionar-examen').forEach(function(btn) {
		btn.addEventListener('click', function() {
			const examenId = this.getAttribute('data-examen-id');
			const examenNombre = this.getAttribute('data-examen-nombre');
			// Evitar duplicados
			if (!examenesSeleccionados.some(e => e.id === examenId)) {
				examenesSeleccionados.push({id: examenId, nombre: examenNombre, valor: ''});
				if (typeof window.actualizarListaExamenes === 'function') {
					window.actualizarListaExamenes();
				}
			}
			modalSeleccionExamen.hide();
		});
	});

	// Si no hay función personalizada, usar la básica
	if (typeof window.actualizarListaExamenes !== 'function') {
		function actualizarListaExamenes() {
			treeExamenes.innerHTML = '';
			examenesSeleccionados.forEach(function(examen, idx) {
				const li = document.createElement('li');
				li.className = 'list-group-item d-flex justify-content-between align-items-center';
				li.innerHTML = `
					<span>${examen.nombre}</span>
					<button type="button" class="btn btn-danger btn-sm btn-remove-examen" data-idx="${idx}"><i class="fas fa-trash"></i></button>
				`;
				treeExamenes.appendChild(li);
			});
			// Actualizar input oculto
			examenesSeleccionadosInput.value = JSON.stringify(examenesSeleccionados);
			// Botón eliminar
			document.querySelectorAll('.btn-remove-examen').forEach(function(btn) {
				btn.addEventListener('click', function() {
					const idx = parseInt(this.getAttribute('data-idx'));
					examenesSeleccionados.splice(idx, 1);
					actualizarListaExamenes();
				});
			});
		}
		window.actualizarListaExamenes = actualizarListaExamenes;
	}
});
