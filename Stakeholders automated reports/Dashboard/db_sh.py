from multiprocessing import connection
from os import path
import logging # Logging Library
from error import KeyNotFound, BadRequest, InspError
from similarity.jarowinkler import JaroWinkler # pip install strsim

# Utility factor to allow results to be used like a dictionary
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# helper function that converts query result to json list, after cursor has executed a query
# this will not work for all endpoints directly, just the ones where you can translate
# a single query to the required json.


def to_json_list(cursor):
    results = cursor.fetchall()
    headers = [d[0] for d in cursor.description]
    return [dict(zip(headers, row)) for row in results]

def similar_rests(restaurant, other_rests):
    '''
    Determines if 2 restaurants are similar, considering
    their name, address, city, state and zip.
    '''
    jarowinkler = JaroWinkler()
    sim_name = jarowinkler.similarity(restaurant['name'], other_rests['name'])
    sim_adress = jarowinkler.similarity(restaurant['address'], other_rests['address'])
    sim_city = jarowinkler.similarity(restaurant['state'], other_rests['state'])
    sim_state = jarowinkler.similarity(restaurant['city'], other_rests['city'])
    sim_zip = jarowinkler.similarity(restaurant['zip'], other_rests['zip'])

    similarity = 0.3 * sim_name + 0.3 * sim_adress + 0.15 * sim_city + 0.15 * sim_state + 0.1 * sim_zip
    if similarity > 0.90:
        return True

    return False

def authoritarian_restaurant(rest_simils):
    '''
    Giving a list of similar restaurants it generates, one that represents them all
    when no clean restaurant can.
    id, name, address, city, state, zip
    '''
    if len(rest_simils) == 1:
        auth_rest = rest_simils[0]
        return auth_rest

    auth_rest = {}
    names = {}
    addresses = {}
    cities = {}
    states = {}
    zips = {}
    fac_types = {}
    latitudes = {}
    longitudes = {}

    auth_rest['id'] = 0
    for rest in rest_simils:
        auth_rest['id'] = max(rest['id'], auth_rest['id'])
        names[rest['name']] = names.get(rest['name'], 0) + 1
        addresses[rest['address']] = addresses.get(rest['address'], 0) + 1
        cities[rest['city']] = cities.get(rest['city'], 0) + 1
        states[rest['state']] = states.get(rest['state'], 0) + 1
        zips[rest['zip']] = zips.get(rest['zip'], 0) + 1
        fac_types[rest['facility_type']] = fac_types.get(rest['facility_type'], 0) + 1
        latitudes[rest['latitude']] = latitudes.get(rest['latitude'], 0) + 1
        longitudes[rest['longitude']] = longitudes.get(rest['longitude'], 0) + 1
    
    auth_rest['name'] = max(names, key = names.get)
    auth_rest['address'] = max(addresses, key = addresses.get)
    auth_rest['city'] = max(cities, key = cities.get)
    auth_rest['state'] = max(states, key = states.get)
    auth_rest['zip'] = max(zips, key = zips.get)
    auth_rest['facility_type'] = max(fac_types, key = fac_types.get)
    auth_rest['latitude'] = max(latitudes, key = latitudes.get)
    auth_rest['longitude'] = max(longitudes, key = longitudes.get)
    auth_rest['clean'] = '1'

    return auth_rest


"""
Wraps a single connection to the database with higher-level functionality.
"""

class DB:
    def __init__(self, connection):
        self.conn = connection
        #self.conn.text_factory = lambda b: b.decode(errors = 'ignore') # permite que pase cualquier texto
        self.conn.text_factory = lambda x: str(x, 'latin1')

    def execute_script(self, script_file):
        with open(script_file, "r") as script:
            c = self.conn.cursor()
            # Only using executescript for running a series of SQL commands.
            c.executescript(script.read())
            self.conn.commit()

    def create_script(self):
        """
        Calls the schema/create.sql file
        """
        script_file = path.join("schema", "create.sql")
        if not path.exists(script_file):
            raise InspError("Create Script not found")
        self.execute_script(script_file)

    def seed_data(self):
        """
        Calls the schema/seed.sql file
        """
        script_file = path.join("schema", "seed.sql")
        if not path.exists(script_file):
            raise InspError("Seed Script not found")
        self.execute_script(script_file)


    def find_restaurant(self, restaurant_id):
        """
        Searches for the restaurant with the given ID. Returns None if the
        restaurant cannot be found in the database.
        """
        if not restaurant_id:
            raise InspError("No Restaurant Id", 404)

        c = self.conn.cursor()

        # Another way of executing a query with named parameters
        query_rest = """
            SELECT * FROM ri_restaurants WHERE id = ?
           """
        c.execute(query_rest, [restaurant_id])                        
        res = to_json_list(c)
        if len(res) == 0:
            return None
        res = res[0]
        self.conn.commit()
        return res

    def find_rest_thr_inspection(self, inspection_id):
        ins = self.find_inspection(inspection_id)
        if not ins:
            return None
        restaurant_id = ins[0]['restaurant_id']
        res = self.find_restaurant(restaurant_id)
        return res

    def count_inspections(self):
        """
        Counts the number of inspections. Returns None if the
        inspection cannot be found in the database.
        """
        c = self.conn.cursor()
        query_ins = """
        SELECT id FROM ri_inspections
        """
        c.execute(query_ins)
        res = to_json_list(c)
        self.conn.commit()

        return len(res)


    def find_inspection(self, inspection_id):
        if not inspection_id:
            raise InspError("No inspection_id", 404)
        """
        Searches for the inspection with the given ID. Returns None if the
        inspection cannot be found in the database.
        """
        c = self.conn.cursor()
        query_ins = """
        SELECT * FROM ri_inspections WHERE id = ?
        """
        c.execute(query_ins, [inspection_id])
        res = to_json_list(c)
        self.conn.commit()

        if len(res) != 0:
            return res
        return None

    def find_inspections(self, restaurant_id):
        """
        Searches for all inspections associated with the given restaurant.
        Returns an empty list if no matching inspections are found.
        """
        if not restaurant_id:
            raise InspError("No Restaurant Id", 404)
        c = self.conn.cursor()
        query_ins = """
            SELECT id, risk, inspection_date, inspection_type, results, violations
            FROM ri_inspections WHERE restaurant_id = ? ORDER BY id ASC
           """
        c.execute(query_ins, [restaurant_id])
        res = to_json_list(c)
        self.conn.commit()

        if len(res) != 0:
            return res

        return []

    def add_tt(self, think_tank):
        """
        Inserts a think tank into the DB.
        """
        try:
            nombre = think_tank['nombre']
            desc = think_tank['desc']
            comments = think_tank['comments']
            web = think_tank['web']
            twitter = think_tank['twitter']
            contacto_g = think_tank['contacto_g']
            contacto_t_nombre = think_tank['contacto_t_nombre']
            contacto_t_puesto = think_tank['contacto_t_puesto']
            contacto_t_correo = think_tank['contacto_t_correo']
            contacto_t_tel = think_tank['contacto_t_tel']
            temas = think_tank['temas']
            posicion_pol = ', '.join(think_tank['posicion_pol'])
            fin_disp = think_tank['fin_disp']
            fin_total = think_tank['fin_total']
            fin_dem = think_tank['fin_dem']
            fin_rep = think_tank['fin_rep']
            estudios = think_tank['estudios']
            fuentes = think_tank['fuentes']

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

        c = self.conn.cursor()

        look_tt = """ SELECT nombre FROM think_tanks
        WHERE nombre = ?
        """
        ya_existe = c.execute(look_tt, [nombre]).fetchall()
        subm = "repeated"
        if not ya_existe:
            insert_tt = """INSERT INTO think_tanks (nombre, desc, comments, web, twitter, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, estudios, fuentes)
            VALUES (UPPER(?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            c.execute(insert_tt, [nombre, desc, comments, web, twitter, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, estudios, fuentes])
            subm = "successful"
            self.conn.commit()
            return "El siguiente Think Tank se agregó correctamente a la base de datos: " + nombre, subm
        else:
            return "El siguiente Think Tank ya se encontraba en la base de datos: " + nombre, subm

        return {"restaurant_id":restaurant_id}, subm ########## creo que borrar


    def add_otros(self, otros):
        """
        Inserts a new other stakeholder into the DB.
        """
        try:
            nombre = otros['nombre']
            tipo = otros['tipo']
            industria = otros['industria']
            desc = otros['desc']
            miembros = otros['miembros']
            ubicacion = otros['ubicacion']
            comments = otros['comments']
            web = otros['web']
            twitter = otros['twitter']
            facebook = otros['facebook']
            youtube = otros['youtube']
            otro_medio = otros['otro_medio']
            contacto_g = otros['contacto_g']
            contacto_t_nombre = otros['contacto_t_nombre']
            contacto_t_puesto = otros['contacto_t_puesto']
            contacto_t_correo = otros['contacto_t_correo']
            contacto_t_tel = otros['contacto_t_tel']
            temas = otros['temas']
            posicion_pol = ', '.join(otros['posicion_pol'])
            fin_disp = otros['fin_disp']
            fin_total = otros['fin_total']
            fin_dem = otros['fin_dem']
            fin_rep = otros['fin_rep']
            estudios = otros['estudios']
            fuentes = otros['fuentes']

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

        c = self.conn.cursor()

        look_tt = """ SELECT nombre FROM otros_actores
        WHERE nombre = ?
        """
        ya_existe = c.execute(look_tt, [nombre]).fetchall()
        subm = "repeated"
        if not ya_existe:
            insert_tt = """INSERT INTO otros_actores (nombre, tipo, industria, desc, miembros, ubicacion, comments, web, twitter, facebook, youtube, otro_medio, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, estudios, fuentes)
            VALUES (UPPER(?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            c.execute(insert_tt, [nombre, tipo, industria, desc, miembros, ubicacion, comments, web, twitter, facebook, youtube, otro_medio, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, estudios, fuentes])
            subm = "successful"
            self.conn.commit()
            return "El siguiente stakeholder se agregó correctamente a la base de datos: " + nombre, subm
        else:
            return "El siguiente stakeholder ya se encontraba en la base de datos: " + nombre, subm

        return {"restaurant_id":restaurant_id}, subm ########## creo que borrar


    def add_emp(self, emp):
        """
        Inserts a new business organization stakeholder into the DB.
        """
        try:
            nombre = emp['nombre']
            acronimo = emp['acronimo']
            industria = emp['industria']
            hs = emp['hs']
            web = emp['web']
            desc = emp['desc']
            comments = emp['comments']
            miembros = emp['miembros']
            ubicacion = emp['ubicacion']
            contacto_g = emp['contacto_g']
            contacto_t_nombre = emp['contacto_t_nombre']
            contacto_t_puesto = emp['contacto_t_puesto']
            contacto_t_correo = emp['contacto_t_correo']
            contacto_t_tel = emp['contacto_t_tel']
            temas = emp['temas']
            posicion_pol = ', '.join(emp['posicion_pol'])
            fin_disp = emp['fin_disp']
            fin_total = emp['fin_total']
            fin_dem = emp['fin_dem']
            fin_rep = emp['fin_rep']
            lobbying_disp = emp['lobbying_disp']
            lobbying_total = emp['lobbying_total']
            exp_mex = emp['exp_mex']
            mkt_share = emp['mkt_share']
            empleos = emp['empleos']
            edos_op = emp['edos_op']
            estudios = emp['estudios']
            twitter = emp['twitter']
            facebook = emp['facebook']
            youtube = emp['youtube']

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

        c = self.conn.cursor()

        look_tt = """ SELECT nombre FROM organizaciones_emp
        WHERE nombre = ?
        """
        ya_existe = c.execute(look_tt, [nombre]).fetchall()
        subm = "repeated"
        if not ya_existe:
            insert_tt = """INSERT INTO organizaciones_emp (nombre, acronimo, industria, hs, web, desc, comments, miembros, ubicacion, contacto_g, contacto_t_nombre, 
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, lobbying_disp, lobbying_total, exp_mex, mkt_share, empleos, edos_op, estudios, twitter, facebook, youtube)
            VALUES (UPPER(?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            c.execute(insert_tt, [nombre, acronimo, industria, hs, web, desc, comments, miembros, ubicacion, contacto_g, contacto_t_nombre, 
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, lobbying_disp, lobbying_total, exp_mex, mkt_share, empleos, edos_op, estudios, twitter, facebook, youtube])
            subm = "successful"
            self.conn.commit()
            return "La siguiente organización empresarial se agregó correctamente a la base de datos: " + nombre, subm
        else:
            return "La siguiente organización empresarial ya se encontraba en la base de datos: " + nombre, subm

        return {"restaurant_id":restaurant_id}, subm ########## creo que borrar
    

    def edit_cp(self, congresista, id_cp, congress_person):
        """
        Permite editar la información de un congresista en la BD.
        """
        try:
            comments = congresista['comments']
            bitacora = congresista['bitacora']
            fuentes = congresista['fuentes']
            staffers = congresista['staffers']

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

        c = self.conn.cursor()

        look_cp = """ SELECT id FROM congresistas
        WHERE id = ?
        """
        ya_existe = c.execute(look_cp, [id_cp]).fetchall()
        subm = "repeated"
        ############## modificar lo de los edits de nombres
        if ya_existe:
            delete_cp = """ DELETE FROM congresistas
            WHERE id = ?
            """
            c.execute(delete_cp, [id_cp])

        insert_tt = """INSERT INTO congresistas (id, comments, bitacora, fuentes, staffers) 
        VALUES (?, ?, ?, ?, ?)"""
        c.execute(insert_tt, [id_cp, comments, bitacora, fuentes, staffers])
        subm = "successful"
        self.conn.commit()
        return "El siguiente congresista se actualizó correctamente en la base de datos: " + congress_person, subm

        #return {"restaurant_id":restaurant_id}, subm ########## creo que borrar


    def edit_tt(self, think_tank, tt_nombre_inicial):
        """
        Permite editar la información de un think tank en la BD.
        """
        try:
            nombre = think_tank['nombre']
            desc = think_tank['desc']
            comments = think_tank['comments']
            web = think_tank['web']
            twitter = think_tank['twitter']
            contacto_g = think_tank['contacto_g']
            contacto_t_nombre = think_tank['contacto_t_nombre']
            contacto_t_puesto = think_tank['contacto_t_puesto']
            contacto_t_correo = think_tank['contacto_t_correo']
            contacto_t_tel = think_tank['contacto_t_tel']
            temas = think_tank['temas']
            posicion_pol = ', '.join(think_tank['posicion_pol'])
            fin_disp = think_tank['fin_disp']
            fin_total = think_tank['fin_total']
            fin_dem = think_tank['fin_dem']
            fin_rep = think_tank['fin_rep']
            estudios = think_tank['estudios']
            fuentes = think_tank['fuentes']

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

        c = self.conn.cursor()

        look_tt = """ SELECT nombre FROM think_tanks
        WHERE nombre = ?
        """
        ya_existe = c.execute(look_tt, [tt_nombre_inicial]).fetchall()
        subm = "repeated"
        ############## modificar lo de los edits de nombres
        if ya_existe:
            delete_tt = """ DELETE FROM think_tanks
            WHERE nombre = ?
            """
            c.execute(delete_tt, [tt_nombre_inicial])

            insert_tt = """INSERT INTO think_tanks (nombre, desc, comments, web, twitter, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, estudios, fuentes)
            VALUES (UPPER(?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            c.execute(insert_tt, [nombre, desc, comments, web, twitter, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, estudios, fuentes])
            subm = "successful"
            self.conn.commit()
            return "El siguiente Think Tank se actualizó correctamente en la base de datos: " + nombre, subm
        else:
            return "El nombre del siguiente Think Tank ya se encuentra en la base de datos: " + nombre, subm

        return {"restaurant_id":restaurant_id}, subm ########## creo que borrar


    def edit_emp(self, emp, emp_nombre_inicial):
        """
        Permite editar la información de un think tank en la BD.
        """
        try:
            nombre = emp['nombre']
            acronimo = emp['acronimo']
            industria = emp['industria']
            hs = emp['hs']
            miembros = emp['miembros']
            ubicacion = emp['ubicacion']
            desc = emp['desc']
            comments = emp['comments']
            web = emp['web']
            twitter = emp['twitter']
            facebook = emp['facebook']
            youtube = emp['youtube']
            contacto_g = emp['contacto_g']
            contacto_t_nombre = emp['contacto_t_nombre']
            contacto_t_puesto = emp['contacto_t_puesto']
            contacto_t_correo = emp['contacto_t_correo']
            contacto_t_tel = emp['contacto_t_tel']
            temas = emp['temas']
            posicion_pol = ', '.join(emp['posicion_pol'])
            fin_disp = emp['fin_disp']
            fin_total = emp['fin_total']
            fin_dem = emp['fin_dem']
            fin_rep = emp['fin_rep']
            lobbying_disp = emp['lobbying_disp']
            lobbying_total = emp['lobbying_total']
            exp_mex = emp['exp_mex']
            mkt_share = emp['mkt_share']
            empleos = emp['empleos']
            edos_op = emp['edos_op']
            estudios = emp['estudios']
            #fuentes = emp['fuentes']

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

        c = self.conn.cursor()

        look_tt = """ SELECT nombre FROM organizaciones_emp
        WHERE nombre = ?
        """
        ya_existe = c.execute(look_tt, [emp_nombre_inicial]).fetchall()
        subm = "repeated"
        ############## modificar lo de los edits de nombres
        if ya_existe:
            delete_tt = """ DELETE FROM organizaciones_emp
            WHERE nombre = ?
            """
            c.execute(delete_tt, [emp_nombre_inicial])

            insert_tt = """INSERT INTO organizaciones_emp (nombre, acronimo, industria, hs, web, desc, comments, miembros, ubicacion, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, lobbying_disp, lobbying_total, exp_mex, mkt_share, empleos, edos_op, estudios, twitter, facebook, youtube)
            VALUES (UPPER(?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            c.execute(insert_tt, [nombre, acronimo, industria, hs, web, desc, comments, miembros, ubicacion, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, lobbying_disp, lobbying_total, exp_mex, mkt_share, empleos, edos_op, estudios, twitter, facebook, youtube])
            subm = "successful"
            self.conn.commit()
            return "La siguiente Organización Empresarial se actualizó correctamente en la base de datos: " + nombre, subm
        else:
            return "La siguiente Organización Empresarial ya se encontraba en la base de datos: " + nombre, subm

        return {"restaurant_id":restaurant_id}, subm ########## creo que borrar


    def edit_otros(self, otros, otro_nombre_inicial):
        """
        Permite editar la información de un stakeholder en la BD.
        """
        try:
            nombre = otros['nombre']
            tipo = otros['tipo']
            industria = otros['industria']
            desc = otros['desc']
            miembros = otros['miembros']
            ubicacion = otros['ubicacion']
            comments = otros['comments']
            web = otros['web']
            twitter = otros['twitter']
            facebook = otros['facebook']
            youtube = otros['youtube']
            otro_medio = otros['otro_medio']
            contacto_g = otros['contacto_g']
            contacto_t_nombre = otros['contacto_t_nombre']
            contacto_t_puesto = otros['contacto_t_puesto']
            contacto_t_correo = otros['contacto_t_correo']
            contacto_t_tel = otros['contacto_t_tel']
            temas = otros['temas']
            posicion_pol = ', '.join(otros['posicion_pol'])
            fin_disp = otros['fin_disp']
            fin_total = otros['fin_total']
            fin_dem = otros['fin_dem']
            fin_rep = otros['fin_rep']
            estudios = otros['estudios']
            fuentes = otros['fuentes']

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

        c = self.conn.cursor()

        look_tt = """ SELECT nombre FROM otros_actores
        WHERE nombre = ?
        """
        ya_existe = c.execute(look_tt, [otro_nombre_inicial]).fetchall()
        subm = "repeated"
        ############## modificar lo de los edits de nombres
        if ya_existe:
            delete_tt = """ DELETE FROM otros_actores
            WHERE nombre = ?
            """
            c.execute(delete_tt, [otro_nombre_inicial])

            insert_tt = """INSERT INTO otros_actores (nombre, tipo, industria, desc, miembros, ubicacion, comments, web, twitter, facebook, youtube, otro_medio, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, estudios, fuentes)
            VALUES (UPPER(?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            c.execute(insert_tt, [nombre, tipo, industria, desc, miembros, ubicacion, comments, web, twitter, facebook, youtube, otro_medio, contacto_g, contacto_t_nombre,
            contacto_t_puesto, contacto_t_correo, contacto_t_tel, temas, posicion_pol, fin_disp, fin_total, fin_dem,
            fin_rep, estudios, fuentes])
            subm = "successful"
            self.conn.commit()
            return "El siguiente Stakeholder se actualizó correctamente en la base de datos: " + nombre, subm
        else:
            return "El nombre del siguiente Stakeholder ya se encontraba en la base de datos: " + nombre, subm

        return {"restaurant_id":restaurant_id}, subm ########## creo que borrar


    def get_tt_list(self):
        """
        Devuelve la lista de think tanks en orden alfabético.
        """
        try:
            look_tt = """ SELECT nombre FROM think_tanks
            ORDER BY nombre
            """
            c = self.conn.cursor()
            think_tanks = c.execute(look_tt).fetchall()
            think_tanks_nombres = [think_tank[0] for think_tank in think_tanks]
            #headers = [d[0] for d in cursor.description]
            return think_tanks_nombres

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

    
    def get_emp_list(self):
        """
        Devuelve la lista de las organizaciones empresariales en orden alfabético.
        """
        try:
            look_tt = """ SELECT nombre FROM organizaciones_emp
            ORDER BY nombre
            """
            c = self.conn.cursor()
            emps = c.execute(look_tt).fetchall()
            emps_nombres = [emp[0] for emp in emps]
            #headers = [d[0] for d in cursor.description]
            return emps_nombres

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")


    
    def get_otros_list(self):
        """
        Devuelve la lista de otros stakeholders en orden alfabético.
        """
        try:
            look_tt = """ SELECT nombre FROM otros_actores
            ORDER BY nombre
            """
            c = self.conn.cursor()
            otros = c.execute(look_tt).fetchall()
            otros_nombres = [think_tank[0] for think_tank in otros]
            #headers = [d[0] for d in cursor.description]
            return otros_nombres

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

    
    def get_tt(self, think_tank):
        """
        Devuelve la info de un think tanks en específico.
        """
        try:
            look_tt = """ SELECT * FROM think_tanks
            WHERE nombre = ?
            """
            c = self.conn.cursor()
            c.execute(look_tt, [think_tank])
            return to_json_list(c)[0]

            #headers = [d[0] for d in cursor.description]
            #return think_tanks_nombres

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")


    def get_emp(self, emp):
        """
        Devuelve la info de una organización empresarial en específico.
        """
        try:
            look_tt = """ SELECT * FROM organizaciones_emp
            WHERE nombre = ?
            """
            c = self.conn.cursor()
            c.execute(look_tt, [emp])
            return to_json_list(c)[0]

            #headers = [d[0] for d in cursor.description]
            #return think_tanks_nombres

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

    
    def get_otros(self, otro):
        """
        Devuelve la info de un stakeholder en específico.
        """
        try:
            look_tt = """ SELECT * FROM otros_actores
            WHERE nombre = ?
            """
            c = self.conn.cursor()
            c.execute(look_tt, [otro])
            return to_json_list(c)[0]

            #headers = [d[0] for d in cursor.description]
            #return think_tanks_nombres

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

    
    def get_cp(self, id_cp):
        """
        Devuelve la info de un congresista en específico almacenada en la BD.
        """
        try:
            look_cp = """ SELECT * FROM congresistas
            WHERE id = ?
            """
            c = self.conn.cursor()
            c.execute(look_cp, [id_cp])
            results = to_json_list(c)
            if results:
                return results[0]
            return {}

            #headers = [d[0] for d in cursor.description]
            #return think_tanks_nombres

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

    
    def get_comite(self, id_cp):
        """
        Devuelve la info de un comité en específico almacenada en la BD.
        """
        try:
            look_cp = """ SELECT * FROM comites
            WHERE codigo = ?
            """

            c = self.conn.cursor()
            c.execute(look_cp, [id_cp])
            results = to_json_list(c)
            if results:
                return results[0]
            return {}

            #headers = [d[0] for d in cursor.description]
            #return think_tanks_nombres

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")


    def add_inspection_for_restaurant(self, inspection, restaurant):
        """
        Finds or creates the restaurant then inserts the inspection and
        associates it with the restaurant.
        """
        try:
            id_insp = inspection['id']
            risk = inspection['risk']
            inspection_date = inspection['inspection_date']
            inspection_type = inspection['inspection_type']
            results = inspection['results']
            violations = inspection['violations']

            name = restaurant['name']
            facility_type = restaurant['facility_type']
            address = restaurant['address']
            city = restaurant['city']
            state = restaurant['state']
            zip = restaurant['zip']
            latitude = restaurant['latitude']
            longitude = restaurant['longitude']
            clean = restaurant['clean']

        except KeyError as e:
            raise BadRequest(message="Required attribute is missing")

        c = self.conn.cursor()

        look_rest = """ SELECT id FROM ri_restaurants
        WHERE name = ? AND facility_type = ? AND address = ? AND city = ? AND state = ? AND zip = ?
        """
        restaurant_id = c.execute(look_rest, [name, facility_type, address, city, state, zip]).fetchall()
        resp_no = 200
        if not restaurant_id:
            insert_rest = """INSERT INTO ri_restaurants (name, facility_type, address, city, state, zip, latitude, longitude, clean)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            c.execute(insert_rest, [name, facility_type, address, city, state, zip, latitude, longitude, clean])
            restaurant_id = c.execute(look_rest, [name, facility_type, address, city, state, zip]).fetchall()
            resp_no = 201
        restaurant_id = restaurant_id[0][0]

        insert_ins = """INSERT INTO ri_inspections (id, risk, inspection_date, inspection_type, results, violations, restaurant_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)"""
        c.execute(insert_ins, [id_insp, risk, inspection_date, inspection_type, results, violations, restaurant_id])

        return {"restaurant_id":restaurant_id}, resp_no

    def inspections_commiter(self):
        '''
        Commits transactions to the DB
        '''
        self.conn.commit()

    def inspections_aborter(self):
        '''
        Aborts/rollback transactions
        '''
        self.conn.rollback()

    def rest_tweet_matcher(self, tweet):
        """
        Matches restaurants with tweets by location or name.
        """

        c = self.conn.cursor()

        rest_names = tweet['rest_names']
        # In case you want case folding on the name
        questionmarks = ['lower(?)'] * len(rest_names)
        # Another way of executing a query with named parameters
        query_rest = """
            SELECT id, name, latitude, longitude FROM ri_restaurants 
            WHERE (ABS(latitude - ?) < 0.00225001 AND ABS(longitude - ?) < 0.00302190)
            OR lower(name) in (%s)
            ORDER BY id
           """ % (",").join(questionmarks)

        c.execute(query_rest, [tweet['lat'], tweet['long']] + rest_names)                        
        results = to_json_list(c)

        for rest_ind in range(len(rest_names)):
            rest_names[rest_ind] = rest_names[rest_ind].upper()

        restaurants = []
        for result in results:
            restaurants.append(result['id'])
            cond_1 = result['name'] in rest_names
            cond_2 = False
            if tweet['lat'] != '' or tweet['long'] != '':
                cond_2 = abs(result['latitude'] - tweet['lat']) < 0.00225001 and abs(result['longitude'] - tweet['long']) < 0.00302190
            if cond_1 and not cond_2:
                match = 'name'
            if cond_1 and cond_2:
                match = 'both'
            if cond_2 and not cond_1:
                match = 'geo'

            insert_match = """INSERT INTO ri_tweetmatch (tkey, restaurant_id, match)
            VALUES (?, ?, ?)"""
            c.execute(insert_match, [tweet['key'], result['id'], match])
        self.conn.commit()

        return restaurants

    def find_rest_tweets(self, restaurant_id):
        """
        Find tweets associated with a given restaurant.
        """
        if not restaurant_id:
            raise InspError("No Restaurant Id", 404)

        c = self.conn.cursor()
        
        # Another way of executing a query with named parameters
        query_rest = """
            SELECT tkey, match FROM ri_tweetmatch WHERE restaurant_id = ? ORDER BY tkey
           """
        c.execute(query_rest, [restaurant_id])       
        self.conn.commit()                 
        res = to_json_list(c)

        if len(res) == 0:
            return None
        return res


    def restaurant_cleaning(self, rest_block):
        c = self.conn.cursor()
        query_rest = """
            SELECT id, name, address, city, state, zip, facility_type, latitude, longitude
            FROM """ + rest_block + """ WHERE clean = 0 """
        c.execute(query_rest)
        unclean_restaurants = to_json_list(c)

        query_rest = """
            SELECT id, name, address, city, state, zip , facility_type, latitude, longitude
            FROM """ + rest_block + """ WHERE clean = 1 """
        c.execute(query_rest)
        clean_restaurants = to_json_list(c)

        auth_ids = {}
        while len(clean_restaurants) > 0:
            restaurant = clean_restaurants[0]
            auth_ids[restaurant['id']] = set()
            auth_ids[restaurant['id']].add(restaurant[id])
            new_unclean = []
            for other_rests in unclean_restaurants:
                if similar_rests(restaurant, other_rests):
                    auth_ids[restaurant['id']].add(other_rests['id'])
                    update_record = """UPDATE ri_restaurants
                    SET clean = 1
                    WHERE id = ?"""
                    c.execute(update_record, [other_rests['id']])
                else:
                    new_unclean.append(other_rests)
            unclean_restaurants = new_unclean

        while len(unclean_restaurants) > 0:
            if len(unclean_restaurants) == 1:
                auth_rest = unclean_restaurants[0]
                auth_ids[auth_rest['id']] = set()
                auth_ids[auth_rest['id']].add(auth_rest['id'])
                update_record = """UPDATE ri_restaurants
                SET clean = 1
                WHERE id = ?"""
                c.execute(update_record, [auth_rest['id']])
                unclean_restaurants = []
            else:
                restaurant = unclean_restaurants[0]
                unclean_restaurants = unclean_restaurants[1:]
                rest_simils = []
                rest_simils.append(restaurant)
                rest_simils_ids = set()
                rest_simils_ids.add(restaurant['id'])
                new_unclean = []
                for other_rests in unclean_restaurants:
                    if similar_rests(restaurant, other_rests):
                        rest_simils.append(other_rests)
                        rest_simils_ids.add(other_rests['id'])
                        update_record = """UPDATE ri_restaurants
                        SET clean = 1
                        WHERE id = ?"""
                        c.execute(update_record, [other_rests['id']])
                    else:
                        new_unclean.append(other_rests)
                
                auth_rest = authoritarian_restaurant(rest_simils)
                auth_id = auth_rest['id']

                update_record = """UPDATE ri_restaurants
                SET name = ?, facility_type = ?, address = ?, city = ?, state = ?, zip = ?, latitude = ?, longitude = ?
                WHERE id = ?"""
                c.execute(update_record, [auth_rest['name'], auth_rest['facility_type'], auth_rest['address'], auth_rest['city'],
                auth_rest['state'], auth_rest['zip'], auth_rest['latitude'], auth_rest['longitude'], auth_id])
                auth_ids[auth_id] = rest_simils_ids
                unclean_restaurants = new_unclean

        c = self.restaurant_links(auth_ids, c)
        self.conn.commit()     

    def restaurant_links(self, auth_ids, c):
        for primary_id, linked_ids in auth_ids.items():
            for original_id in linked_ids:
                insert_links = """INSERT INTO ri_linked (primary_rest_id, original_rest_id)
                VALUES (?, ?)"""
                c.execute(insert_links, [primary_id, original_id])
        
        return c

    def get_primary_restuarant_id(self, rest_id):
        c = self.conn.cursor()
        query_rest = """
            SELECT primary_rest_id, original_rest_id
            FROM ri_linked
            WHERE primary_rest_id = (SELECT primary_rest_id
            FROM ri_linked
            WHERE original_rest_id = ? )
            ORDER BY original_rest_id ASC
           """
        c.execute(query_rest, [rest_id])
        restaurants_ids = to_json_list(c)
        primary_rest_id = restaurants_ids[0]['primary_rest_id']
        
        non_primary_rest_id = []
        for id in restaurants_ids:
            if id['original_rest_id'] != primary_rest_id:
                non_primary_rest_id.append(id['original_rest_id'])
        self.conn.commit()

        return primary_rest_id, non_primary_rest_id

    def blocking(self):
        '''
        Create the blocks to run the cleaning process.
        '''
        c = self.conn.cursor()
        query_zips = """
            SELECT DISTINCT zip
            FROM ri_restaurants
            """
        c.execute(query_zips)
        zips = to_json_list(c)
        
        for zip in zips:
            zip_block = zip['zip']
            zip_block_name = 'block_' + zip_block

            drop_table_q = """DROP TABLE IF EXISTS """ + zip_block_name
            c.execute(drop_table_q)


            create_block = """
                CREATE TEMPORARY TABLE """ + zip_block_name + """
                (id integer PRIMARY KEY,
                name varchar(60) NOT NULL,
                facility_type varchar(30),
                address varchar(60),
                city varchar(30),
                state char(2),
                zip char(5),
                latitude real,
                longitude real,
                clean boolean DEFAULT FALSE)
                """
            c.execute(create_block)

            query_blocks = """
                INSERT INTO """ + zip_block_name + """
                SELECT *
                FROM ri_restaurants
                WHERE zip = ?
                """
            c.execute(query_blocks, [zip_block])

            query_block_index = """
                CREATE INDEX alphabet_name""" + zip_block_name + """
                ON """ + zip_block_name + """ (clean)     
                """
            c.execute(query_block_index)
            
            self.conn.commit()
            rest_block = 'block_' + str(zip_block)
            self.restaurant_cleaning(rest_block)


    # Simple example of how to execute a query against the DB.
    # Again NEVER do this, you should only execute parameterized query
    # See https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.execute
    # This is the qmark style:
    # cur.execute("insert into people values (?, ?)", (who, age))
    # And this is the named style:
    # cur.execute("select * from people where name_last=:who and age=:age", {"who": who, "age": age})
    def run_query(self, query):
        c = self.conn.cursor()
        c.execute(query)
        res =to_json_list(c)
        self.conn.commit()
        return res
