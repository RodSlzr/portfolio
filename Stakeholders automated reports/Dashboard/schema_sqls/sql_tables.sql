DROP TABLE IF EXISTS think_tanks;

CREATE TABLE think_tanks (
    nombre varchar(1000) PRIMARY KEY NOT NULL,
    desc varchar(10000),
    comments varchar(10000),
    web varchar(1000),
    twitter varchar(1000),
    contacto_g varchar(1000),
    contacto_t_nombre varchar(1000),
    contacto_t_puesto varchar(1000),
    contacto_t_correo varchar(1000),
    contacto_t_tel varchar(1000),
    temas varchar(10000),
    posicion_pol varchar(100),
    fin_disp varchar(4),
    fin_total int(30),
    fin_dem real,
    fin_rep real,
    estudios varchar(10000),
    fuentes varchar(10000)
);

.mode csv
.import schema_sqls/think_tanks_data.csv think_tanks

DROP TABLE IF EXISTS congresistas;

CREATE TABLE congresistas (
    id varchar(7) PRIMARY KEY NOT NULL,
    nombre varchar(1000),
    comments varchar(10000),
    bitacora varchar(10000),
    fuentes varchar(10000),
    staffers varchar(10000)
);

DROP TABLE IF EXISTS otros_actores;

CREATE TABLE otros_actores (
    nombre varchar(1000) PRIMARY KEY NOT NULL,
    tipo varchar(1000),
    industria varchar(1000),
    desc varchar(10000),
    miembros varchar(10000),
    ubicacion varchar(1000),
    comments varchar(10000),
    web varchar(1000),
    twitter varchar(1000),
    facebook varchar(1000),
    youtube varchar(1000),
    otro_medio varchar(1000),
    contacto_g varchar(1000),
    contacto_t_nombre varchar(1000),
    contacto_t_puesto varchar(1000),
    contacto_t_correo varchar(1000),
    contacto_t_tel varchar(1000),
    temas varchar(10000),
    posicion_pol varchar(100),
    fin_disp varchar(4),
    fin_total int(30),
    fin_dem real,
    fin_rep real,
    estudios varchar(10000),
    fuentes varchar(10000)
);

DROP TABLE IF EXISTS comites;

CREATE TABLE comites (
    codigo varchar(1000) PRIMARY KEY NOT NULL,
    comite varchar(1000),
    web varchar(1000),
    chairman varchar(1000),
    num_dems varchar(1000),
    dems varchar(10000),
    num_reps varchar(1000),
    reps varchar(10000),
    subcomites varchar(1000),
    bills varchar(10000),
    news varchar(10000),
    twitter varchar(1000),
    facebook varchar(1000),
    youtube varchar(1000)
);

.mode csv
.import schema_sqls/comites_data.csv comites

DROP TABLE IF EXISTS organizaciones_emp;

CREATE TABLE organizaciones_emp (
    nombre varchar(1000) PRIMARY KEY NOT NULL,
    acronimo varchar(1000),
    industria varchar(1000),
    hs varchar(1000),
    web varchar(1000),
    desc varchar(10000),
    comments varchar(10000),
    miembros varchar(10000),
    ubicacion varchar(10000),
    contacto_g varchar(1000),
    contacto_t_nombre varchar(1000),
    contacto_t_puesto varchar(1000),
    contacto_t_correo varchar(1000),
    contacto_t_tel varchar(1000),
    temas varchar(10000),
    posicion_pol varchar(100),
    fin_disp varchar(4),
    fin_total int(30),
    fin_dem real,
    fin_rep real,
    lobbying_disp varchar(4),
    lobbying_total int(30),
    exp_mex varchar(1000),
    mkt_share varchar(1000),
    empleos varchar(1000),
    edos_op varchar(1000),
    estudios varchar(10000),
    twitter varchar(1000),
    facebook varchar(1000),
    youtube varchar(1000)
);

.mode csv
.import schema_sqls/organizaciones_emp.csv organizaciones_emp