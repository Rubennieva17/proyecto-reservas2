# proyecto-reservas2

🧾 README.md — Proyecto de Reservas Deportivas
🎯 Sistema de Reservas de Canchas Deportivas
Proyecto Segundo Parcial – UTN FRT
Desarrollado por Ruben Nieva
🧠 Descripción General
Este proyecto implementa un sistema completo de reservas deportivas, compuesto por:
Backend (API REST) desarrollado con FastAPI y SQLite
Frontend en HTML, CSS y JavaScript puro
Permite gestionar canchas, usuarios, pagos y reservas, cumpliendo con los requisitos del parcial.
El sistema permite:
Registrar nuevas reservas
Listar y filtrar reservas por cancha
Validar que no se dupliquen reservas (misma cancha, fecha y hora)
Eliminar reservas únicamente con clave de administrador
Cargar dinámicamente las opciones de canchas y métodos de pago desde la API
⚙️ Tecnologías Utilizadas
Backend
🐍 Python 3.11+
⚡ FastAPI
💾 SQLite3
🧩 Pydantic (modelos de validación)
🔐 CORS Middleware para conexión con el frontend
Frontend
🧱 HTML5
🎨 CSS3 (con variables y diseño responsive)
⚙️ JavaScript (Fetch API)
📁 Estructura del Proyecto
Copiar código

reservas-deportivas/
│
├── backend/
│   ├── main.py                 # API principal con FastAPI
│   ├── reservas.db             # Base de datos SQLite (se genera automáticamente)
│   └── __init__.py
│
├── frontend/
│   ├── index.html              # Interfaz principal
│   ├── style.css               # Estilos visuales
│   └── app.js                  # Lógica del cliente (fetch, eventos, validaciones)
│
├── README.md                   # Este archivo
└── .gitignore
🚀 Cómo Ejecutar el Proyecto
1️⃣ Clonar el repositorio
Copiar código
Bash
git clone https://github.com/RubenNieva17/proyecto-reservas.git
cd proyecto-reservas/backend
2️⃣ Crear y activar entorno virtual (opcional pero recomendado)
Copiar código
Bash
python -m venv venv
venv\Scripts\activate     # En Windows
# o
source venv/bin/activate  # En Linux/Mac
3️⃣ Instalar dependencias
Copiar código
Bash
pip install fastapi uvicorn
4️⃣ Iniciar el servidor backend
Copiar código
Bash
uvicorn main:app --reload
El backend quedará disponible en
👉 http://127.0.0.1:8000
Podés acceder a la documentación automática en
📘 http://127.0.0.1:8000/docs
5️⃣ Abrir el frontend
Abrí el archivo frontend/index.html directamente en tu navegador, o usá un servidor local como:
Copiar código
Bash
cd frontend
python -m http.server 5500
Luego accedé a
👉 http://127.0.0.1:5500
🔒 Seguridad
Eliminación de reservas protegida con clave de administrador.
Para borrar una reserva se debe ingresar la clave:
Ruben Nieva
Validación en backend: No permite duplicar reservas en la misma cancha, fecha y hora.
🧩 Endpoints principales (API)
Método
Endpoint
Descripción
GET
/canchas
Lista todas las canchas
GET
/pagos
Lista métodos de pago
GET
/reservas
Lista reservas (con filtros opcionales)
POST
/reservas
Crea una nueva reserva
DELETE
/reservas/{id}
Elimina reserva (requiere admin_key)
GET
/resumen
Devuelve estadísticas básicas del sistema
✅ Validaciones Implementadas
No se puede reservar la misma cancha en la misma fecha y hora.
Email de usuario único (se reutiliza si ya existe).
Métodos de pago y canchas deben existir.
Solo el administrador puede eliminar reservas.