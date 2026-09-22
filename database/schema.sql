-- NEXA PostgreSQL schema. Designed for Colombian residential security operations.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(40) UNIQUE NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cedula VARCHAR(20) UNIQUE NOT NULL CHECK (cedula ~ '^[0-9A-Za-z-]{5,20}$'),
    nombre_completo VARCHAR(150) NOT NULL,
    correo VARCHAR(254) UNIQUE NOT NULL CHECK (correo ~* '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'),
    password_hash TEXT NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    consentimiento_datos BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_consentimiento TIMESTAMPTZ,
    fecha_retencion DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '365 days'),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE permisos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(80) UNIQUE NOT NULL,
    descripcion TEXT NOT NULL
);
CREATE TABLE roles_permisos (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id UUID REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY(role_id, permiso_id)
);
CREATE TABLE camaras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(200) NOT NULL,
    url_streaming TEXT NOT NULL,
    url_grabacion TEXT,
    anonimizado BOOLEAN NOT NULL DEFAULT TRUE,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    retencion_dias INTEGER NOT NULL DEFAULT 30 CHECK (retencion_dias BETWEEN 1 AND 3650),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE accesos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id),
    camara_id UUID REFERENCES camaras(id),
    tipo_credencial VARCHAR(20) NOT NULL CHECK (tipo_credencial IN ('biometria','rfid','placa','manual')),
    punto_acceso VARCHAR(100) NOT NULL,
    placa_vehiculo VARCHAR(6) CHECK (placa_vehiculo IS NULL OR placa_vehiculo ~ '^[A-Z]{3}[0-9]{3}$'),
    resultado VARCHAR(10) NOT NULL CHECK (resultado IN ('permitido','denegado')),
    motivo TEXT,
    registrado_por UUID REFERENCES usuarios(id),
    ocurrio_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    fecha_retencion DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '365 days')
);
CREATE TABLE alertas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_id UUID REFERENCES camaras(id),
    usuario_id UUID REFERENCES usuarios(id),
    tipo VARCHAR(60) NOT NULL,
    severidad VARCHAR(10) NOT NULL CHECK (severidad IN ('baja','media','alta','critica')),
    descripcion TEXT NOT NULL,
    estado VARCHAR(15) NOT NULL DEFAULT 'abierta' CHECK (estado IN ('abierta','en_revision','cerrada')),
    creada_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    atendida_en TIMESTAMPTZ,
    atendida_por UUID REFERENCES usuarios(id)
);
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_id UUID NOT NULL REFERENCES camaras(id),
    object_key TEXT NOT NULL UNIQUE,
    checksum_sha256 CHAR(64) NOT NULL,
    anonimizado BOOLEAN NOT NULL DEFAULT FALSE,
    almacenado_en TIMESTAMPTZ NOT NULL DEFAULT now(),
    fecha_retencion DATE NOT NULL,
    eliminado_en TIMESTAMPTZ
);
CREATE TABLE reportes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creado_por UUID NOT NULL REFERENCES usuarios(id),
    tipo VARCHAR(50) NOT NULL,
    parametros JSONB NOT NULL DEFAULT '{}'::jsonb,
    object_key TEXT,
    generado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE auditoria (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_id UUID REFERENCES usuarios(id),
    accion VARCHAR(80) NOT NULL,
    recurso VARCHAR(100) NOT NULL,
    recurso_id UUID,
    resultado VARCHAR(20) NOT NULL CHECK (resultado IN ('exitoso','denegado','error')),
    ip INET,
    detalles JSONB NOT NULL DEFAULT '{}'::jsonb,
    fecha_retencion DATE NOT NULL DEFAULT (CURRENT_DATE + INTERVAL '365 days')
) PARTITION BY RANGE (timestamp);
CREATE TABLE auditoria_2026 PARTITION OF auditoria FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE auditoria_default PARTITION OF auditoria DEFAULT;

CREATE INDEX idx_usuarios_activo ON usuarios(activo);
CREATE INDEX idx_accesos_usuario_fecha ON accesos(usuario_id, ocurrio_en DESC);
CREATE INDEX idx_alertas_estado_severidad ON alertas(estado, severidad);
CREATE INDEX idx_videos_retencion ON videos(fecha_retencion) WHERE eliminado_en IS NULL;
CREATE INDEX idx_auditoria_actor_fecha ON auditoria(actor_id, timestamp DESC);

INSERT INTO roles (nombre, descripcion) VALUES
 ('admin','Administracion total'), ('operador','Operacion de seguridad'), ('residente','Consulta propia'), ('autoridad','Acceso a reportes autorizados')
ON CONFLICT (nombre) DO NOTHING;

CREATE OR REPLACE FUNCTION funcion_anonimizar_rostros(p_video_id UUID)
RETURNS BOOLEAN LANGUAGE plpgsql AS $$
BEGIN
    UPDATE videos SET anonimizado = TRUE WHERE id = p_video_id AND eliminado_en IS NULL;
    RETURN FOUND;
END;
$$;

CREATE OR REPLACE FUNCTION validar_consentimiento() RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.consentimiento_datos AND NEW.fecha_consentimiento IS NULL THEN NEW.fecha_consentimiento = now(); END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER trg_validar_consentimiento BEFORE INSERT OR UPDATE ON usuarios
FOR EACH ROW EXECUTE FUNCTION validar_consentimiento();

CREATE OR REPLACE VIEW vista_accesos_recientes AS
SELECT a.id, a.ocurrio_en, a.punto_acceso, a.resultado, u.cedula, u.nombre_completo, c.nombre AS camara
FROM accesos a JOIN usuarios u ON u.id = a.usuario_id LEFT JOIN camaras c ON c.id = a.camara_id
WHERE a.ocurrio_en >= now() - INTERVAL '30 days';

CREATE OR REPLACE VIEW vista_alertas_activas AS
SELECT al.*, c.nombre AS camara, u.nombre_completo AS usuario
FROM alertas al LEFT JOIN camaras c ON c.id = al.camera_id LEFT JOIN usuarios u ON u.id = al.usuario_id
WHERE al.estado <> 'cerrada';
