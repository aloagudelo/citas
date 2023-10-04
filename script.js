// Función para cargar la lista de médicos disponibles en una lista desplegable
function cargarMedicos() {
    const fechaInput = document.getElementById('fecha');
    const medicoSelect = document.getElementById('medico-select');

    const fecha = fechaInput.value;

    fetch(`https://192.168.0.89:9000/medicos_disponibles?fecha=${fecha}`)
        .then(response => response.json())
        .then(data => {
            medicoSelect.innerHTML = ''; // Limpiar la lista desplegable antes de agregar médicos

            if (data.length > 0) {
                data.forEach(medico => {
                    const medicoOption = document.createElement('option');
                    medicoOption.value = `${medico['NOMBRE PROFESIONAL']} - ${medico['NOMBRE ESPECIALIDAD']} - ${medico['FECHA']} - ${medico['HORA1']}`;
                    medicoOption.textContent = `${medico['NOMBRE PROFESIONAL']} - ${medico['NOMBRE ESPECIALIDAD']} - ${medico['FECHA']} - ${medico['HORA1']}`;
                    medicoSelect.appendChild(medicoOption);
                });
            } else {
                const medicoOption = document.createElement('option');
                medicoOption.textContent = 'No hay médicos disponibles para esta fecha.';
                medicoSelect.appendChild(medicoOption);
            }
        })
        .catch(error => console.error('Error al cargar médicos:', error));
}

// Función para consultar un cliente por cédula
// Función para consultar un cliente por ID
function consultarCliente() {
    const idInput = document.getElementById('id'); // Cambiar a 'id'
    const clienteInfo = document.getElementById('cliente-info');
    const medicosBlock = document.getElementById('medicos-block');

    const id = idInput.value; // Cambiar a 'id'

    fetch(`https://192.168.0.146:9000/clientes?id=${id}`) // Cambiar la URL
        .then(response => response.json())
        .then(data => {
            if ('Nombre' in data) {
                clienteInfo.textContent = `Nombre: ${data.Nombre}, Entidad: ${data.Entidad}, ID: ${data.ID}`;
                medicosBlock.style.display = 'block';
            } else {
                clienteInfo.textContent = 'Usuario no tiene ficha creada en el hospital. Es necesario que se acerque personalmente a nuestras instalaciones a realizar la solicitud de cita';
                medicosBlock.style.display = 'none';
            }
        })
        .catch(error => console.error('Error al consultar cliente:', error));
}


