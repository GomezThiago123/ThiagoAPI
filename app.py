from math import ceil
import sqlite3
from flask import Flask, g, jsonify, request, url_for

def dict_factory(cursor, row):
  """Arma un diccionario con los valores de la fila."""
  fields = [column[0] for column in cursor.description]
  return {key: value for key, value in zip(fields, row)}

def abrirConexion():
   if 'db' not in g:
      g.db = sqlite3.connect("api.sqlite")
      g.db.row_factory = dict_factory
   return g.db

def cerrarConexion(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

app = Flask(__name__)
app.teardown_appcontext(cerrarConexion)
resultados_por_pag = 10
@app.route("/api/artista")
def artistas():
    args = request.args
    pagina = int(args.get('page', '1'))
    descartar = (pagina-1) * resultados_por_pag
    db = abrirConexion()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) AS cant FROM artists;")
    cant = cursor.fetchone()['cant']
    paginas = ceil(cant / resultados_por_pag)

    if pagina <1 or pagina > paginas:
       return jsonify({"Error": "pagina no existente"}), 400
    
    cursor.execute(""" SELECT ArtistId, Name 
                        FROM artists LIMIT ? OFFSET ?; """, 
                        (resultados_por_pag,descartar))
    lista = cursor.fetchall()
    cerrarConexion()
    siguiente = None
    anterior = None
    if pagina > 1:
       anterior = url_for('artistas', page=pagina-1)
    if pagina < paginas:
       siguiente = url_for('artistas', page=pagina+1)
    info = { 'count' : cant, 'pages': paginas,
             'next' : siguiente, 'prev' : anterior }
    res = { 'info' : info, 'results' : lista}
    return jsonify(res)

@app.route("/api/genero")
def generos():
    args = request.args
    pagina = int(args.get('page', '1'))
    descartar = (pagina - 1) * resultados_por_pag
    db = abrirConexion()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) AS cant FROM genres;")
    cant = cursor.fetchone()['cant']
    paginas = ceil(cant / resultados_por_pag)

    if pagina <1 or pagina > paginas:
       return jsonify({"Error": "pagina no existente"}), 400

    cursor.execute(""" SELECT GenreId, Name 
                       FROM genres LIMIT ? OFFSET ?; """,
                   (resultados_por_pag, descartar))
    lista = cursor.fetchall()
    cerrarConexion()

    siguiente = None
    anterior = None
    if pagina > 1:
        anterior = url_for('generos', page=pagina - 1)
    if pagina < paginas:
        siguiente = url_for('generos', page=pagina + 1)

    info = {'count': cant, 'pages': paginas,
            'next': siguiente, 'prev': anterior}
    res = {'info': info, 'results': lista}
    return jsonify(res)
@app.route("/api/artista/<int:id>")
def artista(id):
   db = abrirConexion()
   # esto tiene que devolver un json que represente un diccionario
   # con id, name y url (con la direccion de esta ruta, usar url_for)
   cursor = db.cursor()
   cursor.execute("SELECT ArtistId, Name FROM artists WHERE ArtistId = ?;", (id,))
   fila = cursor.fetchone()
   cerrarConexion()

   if fila is None:
      return jsonify({'error': 'Artista no encontrado'}), 404

   return jsonify({
      'id': fila['ArtistId'],
      'name': fila['Name'],
      'url': url_for('artista', id=id)
   })

@app.route("/api/album/<int:id>")
def album(id):
   db = abrirConexion()
   # esto tiene que devolver un json que represente un diccionario
   # con id, title y url (con la direccionde esta ruta, usar url_for)
   cursor = db.cursor()
   cursor.execute("SELECT AlbumId, Title FROM albums WHERE AlbumId = ?;", (id,))
   fila = cursor.fetchone()
   cerrarConexion()

   if fila is None:
      return jsonify({'error': 'Álbum no encontrado'}), 404

   return jsonify({
      'id': fila['AlbumId'],
      'title': fila['Title'],
      'url': url_for('album', id=id)
   })
