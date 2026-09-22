# NEXA: documento maestro de generacion y estado

## 1. Proposito

Este documento describe como reconstruir NEXA y cual es su estado real en el repositorio. NEXA es una plataforma para conjuntos residenciales de Colombia con:

- Gestion de usuarios y roles.
- Control de accesos.
- Videovigilancia y consulta de camaras.
- Alertas.
- Reportes.
- Auditoria, consentimiento y retencion de datos.
- Cumplimiento de la Ley 1581 de 2012 y la Circular 005 de 2017.

La solucion actual usa:

- Frontend: Angular 19 standalone, TypeScript, SCSS y HttpClient.
- Backend principal: Spring Boot 3.4, Java 21, Spring JDBC, Spring Security, JWT y PostgreSQL.
- Base de datos: PostgreSQL 16.
- Servicios auxiliares: Redis y MinIO definidos en Docker Compose.
- Backend Python: primera implementacion conservada en `app/`; no es el backend principal actual.
- Despliegue: Docker, Railway y GitHub.

## 2. Estado actual

Repositorio remoto:

```text
https://github.com/JcMosquera02/backend_nexa.git
```

Ultimo commit publicado:

```text
5223c4a fix: repair Spring Boot dependency configuration
```

Rama principal publicada:

```text
main
```

Rama local de trabajo observada:

```text
appmod/java-upgrade-20260922140124
```

El `backend-java/pom.xml` ya fue reparado: ahora es un POM unico, valido y compilable. Antes de sobrescribir cambios de trabajo, siempre se debe revisar `git status` y `git diff`.

Validaciones conocidas del estado anterior:

- Angular production build: correcto.
- Pruebas Angular: 2 SUCCESS.
- Pruebas Python existentes: 2 passed.
- Spring Boot fue empaquetado correctamente con Maven 3.9.15.
- Docker no se pudo validar en el equipo porque Docker no estaba instalado.

## 3. Estructura del proyecto

```text
proyecto/
|-- app/                         Backend Python legado/referencia
|   |-- api/
|   |-- core/
|   |-- services/
|   |-- main.py
|   |-- models.py
|   `-- schemas.py
|-- backend-java/                Backend principal Spring Boot
|   |-- pom.xml
|   |-- Dockerfile
|   `-- src/main/
|       |-- java/co/nexa/
|       |   |-- NexaApplication.java
|       |   |-- NexaController.java
|       |   |-- JwtService.java
|       |   `-- SecurityConfig.java
|       `-- resources/application.yml
|-- database/
|   `-- schema.sql                Tablas, vistas, indices y funciones PostgreSQL
|-- frontend/                    Angular 19 standalone
|   |-- package.json
|   |-- angular.json
|   `-- src/app/
|       |-- app.component.ts
|       |-- app.component.html
|       |-- app.component.scss
|       |-- api.service.ts
|       `-- app.component.spec.ts
|-- postman/
|   `-- NEXA.postman_collection.json
|-- requirements/
|   |-- nexa_requisitos.csv
|   |-- nexa_requisitos.xlsx
|   `-- nexa_requisitos.xml
|-- scripts/
|   |-- backup.py
|   `-- generar_excel.py
|-- tests/
|   `-- test_api.py
|-- Dockerfile                    Imagen principal Spring Boot
|-- docker-compose.yml            API, PostgreSQL, Redis y MinIO
|-- railway.json
|-- .env.example
|-- .dockerignore
`-- .gitignore
```

## 4. Requisitos de equipo

Instalar:

- Git.
- Java 21.
- Maven 3.9 o superior.
- Node.js compatible con Angular 19.
- npm.
- PostgreSQL 16 o Docker Desktop.
- Opcional: Python 3.13 para las pruebas del backend legado.
- Opcional: Postman.

En Windows, si Maven fue instalado en la ruta usada durante la validacion:

```powershell
$maven = 'C:\Users\julianM\.maven\maven-3.9.15(1)\bin\mvn.cmd'
```

## 5. Variables de entorno

Copiar el archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

Variables para Spring Boot local:

```dotenv
PGHOST=localhost
PGPORT=5432
PGDATABASE=nexa
PGUSER=nexa
PGPASSWORD=nexa
JDBC_DATABASE_URL=jdbc:postgresql://localhost:5432/nexa
JWT_SECRET=change-this-secret-to-at-least-32-characters
CORS_ORIGIN=http://localhost:4200
```

En Railway se deben configurar las variables en el panel del servicio. Nunca se deben subir contrasenas, tokens ni URLs con credenciales a GitHub.

Para Railway se recomienda usar:

```dotenv
JDBC_DATABASE_URL=jdbc:postgresql://HOST:5432/railway
PGUSER=postgres
PGPASSWORD=SECRET_DE_RAILWAY
CORS_ORIGIN=https://DOMINIO-FRONTEND
JWT_SECRET=SECRET_LARGO_ALEATORIO
```

La contrasena que aparecio en una captura anterior debe considerarse expuesta y debe rotarse en Railway.

## 6. Crear la base de datos

Crear una base local llamada `nexa` y ejecutar el esquema:

```powershell
psql -U nexa -d nexa -f database/schema.sql
```

O usando una URL:

```powershell
psql "$env:DATABASE_URL" -f database/schema.sql
```

El esquema crea:

- `roles`.
- `usuarios`.
- `permisos`.
- `roles_permisos`.
- `camaras`.
- `accesos`.
- `alertas`.
- `videos`.
- `reportes`.
- `auditoria` particionada.
- Indices por usuario, fecha, estado y retencion.
- Vistas de accesos recientes y alertas activas.
- Funcion de anonimizar rostros.
- Trigger de consentimiento.

En Railway el esquema debe ejecutarse una vez antes de iniciar la API.

## 7. Ejecutar backend Spring Boot

Desde la raiz:

```powershell
$maven = 'C:\Users\julianM\.maven\maven-3.9.15(1)\bin\mvn.cmd'
Push-Location backend-java
& $maven spring-boot:run
Pop-Location
```

Para empaquetar:

```powershell
Push-Location backend-java
& $maven -q -DskipTests package
Pop-Location
```

El JAR generado es:

```text
backend-java/target/nexa-backend-0.1.0.jar
```

Puerto local:

```text
http://localhost:8080
```

Health check:

```text
GET http://localhost:8080/health
```

## 8. API Spring Boot actual

### Sistema

```http
GET /health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "service": "NEXA Spring Boot"
}
```

### Dashboard

```http
GET /api/dashboard/summary
```

Devuelve conteos de accesos recientes, alertas activas, camaras activas y usuarios activos.

### Autenticacion

```http
POST /api/auth/register
POST /api/auth/login
```

Registro de ejemplo:

```json
{
  "cedula": "100000001",
  "nombreCompleto": "Administrador NEXA",
  "correo": "admin@nexa.co",
  "password": "CambioSeguro123!",
  "role": "admin",
  "consentimientoDatos": true
}
```

Login de ejemplo:

```json
{
  "correo": "admin@nexa.co",
  "password": "CambioSeguro123!"
}
```

El login devuelve:

```json
{
  "access_token": "JWT_FIRMADO",
  "token_type": "bearer"
}
```

### Accesos

```http
GET /api/accesos
POST /api/accesos
```

Payload de registro:

```json
{
  "usuario_id": "UUID_DEL_USUARIO",
  "tipo_credencial": "rfid",
  "punto_acceso": "Porteria norte",
  "placa_vehiculo": null,
  "resultado": "permitido"
}
```

Regla esencial: un usuario inactivo no puede registrar acceso.

### Alertas

```http
GET /api/alertas
POST /api/alertas
PATCH /api/alertas/{id}/close
```

Payload:

```json
{
  "tipo": "intrusion",
  "severidad": "alta",
  "descripcion": "Movimiento fuera de horario"
}
```

### Camaras

```http
GET /api/cameras
GET /api/cameras/{id}/stream
```

El stream devuelve la URL configurada y si el video esta anonimizado.

### Reportes

```http
GET /api/reportes/access-summary
GET /api/reportes/incident-summary
```

## 9. Frontend Angular

Instalar y ejecutar:

```powershell
Push-Location frontend
npm install
npm start
Pop-Location
```

La aplicacion queda en:

```text
http://localhost:4200
```

El servicio Angular esta en `frontend/src/app/api.service.ts` y apunta a:

```text
http://localhost:8080
```

El dashboard carga mediante HTTP:

- `/api/dashboard/summary`.
- `/api/accesos`.
- `/api/alertas`.
- `/api/cameras`.

Acciones conectadas:

- Estado de API: `GET /health`.
- Nuevo reporte: `GET /api/reportes/access-summary`.
- Actualizar accesos: vuelve a consultar el dashboard y los listados.
- Gestionar alertas: consulta alertas.
- Cerrar alerta: `PATCH /api/alertas/{id}/close`.
- Ver monitor: consulta camaras.
- Abrir camara: `GET /api/cameras/{id}/stream`.
- Buscador: filtra los datos recibidos de la API.

Generar build de produccion:

```powershell
Push-Location frontend
npm run build
Pop-Location
```

Salida:

```text
frontend/dist/frontend
```

## 10. Docker Compose

Con Docker Desktop instalado:

```powershell
Copy-Item .env.example .env
 docker compose up --build
```

Servicios:

- Spring Boot: `http://localhost:8080`.
- PostgreSQL: `localhost:5432`.
- Redis: `localhost:6379`.
- MinIO API: `http://localhost:9000`.
- MinIO console: `http://localhost:9001`.
- Angular: se ejecuta aparte con `npm start`, salvo que se agregue un servicio frontend al Compose.

Nota: el servicio Spring usa `backend-java/Dockerfile`; el Dockerfile raíz tambien esta preparado para construir Spring Boot.

## 11. Postman

Importar:

```text
postman/NEXA.postman_collection.json
```

Cambiar la variable `baseUrl` a:

```text
http://localhost:8080
```

Casos principales definidos o previstos:

- Health.
- Register.
- Login.
- Refresh y listado de usuarios pertenecen al backend Python legado; no forman parte del controlador Spring actual.
- Accesos.
- Alertas.
- Camaras.
- Reportes.

La coleccion debe mantenerse alineada con Spring e incluir `dashboard/summary`, cierre de alertas y stream de camara.

## 12. Pruebas

Backend Python legado:

```powershell
.venv313\Scripts\python.exe -m pytest -q
```

Frontend:

```powershell
Push-Location frontend
npx ng test --watch=false --browsers=ChromeHeadless
Pop-Location
```

Compilacion Java:

```powershell
Push-Location backend-java
& $maven -q -DskipTests package
Pop-Location
```

Validacion sintactica de Python:

```powershell
.venv313\Scripts\python.exe -m compileall -q app scripts
```

## 13. Publicar en GitHub

Configurar el remoto:

```powershell
git remote add origin https://github.com/JcMosquera02/backend_nexa.git
```

Crear commit:

```powershell
git add .
git commit -m "feat: complete NEXA Spring Boot and Angular integration"
```

Publicar:

```powershell
git branch -M main
git push -u origin main
```

Nunca incluir:

- `.env`.
- Credenciales de Railway.
- `backend-java/target`.
- `frontend/node_modules`.
- Tokens JWT.
- Backups con datos personales.

## 14. Despliegue Railway

1. Crear un servicio PostgreSQL en Railway.
2. Crear un servicio desde el repositorio GitHub.
3. Seleccionar el Dockerfile del proyecto.
4. Configurar `JDBC_DATABASE_URL`, `PGUSER`, `PGPASSWORD`, `JWT_SECRET` y `CORS_ORIGIN`.
5. Ejecutar `database/schema.sql` contra la base Railway.
6. Verificar `/health`.
7. Configurar el frontend con la URL publica del backend, sustituyendo `http://localhost:8080` por una variable de entorno de Angular.
8. Activar HTTPS.
9. Rotar cualquier secreto expuesto.

## 15. Seguridad y cumplimiento

Implementado en el codigo actual:

- Hash de contrasenas con BCrypt.
- Emision de JWT firmado durante el login.
- Consentimiento de datos.
- Roles de usuario.
- Restriccion de usuario inactivo.
- Auditoria y fechas de retencion en PostgreSQL.
- Anonimizacion OpenCV en el backend Python de referencia.
- CORS configurable.
- Variables secretas fuera del repositorio.
- Retencion configurable de videos.

Limitaciones actuales y pendientes para produccion:

- Aplicar el filtro JWT y autorizacion por rol a todos los endpoints de escritura Spring. Actualmente `SecurityConfig` permite `/api/**` para facilitar el desarrollo local.
- Validar payloads de accesos y alertas con DTOs tipados y reglas de negocio, en lugar de `Map<String,Object>`.
- Sustituir la concatenacion del UUID en la consulta de creacion de accesos por parametros JDBC tipados.
- Auditoria automatica desde Spring para cada mutacion.
- Migrar todos los reportes a una tabla `reportes` y almacenamiento MinIO/S3.
- WebSockets o Redis Pub/Sub para alertas en tiempo real.
- Integracion real con camaras IP.
- Pruebas de integracion con PostgreSQL real.
- MFA para administradores.
- HTTPS obligatorio y politicas de secretos.
- Procedimiento legal para consulta, rectificacion y supresion de titulares.
- Verificacion de tiempos de retencion con asesor legal colombiano.

## 16. Prompt maestro para regenerar el proyecto

Usa el siguiente texto como prompt de reconstruccion para otro agente o equipo:

```text
Construye NEXA, plataforma colombiana de seguridad residencial, hasta el siguiente estado:

1. Crea un monorepo con backend-java y frontend.
2. Usa Spring Boot 3.4, Java 21, Spring Web, Spring JDBC, Spring Security, BCrypt, JWT, Validation y PostgreSQL.
3. Usa Angular 19 standalone, TypeScript, SCSS y HttpClient.
4. Usa PostgreSQL y ejecuta database/schema.sql antes de iniciar la API.
5. Conserva las entidades y tablas roles, usuarios, accesos, camaras, alertas, videos, reportes y auditoria.
6. Implementa GET /health.
7. Implementa GET /api/dashboard/summary.
8. Implementa POST /api/auth/register y POST /api/auth/login con consentimiento obligatorio y JWT firmado.
9. Implementa GET y POST /api/accesos; rechaza usuarios inactivos.
10. Implementa GET y POST /api/alertas y PATCH /api/alertas/{id}/close.
11. Implementa GET /api/cameras y GET /api/cameras/{id}/stream.
12. Implementa GET /api/reportes/access-summary e incident-summary.
13. Configura CORS para Angular y variables externas para Railway.
14. Crea Dockerfiles para Spring Boot y docker-compose con PostgreSQL, Redis y MinIO.
15. En Angular crea un dashboard operativo, no una landing page.
16. El dashboard debe cargar metricas, accesos, alertas y camaras desde HTTP; no usar arrays estaticos.
17. Los botones deben ejecutar endpoints reales: actualizar, cerrar alerta, generar reporte, consultar stream y cambiar secciones.
18. Incluye tests de Spring/Angular, Postman, README, matriz RF Excel y guia normativa.
19. No incluyas secretos ni contrasenas en Git.
20. Ejecuta build frontend, test Angular, package Maven y verifica git diff --check antes de publicar.
21. Documenta lo que quede pendiente en produccion y no afirmes que una funcionalidad existe si solo esta simulada.
``` 

## 17. Checklist de entrega

- [x] Revisar y reparar `backend-java/pom.xml`.
- [x] Confirmar que Maven empaqueta sin errores.
- [ ] Ejecutar `database/schema.sql` en la base objetivo.
- [ ] Configurar secretos en Railway.
- [ ] Ejecutar Spring Boot con PostgreSQL real y verificar `/health`.
- [ ] Ejecutar Angular y verificar que las metricas dejan de estar en cero.
- [ ] Registrar un usuario con consentimiento.
- [ ] Iniciar sesion y guardar JWT.
- [ ] Consultar accesos, alertas y camaras desde Postman.
- [ ] Cerrar una alerta desde la interfaz.
- [ ] Generar un reporte desde la interfaz.
- [ ] Probar acceso denegado para usuario inactivo.
- [x] Ejecutar tests Angular.
- [x] Ejecutar tests Python heredados.
- [x] Ejecutar build Maven y Angular.
- [ ] Revisar secretos con una busqueda antes de `git push`.
- [x] Publicar `main` en GitHub.
- [ ] Configurar dominio y HTTPS en produccion.
