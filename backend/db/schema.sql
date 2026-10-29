-- Script de creación de esquema inicial
CREATE TABLE IF NOT EXISTS llamadas (
    id SERIAL PRIMARY KEY,
    nombre_archivo VARCHAR(200) NOT NULL,
    duracion_seg INTEGER NOT NULL CHECK (duracion_seg BETWEEN 1 AND 86400),
    fecha_llamada TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS revisiones (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(120) NOT NULL,
    nota VARCHAR(2000) DEFAULT '',
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'revisada')),
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE revisiones 
ADD COLUMN IF NOT EXISTS llamada_id INTEGER REFERENCES llamadas(id) ON DELETE RESTRICT;